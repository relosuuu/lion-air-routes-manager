import sqlite3

conn = sqlite3.connect("routes.db")
cur = conn.cursor()


cur.execute("""
CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    airline TEXT,
    origin TEXT,
    destination TEXT,
    aircraft TEXT,
    flight_time TEXT,
    UNIQUE(airline, origin, destination, aircraft, flight_time)
)
""")


def is_flight_time(s):
    """Returns True if string looks like a valid flight time e.g. '01:30', '1:30'"""
    if ":" not in s:
        return False
    parts = s.strip().split(":")
    if len(parts) != 2:
        return False
    return parts[0].isdigit() and parts[1].isdigit()


def normalize_data(data):
    """Fix rows where flight_time and aircraft might be swapped."""
    fixed = []
    for row in data:
        origin, dest, a, b = row
        if is_flight_time(a):
            flight_time = a
            aircraft = b
        elif is_flight_time(b):
            aircraft = a
            flight_time = b
        else:
            print(f"WARNING: Could not parse row {row}, skipping.")
            continue
        fixed.append((origin, dest, aircraft, flight_time))
    return fixed


def insert_routes(airline, data):
    """
    Insert routes AND their reverse automatically.
    e.g. WAAA->WAMG also inserts WAMG->WAAA with the same aircraft & time.
    Uses INSERT OR IGNORE so no duplicates.
    """
    normalized = [(airline, o, d, a, t.zfill(5)) for (o, d, a, t) in data]

    # Build reverse routes
    reversed_routes = [(airline, d, o, a, t) for (airline, o, d, a, t) in normalized]

    # Combine both directions
    all_routes = normalized + reversed_routes

    cur.executemany("""
        INSERT OR IGNORE INTO routes
        (airline, origin, destination, aircraft, flight_time)
        VALUES (?,?,?,?,?)
    """, all_routes)


# =========================
# LION AIR DATA
# =========================

data_lion_jakarta = [
    ("WIII","WILL","B739","00:50"), ("WIII","WILL","B38M","00:50"),
    ("WIII","WAHS","B739","01:00"), ("WIII","WAHS","B38M","01:00"),
    ("WIII","WIPP","B739","01:00"), ("WIII","WIPP","B38M","01:00"), ("WIII","WIPP","A339","01:00"),
    ("WIII","WIKT","B739","01:00"), ("WIII","WIKT","B38M","01:00"),
    ("WIII","WIKK","B739","01:10"), ("WIII","WIKK","B38M","01:10"),
    ("WIII","WAHI","B739","01:10"), ("WIII","WAHI","B38M","01:10"),
    ("WIII","WAHQ","B739","01:10"), ("WIII","WAHQ","B38M","01:10"), ("WIII","WAHQ","A339","01:10"),
    ("WIII","WIGG","B739","01:30"), ("WIII","WIGG","B38M","01:30"),
    ("WIII","WIJJ","B739","01:30"), ("WIII","WIJJ","B38M","01:30"),
    ("WIII","WARR","B739","01:30"), ("WIII","WARR","B38M","01:30"),
    ("WIII","WARA","B739","01:30"), ("WIII","WARA","B38M","01:30"),
    ("WIII","WIOO","B739","01:40"), ("WIII","WIOO","B38M","01:40"),
    ("WIII","WIDN","B739","01:40"), ("WIII","WIDN","B38M","01:40"),
    ("WIII","WIDD","B739","01:45"), ("WIII","WIDD","B38M","01:45"), ("WIII","WIDD","A339","01:45"),
    ("WIII","WAOO","B739","01:50"), ("WIII","WAOO","B38M","01:50"), ("WIII","WAOO","A339","01:50"),
    ("WIII","WIBB","B739","01:50"), ("WIII","WIBB","B38M","01:50"),
    ("WIII","WIEE","B739","01:50"), ("WIII","WIEE","B38M","01:50"), ("WIII","WIEE","A339","01:50"),
    ("WIII","WAGG","B739","01:50"), ("WIII","WAGG","B38M","01:50"),
    ("WIII","WSSS","B739","01:50"), ("WIII","WSSS","B38M","01:50"),
    ("WIII","WADY","B739","01:50"), ("WIII","WADY","B38M","01:50"),
    ("WIII","WADD","B739","01:55"), ("WIII","WADD","B38M","01:55"), ("WIII","WADD","A339","01:55"),
    ("WIII","WADL","B739","02:00"), ("WIII","WADL","B38M","02:00"), ("WIII","WADL","A339","02:00"),
    ("WIII","WMKK","B739","02:00"), ("WIII","WMKK","B38M","02:00"), ("WIII","WMKK","A339","02:00"),
    ("WIII","WALL","B739","02:20"), ("WIII","WALL","B38M","02:20"), ("WIII","WALL","A339","02:20"),
    ("WIII","WAAA","B739","02:20"), ("WIII","WAAA","B38M","02:20"),
    ("WIII","WIMM","B739","02:20"), ("WIII","WIMM","B38M","02:20"), ("WIII","WIMM","A339","02:20"),
    ("WIII","WAFF","B739","02:40"), ("WIII","WAFF","B38M","02:40"),
    ("WIII","WAQQ","B739","02:40"), ("WIII","WAQQ","B38M","02:40"),
    ("WIII","WAWW","B739","02:40"), ("WIII","WAWW","B38M","02:40"),
    ("WIII","WITT","B739","03:00"), ("WIII","WITT","B38M","03:00"), ("WIII","WITT","A339","03:00"),
    ("WIII","WAEE","B739","03:30"), ("WIII","WAEE","B38M","03:30"),
    ("WIII","WAPP","B739","03:30"), ("WIII","WAPP","B38M","03:30"),
    ("WIII","WAJJ","B739","05:40"), ("WIII","WAJJ","B38M","05:40"),
]

