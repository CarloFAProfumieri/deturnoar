import requests
from bs4 import BeautifulSoup
import json

def load_html_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

html_content = load_html_file("data-raw.html")
soup = BeautifulSoup(html_content, "html.parser")

farmacias = soup.select("#farma-list > li")

pharmacy_data = []
for farmacia in farmacias:
    name_tag = farmacia.select_one("h6.list-fit")
    address_tag = farmacia.select_one("small.list-fit")
    map_link = farmacia.select_one("a[href*='google.com/maps/dir']")

    if name_tag and address_tag and map_link:
        name = name_tag.text.strip()
        address = address_tag.text.strip()

        href = map_link.get("href", "")
        lat_lon = href.split("destination=")[-1] if "destination=" in href else ""
        latitudeAndLongitude = lat_lon.split(",")

        pharmacy_data.append({
            "nombre": name,
            "direccion": address,
            "latitud": latitudeAndLongitude[0],
            "longitud": latitudeAndLongitude[1]
        })

with open("pharmacies.json", "w", encoding="utf-8") as json_file:
    json.dump(pharmacy_data, json_file, indent=4, ensure_ascii=False)