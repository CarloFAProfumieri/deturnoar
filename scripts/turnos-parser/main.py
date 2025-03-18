import cv2
import numpy as np
import imutils
import pytesseract
# Load Image
def getTurnos(turnos):
    for turno in turnos:
        img = turno
        # img = imutils.resize(img, width=img.shape[1] * 4)
        img = cv2.resize(img, (img.shape[1] * 2, img.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
        # show(img)
        # img = cv2.GaussianBlur(img, (3, 3), 2)
        # img = cv2.bilateralFilter(img, 5, 75, 75) its for noise removal but there's no noise here
        # show(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # show(img)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 40)
        # img = cv2.threshold(img, 200, 230, cv2.THRESH_BINARY)[1]
        # show(img)
        # img = cv2.filter2D(img, -1, kernel2)
        # show(img)
        img = thick_font(img)
        # show(img)
        ocr_result = pytesseract.image_to_string(img, lang='spa', config='--psm 11 --oem 3')
        print(ocr_result)
        cv2.destroyAllWindows()
        cv2.imshow("turno n", turno)
        cv2.waitKey(0)
def getCleanTurnos(turnos_ordenados):
    turnos_clean = []
    for turno in turnos_ordenados:
        img = thin_font(turno)
        gray = cv2.cvtColor(turno, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 200, 300)
        # show(edges)
        kernel_tiny = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 3))  # Thin horizontal dilation
        dilate_tiny = cv2.dilate(edges, kernel_tiny, iterations=2)
        # show(dilate_tiny)

        cnts, hierarchy = cv2.findContours(dilate_tiny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if h < 14 and w > 3:  # Large size filter (outer box)
                # cv2.rectangle(turno, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Green Box
                turno[y:y + h, x:x + w] = 255  # Replace the region with white
        turnos_clean.append(turno)
    return turnos_clean
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
kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3,1))  # Thin horizontal dilation
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
            turnos.append((x, y, turno_crop))

# por el formato de imagen, si ordeno por "y, x" obtengo los turnos ordenados y puedo prescindir de detectar el titulo
# del turno
sorted_turnos = sorted(turnos, key=lambda t: (t[1], t[0]))

turnos_ordenados_santoto = []
turnos_ordenados_santafe = []
for x, y, turno in sorted_turnos:
    if x > santoto_line:
        turnos_ordenados_santoto.append(turno)
    else:
        turnos_ordenados_santafe.append(turno)

# debugging
# verTurnosCroppedImgs(turnos_ordenados_santafe)
# verTurnosCroppedImgs(turnos_ordenados_santoto)
turnos_clean_santafe = getCleanTurnos(turnos_ordenados_santafe)
turnos_clean_santoto = getCleanTurnos(turnos_ordenados_santoto)

getTurnos(turnos_clean_santafe)

# Show results
# cv2.imshow("edges", cv2.resize(edges,(850, 1000)))
# cv2.imshow("dilate_large", cv2.resize(dilate_large,(850, 1000)))
# cv2.imshow("dilate_small", cv2.resize(dilate_small,(850, 1000)))
cv2.imshow("Detected Boxes", cv2.resize(image, (850, 1000)))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Save output
cv2.imwrite("../../../../PycharmProjects/learning/turnos-sampleado.png", image)

