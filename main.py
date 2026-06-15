from tkinter import *
import tkintermapview
import requests
import sqlite3
from bs4 import BeautifulSoup


users: list = []
client_markers = []
driver_markers = []
listbox_record_ids = []
current_list_type = None
current_form_type = None
edited_record_id = None
form_entries = {}

class User:
    def __init__(self, imie: str, nazwisko: str, lokalizacja: str):
        self.imie = imie
        self.nazwisko = nazwisko
        self.lokalizacja = lokalizacja
        self.coordinates = get_coordinates_from_location(self.lokalizacja)
        self.marker = map_widget.set_marker(
            self.coordinates[0],
            self.coordinates[1],
            text=self.imie )


def get_coordinates_from_location(lokalizacja: str) -> list:
    try:
        parts = lokalizacja.split(",")

        if len(parts) == 2:
            latitude = float(parts[0].strip().replace(",", "."))
            longitude = float(parts[1].strip().replace(",", "."))
            return [latitude, longitude]

        url = f"https://pl.wikipedia.org/wiki/{lokalizacja}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response_html = BeautifulSoup(response.text, "html.parser")

        latitude = float(response_html.select(".latitude")[1].text.replace(",", "."))
        longitude = float(response_html.select(".longitude")[1].text.replace(",", "."))

        return [latitude, longitude]
    except:
        return [52.2297, 21.0122]


def get_coordinates(self) -> list:
    return get_coordinates_from_location(self.lokalizacja)


def show_users() -> None:
    global current_list_type
    global listbox_record_ids

    current_list_type = "users"
    listbox_record_ids = []

    listbox_lista_obiektow.delete(0, END)

    for idx, user in enumerate(users):
        listbox_lista_obiektow.insert(END, user.imie)
        listbox_record_ids.append(idx)


def get_selected_index():
    selected = listbox_lista_obiektow.curselection()

    if not selected:
        return None

    return selected[0]


def get_selected_record_id():
    i = get_selected_index()

    if i is None:
        return None

    if i >= len(listbox_record_ids):
        return None

    return listbox_record_ids[i]


def remove_user() -> None:
    i = get_selected_index()

    if i is None:
        return

    if current_list_type == "clients":
        record_id = get_selected_record_id()

        if record_id is None:
            return

        delete_client_from_db(record_id)
        show_clients()
        return

    if current_list_type == "drivers":
        record_id = get_selected_record_id()

        if record_id is None:
            return

        delete_driver_from_db(record_id)
        show_drivers()
        return

    if i >= len(users):
        return

    users[i].marker.delete()
    users.pop(i)
    show_users()


def add_user():
    name = form_entries["imie"].get()
    surname = form_entries["nazwisko"].get()
    lokalizacja = form_entries["lokalizacja"].get()

    new_user = User(imie=name, nazwisko=surname, lokalizacja=lokalizacja)
    users.append(new_user)

    clear_form()
    show_users()


def show_user_details():
    i = get_selected_index()

    if i is None:
        return

    if current_list_type == "clients":
        record_id = get_selected_record_id()
        client = get_client_by_id(record_id)

        if client is None:
            return

        label_imie_szczegoly_obiektu_wartosc.config(text=client[1])
        label_nazwisko_szczegoly_obiektu_wartosc.config(text=client[2])
        label_lokalizacja_obiektu_wartosc.config(text=f"{client[4]}, {client[5]}")

        map_widget.set_position(client[4], client[5])
        map_widget.set_zoom(12)
        return

    if current_list_type == "drivers":
        record_id = get_selected_record_id()
        driver = get_driver_by_id(record_id)

        if driver is None:
            return

        label_imie_szczegoly_obiektu_wartosc.config(text=driver[1])
        label_nazwisko_szczegoly_obiektu_wartosc.config(text=driver[2])
        label_lokalizacja_obiektu_wartosc.config(text=f"{driver[4]}, {driver[5]}")

        map_widget.set_position(driver[4], driver[5])
        map_widget.set_zoom(12)
        return

    if i >= len(users):
        return

    imie = users[i].imie
    nazwisko = users[i].nazwisko
    lokalizacja = users[i].lokalizacja

    label_imie_szczegoly_obiektu_wartosc.config(text=imie)
    label_nazwisko_szczegoly_obiektu_wartosc.config(text=nazwisko)
    label_lokalizacja_obiektu_wartosc.config(text=lokalizacja)

    map_widget.set_position(
        users[i].coordinates[0],
        users[i].coordinates[1]
    )
    map_widget.set_zoom(12)


