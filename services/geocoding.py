"""
Geocoding service for taxi application.

Provides address to coordinates conversion using OpenStreetMap Nominatim API.
Supports manual coordinate input and automatic address lookup.

Author: Project BC Team
Version: 1.5
"""

import requests

def pobierz_wspolrzedne_z_lokalizacji(lokalizacja: str) -> list:
    lokalizacja = lokalizacja.strip()

    if not lokalizacja:
        raise ValueError("Podaj adres, np. Aleja Jana Pawła II 12A, Warszawa.")

    parts = lokalizacja.split(",")
    if len(parts) == 2:
        try:
            return [float(parts[0].strip().replace(",", ".")),float(parts[1].strip().replace(",", ".")),]
        except ValueError:
            pass

    try:
        response = requests.get("https://nominatim.openstreetmap.org/search",
            params={"q": lokalizacja,"format": "jsonv2","limit": 1,"countrycodes": "pl",},
            headers={"User-Agent": "Project_BC_taxi_app/1.0"},
            timeout=10,)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as error:
        raise ValueError(
            "Nie udało się połączyć z usługą wyszukiwania adresów."
        ) from error
    if not results:
        raise ValueError(
            "Nie znaleziono adresu. Podaj ulicę, numer budynku i miasto, "
            "np. Aleja Jana Pawła II 12A, Warszawa."
        )

    return [float(results[0]["lat"]), float(results[0]["lon"])]
