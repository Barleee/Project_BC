from tkinter import *

root=Tk()
root.title("Mapbook_BC")
root.geometry("1024x760")

# RAMKI
ramka_lista_obiektow = Frame(root)

ramka_formularz = Frame(root)

ramka_szczegoly_obiektu = Frame(root)

ramka_lista_obiektow.grid(row=0, column=0)
ramka_formularz.grid(row=0, column=1)
ramka_szczegoly_obiektu.grid(row=1, column=0, columnspan=2)

# RAMkA LiSTA OBIEKTÓW

label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista użytkowników: ")
listbox_lista_obiektow = Listbox(ramka_lista_obiektow)
# tworzenei guzików, buttonów pod tabelą ( rodzic ramka_lista_obiektow, tam będzie wyskakiwać

button_pokaz_szczegoly_obiektu = Button(ramka_lista_obiektow, text="Pokaz szczegoly ")
button_usuwanie_obiektu = Button(ramka_lista_obiektow, text="Usuwanie")
button_edytowanie_obiektow =   Button(ramka_lista_obiektow, text="Edytowanie")
# Definiowanie położenia działa na podstawie szereg x kolumna

label_lista_obiektow.grid(row=0, column=0)
listbox_lista_obiektow.grid(row=1, column=0)
button_pokaz_szczegoly_obiektu.grid(row=2, column=0)
button_usuwanie_obiektu.grid(row=2, column=1)
button_edytowanie_obiektow.grid(row=2, column=2)
# Ramka forumlarza 1 ramka 2 polozenie jej
label_formularz = Label(ramka_formularz, text="Formularz: ")
label_formularz.grid(row=0, column=0)
label_imie = Label(ramka_formularz, text="Imię")
label_imie.grid(row=1, column=0)
label_nazwisko =Label(ramka_formularz, text="Nazwisko")
label_nazwisko.grid(row=2, column=0)
label_liczba_postow = Label(ramka_formularz, text="Liczba postów")
label_liczba_postow.grid(row=3, column=0)
label_lokalizacja = Label(ramka_formularz, text="Lokalizacja")
label_lokalizacja.grid(row=4, column=0)

#Wprowadzanie danych
entry_imie=Entry(ramka_formularz)
entry_imie.grid(row=1, column=1)
entry_nazwisko=Entry(ramka_formularz)
entry_nazwisko.grid(row=2, column=1)
entry_liczba_postow=Entry(ramka_formularz)
entry_liczba_postow.grid(row=3, column=1)
entry_lokalizacja=Entry(ramka_formularz)
entry_lokalizacja.grid(row=4, column=1)

button_dodaj_uzytkownika = Button(ramka_formularz, text="Dodaj użytkownika")
button_dodaj_uzytkownika.grid(row=5, column=1, columnspan=2)

# Szczegóły obiektu

labe_szczegoly_obiektu = Label (ramka_szczegoly_obiektu, text="Szczegoly obiektu")
labe_szczegoly_obiektu.grid(row=0, column=2)

# Etykiety
label_imie_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Imie")
label_imie_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartosc")
label_nazwisko_szczegoly_obiektu = Label(ramka_szczegoly_obiektu, text="Nazwisko")
label_nazwisko_szczegoly_obiektu_wartosc =  Label(ramka_szczegoly_obiektu, text="Wartosc")
label_liczba_postow_obiektu = Label(ramka_szczegoly_obiektu, text="Liczba Postów")
label_liczba_postow_obiektu_wartosc = Label(ramka_szczegoly_obiektu, text="Wartosc")
label_lokalizacja_obiektu = Label(ramka_szczegoly_obiektu,text="Lokalizacja")
label_lokalizacja_obiektu_wartosc = Label(ramka_szczegoly_obiektu,text="Wartosc")


label_imie_szczegoly_obiektu.grid(row=1, column=0)
label_imie_szczegoly_obiektu_wartosc.grid(row=1, column=1)
label_nazwisko_szczegoly_obiektu.grid(row=1, column=2)
label_nazwisko_szczegoly_obiektu_wartosc.grid(row=1, column=3)
label_liczba_postow_obiektu.grid(row=1, column=4)
label_liczba_postow_obiektu_wartosc.grid(row=1, column=5)
label_lokalizacja_obiektu.grid(row=1, column=6)
label_liczba_postow_obiektu_wartosc.grid(row=1, column=7)


root.mainloop()
