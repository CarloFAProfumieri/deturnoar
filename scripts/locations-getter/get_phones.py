import json
import requests


def load_api_key(filepath="API_KEY"):
    try:
        with open(filepath, "r") as f:
            return f.read().strip()  # Read and remove leading/trailing whitespace
    except FileNotFoundError:
        print(f"Error: API key file '{filepath}' not found.")
        return None


API_KEY = load_api_key()


def obtener_place_id(nombre, direccion):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{nombre}, {direccion}",
        "inputtype": "textquery",
        "fields": "place_id",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)

    if data.get("candidates"):
        return data["candidates"][0]["place_id"]
    return None


def obtener_telefono(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data.get("result", {}).get("formatted_phone_number", "Unavailable")


# place_id = obtener_place_id("Tonini", "Avellaneda 3498 SANTA FE")
# resultado = obtener_telefono(place_id)
def main():

    with open("../../data/pharmacies_split.json", "r", encoding="utf-8") as f:
        pharmacies = json.load(f)

    for pharmacy in pharmacies:

        nombre = "FARMACIA " + pharmacy["nombre"]
        direccion = pharmacy["direccion"] + " " + pharmacy["localidad"]

        place_id = obtener_place_id(nombre, direccion)
        if place_id:
            telefono = obtener_telefono(place_id)
        else:
            telefono = None
        pharmacy["googlePlaceId"] = place_id
        pharmacy["telefono"] = telefono
        print(f"{nombre} → {telefono}")

    # Guardar el JSON con los teléfonos agregados
    with open("../../data/pharmacies_with_phones.json", "w", encoding="utf-8") as f:
        json.dump(pharmacies, f, indent=4, ensure_ascii=False)

    print("Archivo guardado: pharmacies_with_phones.json")


if __name__ == "__main__":
    main()