data_lion_makassar = [
    ("WAAA","WAWW","B739","00:50"), ("WAAA","WAWW","B38M","00:50"),
    ("WAAA","WAHS","B739","01:00"), ("WAAA","WAHS","B38M","01:00"),
    ("WAAA","WALL","B739","01:10"), ("WAAA","WALL","B38M","01:10"), ("WAAA","WALL","A339","01:10"),
    ("WAAA","WAFF","B739","01:30"), ("WAAA","WAFF","B38M","01:30"),
    ("WAAA","WAOO","B739","01:30"), ("WAAA","WAOO","B38M","01:30"),
    ("WAAA","WADL","B739","01:30"), ("WAAA","WADL","B38M","01:30"),
    ("WAAA","WADD","B739","01:40"), ("WAAA","WADD","B38M","01:40"), ("WAAA","WADD","A339","01:40"),
    ("WAAA","WARR","B739","01:40"), ("WAAA","WARR","B38M","01:40"), ("WAAA","WARR","A339","01:40"),
    ("WAAA","WAMM","B739","01:50"), ("WAAA","WAMM","B38M","01:50"),
    ("WAAA","WAMG","B739","01:50"), ("WAAA","WAMG","B38M","01:50"),
    ("WAAA","WAPP","B739","01:50"), ("WAAA","WAPP","B38M","01:50"),
    ("WAAA","WAQQ","B739","01:50"), ("WAAA","WAQQ","B38M","01:50"),
    ("WAAA","WAHI","B739","02:00"), ("WAAA","WAHI","B38M","02:00"),
    ("WAAA","WAEE","B739","02:00"), ("WAAA","WAEE","B38M","02:00"),
    ("WAAA","WIII","B739","02:20"), ("WAAA","WIII","B38M","02:20"), ("WAAA","WIII","A339","02:20"),
    ("WAAA","WIOO","B739","02:20"), ("WAAA","WIOO","B38M","02:20"),
    ("WAAA","WICA","B739","02:20"), ("WAAA","WICA","B38M","02:20"),
    ("WAAA","WASS","B739","02:20"), ("WAAA","WASS","B38M","02:20"),
    ("WAAA","WAUU","B739","02:30"), ("WAAA","WAUU","B38M","02:30"),
    ("WAAA","WABB","B739","03:00"), ("WAAA","WABB","B38M","03:00"),
    ("WAAA","WAYY","B739","03:00"), ("WAAA","WAYY","B38M","03:00"),
    ("WAAA","WAJJ","B739","03:30"), ("WAAA","WAJJ","B38M","03:30"),
    ("WAAA","WAKK","B739","03:30"), ("WAAA","WAKK","B38M","03:30"),
]

data_lion_surabaya = [
    ("WARR","WADD","00:50","B739"), ("WARR","WADD","00:50","B38M"),
    ("WARR","WADL","01:00","B739"), ("WARR","WADL","01:00","B38M"),
    ("WARR","WAOO","01:10","B739"), ("WARR","WAOO","01:10","B38M"),
    ("WARR","WICA","01:20","B739"), ("WARR","WICA","01:20","B38M"),
    ("WARR","WAGG","01:30","B739"), ("WARR","WAGG","01:30","B38M"),
    ("WARR","WIII","01:30","B739"), ("WARR","WIII","01:30","B38M"), ("WARR","WIII","01:30","A339"),
    ("WARR","WATO","01:30","B739"), ("WARR","WATO","01:30","B38M"),
    ("WARR","WAAA","01:50","B739"), ("WARR","WAAA","01:50","B38M"), ("WARR","WAAA","01:50","A339"),
    ("WARR","WALL","01:50","B739"), ("WARR","WALL","01:50","B38M"),
    ("WARR","WIOO","01:50","B739"), ("WARR","WIOO","01:50","B38M"),
    ("WARR","WIPP","01:50","B739"), ("WARR","WIPP","01:50","B38M"),
    ("WARR","WALS","01:50","B739"), ("WARR","WALS","01:50","B38M"),
    ("WARR","WAWW","02:00","B739"), ("WARR","WAWW","02:00","B38M"),
    ("WARR","WAQT","02:00","B739"), ("WARR","WAQT","02:00","B38M"),
    ("WARR","WATT","02:20","B739"), ("WARR","WATT","02:20","B38M"),
    ("WARR","WIDD","02:20","B739"), ("WARR","WIDD","02:20","B38M"),
    ("WARR","WAQQ","02:20","B739"), ("WARR","WAQQ","02:20","B38M"),
    ("WARR","WIEE","02:20","B739"), ("WARR","WIEE","02:20","B38M"),
    ("WARR","WAMM","02:30","B739"), ("WARR","WAMM","02:30","B38M"),
    ("WARR","WAEE","02:30","B739"), ("WARR","WAEE","02:30","B38M"),
    ("WARR","WIBB","02:40","B739"), ("WARR","WIBB","02:40","B38M"),
    ("WARR","WAPP","02:40","B739"), ("WARR","WAPP","02:40","B38M"),
]

data_lion_bali = [
    ("WADD","WADL","00:30","B739"), ("WADD","WADL","00:30","B38M"),
    ("WADD","WARR","00:50","B739"), ("WADD","WARR","00:50","B38M"),
    ("WADD","WAHQ","01:20","B739"), ("WADD","WAHQ","01:20","B38M"),
    ("WADD","WAHI","01:30","B739"), ("WADD","WAHI","01:30","B38M"),
    ("WADD","WAOO","01:30","B739"), ("WADD","WAOO","01:30","B38M"),
    ("WADD","WAHS","01:30","B739"), ("WADD","WAHS","01:30","B38M"),
    ("WADD","WAAA","01:40","B739"), ("WADD","WAAA","01:40","B38M"), ("WADD","WAAA","01:40","A339"),
    ("WADD","WATT","01:50","B739"), ("WADD","WATT","01:50","B38M"),
    ("WADD","WICA","01:50","B739"), ("WADD","WICA","01:50","B38M"),
    ("WADD","WALL","01:50","B739"), ("WADD","WALL","01:50","B38M"),
    ("WADD","WIII","01:50","B739"), ("WADD","WIII","01:50","B38M"), ("WADD","WIII","01:50","A339"),
    ("WADD","WAMM","02:40","B739"), ("WADD","WAMM","02:40","B38M"),
]

data_lion_balikpapan = [
    ("WALL","WAFF","00:50","B739"), ("WALL","WAFF","00:50","B38M"),
    ("WALL","WAQQ","01:00","B739"), ("WALL","WAQQ","01:00","B38M"),
    ("WALL","WAQT","01:00","B739"), ("WALL","WAQT","01:00","B38M"),
    ("WALL","WAAA","01:00","B739"), ("WALL","WAAA","01:00","B38M"), ("WALL","WAAA","01:00","A339"),
    ("WALL","WIOO","01:40","B739"), ("WALL","WIOO","01:40","B38M"),
    ("WALL","WARR","01:40","B739"), ("WALL","WARR","01:40","B38M"),
    ("WALL","WAMM","01:50","B739"), ("WALL","WAMM","01:50","B38M"),
    ("WALL","WADD","01:50","B739"), ("WALL","WADD","01:50","B38M"),
    ("WALL","WAHS","02:00","B739"), ("WALL","WAHS","02:00","B38M"),
    ("WALL","WAHI","02:00","B739"), ("WALL","WAHI","02:00","B38M"),
    ("WALL","WIII","02:20","B739"), ("WALL","WIII","02:20","B38M"), ("WALL","WIII","02:20","A339"),
    ("WALL","WADL","01:40","B739"),
    ("WALL","WIDD","01:50","B739"),
]

