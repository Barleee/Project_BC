"""
Database module for taxi application.

Handles all database operations including connections, table creation,
and CRUD operations for taxis, drivers, clients, and courses.

Author: Project BC Team
Version: 2.0
"""

import sqlite3

DATABASE_PATH = "taxi_app.db"

def polacz_z_baza():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def utworz_tabele():
    conn = polacz_z_baza()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            color TEXT,
            registration_number TEXT NOT NULL UNIQUE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            taxi_id INTEGER,
            FOREIGN KEY (taxi_id) REFERENCES taxis(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,
            taxi_id INTEGER NOT NULL,
            ride_date TEXT NOT NULL,
            pickup_address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (driver_id) REFERENCES drivers(id),
            FOREIGN KEY (taxi_id) REFERENCES taxis(id)
        )
    """)

    cursor.execute("PRAGMA table_info(taxis)")
    columns = [column[1] for column in cursor.fetchall()]
    if "color" not in columns:
        cursor.execute("ALTER TABLE taxis ADD COLUMN color TEXT")
    if "is_available" not in columns:
        cursor.execute("ALTER TABLE taxis ADD COLUMN is_available INTEGER NOT NULL DEFAULT 1")
    if "address" not in columns:
        cursor.execute("ALTER TABLE taxis ADD COLUMN address TEXT")

    for table_name in ("clients", "drivers"):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        if "address" not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN address TEXT")

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_drivers_unique_taxi
        ON drivers(taxi_id)
        WHERE taxi_id IS NOT NULL
    """)

    conn.commit()
    conn.close()
    _usun_przestarzale_kolumny_klientow()


