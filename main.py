from tkinter import *
import tkintermapview
import requests
import sqlite3
from bs4 import BeautifulSoup
from model import model_user


users:list = []

class User:
    def __init__(self, imie: str, nazwisko: str, lokalizacja: str):
        self.imie = imie
        self.nazwisko = nazwisko
        self.lokalizacja = lokalizacja
        self.coordinates = get_coordinates(self)

        self.marker = map_widget.set_marker(self.coordinates[0],self.coordinates[1],text=self.imie)

def get_coordinates (self) -> list:
    url = f"https://pl.wikipedia.org/wiki/{self.lokalizacja}"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    response_html = BeautifulSoup (response.text,'html.parser')
    latitude = float(response_html.select(".latitude") [1].text.replace(",","."))
    longitude = float(response_html.select(".longitude")[1].text.replace(",","."))
    return [latitude, longitude]

def show_users() -> None:
    listbox_lista_obiektow.delete(0, END)
    for idx, user in enumerate(users):
        listbox_lista_obiektow.insert(END, user.imie)

def remove_user() -> None:
    i = listbox_lista_obiektow.index(ACTIVE)
    users[i].marker.delete()
    users.pop(i)
    show_users()

def add_user():
    name = entry_imie.get()
    surname = entry_nazwisko.get()
    lokalizacja = entry_lokalizacja.get()
    new_user = User(imie=name, nazwisko=surname, lokalizacja=lokalizacja)
    users.append(new_user)
    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_lokalizacja.delete(0, END)

    entry_imie.focus()
    show_users()

def show_user_details():
    i = get_selected_index()
    if i is None:
        return

    imie = users[i].imie
    nazwisko = users[i].nazwisko
    lokalizacja = users[i].lokalizacja

    label_imie_szczegoly_obiektu_wartosc.config(text=imie)
    label_nazwisko_szczegoly_obiektu_wartosc.config(text=nazwisko)
    label_lokalizacja_obiektu_wartosc.config(text=lokalizacja)

    map_widget.set_position(users[i].coordinates[0],users[i].coordinates[1])
    map_widget.set_zoom(12)

def edit_user_details():
    i = listbox_lista_obiektow.index(ACTIVE)
    imie =users[i].imie
    nazwisko =users[i].nazwisko
    lokalizacja=users[i].lokalizacja

    entry_imie.insert(0, imie)
    entry_nazwisko.insert(0, nazwisko)
    entry_lokalizacja.insert(0, lokalizacja)
    show_users()
    entry_imie.focus

    button_dodaj_uzytkownika.config(text= "Zapisz", command=lambda: update_user(i))

def edit_user_details():
    i = get_selected_index()
    if i is None:
        return

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_lokalizacja.delete(0, END)
    imie = users[i].imie
    nazwisko = users[i].nazwisko
    lokalizacja = users[i].lokalizacja
    entry_imie.insert(0, imie)
    entry_nazwisko.insert(0, nazwisko)
    entry_lokalizacja.insert(0, lokalizacja)
    entry_imie.focus()
    button_dodaj_uzytkownika.config(text="Zapisz",command=lambda: update_user(i))
    
def update_user(i):
    users[i].imie = entry_imie.get()
    users[i].nazwisko = entry_nazwisko.get()
    users[i].lokalizacja = entry_lokalizacja.get()
    users[i].coordinates = get_coordinates(users[i])
    users[i].marker.delete()
    users[i].marker = map_widget.set_marker(users[i].coordinates[1],text=users[i].imie)

    button_dodaj_uzytkownika.config(text="Dodaj użytkownika",command=add_user)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_lokalizacja.delete(0, END)

    show_users()

def connect_db():
    conn = sqlite3.connect("taxi_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

# tabela zawierające dane o taksówkarzu, nr.reje, mode,marka,współrzędne.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            registration_number TEXT NOT NULL UNIQUE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)

#tabela dla taksówkarza imie,nazwisko,numer telefonu, współzędne, przypisanie do taksówki? coś co określi czym jeździ.
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
    conn.commit()
    conn.close()
#dodawanie użytkowników do SQL
def add_client_to_db(first_name, last_name, phone, latitude, longitude, taxi_id, ride_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clients (first_name, last_name, phone, latitude, longitude, taxi_id, ride_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, phone, latitude, longitude, taxi_id, ride_date))

    conn.commit()
    conn.close()
#pobieranie danych z bazy SQL  na podstawie parametrów

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
            clients.ride_date,
            taxis.brand,
            taxis.model,
            taxis.registration_number
        FROM clients
        LEFT JOIN taxis ON clients.taxi_id = taxis.id
    """)
#pobieranie danych o klientach z danego dnia
    def get_clients_by_taxi_and_date(taxi_id, ride_date):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT clients.id,
                              clients.first_name,
                              clients.last_name,
                              clients.phone,
                              clients.latitude,
                              clients.longitude,
                              clients.ride_date
                       FROM clients
                       WHERE clients.taxi_id = ?
                         AND clients.ride_date = ?
                       """, (taxi_id, ride_date))

        clients = cursor.fetchall()
        conn.close()

        return clients
    clients = cursor.fetchall()
    conn.close()

    return clients
