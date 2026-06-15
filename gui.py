"""
GUI module for taxi application.

Provides tkinter-based user interface with interactive map view,
form management for taxis, drivers, clients, and courses.

Features:
- Interactive map with tkintermapview
- Tabbed interface for managing entities
- Real-time location updates
- Course tracking and management

Author: Project BC Team
Version: 3.0
"""

from tkinter import *
from tkinter import messagebox
import tkintermapview
import sqlite3
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageTk

from database import (
    aktualizuj_klienta_w_bazie,
    aktualizuj_kierowce_w_bazie,
    aktualizuj_kurs_w_bazie,
    aktualizuj_taksowke_w_bazie,
    dodaj_dane_startowe,
    dodaj_klienta_do_bazy,
    dodaj_kierowce_do_bazy,
    dodaj_kurs_do_bazy,
    dodaj_taksowke_do_bazy,
    pobierz_klienta_po_id,
    pobierz_klientow_taksowki_z_dnia,
    pobierz_kierowce_po_id,
    pobierz_kurs_po_id,
    pobierz_taksowke_po_id,
    pobierz_wszystkich_kierowcow,
    pobierz_wszystkich_klientow,
    pobierz_wszystkie_kursy,
    pobierz_wszystkie_taksowki,
    usun_klienta_z_bazy,
    usun_kierowce_z_bazy,
    usun_kurs_z_bazy,
    usun_taksowke_z_bazy,
    utworz_tabele,
)
from services.geocoding import pobierz_wspolrzedne_z_lokalizacji

stan = SimpleNamespace(
    markery_klientow=[],
    markery_kierowcow=[],
    markery_taksowek=[],
    identyfikatory_rekordow_listy=[],
    aktualny_typ_listy=None,
    aktualny_typ_formularza=None,
    id_edytowanego_rekordu=None,
    pola_formularza={},
    opcje_taksowek={},
    opcje_klientow={},
    opcje_kierowcow={},
    opcje_taksowek_filtra_kursow={},
)
ui = SimpleNamespace()
OPCJE_DOSTEPNOSCI = {"Dostępna": 1, "Niedostępna": 0}


def wczytaj_ikone_markera(nazwa_pliku, rozmiar=(48, 48)):
    sciezka_ikony = Path(__file__).parent / "ikonki" / nazwa_pliku
    obraz_ikony = Image.open(sciezka_ikony).convert("RGBA")
    obraz_ikony.thumbnail(rozmiar, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(obraz_ikony)


def pobierz_wybrany_indeks():
    selected = ui.listbox_lista_obiektow.curselection()

    if not selected:
        return None

    return selected[0]


def pobierz_id_wybranego_rekordu():
    i = pobierz_wybrany_indeks()

    if i is None:
        return None

    if i >= len(stan.identyfikatory_rekordow_listy):
        return None

    return stan.identyfikatory_rekordow_listy[i]


def usun_uzytkownika() -> None:
    i = pobierz_wybrany_indeks()

    if i is None:
        return

    if stan.aktualny_typ_listy == "clients":
        record_id = pobierz_id_wybranego_rekordu()

        if record_id is None:
            return

        try:
            usun_klienta_z_bazy(record_id)
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Nie można usunąć klienta",
                "Klient jest przypisany do istniejącego kursu."
            )
            return

        pokaz_klientow()
        return

    if stan.aktualny_typ_listy == "drivers":
        record_id = pobierz_id_wybranego_rekordu()
        if record_id is None:
            return
        try:
            usun_kierowce_z_bazy(record_id)
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Nie można usunąć kierowcy",
                "Kierowca jest przypisany do istniejącego kursu."
            )
            return

        pokaz_kierowcow()
        return

    if stan.aktualny_typ_listy == "taxis":
        record_id = pobierz_id_wybranego_rekordu()
        if record_id is None:
            return
        try:
            usun_taksowke_z_bazy(record_id)
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Nie można usunąć taksówki",
                "Taksówka jest przypisana do kierowcy lub istniejącego kursu."
            )
            return

        odswiez_opcje_taksowek_filtra()
        pokaz_taksowki()
        return

    if stan.aktualny_typ_listy == "rides":
        record_id = pobierz_id_wybranego_rekordu()

        if record_id is None:
            return

        usun_kurs_z_bazy(record_id)
        pokaz_kursy()
        return

def przybliz_mape(latitude, longitude):
    ui.map_widget.set_position(latitude, longitude)
    ui.map_widget.set_zoom(16)


