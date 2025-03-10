import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import json
import re

# Ruta del archivo PDF
pdf_path = "turnos.pdf"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Convertir el PDF a imágenes
images = convert_from_path(pdf_path)
print(images)
#print("convertion success")
# Extraer texto usando OCR
ocr_text = []
for img in images:
    text = pytesseract.image_to_string(img, "spa")  # Usar español si está instalado
    ocr_text.append(text)
#print(ocr_text)
# Unir el texto extraído
pdf_ocr_text = "\n".join(ocr_text)

# Expresión regular para detectar turnos
turno_pattern = re.compile(r"(PRIMER|SEGUNDO|TERCER|CUARTO) TURNO", re.IGNORECASE)
fecha_pattern = re.compile(r"Desde 8 hs\. .. (\d{2}/\d{2}) - hasta 8 hs\. .. (\d{2}/\d{2})")
farmacia_pattern = re.compile(r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s[A-ZÁÉÍÓÚÑa-záéíóúñ]+)*)\s+\.*\s+(.*)@\s*(\d+)")

turnos = []
current_turno = None

for line in pdf_ocr_text.split("\n"):
    turno_match = turno_pattern.search(line)
    if turno_match:
        # Nuevo turno detectado
        if current_turno:
            turnos.append(current_turno)
        current_turno = {
            "Turno": turno_match.group(1),
            "fechas inicio": [],
            "fechas fin": [],
            "farmacias": [],
            "observaciones": []
        }
        continue

    # Extraer fechas
    fecha_match = fecha_pattern.search(line)
    if fecha_match and current_turno:
        current_turno["fechas inicio"].append(fecha_match.group(1))
        current_turno["fechas fin"].append(fecha_match.group(2))
        continue

    # Extraer farmacias
    farmacia_match = farmacia_pattern.search(line)
    if farmacia_match and current_turno:
        nombre_farmacia = farmacia_match.group(1)
        direccion = farmacia_match.group(2).strip()
        telefono = farmacia_match.group(3)
        current_turno["farmacias"].append({
            "nombre": nombre_farmacia,
            "direccion": direccion,
            "telefono": telefono
        })
        continue

    # Agregar observaciones si hay texto adicional
    if current_turno and line.strip():
        current_turno["observaciones"].append(line.strip())

# Agregar el último turno si existe
if current_turno:
    turnos.append(current_turno)

# Exportar a JSON
json_output = json.dumps(turnos, indent=4, ensure_ascii=False)
with open("turnos.json", "w", encoding="utf-8") as f:
    f.write(json_output)

print("Extracción completada. Datos guardados en 'turnos.json'.")