data_lion_nonhub = [
    ("WAPP","WAPF","01:30","B739"), ("WAPP","WAPF","01:30","B38M"),
    ("WAPP","WAAA","01:50","B739"), ("WAPP","WAAA","01:50","B38M"),
    ("WAPP","WARR","02:40","B739"), ("WAPP","WARR","02:40","B38M"),
    ("WAPP","WIII","03:30","B739"), ("WAPP","WIII","03:30","B38M"),
    ("WITT","WIMM","01:10","B739"), ("WITT","WIMM","01:10","B38M"), ("WITT","WIMM","01:10","A339"),
    ("WITT","WIII","03:00","B739"), ("WITT","WIII","03:00","B38M"), ("WITT","WIII","03:00","A339"),
    ("WILL","WIII","00:50","B739"), ("WILL","WIII","00:50","B38M"),
    ("WILL","WIDD","01:30","B739"), ("WILL","WIDD","01:30","B38M"),
    ("WILL","WAHI","01:30","B739"), ("WILL","WAHI","01:30","B38M"),
    ("WAOO","WARR","01:00","B739"), ("WAOO","WARR","01:00","B38M"),
    ("WAOO","WAHS","01:20","B739"), ("WAOO","WAHS","01:20","B38M"),
    ("WAOO","WADD","01:30","B739"), ("WAOO","WADD","01:30","B38M"),
    ("WAOO","WAAA","01:30","B739"), ("WAOO","WAAA","01:30","B38M"),
    ("WAOO","WIII","01:50","B739"), ("WAOO","WIII","01:50","B38M"), ("WAOO","WIII","01:50","A339"),
    ("WAOO","WAHI","01:50","B739"), ("WAOO","WAHI","01:50","B38M"),
    ("WADY","WIII","01:50","B739"), ("WADY","WIII","01:50","B38M"),
    ("WIDD","WIBB","00:50","B739"), ("WIDD","WIBB","00:50","B38M"),
    ("WIDD","WIJJ","00:50","B739"), ("WIDD","WIJJ","00:50","B38M"),
    ("WIDD","WIPP","01:00","B739"), ("WIDD","WIPP","01:00","B38M"),
    ("WIDD","WIKK","01:10","B739"), ("WIDD","WIKK","01:10","B38M"),
    ("WIDD","WIEE","01:10","B739"), ("WIDD","WIEE","01:10","B38M"),
    ("WIDD","WIOO","01:30","B739"), ("WIDD","WIOO","01:30","B38M"),
    ("WIDD","WIMM","01:30","B739"), ("WIDD","WIMM","01:30","B38M"),
    ("WIDD","WIII","01:50","B739"), ("WIDD","WIII","01:50","B38M"), ("WIDD","WIII","01:50","A339"),
    ("WIDD","WAHS","02:00","B739"), ("WIDD","WAHS","02:00","B38M"),
    ("WIDD","WICA","02:00","B739"), ("WIDD","WICA","02:00","B38M"),
    ("WIDD","WARR","02:20","B739"), ("WIDD","WARR","02:20","B38M"),
    ("WIDD","WALL","02:50","B739"), ("WIDD","WALL","02:50","B38M"),
]


# =========================
# BATIK AIR DATA
# =========================

data_batik_jakarta = [
    ("WIII","WIHH","A320","00:30"),
    ("WIII","WILL","A320","00:50"),
    ("WIII","WAHS","A320","01:00"),
    ("WIII","WIKT","A320","01:00"),
    ("WIII","WAHI","A320","01:00"),
    ("WIII","WIPP","A320","01:00"),
    ("WIII","WIKK","A320","01:00"),
    ("WIII","WAHQ","A320","01:10"),
    ("WIII","WIPB","A320","01:20"),
    ("WIII","WIJJ","A320","01:30"),
    ("WIII","WARR","A320","01:30"),
    ("WIII","WIOO","A320","01:40"),
    ("WIII","WIDD","A320","01:40"),
    ("WIII","WARA","A320","01:40"),
    ("WIII","WIBB","A320","01:50"),
    ("WIII","WIEE","A320","01:50"),
    ("WIII","WAOO","A320","01:50"),
    ("WIII","WAGG","A320","01:50"),
    ("WIII","WADY","A320","01:50"),
    ("WIII","WSSS","A320","01:50"),
    ("WIII","WADD","A320","01:55"),
    ("WIII","WADL","A320","02:00"),
    ("WIII","WIMN","A320","02:00"),
    ("WIII","WMKP","A320","02:00"),
    ("WIII","WMKK","A320","02:00"),
    ("WIII","WALL","A320","02:20"),
    ("WIII","WAAA","A320","02:20"), ("WIII","WAAA","B738","02:20"),
    ("WIII","WIMM","A320","02:20"),
    ("WIII","WAQT","A320","02:30"),
    ("WIII","WALS","A320","02:30"),
    ("WIII","WATO","A320","02:30"),
    ("WIII","WAWW","A320","02:40"),
    ("WIII","WAFF","A320","02:40"),
    ("WIII","WAQQ","A320","02:40"),
    ("WIII","WAFW","A320","02:50"),
    ("WIII","WITT","A320","03:00"),
    ("WIII","WATT","A320","03:00"),
    ("WIII","WAMG","A320","03:00"),
    ("WIII","WAMM","A320","03:00"),
    ("WIII","VTBD","A320","03:30"),
    ("WIII","WAPP","A320","03:30"),
    ("WIII","WAEE","A320","03:30"),
    ("WIII","WAUU","A320","04:30"),
    ("WIII","WAYY","A320","04:50"),
    ("WIII","ZGNN","A320","04:50"),
    ("WIII","ZPPP","A320","04:50"),
    ("WIII","RCTP","A320","04:50"),
    ("WIII","YPPH","A320","04:50"),
    ("WIII","VHHH","A320","04:50"),
    ("WIII","WASS","A320","04:30"),
    ("WIII","WAJJ","B738","05:40"),
    ("WIII","ZGKL","A320","05:40"),
]

data_batik_halim = [
    ("WIHH","WIII","A320","0:30"),
    ("WIHH","WILL","A320","0:50"),
    ("WIHH","WAHS","A320","1:00"),
    ("WIHH","WAHI","A320","1:00"),
    ("WIHH","WIPP","A320","1:00"),
    ("WIHH","WAHQ","A320","1:10"),
    ("WIHH","WIGG","A320","1:30"),
    ("WIHH","WARR","A320","1:30"),
    ("WIHH","WARA","A320","1:30"),
    ("WIHH","WIDD","A320","1:40"),
    ("WIHH","WIBB","A320","1:50"),
    ("WIHH","WIEE","A320","1:50"),
    ("WIHH","WADD","A320","1:55"),
    ("WIHH","WADL","A320","2:00"),
    ("WIHH","WALL","A320","2:20"),
    ("WIHH","WIMM","A320","2:20"),
    ("WIHH","WAAA","A320","2:20"),
    ("WIHH","WAPP","A320","3:30"),
]

data_batik_makassar = [
    ("WAAA","WALL","A320","01:10"),
    ("WAAA","WAFJ","A320","00:50"),
    ("WAAA","WAWW","A320","00:50"),
    ("WAAA","WALS","A320","01:30"),
    ("WAAA","WAFF","A320","01:30"),
    ("WAAA","WADD","A320","01:30"),
    ("WAAA","WARR","A320","01:40"),
    ("WAAA","WAMG","A320","01:40"),
    ("WAAA","WAFW","A320","01:40"),
    ("WAAA","WAEE","A320","02:00"),
    ("WAAA","WIII","A320","02:20"),
    ("WAAA","WIHH","A320","02:20"),
    ("WAAA","WASS","A320","02:20"),
    ("WAAA","WAUU","A320","02:30"),
    ("WAAA","WAYY","A320","02:50"),
    ("WAAA","WSSS","A320","02:50"),
    ("WAAA","WABB","A320","03:00"),
    ("WAAA","WAJJ","A320","03:00"),
    ("WAAA","WAKK","A320","03:00"),
    ("WAAA","WMKK","A320","03:30"),
]