def pokaz_szczegoly_uzytkownika(event=None):
    i = pobierz_wybrany_indeks()

    if i is None:
        return

    if stan.aktualny_typ_listy == "clients":
        record_id = pobierz_id_wybranego_rekordu()
        client = pobierz_klienta_po_id(record_id)

        if client is None:
            return

        ui.label_imie_szczegoly_obiektu.config(text="Imię")
        ui.label_nazwisko_szczegoly_obiektu.config(text="Nazwisko")
        ui.label_lokalizacja_obiektu.config(text="Lokalizacja")
        ui.label_imie_szczegoly_obiektu_wartosc.config(text=client[1])
        ui.label_nazwisko_szczegoly_obiektu_wartosc.config(text=client[2])
        ui.label_lokalizacja_obiektu_wartosc.config(text=client[6] or f"{client[4]}, {client[5]}")

        przybliz_mape(client[4], client[5])
        return

    if stan.aktualny_typ_listy == "drivers":
        record_id = pobierz_id_wybranego_rekordu()
        driver = pobierz_kierowce_po_id(record_id)

        if driver is None:
            return

        ui.label_imie_szczegoly_obiektu.config(text="Imię")
        ui.label_nazwisko_szczegoly_obiektu.config(text="Nazwisko")
        ui.label_lokalizacja_obiektu.config(text="Lokalizacja")
        ui.label_imie_szczegoly_obiektu_wartosc.config(text=driver[1])
        ui.label_nazwisko_szczegoly_obiektu_wartosc.config(text=driver[2])
        ui.label_lokalizacja_obiektu_wartosc.config(text=driver[7] or f"{driver[4]}, {driver[5]}")

        przybliz_mape(driver[4], driver[5])
        return

    if stan.aktualny_typ_listy == "taxis":
        record_id = pobierz_id_wybranego_rekordu()
        taxi = pobierz_taksowke_po_id(record_id)

        if taxi is None:
            return

        ui.label_imie_szczegoly_obiektu.config(text="Taksówka")
        ui.label_nazwisko_szczegoly_obiektu.config(text="Rejestracja")
        ui.label_lokalizacja_obiektu.config(text="Lokalizacja")
        ui.label_imie_szczegoly_obiektu_wartosc.config(
            text=f"{taxi[1]} {taxi[2]} | {taxi[3] or 'brak koloru'}"
        )
        ui.label_nazwisko_szczegoly_obiektu_wartosc.config(text=taxi[4])
        ui.label_lokalizacja_obiektu_wartosc.config(
            text=taxi[8] or f"{taxi[6]}, {taxi[7]}"
        )

        przybliz_mape(taxi[6], taxi[7])
        return

    if stan.aktualny_typ_listy == "rides":
        record_id = pobierz_id_wybranego_rekordu()
        ride = pobierz_kurs_po_id(record_id)

        if ride is None:
            return

        ui.label_imie_szczegoly_obiektu.config(text="Kurs")
        ui.label_nazwisko_szczegoly_obiektu.config(text="Data")
        ui.label_lokalizacja_obiektu.config(text="Adres odbioru")
        ui.label_imie_szczegoly_obiektu_wartosc.config(text=f"Kurs #{ride[0]}")
        ui.label_nazwisko_szczegoly_obiektu_wartosc.config(text=ride[4])
        ui.label_lokalizacja_obiektu_wartosc.config(text=ride[5])

        przybliz_mape(ride[6], ride[7])
        return

def edytuj_szczegoly_uzytkownika():

    i = pobierz_wybrany_indeks()

    if i is None:
        return

    if stan.aktualny_typ_listy == "clients":
        record_id = pobierz_id_wybranego_rekordu()
        client = pobierz_klienta_po_id(record_id)

        if client is None:
            return

        pokaz_formularz_klienta()
        stan.id_edytowanego_rekordu = record_id

        stan.pola_formularza["imie"].insert(0, client[1])
        stan.pola_formularza["nazwisko"].insert(0, client[2])
        stan.pola_formularza["telefon"].insert(0, client[3])
        stan.pola_formularza["lokalizacja"].insert(0, client[6] or f"{client[4]}, {client[5]}")

        ui.button_zapisz_formularz.config(text="Zapisz zmiany klienta")


        return

    if stan.aktualny_typ_listy == "drivers":
        record_id = pobierz_id_wybranego_rekordu()
        driver = pobierz_kierowce_po_id(record_id)

        if driver is None:
            return

        pokaz_formularz_kierowcy()
        stan.id_edytowanego_rekordu = record_id

        stan.pola_formularza["imie"].insert(0, driver[1])
        stan.pola_formularza["nazwisko"].insert(0, driver[2])
        stan.pola_formularza["telefon"].insert(0, driver[3])
        stan.pola_formularza["lokalizacja"].insert(0, driver[7] or f"{driver[4]}, {driver[5]}")
        wybierz_taksowke_w_formularzu(driver[6])


        ui.button_zapisz_formularz.config(text="Zapisz zmiany kierowcy")
        return

    if stan.aktualny_typ_listy == "taxis":
        record_id = pobierz_id_wybranego_rekordu()
        taxi = pobierz_taksowke_po_id(record_id)

        if taxi is None:
            return

        pokaz_formularz_taksowki()
        stan.id_edytowanego_rekordu = record_id

        stan.pola_formularza["marka"].insert(0, taxi[1])
        stan.pola_formularza["model"].insert(0, taxi[2])
        stan.pola_formularza["kolor"].insert(0, taxi[3] or "")
        stan.pola_formularza["rejestracja"].insert(0, taxi[4])
        stan.pola_formularza["lokalizacja"].insert(0, taxi[8] or f"{taxi[6]}, {taxi[7]}")
        wybierz_opcje_w_formularzu("dostepnosc", OPCJE_DOSTEPNOSCI, taxi[5])

        ui.button_zapisz_formularz.config(text="Zapisz zmiany taksówki")
        return

    if stan.aktualny_typ_listy == "rides":
        record_id = pobierz_id_wybranego_rekordu()
        ride = pobierz_kurs_po_id(record_id)

        if ride is None:
            return

        pokaz_formularz_kursu()
        stan.id_edytowanego_rekordu = record_id

        wybierz_opcje_w_formularzu("client_id", stan.opcje_klientow, ride[1])
        wybierz_opcje_w_formularzu("driver_id", stan.opcje_kierowcow, ride[2])
        stan.pola_formularza["data"].insert(0, ride[4])
        stan.pola_formularza["lokalizacja"].insert(0, ride[5])

        ui.button_zapisz_formularz.config(text="Zapisz zmiany kursu")
        return


