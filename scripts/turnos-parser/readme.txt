Puede suceder que este script produzca un error al intentar abrir el archivo pdf de turnos
en ese caso, seguir el procedimiento:

1- Ir a: https://github.com/oschwartz10612/poppler-windows/releases
    Descarga la versión más reciente (poppler-XX.XX.0.zip).
    Extrae el contenido en una carpeta (por ejemplo, C:\poppler).
    Agregar Poppler a la variable de entorno PATH

2- Agregar poppler al PATH
    Presiona Win + R, escribe sysdm.cpl y presiona Enter.
    Ve a la pestaña Opciones Avanzadas y haz clic en Variables de entorno.
    En la sección Variables del sistema, busca Path y edítalo.
    Agrega la ruta de la carpeta bin de Poppler. Por ejemplo:
    C:\poppler-XX.XX.0\bin

3- Verificar la instalación
   Abrir cmd

   pdfinfo -v
Si la instalación fue exitosa, mostrará la versión de Poppler.

-----------------------------------------------------------------------------------------

Lo mismo puede suceder para Tesseract.

1 - Descarga e instala la versión oficial de Tesseract desde:
🔗 https://github.com/UB-Mannheim/tesseract/wiki

2 - Modificar la ruta de tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"