def edit_user_details():
    global edited_record_id

    i = get_selected_index()

    if i is None:
        return

    if current_list_type == "clients":
        record_id = get_selected_record_id()
        client = get_client_by_id(record_id)

        if client is None:
            return

        show_client_form()
        edited_record_id = record_id

        form_entries["imie"].insert(0, client[1])
        form_entries["nazwisko"].insert(0, client[2])
        form_entries["telefon"].insert(0, client[3])
        form_entries["lokalizacja"].insert(0, f"{client[4]}, {client[5]}")
        form_entries["taxi_id"].insert(0, client[6])
        form_entries["data"].insert(0, client[7])

        button_zapisz_formularz.config(text="Zapisz zmiany klienta")


        return

    if current_list_type == "drivers":
        record_id = get_selected_record_id()
        driver = get_driver_by_id(record_id)

        if driver is None:
            return

        show_driver_form()
        edited_record_id = record_id

        form_entries["imie"].insert(0, driver[1])
        form_entries["nazwisko"].insert(0, driver[2])
        form_entries["telefon"].insert(0, driver[3])
        form_entries["lokalizacja"].insert(0, f"{driver[4]}, {driver[5]}")
        form_entries["taxi_id"].insert(0, driver[6])


        button_zapisz_formularz.config(text="Zapisz zmiany kierowcy")
        return


    if i >= len(users):
        return

    show_simple_user_form()

    form_entries["imie"].insert(0, users[i].imie)
    form_entries["nazwisko"].insert(0, users[i].nazwisko)
    form_entries["lokalizacja"].insert(0, users[i].lokalizacja)


    button_zapisz_formularz.config(text="Zapisz",command=lambda: update_user(i))


def update_user(i):
    if i >= len(users):
        return

    users[i].imie = form_entries["imie"].get()
    users[i].nazwisko = form_entries["nazwisko"].get()
    users[i].lokalizacja = form_entries["lokalizacja"].get()
    users[i].coordinates = get_coordinates(users[i])

    users[i].marker.delete()
    users[i].marker = map_widget.set_marker(
        users[i].coordinates[0],
        users[i].coordinates[1],
        text=users[i].imie
    )

    clear_form()
    show_users()


def connect_db():
    conn = sqlite3.connect("taxi_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            color TEXT,
            registration_number TEXT NOT NULL UNIQUE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
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
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            taxi_id INTEGER,
            ride_date TEXT,
            FOREIGN KEY (taxi_id) REFERENCES taxis(id)
        )
    """)

    cursor.execute("PRAGMA table_info(taxis)")
    columns = [column[1] for column in cursor.fetchall()]

    if "color" not in columns:
        cursor.execute("ALTER TABLE taxis ADD COLUMN color TEXT")

    conn.commit()
    conn.close()


def add_start_data():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO taxis (
            id,
            brand,
            model,
            color,
            registration_number,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Toyota", "Corolla", "Żółty", "WA12345", 52.2297, 21.0122))

    cursor.execute("""
        UPDATE taxis
        SET color = ?
        WHERE id = ?
    """, ("Żółty", 1))

    cursor.execute("""
        INSERT OR IGNORE INTO drivers (
            id,
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Jan", "Kowalski", "700800900", 52.2297, 21.0122, 1))

    cursor.execute("""
        INSERT OR IGNORE INTO clients (
            id,
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id,
            ride_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (1, "Kamil", "Nowak", "500600700", 52.2300, 21.0100, 1, "2025-01-20"))

    cursor.execute("""
        INSERT OR IGNORE INTO clients (
            id,
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id,
            ride_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (2, "Artur", "Kowalski", "600700800", 52.2350, 21.0150, 1, "2025-01-20"))

    conn.commit()
    conn.close()


def add_client_to_db(first_name, last_name, phone, latitude, longitude, taxi_id, ride_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clients (
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id,
            ride_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, phone, latitude, longitude, taxi_id, ride_date))

    conn.commit()
    conn.close()


def update_client_in_db(client_id, first_name, last_name, phone, latitude, longitude, taxi_id, ride_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clients
        SET first_name = ?,
            last_name = ?,
            phone = ?,
            latitude = ?,
            longitude = ?,
            taxi_id = ?,
            ride_date = ?
        WHERE id = ?
    """, (first_name, last_name, phone, latitude, longitude, taxi_id, ride_date, client_id))

    conn.commit()
    conn.close()


def delete_client_from_db(client_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))

    conn.commit()
    conn.close()


def add_driver_to_db(first_name, last_name, phone, latitude, longitude, taxi_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drivers (
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, phone, latitude, longitude, taxi_id))

    conn.commit()
    conn.close()


def update_driver_in_db(driver_id, first_name, last_name, phone, latitude, longitude, taxi_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE drivers
        SET first_name = ?,
            last_name = ?,
            phone = ?,
            latitude = ?,
            longitude = ?,
            taxi_id = ?
        WHERE id = ?
    """, (first_name, last_name, phone, latitude, longitude, taxi_id, driver_id))

    conn.commit()
    conn.close()


def delete_driver_from_db(driver_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))

    conn.commit()
    conn.close()


def get_all_clients():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            clients.id,
            clients.first_name,
            clients.last_name,
            clients.phone,
            clients.latitude,
            clients.longitude,
            clients.ride_date
        FROM clients""")

    clients = cursor.fetchall()
    conn.close()

    return clients


def get_client_by_id(client_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id,
            ride_date
        FROM clients
        WHERE id = ?""", (client_id,))

    client = cursor.fetchone()
    conn.close()

    return client