def pobierz_fraze_wyszukiwania():
    if ui.zmienna_wyszukiwania is None:
        return ""

    return ui.zmienna_wyszukiwania.get().strip().casefold()


def odswiez_aktualna_liste(*args):
    if stan.aktualny_typ_listy == "clients":
        pokaz_klientow()
    elif stan.aktualny_typ_listy == "drivers":
        pokaz_kierowcow()
    elif stan.aktualny_typ_listy == "rides":
        pokaz_kursy()
    elif stan.aktualny_typ_listy == "taxis":
        pokaz_taksowki()


def wyczysc_wyszukiwanie():
    ui.zmienna_wyszukiwania.set("")


def pokaz_klientow():

    stan.aktualny_typ_listy = "clients"
    stan.identyfikatory_rekordow_listy = []

    ui.listbox_lista_obiektow.delete(0, END)

    clients = pobierz_wszystkich_klientow()
    search_phrase = pobierz_fraze_wyszukiwania()

    for client in clients:
        client_id = client[0]
        first_name = client[1]
        last_name = client[2]
        phone = client[3]
        address = client[6] or ""

        searchable_text = f"{first_name} {last_name} {phone} {address}".casefold()
        if search_phrase not in searchable_text:
            continue

        ui.listbox_lista_obiektow.insert(
            END,
            f"{client_id}. {first_name} {last_name} | tel. {phone} | {address}"
        )

        stan.identyfikatory_rekordow_listy.append(client_id)


def pokaz_kierowcow():

    stan.aktualny_typ_listy = "drivers"
    stan.identyfikatory_rekordow_listy = []

    ui.listbox_lista_obiektow.delete(0, END)

    drivers = pobierz_wszystkich_kierowcow()
    search_phrase = pobierz_fraze_wyszukiwania()

    for driver in drivers:
        driver_id = driver[0]
        first_name = driver[1]
        last_name = driver[2]
        phone = driver[3]
        taxi_brand = driver[6]
        taxi_model = driver[7]
        taxi_color = driver[8]
        registration_number = driver[9]
        address = driver[10] or ""

        searchable_text = (
            f"{first_name} {last_name} {phone} {taxi_brand} {taxi_model} "
            f"{taxi_color} {registration_number} {address}"
        ).casefold()
        if search_phrase not in searchable_text:
            continue

        ui.listbox_lista_obiektow.insert(END,f"{driver_id}. {first_name} {last_name} | tel. {phone} | {taxi_brand} {taxi_model} | kolor: {taxi_color} | rej. {registration_number}")

        stan.identyfikatory_rekordow_listy.append(driver_id)


def pokaz_taksowki():

    stan.aktualny_typ_listy = "taxis"
    stan.identyfikatory_rekordow_listy = []
    ui.listbox_lista_obiektow.delete(0, END)

    search_phrase = pobierz_fraze_wyszukiwania()
    for taxi in pobierz_wszystkie_taksowki():
        status = "dostępna" if taxi[5] else "niedostępna"
        address = taxi[8] or ""
        searchable_text = (
            f"{taxi[1]} {taxi[2]} {taxi[3]} {taxi[4]} {status} {address}"
        ).casefold()
        if search_phrase not in searchable_text:
            continue

        ui.listbox_lista_obiektow.insert(
            END,
            f"{taxi[0]}. {taxi[1]} {taxi[2]} | {taxi[3]} | "
            f"rej. {taxi[4]} | {status}"
        )
        stan.identyfikatory_rekordow_listy.append(taxi[0])


def pobierz_id_taksowki_z_filtra_kursow():
    if ui.zmienna_taksowki_filtra_kursow is None:
        return None

    selected = ui.zmienna_taksowki_filtra_kursow.get()
    if selected == "Wszystkie taksówki":
        return None

    return stan.opcje_taksowek_filtra_kursow.get(selected)


def odswiez_opcje_taksowek_filtra():

    stan.opcje_taksowek_filtra_kursow = {
        f"{taxi[0]} | {taxi[1]} {taxi[2]} | {taxi[4]}": taxi[0]
        for taxi in pobierz_wszystkie_taksowki()
    }
    menu = ui.menu_taksowek_filtra_kursow["menu"]
    menu.delete(0, END)
    menu.add_command(
        label="Wszystkie taksówki",
        command=lambda: ui.zmienna_taksowki_filtra_kursow.set("Wszystkie taksówki")
    )
    for label in stan.opcje_taksowek_filtra_kursow:
        menu.add_command(
            label=label,
            command=lambda value=label: ui.zmienna_taksowki_filtra_kursow.set(value)
        )

    selected = ui.zmienna_taksowki_filtra_kursow.get()
    if selected not in stan.opcje_taksowek_filtra_kursow:
        ui.zmienna_taksowki_filtra_kursow.set("Wszystkie taksówki")