data_batik_nonhub = [
    ("WAPP", "WIII", "A320", "03:00"), ("WAPP", "WIHH", "A320", "03:00"),
    ("YPAD", "WADD", "A320", "05:30"), ("YSCB", "WADD", "B738", "06:00"),
    ("WALL", "WAQQ", "A320", "01:00"), ("WALL", "WIII", "A320", "02:20"),
    ("WALL", "WIHH", "A320", "02:20"), ("WALL", "WAAA", "A320", "01:10"),
    ("WALL", "WAHI", "A320", "01:50"), ("WALL", "WAHS", "A320", "01:45"),
    ("WALL", "WIOO", "A320", "01:30"), ("WITT", "WMKP", "A320", "01:40"),
    ("WITT", "WIII", "A320", "03:00"), ("WILL", "WIHH", "A320", "00:50"),
    ("WILL", "WIII", "A320", "00:50"), ("VTBD", "WIII", "A320", "03:30"),
    ("VTBD", "WADD", "A320", "04:30"), ("WAOO", "WIII", "A320", "01:50"),
    ("WADY", "WIII", "A320", "01:50"), ("WIDD", "WIII", "A320", "01:50"),
    ("WIDD", "WIHH", "A320", "01:50"), ("WIGG", "WIHH", "A320", "01:30"),
    ("WABB", "WAJJ", "A320", "01:20"), ("WABB", "WAAA", "A320", "03:00"),
    ("VOMM", "WMKK", "A320", "03:40"), ("VOMM", "WIMM", "A320", "03:40"),
    ("WPDL", "WADD", "A320", "02:00"), ("WADD", "WARR", "A320", "00:50"),
    ("WADD", "WATO", "A320", "01:00"), ("WADD", "WAAA", "A320", "01:30"),
    ("WADD", "WIII", "A320", "01:55"), ("WADD", "WIHH", "A320", "01:55"),
    ("WADD", "WPDL", "A320", "02:00"), ("WADD", "WALS", "A320", "02:00"),
    ("WADD", "WSSS", "A320", "02:30"), ("WADD", "WMKK", "A320", "03:00"),
    ("WADD", "YPPH", "A320", "03:30"), ("WADD", "WIMM", "A320", "03:40"),
    ("WADD", "VTBD", "A320", "04:30"), ("WADD", "YPAD", "A320", "05:30"),
    ("WADD", "YSCB", "B738", "05:45"), ("WADD", "YMML", "A320", "05:40"),
    ("WADD", "YSSY", "A320", "05:40"), ("ZLDH", "ZPPP", "A320", "03:30"),
    ("WAMG", "WAAA", "A320", "01:50"), ("WAMG", "WIII", "A320", "03:00"),
    ("ZGKL", "WIII", "A320", "05:40"), ("VHHH", "WIII", "A320", "04:50"),
    ("WIJJ", "WIII", "A320", "01:30"), ("WAJJ", "WAYY", "A320", "01:00"),
    ("WAJJ", "WABB", "A320", "01:20"), ("WAJJ", "WAAA", "A320", "03:00"),
    ("WAJJ", "WARR", "A320", "04:10"), ("WAJJ", "WIII", "A320", "05:40"),
    ("WAQT", "WIII", "A320", "02:30"), ("WAQT", "WARR", "A320", "02:00"),
    ("WAQT", "WAHI", "A320", "02:00"), ("WAEK", "WAMM", "A320", "00:50"),
    ("WAWW", "WAAA", "A320", "00:50"), ("WAWW", "WIII", "A320", "02:30"),
    ("WMKK", "WIMM", "A320", "00:50"), ("WMKK", "WIII", "A320", "02:00"),
    ("WMKK", "WAHI", "A320", "02:30"), ("WMKK", "WADD", "A320", "03:00"),
    ("WMKK", "WAAA", "A320", "03:30"), ("WMKK", "VOMM", "A320", "03:40"),
    ("ZPPP", "WIII", "A320", "04:50"), ("ZPPP", "ZLDH", "A320", "03:30"),
    ("WATT", "WIII", "A320", "03:00"), ("WATO", "WADD", "A320", "01:10"),
    ("WATO", "WARR", "A320", "01:30"), ("WATO", "WIII", "A320", "02:40"),
    ("WADL", "WIII", "A320", "02:00"), ("WADL", "WIHH", "A320", "02:00"),
    ("WIPB", "WIII", "A320", "01:30"), ("WAFW", "WAAA", "A320", "01:30"),
    ("WAFW", "WIII", "A320", "03:30"), ("WARA", "WIHH", "A320", "01:30"),
    ("WARA", "WIII", "A320", "01:40"), ("WAFJ", "WAAA", "A320", "00:50"),
    ("WAMM", "WAEK", "A320", "00:50"), ("WAMM", "WAAA", "A320", "01:50"),
    ("WAMM", "WIII", "A320", "03:00"), ("WAMM", "ZGSZ", "B738", "03:56"),
    ("WAUU", "WASS", "A320", "00:50"), ("WAUU", "WAAA", "A320", "02:30"),
    ("WAUU", "WIII", "A320", "04:30"), ("WIMM", "WMKP", "A320", "00:50"),
    ("WIMM", "WMKK", "A320", "00:50"), ("WIMM", "WSSS", "A320", "01:30"),
    ("WIMM", "WIII", "A320", "02:20"), ("WIMM", "WIHH", "A320", "02:20"),
    ("WIMM", "WADD", "A320", "03:40"), ("WIMM", "VOMM", "A320", "03:40"),
    ("YMML", "WADD", "A320", "05:40"), ("WAKK", "WAAA", "A320", "03:10"),
    ("ZGNN", "WIII", "A320", "04:50"), ("WIEE", "WIII", "A320", "01:50"),
    ("WIEE", "WIHH", "A320", "01:50"), ("WAGG", "WAHI", "A320", "01:30"),
    ("WAGG", "WIII", "A320", "01:50"), ("WIPP", "WIHH", "A320", "01:00"),
    ("WIPP", "WIII", "A320", "01:00"), ("WAFF", "WAAA", "A320", "01:30"),
    ("WAFF", "WIII", "A320", "02:30"), ("WIKK", "WIII", "A320", "01:00"),
    ("WIBB", "WIII", "A320", "01:50"), ("WIBB", "WIHH", "A320", "01:50"),
    ("WMKP", "WIMM", "A320", "00:50"), ("WMKP", "WITT", "A320", "01:40"),
    ("WMKP", "WIII", "A320", "02:30"), ("YPPH", "WADD", "A320", "03:40"),
    ("YPPH", "WIII", "A320", "04:50"), ("WIOO", "WIII", "A320", "01:40"),
    ("WIOO", "WALL", "A320", "01:30"), ("WALS", "WAAA", "A320", "01:30"),
    ("WALS", "WAHI", "A320", "01:50"), ("WALS", "WADD", "A320", "02:00"),
    ("WALS", "WIII", "A320", "02:30"), ("WAHS", "WIHH", "A320", "01:00"),
    ("WAHS", "WALL", "A320", "01:45"), ("WAHS", "WIII", "A320", "01:00"),
    ("ZGSZ", "WAMM", "B738", "03:40"), ("WIMN", "WIII", "A320", "02:00"),
    ("WSSS", "WIMM", "A320", "01:30"), ("WSSS", "WIII", "A320", "01:50"),
    ("WSSS", "WAHI", "A320", "02:00"), ("WSSS", "WARR", "A320", "02:30"),
    ("WSSS", "WADD", "A320", "02:30"), ("WSSS", "WAAA", "A320", "02:50"),
    ("WASS", "WAUU", "A320", "00:50"), ("WASS", "WAAA", "A320", "02:20"),
    ("WASS", "WARR", "A320", "02:50"), ("WASS", "WIII", "A320", "03:40"),
    ("WARR", "WADD", "A320", "00:50"), ("WARR", "WATO", "A320", "01:30"),
    ("WARR", "WADL", "A320", "01:00"), ("WARR", "WIII", "A320", "01:30"),
    ("WARR", "WIHH", "A320", "01:30"), ("WARR", "WAAA", "A320", "01:40"),
    ("WARR", "WAQT", "A320", "02:00"), ("WARR", "WSSS", "A320", "02:30"),
    ("WARR", "WASS", "A320", "02:50"), ("WARR", "WAYY", "A320", "03:30"),
    ("WARR", "WAJJ", "A320", "04:30"), ("WAHQ", "WIII", "A320", "01:10"),
    ("WAHQ", "WIHH", "A320", "01:10"), ("YSSY", "WADD", "A320", "05:40"),
    ("RCTP", "WIII", "A320", "05:40"), ("WIKT", "WIII", "A320", "01:00"),
    ("WIDN", "WIII", "A320", "01:40"), ("WAQQ", "WALL", "A320", "01:10"),
    ("WAQQ", "WIII", "A320", "02:40"), ("WAEE", "WAAA", "A320", "02:00"),
    ("WAEE", "WIII", "A320", "03:30"), ("WAYY", "WAJJ", "A320", "01:00"),
    ("WAYY", "WAAA", "A320", "03:00"), ("WAYY", "WARR", "A320", "03:40"),
    ("WAYY", "WIII", "A320", "04:50"), ("WAHI", "WIII", "A320", "01:10"),
    ("WAHI", "WIHH", "A320", "01:10"), ("WAHI", "WAGG", "A320", "01:30"),
    ("WAHI", "WALS", "A320", "01:50"), ("WAHI", "WSSS", "A320", "02:00"),
    ("WAHI", "WAQT", "A320", "02:00"), ("WAHI", "WALL", "A320", "02:00"),
    ("WAHI", "WMKK", "A320", "02:30"),
]

