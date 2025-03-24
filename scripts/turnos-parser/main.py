import cv2
import numpy as np
import imutils
import pytesseract
import json
from pathlib import Path

def drawLine(anImage, anYCoordinate):
    cv2.line(anImage, (0, anYCoordinate), (anImage.shape[1], anYCoordinate), (0, 255, 0), 2)

def getYpoint(anImage):
    gray = cv2.cvtColor(anImage, cv2.COLOR_BGR2GRAY)

    cv2.waitKey(0)
    # Compute the horizontal projection profile
    projection = np.sum(gray, axis=1)

    # Find the transition point (where it gets significantly brighter)
    diff = np.diff(projection)
    split_index = np.argmax(diff)  # Detect biggest brightness jump

    # Separate sections
    gray_section = gray[:split_index, :]
    white_section = gray[split_index:, :]

    #cv2.imshow("Gray Section", gray_section)
    #cv2.imshow("White Section", white_section)
    #cv2.waitKey(0)
    return split_index

def getTurnos(turnos):
    turnos_text_raw = []
    for i, (turno, separador_cabecera, separador_pie) in enumerate(turnos, start=1):
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
        #cv2.imshow("turnera:", turnera)
        cabecera = cv2.cvtColor(cabecera, cv2.COLOR_BGR2GRAY)
        turnera = cv2.cvtColor(turnera, cv2.COLOR_BGR2GRAY)
        if pie is not None:
            pie = cv2.cvtColor(pie, cv2.COLOR_BGR2GRAY)

        cabecera = cv2.adaptiveThreshold(cabecera, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 40)
        #turnera = cv2.adaptiveThreshold(turnera, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 50)
        _, turnera = cv2.threshold(turnera, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if pie is not None:
            pie = cv2.adaptiveThreshold(pie, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 40)
        #cv2.imshow("turnera:", turnera)

        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 3))
        #turnera = cv2.morphologyEx(turnera, cv2.MORPH_OPEN, kernel, iterations=2)

        cabecera = thick_font(cabecera)
        turnera = thick_font(turnera)
        if pie is not None:
            pie = thick_font(pie)

        horarios = pytesseract.image_to_string(cabecera, lang='spa', config='--psm 6 --oem 3')
        farmacias = pytesseract.image_to_string(turnera, lang='spa', config='--psm 6 --oem 3')
        if pie is not None:
            observaciones = pytesseract.image_to_string(pie, lang='spa', config='--psm 6 --oem 3')
        turnos_text_raw.append((horarios, farmacias))

        print("-----------------------------turno ", i, " agregado-----------------------------")
        print(horarios)
        print("--------------------------------------------------------------------------------")
        print(farmacias)
        if pie is not None:
            print("--------------------------------------------------------------------------------")
            print(observaciones)

        if pie is not None:
            cv2.imshow("pie", pie)
    return turnos_text_raw
def cleanPhoneIcons(turnos_ordenados):
    turnos_clean = []
    for turno, separador_cabecera, separador_pie in turnos_ordenados:
        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)
        # edges = cv2.Canny(gray, 200, 300)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 70)
        kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        dilate_tiny = cv2.dilate(edges, kernel_tiny, iterations=1)
        cnts, hierarchy = cv2.findContours(dilate_tiny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if 8 < h < 12 and 12 < w < 16:
                turno[y:y + h, x:x + w] = 255  # Replace the region with white
        turnos_clean.append((turno, separador_cabecera, separador_pie))
    return turnos_clean
def cleanDots(turnos_ordenados):
    turnos_clean = []
    for turno, separador_cabecera in turnos_ordenados:
        img = thin_font(turno)
        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)
        # edges = cv2.Canny(gray, 200, 300)

        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 15)
        # show(edges)
        # kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 4))  # Thin horizontal dilation
        # dilate_tiny = cv2.dilate(edges, kernel_tiny, iterations=1)
        # show(dilate_tiny)
        cnts, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if 1 < h < 4 and 2 <= w < 4 and y == last_y and last_x - x < 7:
                #print("h: ", h, " w: ", w, " y: ", y, " last_y: ", last_y, " x: ", x, " last_x:", last_x)
                turno[y:y + h, x:x + w] = 255  # Replace the region with white
                #cv2.rectangle(turno, (x, y), (x + w, y + h), (255, 0, 0), 1)  # Blue for inner boxes
                #cv2.imshow("outlines", turno)
                #cv2.waitKey(0)
            last_y = y
            last_x = x
        turnos_clean.append((turno, separador_cabecera))
    return turnos_clean
