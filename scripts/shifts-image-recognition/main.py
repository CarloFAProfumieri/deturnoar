import re
import cv2
import numpy as np
import pytesseract
import json
from rapidfuzz import process, fuzz
from pdf2image import convert_from_path

def draw_line(an_image, an_y_coordinate):
    cv2.line(an_image, (0, an_y_coordinate), (an_image.shape[1], an_y_coordinate), (0, 255, 0), 2)


def get_header_y_coordinate(an_image):
    # This function returns the point at which the image changes brightness, im using it for separating the
    # header of each shift (gray background) from the actual table of data

    gray = cv2.cvtColor(an_image, cv2.COLOR_BGR2GRAY)
    projection = np.sum(gray, axis=1)
    diff = np.diff(projection)
    y_coordinate = np.argmax(diff)  # Detects biggest brightness jump

    # left here for debugging resasons
    # header = gray[:y_coordinate, :]
    # shift_data = gray[y_coordinate:, :]

    return y_coordinate


def debug_print(header_text, shift_text, footer_text, i):
    print("-----------------------------turno: ", i, "-------------------------------------")
    print(header_text)
    print("--------------------------------------------------------------------------------")
    print(shift_text)
    if footer_text is not None:
        print("------------------------------observaciones-----------------------------------")
        print(footer_text)