# =========================
# SUPER AIR JET DATA
# =========================
data_super_jakarta = [
("WIII","WAPP","A320","03:10"),
("WIII","WILL","A320","00:50"),
("WIII","WAHS","A320","01:10"),
("WIII","WIPP","A320","01:10"),
("WIII","WIKK","A320","01:10"),
("WIII","WIKT","A320","01:10"),
("WIII","WAHI","A320","01:15"),
("WIII","WAHQ","A320","01:20"),
("WIII","WIJJ","A320","01:30"),
("WIII","WARR","A320","01:30"),
("WIII","WIGG","A320","01:30"),
("WIII","WIOO","A320","01:40"),
("WIII","WIDD","A320","01:45"),
("WIII","WADY","A320","01:50"),
("WIII","WADD","A320","01:50"),
("WIII","WIBB","A320","01:50"),
("WIII","WIEE","A320","01:50"),
("WIII","WAOO","A320","01:50"),
("WIII","WIKD","A320","00:45"),
("WIII","WAEE","A320","03:40"),
("WIII","WADL","A320","02:00"),
("WIII","WIMN","A320","02:00"),
("WIII","WASS","A320","03:35"),
("WIII","WIMM","A320","02:20"),
("WIII","WAAA","A320","02:20"),
("WIII","WAJJ","A320","05:15"),
("WIII","WAFF","A320","02:40"),
("WIII","WIOD","A320","01:20"),
("WIII","WALL","A320","02:20"),
("WAPP","WIII","A320","03:10"),
("WALL","WAQQ","A320","01:10"),
("WALL","WARD","A320","01:20"),
("WALL","WAAA","A320","01:20"),
("WALL","WIOO","A320","01:40"),
("WALL","WARR","A320","01:45"),
("WALL","WAMM","A320","01:50"),
("WALL","WAHI","A320","02:10"),
("WALL","WIII","A320","02:20"),
("WALL","WICA","A320","02:20"),

("WILL","WIMM","A320","01:41"),
("WILL","WIII","A320","00:50"),

("WAOO","WARR","A320","01:10"),
("WAOO","WAHI","A320","01:40"),
("WAOO","WIII","A320","01:50"),
("WAOO","WICA","A320","01:50"),

("WADY","WIII","A320","01:50"),

("WITT","WMKK","A320","02:28"),
("WITT","WIDD","A320","02:00"),
("WITT","WIMM","A320","01:13"),

("WIGG","WIDD","A320","01:15"),
("WIGG","WIII","A320","01:30"),

("WIDD","WAHI","A320","02:00"),
("WIDD","WIBB","A320","00:50"),
("WIDD","WIEE","A320","01:10"),
("WIDD","WIII","A320","01:45"),
("WIDD","WAHS","A320","02:00"),
("WIDD","WIMN","A320","01:10"),
("WIDD","WITT","A320","02:00"),
("WIDD","WICA","A320","02:00"),
("WIDD","WADL","A320","02:30"),
("WIDD","WIJJ","A320","00:40"),
("WIDD","WIPK","A320","00:50"),

("WADD","WARR","A320","00:50"),
("WADD","WAAA","A320","01:30"),
("WADD","WAHQ","A320","01:30"),
("WADD","WICA","A320","01:45"),
("WADD","WIII","A320","01:50"),

("WIJJ","WIMM","A320","01:15"),
("WIJJ","WIII","A320","01:30"),
("WIJJ","WAHI","A320","01:30"),
("WIJJ","WIDD","A320","00:40"),

("WAJJ","WAUU","A320","01:30"),
("WAJJ","WIII","A320","05:15"),

("WAWW","WAAA","A320","00:50"),
("WAWW","WIII","A320","02:30"),

("WMKK","WIBB","A320","00:50"),
("WMKK","WIEE","A320","01:15"),
("WMKK","WARR","A320","02:30"),
("WMKK","WADL","A320","02:50"),
("WMKK","WITT","A320","02:30"),

("WATT","WARR","A320","02:20"),

("WATO","WARR","A320","01:40"),

("WADL","WARR","A320","01:10"),
("WADL","WAHI","A320","01:40"),
("WADL","WIII","A320","02:00"),
("WADL","WIDD","A320","02:30"),

("WAUU","WAJJ","A320","01:20"),
("WAUU","WAAA","A320","02:40"),
("WAUU","WASS","A320","01:05"),

("WICA","WIPP","A320","01:10"),
("WICA","WAOO","A320","01:40"),
("WICA","WADD","A320","01:45"),
("WICA","WIDD","A320","02:00"),
("WICA","WAAA","A320","02:20"),
("WICA","WALL","A320","02:20"),
("WICA","WIMM","A320","02:30"),

("WAAA","WAWW","A320","00:50"),
("WAAA","WALL","A320","01:20"),
("WAAA","WALS","A320","01:20"),
("WAAA","WADD","A320","01:30"),
("WAAA","WARR","A320","01:45"),
("WAAA","WAEE","A320","02:00"),
("WAAA","WIII","A320","02:20"),
("WAAA","WAUU","A320","02:30"),
("WAAA","WICA","A320","02:20"),
("WAAA","WASS","A320","00:45"),

("WAMM","WALL","A320","01:50"),

("WIMM","WIEE","A320","01:10"),
("WIMM","WIPP","A320","01:50"),
("WIMM","WIII","A320","02:20"),
("WIMM","WICA","A320","02:30"),
("WIMM","WITT","A320","01:15"),
("WIMM","WIJJ","A320","01:15"),
("WIMM","WILL","A320","01:40"),
("WIMM","WARR","A320","03:00"),

("WAGG","WAHI","A320","01:45"),

("WIKK","WIII","A320","01:10"),

("WIPK","WAHI","A320","01:22"),
("WIPK","WARR","A320","01:25"),
("WIPK","WIKD","A320","00:20"),
("WIPK","WIPP","A320","00:30"),
("WIPK","WIDD","A320","00:50"),

("WIEE","WAHS","A320","02:00"),
("WIEE","WIDD","A320","01:10"),
("WIEE","WAHI","A320","02:00"),
("WIEE","WIMM","A320","01:10"),
("WIEE","WMKK","A320","01:15"),
("WIEE","WIII","A320","01:50"),

("WIPP","WIII","A320","01:10"),
("WIPP","WICA","A320","01:10"),
("WIPP","WAHI","A320","01:45"),
("WIPP","WIMM","A320","01:50"),
("WIPP","WIPK","A320","00:25"),

("WAFF","WIII","A320","02:40"),

("WIBB","WIDD","A320","00:50"),
("WIBB","WMKK","A320","00:50"),
("WIBB","WIII","A320","01:50"),
("WIBB","WAHS","A320","02:00"),

("WIOO","WIII","A320","01:40"),
("WIOO","WALL","A320","01:40"),
("WIOO","WAHQ","A320","01:45"),
("WIOO","WAHI","A320","02:10"),

("WALS","WAAA","A320","01:20"),
("WALS","WARR","A320","01:50"),
("WALS","WAHI","A320","02:20"),

("WAHS","WIII","A320","01:10"),
("WAHS","WIEE","A320","02:00"),
("WAHS","WIDD","A320","02:00"),
("WAHS","WIBB","A320","01:45"),

("WIMN","WIDD","A320","01:10"),
("WIMN","WIII","A320","02:00"),

("WIOD","WIII","A320","01:20"),

("WASS","WAAA","A320","02:15"),
("WASS","WAUU","A320","00:45"),
("WASS","WIII","A320","03:35"),

("WIKD","WIPK","A320","00:30"),
("WIKD","WIII","A320","00:43"),

("WAEE","WAAA","A320","01:35"),
("WAEE","WIII","A320","03:40"),

("WAHI","WIDD","A320","02:00"),
("WAHI","WIPK","A320","01:12"),
("WAHI","WIJJ","A320","01:30"),
("WAHI","WIEE","A320","02:00"),
("WAHI","WALS","A320","01:45"),
("WAHI","WIPP","A320","01:20"),
("WAHI","WAGG","A320","01:45"),
]