def pokaz_kursy():

    stan.aktualny_typ_listy = "rides"
    stan.identyfikatory_rekordow_listy = []

    ui.listbox_lista_obiektow.delete(0, END)

    taxi_id = pobierz_id_taksowki_z_filtra_kursow()
    ride_date = ui.zmienna_daty_filtra_kursow.get().strip() if ui.zmienna_daty_filtra_kursow is not None else ""
    search_phrase = pobierz_fraze_wyszukiwania()

    for ride in pobierz_wszystkie_kursy(taxi_id, ride_date):
        searchable_text = f"{ride[1]} {ride[2]} {ride[3]} {ride[4]} {ride[5]}".casefold()
        if search_phrase not in searchable_text:
            continue

        ui.listbox_lista_obiektow.insert(
            END,
            f"{ride[0]}. {ride[4]} | klient: {ride[1]} | kierowca: {ride[2]} | {ride[3]}"
        )
        stan.identyfikatory_rekordow_listy.append(ride[0])


def wyczysc_filtry_kursow():
    ui.zmienna_taksowki_filtra_kursow.set("Wszystkie taksówki")
    ui.zmienna_daty_filtra_kursow.set("")
    pokaz_kursy()


def pokaz_wszystkie_kursy_z_wybranego_dnia():
    ride_date = ui.zmienna_daty_filtra_kursow.get().strip()

    if not ride_date:
        messagebox.showerror(
            "Nie można wyświetlić kursów",
            "Podaj datę w formacie RRRR-MM-DD."
        )
        return

    try:
        datetime.strptime(ride_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Nie można wyświetlić kursów",
            "Niepoprawna data. Użyj formatu RRRR-MM-DD."
        )
        return

    ui.zmienna_taksowki_filtra_kursow.set("Wszystkie taksówki")
    pokaz_kursy()


def pokaz_klientow_wybranej_taksowki_z_dnia():

    taxi_id = pobierz_id_taksowki_z_filtra_kursow()
    ride_date = ui.zmienna_daty_filtra_kursow.get().strip()

    if taxi_id is None or not ride_date:
        messagebox.showerror("Nie można wyświetlić klientów","Wybierz konkretną taksówkę i podaj datę.")
        return

    stan.aktualny_typ_listy = "clients"
    stan.identyfikatory_rekordow_listy = []
    ui.listbox_lista_obiektow.delete(0, END)

    for client in pobierz_klientow_taksowki_z_dnia(taxi_id, ride_date):
        ui.listbox_lista_obiektow.insert(END,f"{client[0]}. {client[1]} {client[2]} | tel. {client[3]} | {client[6]}")
        stan.identyfikatory_rekordow_listy.append(client[0])


def pokaz_klientow_na_mapie():

    if stan.markery_klientow:
        for marker in stan.markery_klientow:
            marker.delete()

        stan.markery_klientow = []
        ui.button_klienci_na_mapie.config(text="Pokaż klientów na mapie")
        return

    clients = pobierz_wszystkich_klientow()

    for client in clients:
        first_name = client[1]
        last_name = client[2]
        latitude = client[4]
        longitude = client[5]

        marker = ui.map_widget.set_marker(latitude,longitude,text=f"{first_name} {last_name}",icon=ui.ikona_klienta,icon_anchor="s")

        stan.markery_klientow.append(marker)

    ui.button_klienci_na_mapie.config(text="Ukryj klientów na mapie")


def pokaz_kierowcow_na_mapie():

    if stan.markery_kierowcow:
        for marker in stan.markery_kierowcow:
            marker.delete()

        stan.markery_kierowcow = []
        ui.button_kierowcy_na_mapie.config(text="Pokaż kierowców na mapie")
        return

    drivers = pobierz_wszystkich_kierowcow()

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

        marker = ui.map_widget.set_marker(latitude,longitude,text=f"{first_name} {last_name} | tel. {phone} | {taxi_brand} "f"{taxi_model} | {taxi_color} | {registration_number}",icon=ui.ikona_kierowcy,icon_anchor="s")

        stan.markery_kierowcow.append(marker)

    ui.button_kierowcy_na_mapie.config(text="Ukryj kierowców na mapie")


def pokaz_taksowki_na_mapie():

    if stan.markery_taksowek:
        for marker in stan.markery_taksowek:
            marker.delete()

        stan.markery_taksowek = []
        ui.button_taksowki_na_mapie.config(text="Pokaż taksówki na mapie")
        return

    for taxi in pobierz_wszystkie_taksowki():
        status = "dostępna" if taxi[5] else "niedostępna"
        ikona_taksowki = (ui.ikona_taksowki_aktywnej if taxi[5] else ui.ikona_taksowki_nieaktywnej)

        marker = ui.map_widget.set_marker(taxi[6],taxi[7],text=f"{taxi[1]} {taxi[2]} | {taxi[4]} | {status}",icon=ikona_taksowki,icon_anchor="s")
        stan.markery_taksowek.append(marker)

    ui.button_taksowki_na_mapie.config(text="Ukryj taksówki na mapie")


def wyczysc_formularz():
    for widget in ui.ramka_formularz.winfo_children():
        widget.destroy()

    stan.pola_formularza.clear()


def utworz_pole_formularza(label_text, key, row):
    label = Label(ui.ramka_formularz, text=label_text)
    label.grid(row=row, column=0, sticky=W)

    entry = Entry(ui.ramka_formularz, width=34)
    entry.grid(row=row, column=1, sticky=EW)

    stan.pola_formularza[key] = entry


