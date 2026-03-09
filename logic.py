import sqlite3
from datetime import timedelta

DB = "routes.db"

# ======================
# UTIL
# ======================
def parse_time(t):
    h, m = t.split(":")
    return timedelta(hours=int(h), minutes=int(m))


# ======================
# GET ROUTES
# ======================
def get_routes(origin, airline=None):
    origin = origin.strip().upper()
    if airline:
        airline = airline.strip().upper()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    if airline:
        cur.execute("""
            SELECT destination, aircraft, flight_time
            FROM routes
            WHERE origin = ? COLLATE NOCASE
            AND airline = ? COLLATE NOCASE
        """, (origin, airline))
    else:
        cur.execute("""
            SELECT destination, aircraft, flight_time
            FROM routes
            WHERE origin = ? COLLATE NOCASE
        """, (origin,))

    rows = cur.fetchall()
    conn.close()
    return rows


# ======================
# SIMPLE RANDOM (1 LEG)
# ======================
def simple_random(origin, airline=None, max_hours=8):
    origin = origin.strip().upper()
    rows = get_routes(origin, airline)

    max_time = timedelta(hours=max_hours)
    results = []

    for dest, ac, t in rows:
        try:
            ft = parse_time(t)
            if ft <= max_time:
                results.append({
                    "origin": origin,
                    "destination": dest,
                    "aircraft": ac,
                    "flight_time": t
                })
        except:
            continue

    return results


# ======================
# CONNECTING ROUTE (2 LEG)
# ======================
def two_leg_route(origin, airline=None, max_hours=8):
    origin = origin.strip().upper()
    max_time = timedelta(hours=max_hours)
    results = []

    first_legs = get_routes(origin, airline)

    for mid, ac1, t1 in first_legs:
        try:
            t1_td = parse_time(t1)
        except:
            continue

        second_legs = get_routes(mid, airline)

        for dest, ac2, t2 in second_legs:
            try:
                t2_td = parse_time(t2)
            except:
                continue

            total = t1_td + t2_td

            if total <= max_time and dest != origin:
                results.append({
                    "route": [origin, mid, dest],
                    "aircraft": [ac1, ac2],
                    "total_time": str(total)
                })

    return results