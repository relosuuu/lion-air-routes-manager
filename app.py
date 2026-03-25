from flask import Flask, render_template, request
import sqlite3
import random
import os
import json
from icao_coords import ICAO_COORDS

app = Flask(__name__)

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "routes.db")


# Major hubs per airline — destinations matching these get a slight priority boost
AIRLINE_HUBS = {
    "lion":        {"WIII", "WAAA", "WARR", "WADD", "WALL"},
    "batik":       {"WIII", "WIHH", "WAAA", "WARR", "WADD", "WALL"},
    "superairjet": {"WIII", "WAAA", "WARR", "WADD"},
    "wings":       {"WIII", "WAAA", "WARR", "WADD"},
    "thailion":    {"VTBD"},
}

def get_hubs(airline):
    return AIRLINE_HUBS.get(airline.lower(), set())


# =========================
# DATABASE
# =========================
def get_direct_routes(airline, origin, aircraft=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    if aircraft:
        cur.execute("""
            SELECT destination, aircraft, flight_time
            FROM routes
            WHERE origin = ? COLLATE NOCASE
            AND airline = ? COLLATE NOCASE
            AND aircraft LIKE ?
        """, (origin.upper(), airline, f"%{aircraft}%"))
    else:
        cur.execute("""
            SELECT destination, aircraft, flight_time
            FROM routes
            WHERE origin = ? COLLATE NOCASE
            AND airline = ? COLLATE NOCASE
        """, (origin.upper(), airline))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_aircraft_for_airline(airline):
    """Return sorted list of distinct aircraft types for a given airline.
    Filters out any corrupted rows where a flight time ended up in the aircraft column.
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT aircraft
        FROM routes
        WHERE airline = ? COLLATE NOCASE
        ORDER BY aircraft
    """, (airline,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows if ":" not in r[0]]


def get_random_origin(airline):
    """Return a random origin airport for the given airline."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT origin FROM routes
        WHERE airline = ? COLLATE NOCASE
        ORDER BY RANDOM()
        LIMIT 1
    """, (airline,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


def parse_time(t):
    try:
        parts = t.strip().split(":")
        if len(parts) != 2:
            return 0
        h, m = parts
        if not h.isdigit() or not m.isdigit():
            return 0
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return 0


def generate_multi_leg(airline, departure, max_minutes=480, aircraft=None, allow_change=False):
    """
    Build a multi-leg route aiming for 3-5 legs close to max_minutes total.
    - While remaining time > 150 min: pick SHORT legs (<=120 min) to stack hops.
    - When remaining time <= 150 min: pick leg closest to remaining time.
    - Avoids revisiting airports but allows returning if truly stuck.
    - Hub destinations get a small priority boost (~2x more likely to be picked).
    - Runs 3 attempts, returns the one with the most legs.
    """
    best_chain = []
    best_total = 0
    hubs = get_hubs(airline)

    for _attempt in range(3):
        current = departure.upper()
        total_minutes = 0
        route_chain = []
        visited = set()
        last_visited = None

        for _hop in range(8):
            remaining = max_minutes - total_minutes
            if remaining <= 0:
                break

            routes = get_direct_routes(
                airline,
                current,
                None if allow_change else aircraft
            )

            # Block only the airport we just came from to prevent A->B->A bouncing
            blocked = {last_visited} if last_visited else set()

            # First: prefer unvisited airports
            forward_routes = [
                r for r in routes
                if r[0] not in blocked
                and r[0] not in visited
                and parse_time(r[2]) > 0
                and parse_time(r[2]) <= remaining
            ]

            # If no fresh airports, allow revisiting anything except last stop
            if not forward_routes:
                forward_routes = [
                    r for r in routes
                    if r[0] not in blocked
                    and parse_time(r[2]) > 0
                    and parse_time(r[2]) <= remaining
                ]

            # In mixed mode, DB returns multiple rows per destination (one per
            # aircraft type). Group by destination and pick one aircraft randomly
            # so all airports get equal chance AND aircraft variety is preserved.
            if allow_change:
                dest_groups = {}
                for r in forward_routes:
                    dest = r[0]
                    if dest not in dest_groups:
                        dest_groups[dest] = []
                    dest_groups[dest].append(r)
                forward_routes = [random.choice(options) for options in dest_groups.values()]

            if not forward_routes:
                break

            if remaining > 150:
                # Use all valid routes as the pool — no artificial slicing
                # This ensures every reachable airport has a chance to be picked
                pool = forward_routes

                # Slightly prefer shorter legs by weighting: each route gets
                # added extra times inversely proportional to its flight time
                # so short legs are more likely but long legs still appear
                weighted_pool = []
                for r in pool:
                    t = parse_time(r[2])
                    # Mild preference for shorter legs: weight 2 if <=120 min,
                    # weight 1 otherwise — keeps variety without heavy bias
                    weight = 2 if t <= 120 else 1
                    weighted_pool.extend([r] * weight)
            else:
                # Pick leg closest to remaining time to fill schedule
                forward_routes = sorted(forward_routes, key=lambda r: abs(parse_time(r[2]) - remaining))
                weighted_pool = forward_routes[:5]

            # Give hub destinations an extra boost on top
            hub_candidates = [r for r in weighted_pool if r[0] in hubs]
            weighted_pool = weighted_pool + hub_candidates
            dest, ac, time = random.choice(weighted_pool)

            route_chain.append((current, dest, ac, time))
            total_minutes += parse_time(time)
            visited.add(current)
            last_visited = current
            current = dest

        # Keep attempt with most legs; tiebreak by total time
        if len(route_chain) > len(best_chain) or (
            len(route_chain) == len(best_chain) and total_minutes > best_total
        ):
            best_chain = route_chain
            best_total = total_minutes

    return best_chain, best_total


# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/airline")
def airline_page():
    airline = request.args.get("airline")
    return render_template("airline.html", airline=airline)


@app.route("/route-form")
def route_form():
    airline = request.args.get("airline")
    route_type = request.args.get("type")
    aircraft_list = get_aircraft_for_airline(airline) if route_type == "single" else []
    return render_template(
        "route-form.html",
        airline=airline,
        route_type=route_type,
        aircraft_list=aircraft_list
    )


@app.route("/random-origin")
def random_origin():
    from flask import jsonify
    airline = request.args.get("airline")
    origin = get_random_origin(airline)
    return jsonify({"origin": origin})


@app.route("/generate", methods=["POST"])
def generate():
    airline = request.form.get("airline")
    route_type = request.form.get("type")
    departure = request.form.get("departure")
    aircraft = request.form.get("aircraft")
    aircraft_list = get_aircraft_for_airline(airline) if route_type == "single" else []

    if not departure:
        return render_template(
            "route-form.html",
            airline=airline,
            route_type=route_type,
            aircraft_list=aircraft_list,
            result="Please enter departure ICAO"
        )

    departure = departure.strip().upper()

    # If user typed "auto", pick a random origin for this airline
    if departure == "AUTO":
        departure = get_random_origin(airline)
        if not departure:
            return render_template(
                "route-form.html",
                airline=airline,
                route_type=route_type,
                aircraft_list=aircraft_list,
                result="No airports found for this airline."
            )

    if route_type == "random":
        routes = get_direct_routes(airline, departure, None)
        if not routes:
            result = f"No routes found from {departure} for {airline}. Check the ICAO code."
            route_chain_for_map = []
        else:
            dest, ac, time = random.choice(routes)
            result = f"{departure} → {dest} | {ac} | {time}"
            route_chain_for_map = [(departure, dest, ac, time)]

    elif route_type == "single":
        if not aircraft:
            return render_template(
                "route-form.html",
                airline=airline,
                route_type=route_type,
                aircraft_list=aircraft_list,
                result="Please select an aircraft type."
            )

        chain, total = generate_multi_leg(
            airline, departure, max_minutes=480,
            aircraft=aircraft, allow_change=False
        )

        if not chain:
            result = f"No routes found from {departure} with {aircraft} for {airline}."
            route_chain_for_map = []
        else:
            result = ""
            for o, d, ac, t in chain:
                result += f"{o} → {d} | {ac} | {t}\n"
            hours, minutes = total // 60, total % 60
            result += f"\nTotal Time: {hours:02d}:{minutes:02d}"
            route_chain_for_map = chain

    elif route_type == "mixed":
        chain, total = generate_multi_leg(
            airline, departure, max_minutes=480, allow_change=True
        )

        if not chain:
            result = f"No routes found from {departure} for {airline}."
            route_chain_for_map = []
        else:
            result = ""
            for o, d, ac, t in chain:
                result += f"{o} → {d} | {ac} | {t}\n"
            hours, minutes = total // 60, total % 60
            result += f"\nTotal Time: {hours:02d}:{minutes:02d}"
            route_chain_for_map = chain

    else:
        result = "Invalid route type"
        route_chain_for_map = []
        route_chain_for_map = []

    # Build map data from route chain
    map_airports = []
    map_legs = []
    seen_icao = []
    for o, d, ac, t in route_chain_for_map:
        if o not in seen_icao:
            seen_icao.append(o)
            if o in ICAO_COORDS:
                lat, lon = ICAO_COORDS[o]
                map_airports.append({"icao": o, "lat": lat, "lon": lon})
        if d not in seen_icao:
            seen_icao.append(d)
            if d in ICAO_COORDS:
                lat, lon = ICAO_COORDS[d]
                map_airports.append({"icao": d, "lat": lat, "lon": lon})
        if o in ICAO_COORDS and d in ICAO_COORDS:
            map_legs.append([list(ICAO_COORDS[o]), list(ICAO_COORDS[d])])

    return render_template(
        "route-form.html",
        airline=airline,
        route_type=route_type,
        aircraft_list=aircraft_list,
        result=result,
        map_airports=json.dumps(map_airports),
        map_legs=json.dumps(map_legs)
    )


if __name__ == "__main__":
    app.run(debug=True)