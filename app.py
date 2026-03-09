from flask import Flask, render_template, request
import sqlite3
import random

app = Flask(__name__)

DB = "routes.db"


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

    Strategy:
    - While remaining time > 150 min: pick SHORT legs (<=120 min) to stack hops.
    - When remaining time <= 150 min: pick leg closest to remaining time.
    - Never revisit an airport.
    - Runs 3 attempts, returns the one with the most legs.
    """
    best_chain = []
    best_total = 0

    for _attempt in range(3):
        current = departure.upper()
        total_minutes = 0
        route_chain = []
        visited = {current}

        for _hop in range(8):
            remaining = max_minutes - total_minutes
            if remaining <= 0:
                break

            routes = get_direct_routes(
                airline,
                current,
                None if allow_change else aircraft
            )

            # Filter: no revisits, valid time, must fit remaining budget
            routes = [
                r for r in routes
                if r[0] not in visited
                and parse_time(r[2]) > 0
                and parse_time(r[2]) <= remaining
            ]

            if not routes:
                break

            if remaining > 150:
                # Prefer short legs to keep chaining hops
                short = [r for r in routes if parse_time(r[2]) <= 120]
                pool = short if short else routes
                pool = sorted(pool, key=lambda r: parse_time(r[2]))
                candidates = pool[:5]
            else:
                # Pick leg that fills remaining time most snugly
                routes = sorted(routes, key=lambda r: abs(parse_time(r[2]) - remaining))
                candidates = routes[:3]

            dest, ac, time = random.choice(candidates)
            route_chain.append((current, dest, ac, time))
            total_minutes += parse_time(time)
            visited.add(dest)
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
    return render_template(
        "route-form.html",
        airline=airline,
        route_type=route_type
    )


@app.route("/generate", methods=["POST"])
def generate():
    airline = request.form.get("airline")
    route_type = request.form.get("type")
    departure = request.form.get("departure")
    aircraft = request.form.get("aircraft")

    if not departure:
        return render_template(
            "route-form.html",
            airline=airline,
            route_type=route_type,
            result="Please enter departure ICAO"
        )

    departure = departure.strip().upper()

    if route_type == "random":
        routes = get_direct_routes(airline, departure, None)

        if not routes:
            result = f"No routes found from {departure} for {airline}. Check the ICAO code."
        else:
            dest, ac, time = random.choice(routes)
            result = f"{departure} → {dest} | {ac} | {time}"

    elif route_type == "single":
        if not aircraft:
            return render_template(
                "route-form.html",
                airline=airline,
                route_type=route_type,
                result="Please select an aircraft type."
            )

        chain, total = generate_multi_leg(
            airline,
            departure,
            max_minutes=480,
            aircraft=aircraft,
            allow_change=False
        )

        if not chain:
            result = f"No routes found from {departure} with {aircraft} for {airline}."
        else:
            result = ""
            for o, d, ac, t in chain:
                result += f"{o} → {d} | {ac} | {t}\n"
            hours = total // 60
            minutes = total % 60
            result += f"\nTotal Time: {hours:02d}:{minutes:02d}"

    elif route_type == "mixed":
        chain, total = generate_multi_leg(
            airline,
            departure,
            max_minutes=480,
            allow_change=True
        )

        if not chain:
            result = f"No routes found from {departure} for {airline}."
        else:
            result = ""
            for o, d, ac, t in chain:
                result += f"{o} → {d} | {ac} | {t}\n"
            hours = total // 60
            minutes = total % 60
            result += f"\nTotal Time: {hours:02d}:{minutes:02d}"

    else:
        result = "Invalid route type"

    return render_template(
        "route-form.html",
        airline=airline,
        route_type=route_type,
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)