def utworz_pole_taksowki(row):

    Label(ui.ramka_formularz, text="Taksówka").grid(row=row, column=0, sticky=W)

    stan.opcje_taksowek = {}
    taxi_variable = StringVar()
    taxi_menu_button = Menubutton(ui.ramka_formularz,textvariable=taxi_variable,relief=RAISED,width=34,anchor=W)
    taxi_menu = Menu(taxi_menu_button, tearoff=False)
    taxi_menu_button.config(menu=taxi_menu)
    taxi_menu_button.grid(row=row, column=1)

    first_available_label = None

    for taxi in pobierz_wszystkie_taksowki():
        label = f"{taxi[0]} | {taxi[1]} {taxi[2]} | {taxi[4]}"

        if taxi[5]:
            stan.opcje_taksowek[label] = taxi[0]
            taxi_menu.add_command(label=label,command=lambda value=label: taxi_variable.set(value))
            if first_available_label is None:
                first_available_label = label
        else:
            taxi_menu.add_command(label=f"{label} | NIEDOSTĘPNA",state=DISABLED)

    if first_available_label is not None:
        taxi_variable.set(first_available_label)
    else:
        taxi_variable.set("Brak dostępnych taksówek")

    stan.pola_formularza["taxi_id"] = taxi_variable


def pobierz_id_wybranej_taksowki():
    selected_taxi = stan.pola_formularza["taxi_id"].get()

    if selected_taxi not in stan.opcje_taksowek:
        raise ValueError("Wybierz istniejącą taksówkę z listy.")

    return stan.opcje_taksowek[selected_taxi]


def wybierz_taksowke_w_formularzu(taxi_id):
    for label, existing_taxi_id in stan.opcje_taksowek.items():
        if existing_taxi_id == taxi_id:
            stan.pola_formularza["taxi_id"].set(label)
            return


def utworz_pole_wyboru(label_text, key, row, choices):
    Label(ui.ramka_formularz, text=label_text).grid(row=row, column=0, sticky=W)

    variable = StringVar()
    labels = list(choices.keys())
    option_menu = OptionMenu(ui.ramka_formularz, variable, *labels)
    option_menu.config(width=30, anchor=W)
    option_menu.grid(row=row, column=1, sticky=EW)

    if labels:
        variable.set(labels[0])

    stan.pola_formularza[key] = variable


def pobierz_id_wybranej_opcji(key, choices):
    selected = stan.pola_formularza[key].get()

    if selected not in choices:
        raise ValueError(f"Wybierz wartość w polu: {key}.")

    return choices[selected]


def wybierz_opcje_w_formularzu(key, choices, selected_id):
    for label, record_id in choices.items():
        if record_id == selected_id:
            stan.pola_formularza[key].set(label)
            return


def pokaz_formularz_kursu():

    stan.aktualny_typ_formularza = "ride"
    stan.id_edytowanego_rekordu = None

    wyczysc_formularz()

    label_formularz = Label(ui.ramka_formularz, text="Rejestracja kursu")
    label_formularz.grid(row=0, column=0, columnspan=2)

    stan.opcje_klientow = {f"{client[0]} | {client[1]} {client[2]} | {client[3]}": client[0]for client in pobierz_wszystkich_klientow()}
    stan.opcje_kierowcow = {f"{driver[0]} | {driver[1]} {driver[2]} | {driver[6]} {driver[7]}": driver[0]
        for driver in pobierz_wszystkich_kierowcow()}

    utworz_pole_wyboru("Klient", "client_id", 1, stan.opcje_klientow)
    utworz_pole_wyboru("Kierowca", "driver_id", 2, stan.opcje_kierowcow)
    utworz_pole_formularza("Data kursu (RRRR-MM-DD)", "data", 3)
    utworz_pole_formularza("Adres odbioru", "lokalizacja", 4)

    ui.button_zapisz_formularz = Button(ui.ramka_formularz,text="Dodaj kurs",command=zapisz_formularz)
    ui.button_zapisz_formularz.grid(row=5, column=1, columnspan=2)


def pokaz_formularz_klienta():

    stan.aktualny_typ_formularza = "client"
    stan.id_edytowanego_rekordu = None

    wyczysc_formularz()

    label_formularz = Label(ui.ramka_formularz, text="Rejestracja klienta")
    label_formularz.grid(row=0, column=0, columnspan=2)

    utworz_pole_formularza("Imię", "imie", 1)
    utworz_pole_formularza("Nazwisko", "nazwisko", 2)
    utworz_pole_formularza("Telefon", "telefon", 3)
    utworz_pole_formularza("Lokalizacja", "lokalizacja", 4)

    ui.button_zapisz_formularz = Button(ui.ramka_formularz,text="Dodaj klienta",command=zapisz_formularz)

    ui.button_zapisz_formularz.grid(row=5, column=1, columnspan=2)


def pokaz_formularz_kierowcy():

    stan.aktualny_typ_formularza = "driver"
    stan.id_edytowanego_rekordu = None

    wyczysc_formularz()

    label_formularz = Label(ui.ramka_formularz, text="Rejestracja kierowcy")
    label_formularz.grid(row=0, column=0, columnspan=2)

    utworz_pole_formularza("Imię", "imie", 1)
    utworz_pole_formularza("Nazwisko", "nazwisko", 2)
    utworz_pole_formularza("Telefon", "telefon", 3)
    utworz_pole_formularza("Lokalizacja", "lokalizacja", 4)
    utworz_pole_taksowki(5)

    ui.button_zapisz_formularz = Button(ui.ramka_formularz,text="Dodaj kierowcę",command=zapisz_formularz)

    ui.button_zapisz_formularz.grid(row=6, column=1, columnspan=2)