#wyświetlanie klientów
def show_clients():
    listbox_lista_obiektow.delete(0, END)

    clients = get_all_clients()

    for client in clients:
        client_id = client[0]
        first_name = client[1]
        last_name = client[2]
        ride_date = client[6]
        taxi_brand = client[7]
        taxi_model = client[8]
        registration_number = client[9]

        listbox_lista_obiektow.insert(
            END,
            f"{client_id}. {first_name} {last_name} | {ride_date} | {taxi_brand} {taxi_model} {registration_number}")

#wyświetlanie klientów na mapie z markerami
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

        marker = map_widget.set_marker(
            latitude,
            longitude,
            text=f"{first_name} {last_name}"
        )

        client_markers.append(marker)



root=Tk()
root.title("Mapbook_BC")
root.geometry("1024x760")
create_tables()

# RAMKI
ramka_lista_obiektow = Frame(root)

ramka_formularz = Frame(root)

ramka_szczegoly_obiektu = Frame(root)

ramka_mapa= Frame(root)

ramka_lista_obiektow.grid(row=0, column=0, padx=50)
ramka_formularz.grid(row=0, column=1)
ramka_szczegoly_obiektu.grid(row=1, column=0, columnspan=2, pady=20, padx=50)
ramka_mapa.grid(row=2, column=0, columnspan=2)

# RAMkA LiSTA OBIEKTÓW

label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista użytkowników: ")
listbox_lista_obiektow = Listbox(ramka_lista_obiektow)
# tworzenei guzików, buttonów pod tabelą ( rodzic ramka_lista_obiektow, tam będzie wyskakiwać

button_pokaz_szczegoly_obiektu = Button(ramka_lista_obiektow, text="Pokaz szczegoly ", command= show_user_details )
button_usuwanie_obiektu = Button(ramka_lista_obiektow, text="Usuwanie", command = remove_user)
button_edytowanie_obiektow = Button(ramka_lista_obiektow,text="Edytowanie",command=edit_user_details)
# Definiowanie położenia działa na podstawie szereg x kolumna

label_lista_obiektow.grid(row=0, column=0)
listbox_lista_obiektow.grid(row=1, column=0)
button_pokaz_szczegoly_obiektu.grid(row=2, column=0)
button_usuwanie_obiektu.grid(row=2, column=1)
button_edytowanie_obiektow.grid(row=2, column=2)

# Ramka forumlarza 1 ramka 2 polozenie jej
label_formularz = Label(ramka_formularz, text="Formularz: ")
label_formularz.grid(row=0, column=0, columnspan=2)
label_imie = Label(ramka_formularz, text="Imię")
label_imie.grid(row=1, column=0, sticky=W)
label_nazwisko =Label(ramka_formularz, text="Nazwisko")
label_nazwisko.grid(row=2, column=0, sticky=W)
label_lokalizacja = Label(ramka_formularz, text="Lokalizacja")
label_lokalizacja.grid(row=4, column=0,sticky=W)

#Wprowadzanie danych
entry_imie=Entry(ramka_formularz)
entry_imie.grid(row=1, column=1)
entry_nazwisko=Entry(ramka_formularz)
entry_nazwisko.grid(row=2, column=1)
entry_lokalizacja=Entry(ramka_formularz)
entry_lokalizacja.grid(row=4, column=1)


button_dodaj_uzytkownika = Button(ramka_formularz, text="Dodaj użytkownika", command = add_user)
button_dodaj_uzytkownika.grid(row=5, column=1, columnspan=2)

# Szczegóły obiektu

labe_szczegoly_obiektu = Label (ramka_szczegoly_obiektu, text="Szczegóły obiektu")
labe_szczegoly_obiektu.grid(row=0, column=2)


# Etykiety
label_imie_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Imie")
label_imie_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartosc")
label_nazwisko_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Nazwisko")
label_nazwisko_szczegoly_obiektu_wartosc =  Label(ramka_szczegoly_obiektu, text="Wartosc")
label_lokalizacja_obiektu = Label(ramka_szczegoly_obiektu,text="Lokalizacja")
label_lokalizacja_obiektu_wartosc = Label(ramka_szczegoly_obiektu,text="Wartosc")


label_imie_szczegoly_obiektu.grid(row=1, column=0)
label_imie_szczegoly_obiektu_wartosc.grid(row=1, column=1)
label_nazwisko_szczegoly_obiektu.grid(row=1, column=2)
label_nazwisko_szczegoly_obiektu_wartosc.grid(row=1, column=3)
label_lokalizacja_obiektu.grid(row=1, column=6)

# Ramka dla mapy
map_widget = tkintermapview.TkinterMapView(ramka_mapa,width=900,  height=480, corner_radius=4)
map_widget.set_zoom(6)
map_widget.set_position(52.2,21.0)
map_widget.grid(row=0, column=0)

root.mainloop()