def _usun_przestarzale_kolumny_klientow():
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        columns = [
            column[1]
            for column in conn.execute("PRAGMA table_info(clients)").fetchall()]
        if "taxi_id" not in columns and "ride_date" not in columns:
            return

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")
        conn.execute("""
            CREATE TABLE clients_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        """)
        conn.execute("""
            INSERT INTO clients_new (
                id, first_name, last_name, phone, address, latitude, longitude
            )
            SELECT id, first_name, last_name, phone, address, latitude, longitude
            FROM clients
        """)
        conn.execute("DROP TABLE clients")
        conn.execute("ALTER TABLE clients_new RENAME TO clients")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def dodaj_dane_startowe():
    conn = polacz_z_baza()
    cursor = conn.cursor()

    existing_records = sum(
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        for table_name in ("taxis", "drivers", "clients", "rides"))
    if existing_records:
        conn.close()
        return

    taxis = [
        (1, "Toyota", "Corolla", "Żółty", "WA12345", 52.2297, 21.0122, 1),
        (2, "Skoda", "Octavia", "Biały", "WA23456", 52.2370, 21.0175, 1),
        (3, "Toyota", "Camry", "Czarny", "WA34567", 52.2212, 21.0055, 1),
        (4, "Kia", "Ceed", "Srebrny", "WA45678", 52.2440, 21.0300, 1),
        (5, "Hyundai", "i30", "Biały", "WA56789", 52.2100, 21.0200, 1),
        (6, "Ford", "Focus", "Niebieski", "WA67890", 52.2500, 21.0100, 1),
        (7, "Volkswagen", "Passat", "Czarny", "WA78901", 52.2300, 21.0400, 1),
        (8, "Renault", "Megane", "Szary", "WA89012", 52.2180, 20.9900, 1),
        (9, "Opel", "Astra", "Biały", "WA90123", 52.2600, 21.0250, 1),
        (10, "Mercedes", "E-Class", "Czarny", "WA01234", 52.2050, 21.0350, 1),
        (11, "Toyota", "Prius", "Srebrny", "WA11223", 52.2400, 20.9800, 0),
        (12, "Skoda", "Superb", "Granatowy", "WA22334", 52.2700, 21.0100, 0),
        (13, "Peugeot", "508", "Biały", "WA33445", 52.2000, 20.9950, 0),
        (14, "Volvo", "S90", "Czarny", "WA44556", 52.2550, 21.0450, 0),
        (15, "Nissan", "Leaf", "Zielony", "WA55667", 52.2150, 21.0500, 0),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO taxis (
            id, brand, model, color, registration_number,
            latitude, longitude, is_available
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, taxis)

    drivers = [
        (1, "Jan", "Kowalski", "700800900", "Plac Defilad 1, Warszawa", 52.2297, 21.0122, 1),
        (2, "Anna", "Nowak", "700800901", "Marszałkowska 1, Warszawa", 52.2144, 21.0209, 2),
        (3, "Piotr", "Wiśniewski", "700800902", "Nowy Świat 1, Warszawa", 52.2301, 21.0217, 3),
        (4, "Maria", "Wójcik", "700800903", "Puławska 2, Warszawa", 52.2137, 21.0205, 4),
        (5, "Tomasz", "Kamiński", "700800904", "Grójecka 5, Warszawa", 52.2190, 20.9830, 5),
        (6, "Katarzyna", "Lewandowska", "700800905", "Targowa 12, Warszawa", 52.2500, 21.0400, 6),
        (7, "Marek", "Zieliński", "700800906", "Wolska 10, Warszawa", 52.2320, 20.9750, 7),
        (8, "Ewa", "Szymańska", "700800907", "Mokotowska 20, Warszawa", 52.2200, 21.0180, 8),
        (9, "Paweł", "Woźniak", "700800908", "Kasprzaka 18, Warszawa", 52.2280, 20.9600, 9),
        (10, "Joanna", "Dąbrowska", "700800909", "Świętokrzyska 30, Warszawa", 52.2350, 21.0080, 10),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO drivers (
            id, first_name, last_name, phone, address,
            latitude, longitude, taxi_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, drivers)

    clients = [
        (1, "Kamil", "Nowak", "500600700", "Złota 44, Warszawa", 52.2339, 21.0021),
        (2, "Artur", "Kowalski", "500600701", "Krucza 10, Warszawa", 52.2260, 21.0180),
        (3, "Paweł", "Gaweł", "500600702", "Marszałkowska 4, Warszawa", 52.2145, 21.0214),
        (4, "Alicja", "Mazur", "500600703", "Chmielna 20, Warszawa", 52.2310, 21.0100),
        (5, "Robert", "Krawczyk", "500600704", "Długa 5, Warszawa", 52.2490, 21.0080),
        (6, "Monika", "Piotrowska", "500600705", "Belwederska 10, Warszawa", 52.2100, 21.0280),
        (7, "Łukasz", "Grabowski", "500600706", "Sienna 15, Warszawa", 52.2310, 20.9950),
        (8, "Natalia", "Pawłowska", "500600707", "Solec 20, Warszawa", 52.2250, 21.0380),
        (9, "Adam", "Michalski", "500600708", "Żelazna 30, Warszawa", 52.2300, 20.9860),
        (10, "Karolina", "Król", "500600709", "Prosta 10, Warszawa", 52.2320, 20.9910),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO clients (
            id, first_name, last_name, phone, address,
            latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, clients)

    rides = [
        (1, 1, 1, 1, "2026-06-10", "Złota 44, Warszawa", 52.2339, 21.0021),
        (2, 2, 2, 2, "2026-06-10", "Krucza 10, Warszawa", 52.2260, 21.0180),
        (3, 3, 3, 3, "2026-06-10", "Marszałkowska 4, Warszawa", 52.2145, 21.0214),
        (4, 4, 4, 4, "2026-06-11", "Chmielna 20, Warszawa", 52.2310, 21.0100),
        (5, 5, 5, 5, "2026-06-11", "Długa 5, Warszawa", 52.2490, 21.0080),
        (6, 6, 6, 6, "2026-06-11", "Belwederska 10, Warszawa", 52.2100, 21.0280),
        (7, 7, 7, 7, "2026-06-12", "Sienna 15, Warszawa", 52.2310, 20.9950),
        (8, 8, 8, 8, "2026-06-12", "Solec 20, Warszawa", 52.2250, 21.0380),
        (9, 9, 9, 9, "2026-06-12", "Żelazna 30, Warszawa", 52.2300, 20.9860),
        (10, 10, 10, 10, "2026-06-13", "Prosta 10, Warszawa", 52.2320, 20.9910),
        (101, 1, 4, 4, "2026-06-01", "Złota 44, Warszawa", 52.2339, 21.0021),
        (102, 2, 4, 4, "2026-06-01", "Krucza 10, Warszawa", 52.2260, 21.0180),
        (103, 3, 4, 4, "2026-06-02", "Marszałkowska 4, Warszawa", 52.2145, 21.0214),
        (104, 4, 4, 4, "2026-06-02", "Chmielna 20, Warszawa", 52.2310, 21.0100),
        (105, 5, 4, 4, "2026-06-03", "Długa 5, Warszawa", 52.2490, 21.0080),
        (106, 6, 4, 4, "2026-06-03", "Belwederska 10, Warszawa", 52.2100, 21.0280),
        (107, 7, 4, 4, "2026-06-04", "Sienna 15, Warszawa", 52.2310, 20.9950),
        (108, 8, 4, 4, "2026-06-04", "Solec 20, Warszawa", 52.2250, 21.0380),
        (109, 9, 4, 4, "2026-06-05", "Żelazna 30, Warszawa", 52.2300, 20.9860),
        (110, 10, 4, 4, "2026-06-05", "Prosta 10, Warszawa", 52.2320, 20.9910),
        (111, 1, 4, 4, "2026-06-06", "Nowy Świat 1, Warszawa", 52.2301, 21.0217),
        (112, 3, 4, 4, "2026-06-06", "Puławska 2, Warszawa", 52.2137, 21.0205),
        (113, 5, 4, 4, "2026-06-07", "Grójecka 5, Warszawa", 52.2190, 20.9830),
        (114, 7, 4, 4, "2026-06-08", "Wolska 10, Warszawa", 52.2320, 20.9750),
        (115, 9, 4, 4, "2026-06-09", "Kasprzaka 18, Warszawa", 52.2280, 20.9600),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO rides (
            id, client_id, driver_id, taxi_id, ride_date,
            pickup_address, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rides)

    conn.commit()
    conn.close()


def dodaj_klienta_do_bazy(first_name, last_name, phone, address, latitude, longitude):
    _wykonaj_zapis("""
        INSERT INTO clients (
            first_name, last_name, phone, address,
            latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, phone, address, latitude, longitude))


def aktualizuj_klienta_w_bazie(client_id, first_name, last_name, phone, address, latitude, longitude):
    _wykonaj_zapis("""
        UPDATE clients
        SET first_name = ?, last_name = ?, phone = ?, address = ?,
            latitude = ?, longitude = ?
        WHERE id = ?
    """, (first_name, last_name, phone, address, latitude, longitude, client_id))


def dodaj_taksowke_do_bazy(brand, model, color, registration_number, address, latitude, longitude, is_available):
    _wykonaj_zapis("""
        INSERT INTO taxis (
            brand, model, color, registration_number, address,
            latitude, longitude, is_available
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (brand, model, color, registration_number, address, latitude, longitude, is_available))


def aktualizuj_taksowke_w_bazie(taxi_id, brand, model, color, registration_number, address, latitude, longitude, is_available):
    _wykonaj_zapis("""
        UPDATE taxis
        SET brand = ?, model = ?, color = ?, registration_number = ?,
            address = ?, latitude = ?, longitude = ?, is_available = ?
        WHERE id = ?
    """, (brand, model, color, registration_number, address, latitude, longitude, is_available, taxi_id))


def usun_taksowke_z_bazy(taxi_id):
    _wykonaj_zapis("DELETE FROM taxis WHERE id = ?", (taxi_id,))


def usun_klienta_z_bazy(client_id):
    _wykonaj_zapis("DELETE FROM clients WHERE id = ?", (client_id,))


def dodaj_kierowce_do_bazy(first_name, last_name, phone, address, latitude, longitude, taxi_id):
    _wykonaj_zapis("""
        INSERT INTO drivers (
            first_name, last_name, phone, address, latitude, longitude, taxi_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, phone, address, latitude, longitude, taxi_id))


def aktualizuj_kierowce_w_bazie(driver_id, first_name, last_name, phone, address, latitude, longitude, taxi_id):
    _wykonaj_zapis("""
        UPDATE drivers
        SET first_name = ?, last_name = ?, phone = ?, address = ?,
            latitude = ?, longitude = ?, taxi_id = ?
        WHERE id = ?
    """, (first_name, last_name, phone, address, latitude, longitude, taxi_id, driver_id))


def usun_kierowce_z_bazy(driver_id):
    _wykonaj_zapis("DELETE FROM drivers WHERE id = ?", (driver_id,))


def dodaj_kurs_do_bazy(client_id, driver_id, taxi_id, ride_date, pickup_address, latitude, longitude):
    _sprawdz_kolizje_kursu(driver_id, taxi_id, ride_date)
    _wykonaj_zapis("""
        INSERT INTO rides (
            client_id, driver_id, taxi_id, ride_date,
            pickup_address, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client_id, driver_id, taxi_id, ride_date, pickup_address, latitude, longitude))


def aktualizuj_kurs_w_bazie(ride_id, client_id, driver_id, taxi_id, ride_date, pickup_address, latitude, longitude):
    _sprawdz_kolizje_kursu(driver_id, taxi_id, ride_date, ride_id)
    _wykonaj_zapis("""
        UPDATE rides
        SET client_id = ?, driver_id = ?, taxi_id = ?, ride_date = ?,
            pickup_address = ?, latitude = ?, longitude = ?
        WHERE id = ?
    """, (client_id, driver_id, taxi_id, ride_date, pickup_address, latitude, longitude, ride_id))


def usun_kurs_z_bazy(ride_id):
    _wykonaj_zapis("DELETE FROM rides WHERE id = ?", (ride_id,))


def _sprawdz_kolizje_kursu(driver_id, taxi_id, ride_date, ignored_ride_id=None):
    query = """
        SELECT driver_id, taxi_id
        FROM rides
        WHERE ride_date = ?
          AND (driver_id = ? OR taxi_id = ?)
    """
    parameters = [ride_date, driver_id, taxi_id]
    if ignored_ride_id is not None:
        query += " AND id != ?"
        parameters.append(ignored_ride_id)

    collisions = _pobierz_wszystkie(query, parameters)
    if any(ride_driver_id == driver_id for ride_driver_id, _ in collisions):
        raise ValueError("Wybrany kierowca ma już kurs w tym dniu.")
    if any(ride_taxi_id == taxi_id for _, ride_taxi_id in collisions):
        raise ValueError("Wybrana taksówka ma już kurs w tym dniu.")


def _wykonaj_zapis(query, parameters=()):
    conn = polacz_z_baza()
    try:
        conn.execute(query, parameters)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _pobierz_wszystkie(query, parameters=()):
    conn = polacz_z_baza()
    try:
        return conn.execute(query, parameters).fetchall()
    finally:
        conn.close()


def _pobierz_jeden(query, parameters):
    conn = polacz_z_baza()
    try:
        return conn.execute(query, parameters).fetchone()
    finally:
        conn.close()


def pobierz_wszystkich_klientow():
    return _pobierz_wszystkie("""
        SELECT id, first_name, last_name, phone, latitude, longitude, address
        FROM clients
    """)


def pobierz_wszystkie_taksowki():
    return _pobierz_wszystkie("""
        SELECT id, brand, model, color, registration_number, is_available,
               latitude, longitude, address
        FROM taxis
        ORDER BY brand, model, registration_number
    """)


def pobierz_klienta_po_id(client_id):
    return _pobierz_jeden("""
        SELECT id, first_name, last_name, phone, latitude, longitude, address
        FROM clients
        WHERE id = ?
    """, (client_id,))


def pobierz_taksowke_po_id(taxi_id):
    return _pobierz_jeden("""
        SELECT id, brand, model, color, registration_number, is_available,
               latitude, longitude, address
        FROM taxis
        WHERE id = ?
    """, (taxi_id,))


def pobierz_wszystkich_kierowcow():
    return _pobierz_wszystkie("""
        SELECT drivers.id, drivers.first_name, drivers.last_name, drivers.phone,
               drivers.latitude, drivers.longitude, taxis.brand, taxis.model,
               taxis.color, taxis.registration_number, drivers.address
        FROM drivers
        LEFT JOIN taxis ON drivers.taxi_id = taxis.id
    """)


def pobierz_kierowce_po_id(driver_id):
    return _pobierz_jeden("""
        SELECT id, first_name, last_name, phone, latitude, longitude, taxi_id, address
        FROM drivers
        WHERE id = ?
    """, (driver_id,))


def pobierz_wszystkie_kursy(taxi_id=None, ride_date=None):
    query = """
        SELECT rides.id,
               clients.first_name || ' ' || clients.last_name,
               drivers.first_name || ' ' || drivers.last_name,
               taxis.brand || ' ' || taxis.model || ' | ' || taxis.registration_number,
               rides.ride_date, rides.pickup_address, rides.latitude, rides.longitude,
               rides.client_id, rides.driver_id, rides.taxi_id
        FROM rides
        JOIN clients ON rides.client_id = clients.id
        JOIN drivers ON rides.driver_id = drivers.id
        JOIN taxis ON rides.taxi_id = taxis.id
        WHERE 1 = 1
    """
    parameters = []
    if taxi_id is not None:
        query += " AND rides.taxi_id = ?"
        parameters.append(taxi_id)
    if ride_date:
        query += " AND rides.ride_date = ?"
        parameters.append(ride_date)
    query += " ORDER BY rides.ride_date, rides.id"
    return _pobierz_wszystkie(query, parameters)


def pobierz_kurs_po_id(ride_id):
    return _pobierz_jeden("""
        SELECT id, client_id, driver_id, taxi_id, ride_date,
               pickup_address, latitude, longitude
        FROM rides
        WHERE id = ?
    """, (ride_id,))


def pobierz_klientow_taksowki_z_dnia(taxi_id, ride_date):
    return _pobierz_wszystkie("""
        SELECT clients.id, clients.first_name, clients.last_name, clients.phone,
               clients.latitude, clients.longitude, rides.ride_date, clients.address
        FROM clients
        JOIN rides ON rides.client_id = clients.id
        WHERE rides.taxi_id = ? AND rides.ride_date = ?
        GROUP BY clients.id
    """, (taxi_id, ride_date))