def pokaz_formularz_taksowki():

    stan.aktualny_typ_formularza = "taxi"
    stan.id_edytowanego_rekordu = None
    wyczysc_formularz()

    Label(ui.ramka_formularz, text="Rejestracja taksówki").grid(row=0, column=0, columnspan=2)
    utworz_pole_formularza("Marka", "marka", 1)
    utworz_pole_formularza("Model", "model", 2)
    utworz_pole_formularza("Kolor", "kolor", 3)
    utworz_pole_formularza("Numer rejestracyjny", "rejestracja", 4)
    utworz_pole_formularza("Lokalizacja", "lokalizacja", 5)
    utworz_pole_wyboru("Dostępność", "dostepnosc", 6, OPCJE_DOSTEPNOSCI)

    ui.button_zapisz_formularz = Button(ui.ramka_formularz,text="Dodaj taksówkę",command=zapisz_formularz)
    ui.button_zapisz_formularz.grid(row=7, column=1, columnspan=2)


def zapisz_formularz():

    if stan.aktualny_typ_formularza == "ride":
        ride_date = stan.pola_formularza["data"].get().strip()
        pickup_address = stan.pola_formularza["lokalizacja"].get().strip()

        try:
            datetime.strptime(ride_date, "%Y-%m-%d")
            coordinates = pobierz_wspolrzedne_z_lokalizacji(pickup_address)
            client_id = pobierz_id_wybranej_opcji("client_id", stan.opcje_klientow)
            driver_id = pobierz_id_wybranej_opcji("driver_id", stan.opcje_kierowcow)

            driver = pobierz_kierowce_po_id(driver_id)
            if driver is None or driver[6] is None:
                raise ValueError("Wybrany kierowca nie ma przypisanej taksówki.")
            taxi_id = driver[6]
        except ValueError as error:
            messagebox.showerror("Nie można zapisać kursu", str(error))
            return

        try:
            if stan.id_edytowanego_rekordu is None:
                dodaj_kurs_do_bazy(client_id,driver_id,taxi_id,ride_date,pickup_address,coordinates[0],coordinates[1])
            else:
                aktualizuj_kurs_w_bazie(stan.id_edytowanego_rekordu,client_id,driver_id,taxi_id,ride_date,pickup_address,coordinates[0],coordinates[1])
        except ValueError as error:
            messagebox.showerror("Kolizja kursów", str(error))
            return

        stan.id_edytowanego_rekordu = None
        pokaz_formularz_kursu()
        pokaz_kursy()
        return

    if stan.aktualny_typ_formularza == "client":
        first_name = stan.pola_formularza["imie"].get()
        last_name = stan.pola_formularza["nazwisko"].get()
        phone = stan.pola_formularza["telefon"].get()
        address = stan.pola_formularza["lokalizacja"].get().strip()

        try:
            coordinates = pobierz_wspolrzedne_z_lokalizacji(address)
        except ValueError as error:
            messagebox.showerror("Nie można zapisać klienta", str(error))
            return

        if stan.id_edytowanego_rekordu is None:
            dodaj_klienta_do_bazy(first_name,last_name,phone,address,coordinates[0],coordinates[1])
        else:
            aktualizuj_klienta_w_bazie(stan.id_edytowanego_rekordu,first_name,last_name,phone,address,coordinates[0],coordinates[1])

        stan.id_edytowanego_rekordu = None
        pokaz_formularz_klienta()
        pokaz_klientow()
        return

    if stan.aktualny_typ_formularza == "taxi":
        brand = stan.pola_formularza["marka"].get().strip()
        model = stan.pola_formularza["model"].get().strip()
        color = stan.pola_formularza["kolor"].get().strip()
        registration_number = stan.pola_formularza["rejestracja"].get().strip().upper()
        address = stan.pola_formularza["lokalizacja"].get().strip()

        try:
            if not brand or not model or not registration_number:
                raise ValueError("Marka, model i numer rejestracyjny są wymagane.")
            coordinates = pobierz_wspolrzedne_z_lokalizacji(address)
            is_available = pobierz_id_wybranej_opcji("dostepnosc", OPCJE_DOSTEPNOSCI)
            if stan.id_edytowanego_rekordu is None:
                dodaj_taksowke_do_bazy(brand,model,color,registration_number,address,coordinates[0],coordinates[1],is_available)
            else:
                aktualizuj_taksowke_w_bazie(stan.id_edytowanego_rekordu,brand,model,color,registration_number,address,coordinates[0],coordinates[1],is_available)
        except (ValueError, sqlite3.IntegrityError) as error:
            message = ("Numer rejestracyjny musi być unikalny."if isinstance(error, sqlite3.IntegrityError) else str(error))
            messagebox.showerror("Nie można zapisać taksówki", message)
            return

        stan.id_edytowanego_rekordu = None
        odswiez_opcje_taksowek_filtra()
        pokaz_formularz_taksowki()
        pokaz_taksowki()
        return

    if stan.aktualny_typ_formularza == "driver":
        first_name = stan.pola_formularza["imie"].get()
        last_name = stan.pola_formularza["nazwisko"].get()
        phone = stan.pola_formularza["telefon"].get()
        address = stan.pola_formularza["lokalizacja"].get().strip()

        try:
            coordinates = pobierz_wspolrzedne_z_lokalizacji(address)
            taxi_id = pobierz_id_wybranej_taksowki()
        except ValueError as error:
            messagebox.showerror("Nie można zapisać kierowcy", str(error))
            return

        try:
            if stan.id_edytowanego_rekordu is None:
                dodaj_kierowce_do_bazy( first_name,last_name,phone,address,coordinates[0],coordinates[1], taxi_id)
            else:
                aktualizuj_kierowce_w_bazie(stan.id_edytowanego_rekordu,first_name,last_name,phone,address,coordinates[0],coordinates[1],taxi_id)
        except sqlite3.IntegrityError:
            messagebox.showerror( "Nie można zapisać kierowcy","Wybrana taksówka jest już przypisana do innego kierowcy.")
            return

        stan.id_edytowanego_rekordu = None
        pokaz_formularz_kierowcy()
        pokaz_kierowcow()
        return