def get_shifts(turnos):
    """
    this function is where ocr is performed
    it receives an array that contains each shift cropped into header, tabular data, and footer
    the point is to be able to preprocess each differently since each has a different font weight, font size, and
    general structure
    """

    turnos_text_raw = []
    for i, (turno, separador_cabecera, separador_pie) in enumerate(turnos, start=1):
        observaciones = ""
        cv2.destroyAllWindows()
        cabecera = turno[:separador_cabecera, :]
        if separador_pie == 0:
            turnera = turno[separador_cabecera:, :]
            pie = None  # No hay pie
        else:
            turnera = turno[separador_cabecera:separador_pie, :]
            pie = turno[separador_pie:, :]

        cabecera = cv2.resize(cabecera, (cabecera.shape[1] * 2, cabecera.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
        turnera = cv2.resize(turnera, (turnera.shape[1] * 3, turnera.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
        if pie is not None:
            pie = cv2.resize(pie, (pie.shape[1] * 3, pie.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
        # cv2.imshow("turnera:", turnera)
        cabecera = cv2.cvtColor(cabecera, cv2.COLOR_BGR2GRAY)
        turnera = cv2.cvtColor(turnera, cv2.COLOR_BGR2GRAY)
        if pie is not None:
            pie = cv2.cvtColor(pie, cv2.COLOR_BGR2GRAY)

        cabecera = cv2.adaptiveThreshold(cabecera, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 40)
        # turnera = cv2.adaptiveThreshold(turnera, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 50)
        _, turnera = cv2.threshold(turnera, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if pie is not None:
            pie = cv2.adaptiveThreshold(pie, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 40)
        # cv2.imshow("turnera:", turnera)

        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 3))
        # turnera = cv2.morphologyEx(turnera, cv2.MORPH_OPEN, kernel, iterations=2)

        cabecera = thick_font(cabecera)
        turnera = thick_font(turnera)
        if pie is not None:
            pie = thick_font(pie)

        horarios = pytesseract.image_to_string(cabecera, lang='spa', config='--psm 6 --oem 3')
        farmacias = pytesseract.image_to_string(turnera, lang='spa', config='--psm 6 --oem 3')
        if pie is not None:
            observaciones = pytesseract.image_to_string(pie, lang='spa', config='--psm 6 --oem 3')

        # debug_print(horarios,farmacias,observaciones,i)

        turnos_text_raw.append((horarios, farmacias, observaciones))

    return turnos_text_raw


def clean_phone_icons(cropped_shifts):
    # blurs the whole crop, and finds the specific shape that the phone icons have, with some added tolerance
    # otherwise, I get glitches when applying ocr
    turnos_clean = []
    for turno, separador_cabecera, separador_pie in cropped_shifts:
        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 70)
        kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        dilate_tiny = cv2.dilate(edges, kernel_tiny, iterations=1)
        cnts, hierarchy = cv2.findContours(dilate_tiny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if 8 < h < 12 < w < 16:  # basically it's a box wider than taller, like me after my vacations
                turno[y:y + h, x:x + w] = 255
        turnos_clean.append((turno, separador_cabecera, separador_pie))
    return turnos_clean


def clean_dots(turnos_ordenados):
    # this was a game changer. The original image has some annoying dots used for presentation that throw ocr WAY off.

    # this functions' purpose is to remove dots. It does it by detecting very small contours in the binarized image
    # and then only removing them if they are in close proximity to another dot, else, it screws up 'i's and 'j's
    # and for some unholy reason 'm' characters as well

    # it spares the first and last dot in a line of dots, because it aids in postprocessing
    # (and some dots have to remain, to tell the story to other dots, or else they'll never learn of the dot massacre)
    turnos_clean = []
    for turno, separador_cabecera in turnos_ordenados:

        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)

        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 15)

        cnts, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        last_x, last_y = 0, 0
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            # I'm aiming to delete dots only if im VERY sure they are the ones I want to delete, I don't care if some remain
            if 1 < h < 4 and 2 <= w < 4 and y == last_y and last_x - x < 7:
                turno[y:y + h, x:x + w] = 255
            last_y = y
            last_x = x
        turnos_clean.append((turno, separador_cabecera))
    return turnos_clean


def get_footer_separator(turnos_ordenados):
    # this one just finds the height of the line of hyphens ands appends it to the shifts array
    # this is later used for separating the footer
    turnos_separated = []
    for turno, separador_cabecera in turnos_ordenados:
        foot_separator_height = 0
        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 300, 400)
        # Thin horizontal dilation, basically converts the hyphen line in a very cv2 detectable thick, continuous line
        kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 4))
        dilate_tiny = cv2.dilate(edges, kernel_tiny, iterations=1)
        cnts, hierarchy = cv2.findContours(dilate_tiny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if 5 < h < 10 and w > 200:
                turno[y:y + h, x:x + w] = 255
                foot_separator_height = y + h
        turnos_separated.append((turno, separador_cabecera, foot_separator_height))
    return turnos_separated


def ver_turnos_cropped_imgs(turnos_imagenes):
    global turno
    for turno in turnos_imagenes:
        cv2.imshow("turno:", turno)
        cv2.waitKey(0)


def extract_dates(text):
    matches = re.findall(r"(\d{2}/\d{2})", text)
    dates = []
    for match in matches:
        dates.append(match)
    return dates


def show(image):
    cv2.imshow("", image)
    cv2.waitKey(0)


def thick_font(image):
    # image is inverted, then dilated with cv2 and then inverted again (so it returns how you would expect)
    # honestly, it just works out of the box, I havent touched it

    inverted = cv2.bitwise_not(image)
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(inverted, kernel, iterations=1)
    thickened = cv2.bitwise_not(dilated)
    return thickened


def thin_font(image):
    # Same as thick font, but "erodes" the image
    inverted = cv2.bitwise_not(image)
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.erode(inverted, kernel, iterations=1)  # Reduce iterations
    thined = cv2.bitwise_not(dilated)
    return thined


def extract_pharmacy_names(turno, nombres_farmacias):
    # this parses through the set of image extracted names and then compares it with all pharmacy names given
    # if it finds no match, its splits with spaces and iterates over it, but with a much lower tolerance for error
    potential_names = [re.split(r"[.«,\-]", line)[0].strip().upper() for line in turno.strip().split("\n")]
    matched_names = []
    for name in potential_names:
        best_match, score, _ = process.extractOne(name, nombres_farmacias, scorer=fuzz.ratio)

        if score >= 75:
            matched_names.append(best_match)
        else:
            words = name.split()
            for word in words:
                best_match, score, _ = process.extractOne(word, nombres_farmacias, scorer=fuzz.ratio)
                if score >= 90:
                    matched_names.append(best_match)
                    break
    return matched_names


def separate_dates(dates):
    dates_from = []
    dates_to = []

    # Iteramos sobre las fechas y las separamos
    for i, date in enumerate(dates):
        if i % 2 == 0:
            # Índices pares (desde)
            dates_from.append(date)
        else:
            # Índices impares (hasta)
            dates_to.append(date)

    return dates_from, dates_to


def pdf_to_image(pdf_path, dpi=300):
    page = convert_from_path(pdf_path, dpi=dpi)[0]  # Read only the first page
    image = np.array(page)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
def main():
    """
    The pipeline is as follows:
    I load the image, gray it out, then apply a small and a large kernel
    The large kernel serves me to detect the outer boxes, since there are two cities in two different boxes
    The smaller kernel lets me separate every shift box to finally get it cropped, then I sort each crop by x, y
    While im at it, I also separate each header with dates from the table with the pharmacy's data
    Finally, I separate the footer from the table, and send the whole thing to ocr function, which takes care of
    preprocessing and the ocr itself
    Then, i get this raw data, and spellcheck the names of the pharmacies with rapidfuzz, using all the parsed
    names that I previously scraped. I also use re to parse the dates of the shifts
    All this data is then saved in json format
    """
    with open("../../data/pharmacies_with_phones.json", "r", encoding="utf-8") as f:
        pharmacies = json.load(f)

    image = pdf_to_image("turnos-septiembre.pdf")

    # the original image I got was this and measurements are based on it:
    image = cv2.resize(image, (1687, 2519), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 250, 500)

    # Outer Box
    kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
    dilate_large = cv2.dilate(edges, kernel_large, iterations=1)
    cnts, hierarchy = cv2.findContours(dilate_large, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    santoto_line = 0
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 500 and 200 < w:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            if x > 0:
                santoto_line = x + w

    # Inner Box
    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
    dilate_small = cv2.dilate(edges, kernel_small, iterations=2)

    cnts, hierarchy = cv2.findContours(dilate_small, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    inner_boxes = []
    turnos = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if 150 < w < 500 and 150 < h < 1000:
            is_duplicate = False
            for xb, yb, wb, hb in inner_boxes:
                if abs(x - xb) < 15 and abs(y - yb) < 15 and abs(w - wb) < 15 and abs(h - hb) < 15:
                    is_duplicate = True
                    break
            if not is_duplicate:
                inner_boxes.append((x, y, w, h))
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue for inner boxes
                cut_corners = 10
                titulo_turno = 25
                # recorto cada imagen verticalmente desde y + el espacio que necesito para sacar el contorno  del cuadro
                # + el titulo del turno :hasta: y + la altura 'h' del cuadro detectado por cv2 - el espacio del contorno
                # horizontalmente desde x + el contorno decorativo :hasta: x + el ancho del cuadro detectado por
                # cv2 - el contorno decorativo
                turno_crop = image[y + cut_corners + titulo_turno: y + h - cut_corners,
                             x + cut_corners:x + w - cut_corners]
                snippet = image[y + cut_corners + titulo_turno: y + h - cut_corners * 2,
                          x + cut_corners:x + cut_corners + 2]

                header_separator_height = get_header_y_coordinate(snippet)

                turnos.append((x, y, turno_crop, header_separator_height))

    # por el formato de imagen, si ordeno por "y, x" obtengo los turnos ordenados y puedo prescindir de detectar
    # el titulo del turno
    sorted_turnos = sorted(turnos, key=lambda t: (t[1], t[0]))

    turnos_ordenados_santoto = []
    turnos_ordenados_santafe = []
    for x, y, turno, header_separator_height in sorted_turnos:
        if x > santoto_line:
            turnos_ordenados_santoto.append((turno, header_separator_height))
        else:
            turnos_ordenados_santafe.append((turno, header_separator_height))

    # checkpoint for debugging purposes
    # verTurnosCroppedImgs(turnos_ordenados_santafe)
    # verTurnosCroppedImgs(turnos_ordenados_santoto)

    turnos_clean_santafe = clean_dots(turnos_ordenados_santafe)
    turnos_clean_santoto = clean_dots(turnos_ordenados_santoto)

    turnos_header_footer_santafe = get_footer_separator(turnos_ordenados_santafe)
    turnos_header_footer_santoto = get_footer_separator(turnos_clean_santoto)

    clean_phone_icons(turnos_header_footer_santafe)
    clean_phone_icons(turnos_header_footer_santoto)

    turnos_text_raw_santa_fe = get_shifts(turnos_header_footer_santafe)
    turnos_text_raw_santoto = get_shifts(turnos_header_footer_santoto)

    nombres_farmacias_santa_fe = []
    for pharmacy in pharmacies:
        if pharmacy["localidad"].upper() == "SANTA FE LA CAPITAL":
            nombres_farmacias_santa_fe.append(pharmacy["nombre"])

    nombres_farmacias_santoto = []
    for pharmacy in pharmacies:
        if pharmacy["localidad"].upper() == "SANTO TOME LA CAPITAL":
            nombres_farmacias_santoto.append(pharmacy["nombre"])

    turnos_extracted_text_santa_fe = []
    turnos_especiales = []
    for cabecera, turno, pie in turnos_text_raw_santa_fe:
        turno = turno.upper().replace(" A.", " A ").replace("SEN - COLTRINARI", "SEN COLTRINARI")
        farmacias_en_el_turno = extract_pharmacy_names(turno, nombres_farmacias_santa_fe)
        fechas_del_turno = extract_dates(cabecera)
        dates_from, dates_to = separate_dates(fechas_del_turno)
        turnos_extracted_text_santa_fe.append((dates_from, dates_to, farmacias_en_el_turno))
        if len(pie) < 2:
            continue

        pie = pie.upper().replace(" A.", " A ").replace("SEN - COLTRINARI", "SEN COLTRINARI")
        pie = pie.splitlines()
        pie = [line for line in pie if line.strip() != '']
        for i in range(0, len(pie) - 1, 2):
            linea_nombre = pie[i]
            linea_turno = pie[i + 1]
            farmacias_pie = extract_pharmacy_names(linea_nombre, nombres_farmacias_santa_fe)
            fechas_del_pie = extract_dates(linea_turno)
            dates_from_pie, dates_to_pie = separate_dates(fechas_del_pie)
            turnos_especiales.append((dates_from_pie, dates_to_pie, farmacias_pie))

    turnos_santa_fe_json = [{"datesFrom": dates_from, "datesTo": dates_to, "pharmacies": farmacias}
                   for dates_from, dates_to, farmacias in turnos_extracted_text_santa_fe]

    # los turnos del pie
    turnos_santa_fe_especiales_json = [{"datesFrom": dates_from, "datesTo": dates_to, "pharmacies": farmacias_pie}
                   for dates_from, dates_to, farmacias_pie in turnos_especiales]

    with open("../../data/turnos-santa-fe.json", "w", encoding="utf-8") as f:
        json.dump(turnos_santa_fe_json, f, indent=4, ensure_ascii=False)
    print("turnos santa fe guardados correctamente")

    with open("../../data/turnos-especiales-santa-fe.json", "w", encoding="utf-8") as f:
        json.dump(turnos_santa_fe_especiales_json, f, indent=4, ensure_ascii=False)
    print("turnos especiales guardados")

    turnos_extracted_text_santoto = []
    for cabecera, turno, pie in turnos_text_raw_santoto:
        turno = turno.upper().replace(" A.", " A ").replace("SEN - COLTRINARI", "SEN COLTRINARI")
        farmacias_en_el_turno = extract_pharmacy_names(turno, nombres_farmacias_santoto)
        fechas_del_turno = extract_dates(cabecera)
        dates_from, dates_to = separate_dates(fechas_del_turno)
        turnos_extracted_text_santoto.append((dates_from, dates_to, farmacias_en_el_turno))

    turnos_santa_fe_json = [{"datesFrom": dates_from, "datesTo": dates_to, "pharmacies": farmacias}
                            for dates_from, dates_to, farmacias in turnos_extracted_text_santoto]

    with open("../../data/turnos-santo-tome.json", "w", encoding="utf-8") as f:
        json.dump(turnos_santa_fe_json, f, indent=4, ensure_ascii=False)
    print("turnos santo tome guardados correctamente")


if __name__ == "__main__":
    main()
