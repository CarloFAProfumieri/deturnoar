import json
import re

def limpiar_direccion(direccion):
    altura = ""
    localidad = ""
    # Expresión regular para detectar el primer número en la dirección
    match = re.search(r"(\D+?)\s(\d{3,4})", direccion)
    if match:
        calle = match.group(1).strip()  # Parte de la calle
        altura = match.group(2).strip()  # Número de la dirección

        # Extraer lo que está después del número
        resto = direccion[match.end():].strip()

        return {"calle": calle, "altura": altura, "localidad": resto}
    else:
        if any(loc in direccion for loc in ["SANTA FE", "LA CAPITAL", "DE LA VERA CRUZ"]):
            direccion = (direccion.upper().replace("SANTA FE", "").replace("LA CAPITAL", "")
                         .replace("DE LA VERA CRUZ", "")).strip()
            localidad = "SANTA FE"

        if "SANTO TOME" in direccion:
            direccion = direccion.upper().replace("SANTO TOME", "").strip()
            localidad = "SANTO TOME"

        if "LAS COLONIAS" in direccion:
            direccion = direccion.upper().replace("LAS COLONIAS", "").strip()
            localidad = "LAS COLONIAS"

        if "ARROYO LEYES" in direccion:
            direccion = direccion.upper().replace("ARROYO LEYES", "").strip()
            localidad = "ARROYO LEYES"

        if "S/N" in direccion:
            direccion = direccion.upper().replace("S/N", "").strip()
            altura = "S/N"

        return {"calle": direccion, "altura": "", "localidad": localidad}

def main():
    with open("../../data/pharmacies.json", "r", encoding="utf-8") as f:
        pharmacies = json.load(f)

    for i, pharmacy in enumerate(pharmacies):
        nombre = pharmacy["nombre"].upper()
        direccion = pharmacy["direccion"].upper()
        if "SANTA FE" in nombre and nombre != "SANTA FE":
            nombre = nombre.replace("SANTA FE", "").strip()
            pharmacy["localidad"] = "santa fe"

        if "SANTO TOME" in nombre:
            nombre = nombre.replace("SANTO TOME", "").strip()
            pharmacy["localidad"] = "santo tome"

        if "(ART. 57)" in nombre:
            nombre = nombre.replace("(ART. 57)", "").strip()

        #print(direccion)
        direccion_clean = limpiar_direccion(direccion)
        pharmacy["calle"] = direccion_clean["calle"]
        pharmacy["altura"] = direccion_clean["altura"]
        pharmacy["localidad"] = direccion_clean["localidad"]
        pharmacy["direccion"] = direccion_clean["calle"] + " " + direccion_clean["altura"]
    with open("../../data/pharmacies_split.json", "w", encoding="utf-8") as f:
        json.dump(pharmacies, f, indent=4, ensure_ascii=False)

    print("Archivo pharmacies_split.json guardado con éxito.")
if __name__ == "__main__":
    main()