import pandas as pd
import random
import re

# ================= CONFIG HUB =================
import os
FILE = os.path.join(os.path.dirname(__file__), "routes.xlsx")


HUBS = {
    "WIII": 5,
    "WAAA": 3,
    "WADD": 3,
    "WARR": 2,
    "WALL": 2
}

MAX_TOTAL_HOURS = 8.0
MAX_LEG = 4
# =========================================

df = pd.read_excel(FILE)

routes = {}
route_detail = {}

icao_pattern = re.compile(r"\(([A-Z]{4})\)")

# ========== UTIL ==========
def split_aircraft(ac_str):
    return [a.strip() for a in ac_str.split("//") if a.strip()]

def parse_flight_time(value):
    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    try:
        parts = value.split(":")
        h = int(parts[0])
        m = int(parts[1])
        s = int(parts[2]) if len(parts) == 3 else 0
        return round(h + m/60 + s/3600, 2)
    except:
        return None

def hours_to_hhmm(hours):
    total_minutes = int(round(hours * 60))
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"

def dynamic_leg_limit(total_hours):
    if total_hours < 3:
        return 4
    elif total_hours < 6:
        return 3
    elif total_hours < 8:
        return 2
    else:
        return 1

def weighted_origin():
    pool = []
    for o in routes:
        pool.extend([o] * HUBS.get(o, 1))
    return random.choice(pool)

# ===== LOAD DATABASE =====
for _, row in df.iterrows():
    try:
        dep = str(row.iloc[3])
        arr = str(row.iloc[5])
        aircraft_raw = str(row.iloc[8]).upper()
        hours = parse_flight_time(row.iloc[7])
    except:
        continue

    dep_m = icao_pattern.search(dep)
    arr_m = icao_pattern.search(arr)

    if not dep_m or not arr_m or hours is None:
        continue

    origin = dep_m.group(1)
    dest = arr_m.group(1)

    for ac in split_aircraft(aircraft_raw):
        routes.setdefault(origin, []).append(dest)
        route_detail.setdefault(origin, []).append((dest, ac, hours))

print("Database loaded.")
print("Total origins:", len(routes))

# ========== MODE 2 au ah ==========
def advanced_mode():
    while True:
        origin_input = input("Origin ICAO / AUTO / exit: ").strip().upper()
        if origin_input == "EXIT":
            break

        origin = weighted_origin() if origin_input in ["", "AUTO"] else origin_input
        if origin not in routes:
            print("Origin tidak ditemukan.\n")
            continue

        aircraft_available = sorted(set(ac for _, ac, _ in route_detail[origin]))

        print(f"\nPesawat tersedia dari {origin}:")
        for i, ac in enumerate(aircraft_available, 1):
            print(f"{i}. {ac}")

        try:
            aircraft_selected = aircraft_available[int(input("Pilih pesawat: ")) - 1]
        except:
            print("Input invalid.\n")
            continue

        current = origin
        flown = []
        total_hours = 0.0

        for _ in range(MAX_LEG):
            options = [
                (d, h) for d, ac, h in route_detail[current]
                if ac == aircraft_selected and total_hours + h <= MAX_TOTAL_HOURS
            ]

            if not options:
                break

            dest, h = random.choice(options)
            flown.append((current, dest, aircraft_selected, h))
            total_hours += h
            current = dest

        print("\nFlight sequence:")
        for o, d, ac, h in flown:
            print(f" {o} → {d} | {ac} | {hours_to_hhmm(h)}")

        print("Total time:", hours_to_hhmm(total_hours), "\n")

# ========== MODE expert uy ==========
def mixed_aircraft_mode():
    while True:
        origin_input = input("Origin ICAO / AUTO / exit: ").strip().upper()
        if origin_input == "EXIT":
            break

        current = weighted_origin() if origin_input in ["", "AUTO"] else origin_input
        if current not in routes:
            print("Origin tidak ditemukan.\n")
            continue

        flown = []
        total_hours = 0.0

        for _ in range(dynamic_leg_limit(total_hours)):
            options = [
                (d, ac, h) for d, ac, h in route_detail[current]
                if total_hours + h <= MAX_TOTAL_HOURS
            ]

            if not options:
                break

            dest, ac, h = random.choice(options)
            flown.append((current, dest, ac, h))
            total_hours += h
            current = dest

        print("\nFlight sequence (mixed aircraft):")
        for o, d, ac, h in flown:
            print(f" {o} → {d} | {ac} | {hours_to_hhmm(h)}")

        print("Total time:", hours_to_hhmm(total_hours), "\n")

# ========== MENU ==========
while True:
    print("=== PILOT ROUTE SIM ===")
    print("1. Simple random route")
    print("2. Advanced (single aircraft)")
    print("3. Mixed aircraft rotation")
    print("0. Exit")

    choice = input("Pilih mode: ").strip()

    if choice == "1":
        o = input("Origin ICAO: ").strip().upper()
        if o in routes:
            print(f"{o} → {random.choice(routes[o])}\n")
        else:
            print("Origin tidak ditemukan.\n")

    elif choice == "2":
        advanced_mode()

    elif choice == "3":
        mixed_aircraft_mode()

    elif choice == "0":
        print("Program selesai.")
        break

    else:
        print("Pilihan tidak valid.\n")
