from bs4 import BeautifulSoup
import requests
import folium

def read_users(users_data:list)->None:
    for users in users_data:
        print(f"Twój znajomy {users["Name"]}, z miejscowośći {users["Location"]}, zamieścił post {users["Posts"][-1]}")


def add_user(users_data:list)->None:
    users_data.append({"Name":input("Podaj imię  "),"Location":input("Twoja Lokalizacja  "), "Posts":input("Dołączono do znajomych  ")})

def remove_user(users_data:list)->None:
    user_to_remove = input("Podaj imię znajomego do usunięcia  ")
    for user in users_data:
        if user["Name"] == user_to_remove:
            user.data.remove(user)


def update_user(users_data:list)->None:
    user_to_update = input("Podaj imię znajomego do updatu  ")
    for user in users_data:
        if user["Name"] == user_to_update:
            user["Name"] = input("Podaj nowe imię użytkownika: ")
            user["Location"] = input("Podaj nową lokalizację: ")
            return


def update_user_post(users_data:list)->None:
    user_to_update = input("Podaj imię znajomego do updatu  ")
    for user in users_data:
        if user["Name"] == user_to_update:
            user ["Posts"].append(input("Co słychać  "))



def get_coordinates (location: str) -> list:
    url = f"https://pl.wikipedia.org/wiki/{location}"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    response_html = BeautifulSoup (response.text,'html.parser')
    latitude = float(response_html.select(".latitude") [1].text.replace(",","."))
    longitude = float(response_html.select(".longitude")[1].text.replace(",","."))
    return [latitude, longitude]

def get_user_map(users_data : list) -> None:
    m = folium.Map ([52.23, 21], zoom_start=6)


    for user in users_data:
        try:
            coords = get_coordinates(user["Location"])
            folium.Marker(
            location=coords,
            tooltip=user["Name"],
            popup=user["Posts"][-1],
            icon=folium.Icon(icon="cloud")
            ).add_to(m)
        except Exception as e:
            print(f"Nie zlokalizowano dla {user['Location']}: {e}")

    m.save("mapa_znajomych.html")
    print("Mapa została wygenerowana i zapisana jako 'mapa_znajomych.html'")