# =========================
# WINGS AIR DATA
# =========================
data_wings_abadi = [
("WATM","WATT","ATR72","01:30"),
("WAPP","WAPN","ATR72","00:50"),
("WAPP","WAPD","ATR72","01:30"),
("WAPP","WASO","ATR72","01:30"),
("WAPP","WASS","ATR72","01:40"),
("WAPP","WAPS","ATR72","01:40"),
("WAPP","WABI","ATR72","01:40"),
("WAPP","WAPF","ATR72","01:40"),

("WATA","WATT","ATR72","01:00"),

("WASO","WAPP","ATR72","01:30"),

("WATW","WATT","ATR72","01:20"),

("WALL","WALE","ATR72","01:00"),
("WALL","WAQD","ATR72","01:20"),
("WALL","WAFJ","ATR72","01:20"),
("WALL","WAQT","ATR72","01:25"),
("WALL","WAQQ","ATR72","01:30"),
("WALL","WAGG","ATR72","01:30"),
("WALL","WAFF","ATR72","01:30"),
("WALL","WAOO","ATR72","01:30"),
("WALL","WAQM","ATR72","01:30"),
("WALL","WAFT","ATR72","01:30"),
("WALL","WAMM","ATR72","02:00"),

("WITT","WIMM","ATR72","01:30"),

("WILL","WILP","ATR72","01:00"),
("WILL","WIHP","ATR72","01:00"),
("WILL","WIPP","ATR72","01:20"),
("WILL","WIGG","ATR72","01:20"),
("WILL","WIJJ","ATR72","01:30"),
("WILL","WICC","ATR72","01:30"),

("WICC","WIHH","ATR72","00:50"),
("WICC","WAHH","ATR72","01:20"),
("WICC","WAHS","ATR72","01:20"),
("WICC","WILL","ATR72","01:30"),
("WICC","WAHQ","ATR72","01:30"),
("WICC","WIKK","ATR72","01:40"),
("WICC","WIKT","ATR72","01:40"),
("WICC","WARA","ATR72","01:50"),
("WICC","WIPP","ATR72","01:50"),
("WICC","WARR","ATR72","01:50"),
("WICC","WIGG","ATR72","02:20"),
("WICC","WIJJ","ATR72","02:30"),

("WAOO","WAOK","ATR72","00:50"),
("WAOO","WAGS","ATR72","01:00"),
("WAOO","WAGB","ATR72","01:20"),
("WAOO","WALL","ATR72","01:30"),

("WADY","WARR","ATR72","01:00"),

("WIDD","WIDT","ATR72","00:50"),
("WIDD","WIDN","ATR72","00:50"),
("WIDD","WIDS","ATR72","01:00"),
("WIDD","WIBD","ATR72","01:00"),
("WIDD","WIDL","ATR72","01:10"),
("WIDD","WIBB","ATR72","01:30"),
("WIDD","WIKK","ATR72","01:30"),
("WIDD","WIGG","ATR72","01:30"),
("WIDD","WIJJ","ATR72","01:30"),
("WIDD","WIPP","ATR72","01:30"),
("WIDD","WIDO","ATR72","01:40"),
("WIDD","WIOO","ATR72","01:50"),

("WAOC","WAAA","ATR72","01:30"),

("WAWB","WAWW","ATR72","00:50"),
("WAWB","WAAA","ATR72","01:20"),

("WIGG","WIGM","ATR72","01:00"),
("WIGG","WIPP","ATR72","01:10"),
("WIGG","WILL","ATR72","01:20"),
("WIGG","WIDD","ATR72","01:30"),
("WIGG","WIEE","ATR72","01:30"),
("WIGG","WICC","ATR72","02:20"),

("WADB","WADL","ATR72","01:00"),
("WADB","WADD","ATR72","01:20"),

("WRSC","WIHP","ATR72","02:00"),

("WAEM","WAEE","ATR72","00:50"),

("WAFY","WAFF","ATR72","01:20"),

("WAVD","WAJJ","ATR72","01:30"),

("WADD","WADL","ATR72","00:50"),
("WADD","WADB","ATR72","01:20"),
("WADD","WATK","ATR72","01:30"),
("WADD","WATO","ATR72","01:30"),
("WADD","WARA","ATR72","01:30"),
("WADD","WATC","ATR72","01:40"),
("WADD","WAHS","ATR72","01:40"),
("WADD","WATU","ATR72","01:40"),
("WADD","WAHQ","ATR72","01:50"),
("WADD","WAHH","ATR72","01:50"),

("WAPD","WAPP","ATR72","01:30"),

("WIBD","WIBB","ATR72","00:50"),
("WIBD","WIDD","ATR72","01:00"),
("WIBD","WIMM","ATR72","01:00"),

("WATE","WATO","ATR72","01:00"),
("WATE","WATT","ATR72","01:00"),

("WAKG","WAYY","ATR72","01:00"),
("WAKG","WAKK","ATR72","01:00"),

("WASF","WASS","ATR72","01:00"),
("WASF","WAUU","ATR72","01:20"),
("WASF","WAPP","ATR72","01:40"),

("WAEG","WAMM","ATR72","01:20"),

("WAMG","WAMM","ATR72","01:20"),
("WAMG","WAFF","ATR72","01:50"),

("WIMB","WIMM","ATR72","01:10"),
("WIMB","WIEE","ATR72","01:20"),

("WIHH","WICC","ATR72","00:50"),
("WIHH","WICA","ATR72","00:50"),
("WIHH","WICM","ATR72","01:00"),

("WIJJ","WIBB","ATR72","01:00"),
("WIJJ","WIJB","ATR72","01:00"),
("WIJJ","WIPP","ATR72","01:20"),
("WIJJ","WIDD","ATR72","01:30"),
("WIJJ","WIEE","ATR72","01:30"),
("WIJJ","WILL","ATR72","01:30"),
("WIJJ","WIMM","ATR72","01:50"),
("WIJJ","WICC","ATR72","02:30"),

("WAJJ","WAVV","ATR72","01:20"),
("WAJJ","WAVD","ATR72","01:30"),
("WAJJ","WAKT","ATR72","01:30"),
("WAJJ","WABI","ATR72","01:40"),

("WARE","WARR","ATR72","01:00"),

("WASK","WASS","ATR72","01:00"),

("WAQT","WAQQ","ATR72","01:00"),
("WAQT","WALS","ATR72","01:00"),
("WAQT","WALL","ATR72","01:25"),

("WAEK","WAMM","ATR72","01:20"),

("WAHU","WAHS","ATR72","00:50"),

("WAWW","WAWB","ATR72","00:50"),
("WAWW","WAWD","ATR72","01:00"),
("WAWW","WAFO","ATR72","01:20"),
]