def uruchom_aplikacje():
    root = Tk()
    root.title("Mapbook_BC")
    root.geometry("1500x950")
    root.minsize(1200, 800)

    ui.ikona_klienta = wczytaj_ikone_markera("ikona_klient.png")
    ui.ikona_kierowcy = wczytaj_ikone_markera("ikona_kierowca.png")
    ui.ikona_taksowki_aktywnej = wczytaj_ikone_markera("ikona_aktywnatax.png")
    ui.ikona_taksowki_nieaktywnej = wczytaj_ikone_markera("ikona_nieaktywnatax.png")
    
    utworz_tabele()
    dodaj_dane_startowe()
    
    ramka_lista_obiektow = Frame(root)
    ramka_formularz_typ = Frame(root)
    ui.ramka_formularz = Frame(root)
    ramka_filtry_kursow = Frame(root)
    ramka_szczegoly_obiektu = Frame(root)
    ramka_mapa = Frame(root)
    
    ramka_lista_obiektow.grid(row=0, column=0, padx=(30, 20), sticky=NW)
    ramka_formularz_typ.grid(row=0, column=1, sticky=N)
    ui.ramka_formularz.grid(row=0, column=2, padx=(20, 0), sticky=N)
    ramka_filtry_kursow.grid(row=1,column=0,columnspan=3,padx=(30, 0),pady=5,sticky=W)
    ramka_szczegoly_obiektu.grid(row=2, column=0, columnspan=3, pady=10, padx=50)
    ramka_mapa.grid(row=3, column=0, columnspan=3, padx=(140, 0), sticky=W)

    label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista obiektów:")
    label_wyszukiwanie = Label(ramka_lista_obiektow, text="Szukaj:")
    ui.zmienna_wyszukiwania = StringVar()
    ui.zmienna_wyszukiwania.trace_add("write", odswiez_aktualna_liste)
    entry_wyszukiwanie = Entry(ramka_lista_obiektow,textvariable=ui.zmienna_wyszukiwania,width=70)
    button_wyczysc_wyszukiwanie = Button(ramka_lista_obiektow,text="Wyczyść wyszukiwanie",command=wyczysc_wyszukiwanie)
    scrollbar_lista_pionowa = Scrollbar(ramka_lista_obiektow, orient=VERTICAL)
    scrollbar_lista_pozioma = Scrollbar(ramka_lista_obiektow, orient=HORIZONTAL)
    ui.listbox_lista_obiektow = Listbox(ramka_lista_obiektow,width=105,height=10,xscrollcommand=scrollbar_lista_pozioma.set,yscrollcommand=scrollbar_lista_pionowa.set)
    scrollbar_lista_pionowa.config(command=ui.listbox_lista_obiektow.yview)
    scrollbar_lista_pozioma.config(command=ui.listbox_lista_obiektow.xview)
    ui.listbox_lista_obiektow.bind("<<ListboxSelect>>", pokaz_szczegoly_uzytkownika)
    
    button_usuwanie_obiektu = Button(ramka_formularz_typ,text="Usuwanie",command=usun_uzytkownika)
    
    button_edytowanie_obiektow = Button(ramka_formularz_typ,text="Edytowanie",command=edytuj_szczegoly_uzytkownika)
    
    button_pokaz_klientow = Button(ramka_lista_obiektow,text="Pokaż klientów",command=pokaz_klientow)
    
    ui.button_klienci_na_mapie = Button(ramka_lista_obiektow,text="Pokaż klientów na mapie",command=pokaz_klientow_na_mapie)
    
    button_pokaz_kierowcow = Button(ramka_lista_obiektow,text="Pokaż kierowców",command=pokaz_kierowcow)
    
    ui.button_kierowcy_na_mapie = Button(ramka_lista_obiektow,text="Pokaż kierowców na mapie",command=pokaz_kierowcow_na_mapie)
    
    button_pokaz_kursy = Button(ramka_lista_obiektow,text="Pokaż kursy",command=pokaz_kursy)
    
    button_pokaz_taksowki = Button(ramka_lista_obiektow,text="Lista taksówek",command=pokaz_taksowki)
    
    ui.button_taksowki_na_mapie = Button(ramka_lista_obiektow,text="Pokaż taksówki na mapie",command=pokaz_taksowki_na_mapie)
    
    label_lista_obiektow.grid(row=0, column=0, columnspan=3)
    label_wyszukiwanie.grid(row=1, column=0, sticky=E)
    entry_wyszukiwanie.grid(row=1, column=1, sticky=EW)
    button_wyczysc_wyszukiwanie.grid(row=1, column=2)
    ui.listbox_lista_obiektow.grid(row=2, column=0, columnspan=3, sticky=NSEW)
    scrollbar_lista_pionowa.grid(row=2, column=3, sticky=NS)
    scrollbar_lista_pozioma.grid(row=3, column=0, columnspan=3, sticky=EW)
    
    button_pokaz_klientow.grid(row=5, column=0)
    ui.button_klienci_na_mapie.grid(row=4, column=1)
    
    button_pokaz_kierowcow.grid(row=6, column=0)
    ui.button_kierowcy_na_mapie.grid(row=5, column=1)
    button_pokaz_kursy.grid(row=7, column=0)
    ui.button_taksowki_na_mapie.grid(row=6, column=1)
    button_pokaz_taksowki.grid(row=8, column=0)
    
    label_typ_formularza = Label(ramka_formularz_typ, text="Wybierz formularz:")
    label_typ_formularza.grid(row=0, column=0, columnspan=2)
    
    button_formularz_klient = Button(ramka_formularz_typ,text="Klient",command=pokaz_formularz_klienta)
    button_formularz_kierowca = Button(ramka_formularz_typ,text="Kierowca",command=pokaz_formularz_kierowcy)
    button_formularz_kurs = Button(ramka_formularz_typ,text="Kurs",command=pokaz_formularz_kursu)
    button_formularz_taksowka = Button(ramka_formularz_typ,text="Taksówka",command=pokaz_formularz_taksowki)
    button_formularz_klient.grid(row=1, column=0)
    button_formularz_kierowca.grid(row=1, column=1)
    button_formularz_kurs.grid(row=2, column=0)
    button_formularz_taksowka.grid(row=2, column=1)
    button_edytowanie_obiektow.grid(row=4, column=0, columnspan=2, pady=(20, 2))
    button_usuwanie_obiektu.grid(row=5, column=0, columnspan=2)
    
    Label(ramka_filtry_kursow, text="Filtr kursów - taksówka:").grid(row=0, column=0)
    stan.opcje_taksowek_filtra_kursow = {f"{taxi[0]} | {taxi[1]} {taxi[2]} | {taxi[4]}": taxi[0]
        for taxi in pobierz_wszystkie_taksowki()}
    
    ui.zmienna_taksowki_filtra_kursow = StringVar(value="Wszystkie taksówki")
    ui.menu_taksowek_filtra_kursow = OptionMenu(ramka_filtry_kursow,ui.zmienna_taksowki_filtra_kursow,"Wszystkie taksówki",*stan.opcje_taksowek_filtra_kursow.keys())
    ui.menu_taksowek_filtra_kursow.grid(row=0, column=1)
    
    Label(ramka_filtry_kursow, text="Data RRRR-MM-DD:").grid(row=0, column=2)
    ui.zmienna_daty_filtra_kursow = StringVar()
    Entry(ramka_filtry_kursow, textvariable=ui.zmienna_daty_filtra_kursow, width=12).grid(row=0, column=3)
    Button(ramka_filtry_kursow,text="Wszystkie kursy z dnia",command=pokaz_wszystkie_kursy_z_wybranego_dnia).grid(row=0, column=4)
    Button(ramka_filtry_kursow,text="Pokaż klientów taksówki",command=pokaz_klientow_wybranej_taksowki_z_dnia).grid(row=0, column=5)
    Button(ramka_filtry_kursow, text="Wyczyść filtry", command=wyczysc_filtry_kursow).grid(row=0, column=6)
    
    label_szczegoly_obiektu = Label(ramka_szczegoly_obiektu,text="Szczegóły obiektu")
    label_szczegoly_obiektu.grid(row=0, column=0, columnspan=8)
    
    ui.label_imie_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Imię")
    ui.label_imie_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartość")
    
    ui.label_nazwisko_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Nazwisko")
    ui.label_nazwisko_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartość")
    
    ui.label_lokalizacja_obiektu = Label(ramka_szczegoly_obiektu, text="Lokalizacja")
    ui.label_lokalizacja_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartość")
    
    ui.label_imie_szczegoly_obiektu.grid(row=1, column=0)
    ui.label_imie_szczegoly_obiektu_wartosc.grid(row=1, column=1)
    
    ui.label_nazwisko_szczegoly_obiektu.grid(row=1, column=2)
    ui.label_nazwisko_szczegoly_obiektu_wartosc.grid(row=1, column=3)
    
    ui.label_lokalizacja_obiektu.grid(row=1, column=4)
    ui.label_lokalizacja_obiektu_wartosc.grid(row=1, column=5)
    
    ui.map_widget = tkintermapview.TkinterMapView(ramka_mapa,width=1200,height=520,corner_radius=4)
    
    ui.map_widget.set_position(52.2297, 21.0122)
    ui.map_widget.set_zoom(11)
    ui.map_widget.grid(row=0, column=0)
    
    pokaz_formularz_klienta()
    
    root.mainloop()