def get_all_drivers():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            drivers.id,
            drivers.first_name,
            drivers.last_name,
            drivers.phone,
            drivers.latitude,
            drivers.longitude,
            taxis.brand,
            taxis.model,
            taxis.color,
            taxis.registration_number
        FROM drivers
        LEFT JOIN taxis ON drivers.taxi_id = taxis.id""")

    drivers = cursor.fetchall()
    conn.close()

    return drivers


def get_driver_by_id(driver_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            first_name,
            last_name,
            phone,
            latitude,
            longitude,
            taxi_id
        FROM drivers
        WHERE id = ?""", (driver_id,))

    driver = cursor.fetchone()
    conn.close()

    return driver


def get_clients_by_taxi_and_date(taxi_id, ride_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            clients.id,
            clients.first_name,
            clients.last_name,
            clients.phone,
            clients.latitude,
            clients.longitude,
            clients.ride_date
        FROM clients
        WHERE clients.taxi_id = ? AND clients.ride_date = ?""", (taxi_id, ride_date))

    clients = cursor.fetchall()
    conn.close()

    return clients


def show_clients():
    global current_list_type
    global listbox_record_ids

    current_list_type = "clients"
    listbox_record_ids = []

    listbox_lista_obiektow.delete(0, END)

    clients = get_all_clients()

    for client in clients:
        client_id = client[0]
        first_name = client[1]
        last_name = client[2]
        phone = client[3]
        ride_date = client[6]

        listbox_lista_obiektow.insert(END,f"{client_id}. {first_name} {last_name} | tel. {phone} | {ride_date}")

        listbox_record_ids.append(client_id)


def show_drivers():
    global current_list_type
    global listbox_record_ids

    current_list_type = "drivers"
    listbox_record_ids = []

    listbox_lista_obiektow.delete(0, END)

    drivers = get_all_drivers()

    for driver in drivers:
        driver_id = driver[0]
        first_name = driver[1]
        last_name = driver[2]
        phone = driver[3]
        taxi_brand = driver[6]
        taxi_model = driver[7]
        taxi_color = driver[8]
        registration_number = driver[9]

        listbox_lista_obiektow.insert(END,f"{driver_id}. {first_name} {last_name} | tel. {phone} | {taxi_brand} {taxi_model} | kolor: {taxi_color} | rej. {registration_number}")

        listbox_record_ids.append(driver_id)


def show_clients_on_map():
    global client_markers

    for marker in client_markers:
        marker.delete()

    client_markers = []

    clients = get_all_clients()

    for client in clients:
        first_name = client[1]
        last_name = client[2]
        latitude = client[4]
        longitude = client[5]

        marker = map_widget.set_marker(latitude,longitude,text=f"{first_name} {last_name}")

        client_markers.append(marker)


def show_drivers_on_map():
    global driver_markers

    for marker in driver_markers:
        marker.delete()

    driver_markers = []

    drivers = get_all_drivers()

    for driver in drivers:
        first_name = driver[1]
        last_name = driver[2]
        phone = driver[3]
        latitude = driver[4]
        longitude = driver[5]
        taxi_brand = driver[6]
        taxi_model = driver[7]
        taxi_color = driver[8]
        registration_number = driver[9]

        marker = map_widget.set_marker(latitude,longitude,text=f"{first_name} {last_name} | tel. {phone} | {taxi_brand} {taxi_model} | {taxi_color} | {registration_number}")

        driver_markers.append(marker)


def clear_form():
    for widget in ramka_formularz.winfo_children():
        widget.destroy()

    form_entries.clear()


def create_form_field(label_text, key, row):
    label = Label(ramka_formularz, text=label_text)
    label.grid(row=row, column=0, sticky=W)

    entry = Entry(ramka_formularz)
    entry.grid(row=row, column=1)

    form_entries[key] = entry


def show_client_form():
    global current_form_type
    global edited_record_id
    global button_zapisz_formularz

    current_form_type = "client"
    edited_record_id = None

    clear_form()

    label_formularz = Label(ramka_formularz, text="Rejestracja klienta")
    label_formularz.grid(row=0, column=0, columnspan=2)

    create_form_field("Imię", "imie", 1)
    create_form_field("Nazwisko", "nazwisko", 2)
    create_form_field("Telefon", "telefon", 3)
    create_form_field("Lokalizacja", "lokalizacja", 4)
    create_form_field("ID taksówki", "taxi_id", 5)
    create_form_field("Data kursu", "data", 6)

    button_zapisz_formularz = Button(
        ramka_formularz,
        text="Dodaj klienta",
        command=save_form
    )

    button_zapisz_formularz.grid(row=7, column=1, columnspan=2)


def show_driver_form():
    global current_form_type
    global edited_record_id
    global button_zapisz_formularz

    current_form_type = "driver"
    edited_record_id = None

    clear_form()

    label_formularz = Label(ramka_formularz, text="Rejestracja kierowcy")
    label_formularz.grid(row=0, column=0, columnspan=2)

    create_form_field("Imię", "imie", 1)
    create_form_field("Nazwisko", "nazwisko", 2)
    create_form_field("Telefon", "telefon", 3)
    create_form_field("Lokalizacja", "lokalizacja", 4)
    create_form_field("ID taksówki", "taxi_id", 5)

    button_zapisz_formularz = Button(
        ramka_formularz,
        text="Dodaj kierowcę",
        command=save_form
    )

    button_zapisz_formularz.grid(row=6, column=1, columnspan=2)


def show_simple_user_form():
    global current_form_type
    global edited_record_id
    global button_zapisz_formularz

    current_form_type = "user"
    edited_record_id = None

    clear_form()

    label_formularz = Label(ramka_formularz, text="Formularz")
    label_formularz.grid(row=0, column=0, columnspan=2)

    create_form_field("Imię", "imie", 1)
    create_form_field("Nazwisko", "nazwisko", 2)
    create_form_field("Lokalizacja", "lokalizacja", 3)

    button_zapisz_formularz = Button(
        ramka_formularz,
        text="Dodaj użytkownika",
        command=add_user
    )

    button_zapisz_formularz.grid(row=4, column=1, columnspan=2)


def save_form():
    global edited_record_id

    if current_form_type == "client":
        first_name = form_entries["imie"].get()
        last_name = form_entries["nazwisko"].get()
        phone = form_entries["telefon"].get()
        coordinates = get_coordinates_from_location(form_entries["lokalizacja"].get())
        taxi_id = int(form_entries["taxi_id"].get())
        ride_date = form_entries["data"].get()

        if edited_record_id is None:
            add_client_to_db(
                first_name,
                last_name,
                phone,
                coordinates[0],
                coordinates[1],
                taxi_id,
                ride_date
            )
        else:
            update_client_in_db(
                edited_record_id,
                first_name,
                last_name,
                phone,
                coordinates[0],
                coordinates[1],
                taxi_id,
                ride_date
            )

        edited_record_id = None
        show_client_form()
        show_clients()
        return

    if current_form_type == "driver":
        first_name = form_entries["imie"].get()
        last_name = form_entries["nazwisko"].get()
        phone = form_entries["telefon"].get()
        coordinates = get_coordinates_from_location(form_entries["lokalizacja"].get())
        taxi_id = int(form_entries["taxi_id"].get())

        if edited_record_id is None:
            add_driver_to_db(
                first_name,
                last_name,
                phone,
                coordinates[0],
                coordinates[1],
                taxi_id
            )
        else:
            update_driver_in_db(
                edited_record_id,
                first_name,
                last_name,
                phone,
                coordinates[0],
                coordinates[1],
                taxi_id
            )

        edited_record_id = None
        show_driver_form()
        show_drivers()
        return


root = Tk()
root.title("Mapbook_BC")
root.geometry("1120x760")

create_tables()
add_start_data()

ramka_lista_obiektow = Frame(root)
ramka_formularz_typ = Frame(root)
ramka_formularz = Frame(root)
ramka_szczegoly_obiektu = Frame(root)
ramka_mapa = Frame(root)

ramka_lista_obiektow.grid(row=0, column=0, padx=50)
ramka_formularz_typ.grid(row=0, column=1, sticky=N)
ramka_formularz.grid(row=0, column=2, sticky=N)
ramka_szczegoly_obiektu.grid(row=1, column=0, columnspan=3, pady=20, padx=50)
ramka_mapa.grid(row=2, column=0, columnspan=3)

label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista użytkowników:")
listbox_lista_obiektow = Listbox(ramka_lista_obiektow, width=80)

button_pokaz_szczegoly_obiektu = Button(
    ramka_lista_obiektow,
    text="Pokaż szczegóły",
    command=show_user_details
)

button_usuwanie_obiektu = Button(
    ramka_lista_obiektow,
    text="Usuwanie",
    command=remove_user
)

button_edytowanie_obiektow = Button(
    ramka_lista_obiektow,
    text="Edytowanie",
    command=edit_user_details
)

button_pokaz_klientow = Button(
    ramka_lista_obiektow,
    text="Pokaż klientów",
    command=show_clients
)

button_klienci_na_mapie = Button(
    ramka_lista_obiektow,
    text="Klienci na mapie",
    command=show_clients_on_map
)

button_pokaz_kierowcow = Button(
    ramka_lista_obiektow,
    text="Pokaż kierowców",
    command=show_drivers
)

button_kierowcy_na_mapie = Button(
    ramka_lista_obiektow,
    text="Kierowcy na mapie",
    command=show_drivers_on_map
)

label_lista_obiektow.grid(row=0, column=0, columnspan=3)
listbox_lista_obiektow.grid(row=1, column=0, columnspan=3)

button_pokaz_szczegoly_obiektu.grid(row=2, column=0)
button_usuwanie_obiektu.grid(row=2, column=1)
button_edytowanie_obiektow.grid(row=2, column=2)

button_pokaz_klientow.grid(row=3, column=0)
button_klienci_na_mapie.grid(row=3, column=1)

button_pokaz_kierowcow.grid(row=4, column=0)
button_kierowcy_na_mapie.grid(row=4, column=1)

label_typ_formularza = Label(ramka_formularz_typ, text="Wybierz formularz:")
label_typ_formularza.grid(row=0, column=0, columnspan=2)

button_formularz_klient = Button(
    ramka_formularz_typ,
    text="Klient",
    command=show_client_form
)

button_formularz_kierowca = Button(
    ramka_formularz_typ,
    text="Kierowca",
    command=show_driver_form
)

button_formularz_klient.grid(row=1, column=0)
button_formularz_kierowca.grid(row=1, column=1)

label_szczegoly_obiektu = Label(
    ramka_szczegoly_obiektu,
    text="Szczegóły obiektu"
)

label_szczegoly_obiektu.grid(row=0, column=0, columnspan=8)

label_imie_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Imię")
label_imie_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartość")

label_nazwisko_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Nazwisko")
label_nazwisko_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartość")

label_lokalizacja_obiektu = Label(ramka_szczegoly_obiektu, text="Lokalizacja")
label_lokalizacja_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartość")

label_imie_szczegoly_obiektu.grid(row=1, column=0)
label_imie_szczegoly_obiektu_wartosc.grid(row=1, column=1)

label_nazwisko_szczegoly_obiektu.grid(row=1, column=2)
label_nazwisko_szczegoly_obiektu_wartosc.grid(row=1, column=3)

label_lokalizacja_obiektu.grid(row=1, column=4)
label_lokalizacja_obiektu_wartosc.grid(row=1, column=5)

map_widget = tkintermapview.TkinterMapView(
    ramka_mapa,
    width=1000,
    height=480,
    corner_radius=4
)

map_widget.set_zoom(6)
map_widget.set_position(52.2, 21.0)
map_widget.grid(row=0, column=0)

show_client_form()

root.mainloop()