# =========================
# THAI LION DATA
# =========================
data_thai_bangkok = [
("VTBD","VTUK","B739","00:50"),
("VTBD","VTPP","B739","00:50"),
("VTBD","VTUD","B739","01:00"),
("VTBD","VTUU","B739","01:00"),

("VTBD","VTCC","B739","01:20"), ("VTBD","VTCC","A333","01:20"), ("VTBD","VTCC","A339","01:20"),

("VTBD","VTSG","B739","01:30"), ("VTBD","VTSG","A333","01:30"), ("VTBD","VTSG","A339","01:30"),
("VTBD","VTSF","B739","01:30"),

("VTBD","VTSS","B739","01:30"), ("VTBD","VTSS","A333","01:30"), ("VTBD","VTSS","A339","01:30"),
("VTBD","VTSP","B739","01:30"), ("VTBD","VTSP","A333","01:30"), ("VTBD","VTSP","A339","01:30"),

("VTBD","VTCT","B739","01:30"),
("VTBD","VTST","B739","01:30"),
("VTBD","VYYY","B739","01:30"),

("VTBD","VTSB","B739","01:40"),

("VTBD","VVNB","B739","01:50"),

("VTBD","WIDD","B739","06:15"),

("VTBD","WSSS","B739","02:00"), ("VTBD","WSSS","A333","02:00"), ("VTBD","WSSS","A339","02:00"),
("VTBD","WMKP","B739","02:00"),

("VTBD","ZJHK","B739","02:20"),
("VTBD","SJSY","B739","02:20"),

("VTBD","VMMC","B739","02:40"),

("VTBD","ZGSZ","B739","02:50"),
("VTBD","VNKT","B739","02:50"),
("VTBD","ZGHA","B739","02:50"),
("VTBD","ZGGG","B739","02:50"),

("VTBD","ZUCK","B739","03:00"),
("VTBD","ZUUU","B739","03:00"),

("VTBD","WIII","B739","03:30"),

("VTBD","ZHHH","B739","03:30"),
("VTBD","ZSCN","B739","03:30"), ("VTBD","ZSCN","A333","03:30"), ("VTBD","ZSCN","A339","03:30"),

("VTBD","VCBI","B739","03:30"),

("VTBD","RCTP","B739","03:30"), ("VTBD","RCTP","A333","03:30"), ("VTBD","RCTP","A339","03:30"),

("VTBD","ZSNB","B739","03:40"),
("VTBD","ZSNJ","B739","03:40"),
("VTBD","ZLXY","B739","03:40"),

("VTBD","WADD","B739","03:40"), ("VTBD","WADD","A333","03:40"), ("VTBD","WADD","A339","03:40"),

("VTBD","ZHCC","B739","04:00"), ("VTBD","ZHCC","A333","04:00"), ("VTBD","ZHCC","A339","04:00"),
("VTBD","VOBL","B739","04:00"),

("VTBD","ZSPD","B739","04:30"), ("VTBD","ZSPD","A333","04:30"), ("VTBD","ZSPD","A339","04:30"),
("VTBD","ZSCG","B739","04:30"),
("VTBD","WAMM","B739","04:30"),

("VTBD","VABB","B739","04:30"), ("VTBD","VABB","A333","04:30"), ("VTBD","VABB","A339","04:30"),

("VTBD","ZSHC","B739","04:30"),

("VTBD","ZSJN","B739","05:00"),

("VTBD","RJFF","B739","05:30"), ("VTBD","RJFF","A333","05:30"), ("VTBD","RJFF","A339","05:30"),
("VTBD","ZBTJ","B739","05:30"),

("VTBD","RJBB","A333","06:20"), ("VTBD","RJBB","A339","06:20"),

("VTBD","RJGG","B739","06:20"), ("VTBD","RJGG","A333","06:20"), ("VTBD","RJGG","A339","06:20"),

("VTBD","RJAA","A333","06:30"), ("VTBD","RJAA","A339","06:30"),
]