def getCleanFooters(turnos_ordenados):
    turnos_separated = []
    for turno, separador_cabecera in turnos_ordenados:
        foot_separator = 0
        img = thin_font(turno)
        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 300, 400)
        # edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 15)
        # show(edges)
        kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 4))  # Thin horizontal dilation
        dilate_tiny = cv2.dilate(edges, kernel_tiny, iterations=1)
        #cv2.imshow("kernel:", dilate_tiny)
        #show(dilate_tiny)
        cnts, hierarchy = cv2.findContours(dilate_tiny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if 5 < h < 10 and w > 200:
                turno[y:y + h, x:x + w] = 255
                foot_separator = y + h
        turnos_separated.append((turno, separador_cabecera, foot_separator))
    return turnos_separated
def verTurnosCroppedImgs(turnos_imagenes):
    global turno
    for turno in turnos_imagenes:
        cv2.imshow("turno:", turno)
        cv2.waitKey(0)


def show(image):
    cv2.imshow("", image)
    cv2.waitKey(0)


def thick_font(image):
    # Invert the image (white text on black background)
    inverted = cv2.bitwise_not(image)

    # Dilate the white regions to make text thicker
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(inverted, kernel, iterations=1)  # Reduce iterations

    # Revert to original color scheme
    thickened = cv2.bitwise_not(dilated)
    return thickened


def thin_font(image):
    # Invert the image (white text on black background)
    inverted = cv2.bitwise_not(image)

    # Dilate the white regions to make text thicker
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.erode(inverted, kernel, iterations=1)  # Reduce iterations

    # Revert to original color scheme
    thined = cv2.bitwise_not(dilated)
    return thined

def main():
    with open("../../data/farmacias.json", "r", encoding="utf-8") as f:
        pharmacies = json.load(f)  # Expecting a list of names
    image = cv2.imread("../../../../PycharmProjects/learning/turnos.png")

    base_image = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    procesada = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Detect edges
    edges = cv2.Canny(gray, 250, 500)

    # First Dilation for Outer Box (Large Kernel)
    kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
    dilate_large = cv2.dilate(edges, kernel_large, iterations=1)

    # Find contours for outer box
    cnts, hierarchy = cv2.findContours(dilate_large, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    santoto_line = 0
    # Draw only the largest contour (the outer box)
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 500 and 200 < w:  # Large size filter (outer box)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Green Box}
            if x > 0:
                santoto_line = x + w

    # Second Dilation for Inner Boxes (Smaller Kernel)
    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))  # Thin horizontal dilation
    dilate_small = cv2.dilate(edges, kernel_small, iterations=2)

    # Find contours for inner boxes
    cnts, hierarchy = cv2.findContours(dilate_small, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw inner boxes, ignoring the outer box
    inner_boxes = []
    turnos = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if 150 < w < 500 and 150 < h < 1000:  # Ignore very small or too large boxes
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
                # horizontalmente desde x + el contorno decorativo :hasta: x + el ancho del cuadro detectado por cv2 - el
                # contorno decorativo
                turno_crop = image[y + cut_corners + titulo_turno: y + h - cut_corners, x + cut_corners:x + w - cut_corners]
                snippet = image[y + cut_corners + titulo_turno: y + h - cut_corners*2, x + cut_corners:x + cut_corners + 2]

                header_separator = getYpoint(snippet)  # This function returns a y-coordinate to draw the line


                turnos.append((x, y, turno_crop, header_separator))

    # por el formato de imagen, si ordeno por "y, x" obtengo los turnos ordenados y puedo prescindir de detectar el titulo
    # del turno
    sorted_turnos = sorted(turnos, key=lambda t: (t[1], t[0]))


    turnos_ordenados_santoto = []
    turnos_ordenados_santafe = []
    for x, y, turno, header_separator in sorted_turnos:
        if x > santoto_line:
            turnos_ordenados_santoto.append((turno, header_separator))
        else:
            turnos_ordenados_santafe.append((turno, header_separator))

    # debugging
    # verTurnosCroppedImgs(turnos_ordenados_santafe)
    # verTurnosCroppedImgs(turnos_ordenados_santoto)

    turnos_clean_santafe = cleanDots(turnos_ordenados_santafe)
    turnos_clean_santoto = cleanDots(turnos_ordenados_santoto)

    turnos_header_footer_santafe = getCleanFooters(turnos_ordenados_santafe)
    turnos_header_footer_santoto = getCleanFooters(turnos_clean_santoto)

    cleanPhoneIcons(turnos_header_footer_santafe)

    turnos_text_raw = getTurnos(turnos_header_footer_santafe)



    # Show results
    # cv2.imshow("edges", cv2.resize(edges,(850, 1000)))
    # cv2.imshow("dilate_large", cv2.resize(dilate_large,(850, 1000)))
    # cv2.imshow("dilate_small", cv2.resize(dilate_small,(850, 1000)))
    # cv2.imshow("Detected Boxes", cv2.resize(image, (850, 1000)))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Save output
    # cv2.imwrite("../../../../PycharmProjects/learning/turnos-sampleado.png", image)

if __name__ == "__main__":
    main()