# =========================
# THAI LION NON HUB DATA
# =========================
data_thai_nonhub = [
("WIDD","VTBD","B739","02:00"),
("VOBL","VTBD","B739","04:00"),
("ZGHA","VTBD","B739","02:50"),
("ZSCG","VTBD","B739","04:30"),
("ZUUU","VTBD","B739","03:00"),

("VOMM","VTBS","A333","03:40"), ("VOMM","VTBS","A339","03:40"),

("VTCC","VTBD","B739","01:20"), ("VTCC","VTBD","A333","01:20"), ("VTCC","VTBD","A339","01:20"),
("VTCC","VTBU","B739","01:30"),
("VTCC","ZGGG","B739","02:40"),
("VTCC","VIDP","A333","04:15"), ("VTCC","VIDP","A339","04:15"),

("VTCT","VTBD","B739","01:30"),

("ZUCK","VTBD","B739","03:00"),
("ZUCK","VTSP","B739","03:40"),

("VCBI","VTBD","B739","03:30"),

("WADD","VTBD","B739","03:40"), ("WADD","VTBD","A333","03:40"), ("WADD","VTBD","A339","03:40"),

("RJFF","VTBD","B739","05:30"), ("RJFF","VTBD","A333","05:30"), ("RJFF","VTBD","A339","05:30"),

("ZGGG","VTCC","B739","02:40"), ("ZGGG","VTCC","A333","02:40"), ("ZGGG","VTCC","A339","02:40"),
("ZGGG","VTBD","B739","02:50"),

("ZJHK","VTBU","B739","02:20"),
("ZJHK","VTBD","B739","02:20"),

("ZSHC","VTBD","B739","04:30"),
("ZSHC","VTSP","B739","05:25"),

("VVNB","VTBD","B739","01:50"),

("VTSS","VTBD","B739","01:30"), ("VTSS","VTBD","A333","01:30"), ("VTSS","VTBD","A339","01:30"),

("ZSOF","VTSP","B739","05:10"),

("WIII","VTBD","B739","03:30"),

("ZSJN","VTBD","B739","05:00"),

("RJBB","VTBD","A333","06:20"), ("RJBB","VTBD","A339","06:20"),

("VNKT","VTBD","B739","02:50"),

("VTUK","VTBD","B739","00:50"),

("VTSG","VTBD","B739","01:30"), ("VTSG","VTBD","A333","01:30"), ("VTSG","VTBD","A339","01:30"),

("VMMC","VTBD","B739","02:40"),

("WAMM","VTBD","B739","04:30"),

("VABB","VTBD","B739","04:30"), ("VABB","VTBD","A333","04:30"), ("VABB","VTBD","A339","04:30"),

("RJGG","VTBD","B739","06:20"), ("RJGG","VTBD","A333","06:20"), ("RJGG","VTBD","A339","06:20"),

("VTSF","VTBD","B739","01:30"),

("ZSCN","VTBD","B739","03:30"), ("ZSCN","VTBD","A333","03:30"), ("ZSCN","VTBD","A339","03:30"),

("ZSNJ","VTBD","B739","03:40"),
("ZSNJ","VTSP","B739","05:20"),

("ZSNB","VTBD","B739","03:40"),

("WMKP","VTBD","B739","02:00"),

("VTPP","VTBD","B739","00:50"),

("VTSP","VTBD","B739","01:30"), ("VTSP","VTBD","A333","01:30"), ("VTSP","VTBD","A339","01:30"),
("VTSP","ZUCK","B739","03:40"),
("VTSP","ZLXY","B739","05:00"),
("VTSP","ZSOF","B739","05:10"),
("VTSP","ZSNJ","B739","05:20"),
("VTSP","ZSHC","B739","05:25"),
("VTSP","ZBTJ","B739","05:40"),

("ZSPD","VTBD","B739","04:30"), ("ZSPD","VTBD","A333","04:30"), ("ZSPD","VTBD","A339","04:30"),

("ZGSZ","VTBD","B739","02:50"),

("ZJSY","VTBD","B739","02:20"),

("WSSS","VTBD","B739","02:00"), ("WSSS","VTBD","A333","02:00"), ("WSSS","VTBD","A339","02:00"),

("VTSB","VTBD","B739","01:40"),

("RCTP","VTBD","B739","03:30"), ("RCTP","VTBD","A333","03:30"), ("RCTP","VTBD","A339","03:30"),

("RCTP","RJAA","B739","03:30"),
("RJAA","RCTP","B739","03:30"),

("ZBTJ","VTBD","B739","05:30"),
("ZBTJ","VTSP","B739","05:40"),

("RJAA","VTBD","A333","06:30"), ("RJAA","VTBD","A339","06:30"),

("VTST","VTBD","B739","01:30"),

("VTBU","VTCC","B739","01:30"),
("VTBU","ZJHK","B739","02:20"),

("VTUU","VTBD","B739","01:00"),
]

# =========================
# INSERT ALL DATA
# =========================

# Normalize ALL datasets before inserting
data_lion_jakarta     = normalize_data(data_lion_jakarta)
data_lion_makassar    = normalize_data(data_lion_makassar)
data_lion_surabaya    = normalize_data(data_lion_surabaya)
data_lion_bali        = normalize_data(data_lion_bali)
data_lion_balikpapan  = normalize_data(data_lion_balikpapan)
data_lion_nonhub      = normalize_data(data_lion_nonhub)

data_batik_jakarta    = normalize_data(data_batik_jakarta)
data_batik_halim      = normalize_data(data_batik_halim)
data_batik_makassar   = normalize_data(data_batik_makassar)
data_batik_nonhub     = normalize_data(data_batik_nonhub)

data_super_jakarta    = normalize_data(data_super_jakarta)

data_wings_abadi      = normalize_data(data_wings_abadi)

data_thai_bangkok     = normalize_data(data_thai_bangkok)
data_thai_nonhub      = normalize_data(data_thai_nonhub)

insert_routes("Lion",  data_lion_jakarta)
insert_routes("Lion",  data_lion_makassar)
insert_routes("Lion",  data_lion_surabaya)
insert_routes("Lion",  data_lion_bali)
insert_routes("Lion",  data_lion_balikpapan)
insert_routes("Lion",  data_lion_nonhub)

insert_routes("Batik", data_batik_jakarta)
insert_routes("Batik", data_batik_halim)
insert_routes("Batik", data_batik_makassar)
insert_routes("Batik", data_batik_nonhub)

insert_routes("Super", data_super_jakarta)

insert_routes("wings", data_wings_abadi)

insert_routes("thai", data_thai_bangkok)
insert_routes("thai", data_thai_nonhub)

conn.commit()
conn.close()

print("Database successfully updated — all routes and their reverses inserted!")