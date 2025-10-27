"""
Módulo para generar PDFs de formularios EPS con datos de empleados
"""
import fitz  # PyMuPDF
import os
from django.conf import settings

# Coordenadas de los campos en el PDF
COORDENADAS_CAMPOS = {
    'CEDULA': {'x': 130, 'y': 181},
    'PRIMER_APELLIDO': {'x': 75, 'y': 163},
    'SEGUNDO_APELLIDO': {'x': 200, 'y': 163},
    'PRIMER_NOMBRE': {'x': 330, 'y': 163},
    'SEGUNDO_NOMBRE': {'x': 480, 'y': 163},
    'PAIS_NACIMIENTO': {'x': 505, 'y': 181},
    'DEPARTAMENTO_NACIMIENTO': {'x': 50, 'y': 200},
    'CIUDAD_NACIMIENTO': {'x': 130, 'y': 200},
}

# Coordenadas para fecha de nacimiento (cada dígito en su posición)
# Formato: DDMMYYYY
COORDENADAS_FECHA_NACIMIENTO = [
    {'x': 290, 'y': 200},  # D1
    {'x': 310, 'y': 200},  # D2
    {'x': 330, 'y': 200},  # M1
    {'x': 350, 'y': 200},  # M2
    {'x': 370, 'y': 200},  # Y1
    {'x': 390, 'y': 200},  # Y2
    {'x': 410, 'y': 200},  # Y3
    {'x': 435, 'y': 200},  # Y4
]

# Coordenadas para marcar sexo con X
COORDENADAS_SEXO = {
    '0': {'x': 302.5, 'y': 176.5},  # Masculino
    '1': {'x': 267.5, 'y': 176.5},  # Femenino
}

# Ruta al PDF original (plantilla)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_TEMPLATE = os.path.join(BASE_DIR, 'formatos', 'formulario_de_afiliacion_eps_delagente_comfenalco_valle.pdf')


def convertir_fecha_yyyymmdd_a_ddmmyyyy(fecha_str):
    """
    Convierte fecha de formato YYYYMMDD a DDMMYYYY.

    Args:
        fecha_str (str): Fecha en formato YYYYMMDD (ej: "19900315")

    Returns:
        str: Fecha en formato DDMMYYYY (ej: "15031990")
    """
    if not fecha_str or len(fecha_str) != 8:
        return ''

    # Limpiar espacios
    fecha_str = str(fecha_str).strip()

    try:
        # YYYYMMDD -> DDMMYYYY
        yyyy = fecha_str[0:4]
        mm = fecha_str[4:6]
        dd = fecha_str[6:8]

        return dd + mm + yyyy
    except:
        return ''


def split_nombres(nombres_completos):
    """
    Divide los nombres en primer y segundo nombre.

    Args:
        nombres_completos (str): Nombres completos del empleado

    Returns:
        tuple: (primer_nombre, segundo_nombre)
    """
    if not nombres_completos:
        return ('', '')

    # Limpiar espacios extras
    nombres = nombres_completos.strip().split()

    if len(nombres) == 0:
        return ('', '')
    elif len(nombres) == 1:
        return (nombres[0], '')
    else:
        # Primer nombre y resto como segundo nombre
        primer_nombre = nombres[0]
        segundo_nombre = ' '.join(nombres[1:])
        return (primer_nombre, segundo_nombre)


def insertar_texto_en_pdf(page, texto, x, y, fontsize=10, color=(0, 0, 0)):
    """
    Inserta texto en una coordenada específica del PDF.

    Args:
        page: Página de PyMuPDF
        texto (str): Texto a insertar
        x (int/float): Coordenada X
        y (int/float): Coordenada Y
        fontsize (int): Tamaño de fuente
        color (tuple): Color RGB (0-1, 0-1, 0-1)
    """
    if not texto:
        return

    # Crear rectángulo para el texto (amplio para que no se corte)
    text_rect = fitz.Rect(x, y - fontsize, x + 200, y + fontsize)

    # Insertar texto
    page.insert_textbox(
        text_rect,
        str(texto),
        fontsize=fontsize,
        fontname="helv",  # Helvetica
        color=color,
        align=fitz.TEXT_ALIGN_LEFT
    )


def marcar_x_en_pdf(page, x, y, size=7, color=(0, 0, 0)):
    """
    Marca una X en una coordenada específica del PDF.

    Args:
        page: Página de PyMuPDF
        x (int/float): Coordenada X
        y (int/float): Coordenada Y
        size (int): Tamaño de la X
        color (tuple): Color RGB (0-1, 0-1, 0-1)
    """
    # Dibujar línea diagonal de arriba-izquierda a abajo-derecha
    page.draw_line(
        (x - size/2, y - size/2),
        (x + size/2, y + size/2),
        color=color,
        width=1.5
    )

    # Dibujar línea diagonal de arriba-derecha a abajo-izquierda
    page.draw_line(
        (x + size/2, y - size/2),
        (x - size/2, y + size/2),
        color=color,
        width=1.5
    )


def insertar_fecha_nacimiento(page, fecha_yyyymmdd):
    """
    Inserta la fecha de nacimiento distribuyendo cada dígito en su coordenada.

    Args:
        page: Página de PyMuPDF
        fecha_yyyymmdd (str): Fecha en formato YYYYMMDD
    """
    # Convertir a DDMMYYYY
    fecha_ddmmyyyy = convertir_fecha_yyyymmdd_a_ddmmyyyy(fecha_yyyymmdd)

    if not fecha_ddmmyyyy or len(fecha_ddmmyyyy) != 8:
        return

    # Insertar cada dígito en su coordenada
    for i, digito in enumerate(fecha_ddmmyyyy):
        coords = COORDENADAS_FECHA_NACIMIENTO[i]
        insertar_texto_en_pdf(page, digito, coords['x'], coords['y'], fontsize=10)


def rellenar_pdf_empleado(datos_empleado, output_path):
    """
    Rellena el PDF del formulario EPS con los datos del empleado.

    Args:
        datos_empleado (dict): Diccionario con los datos del empleado
            Debe contener: CEDULA, PRIMER_APELLIDO, SEGUNDO_APELLIDO, NOMBRES
        output_path (str): Ruta donde guardar el PDF generado

    Returns:
        str: Ruta del PDF generado

    Raises:
        FileNotFoundError: Si no se encuentra el PDF template
        Exception: Si hay error al generar el PDF
    """
    # Verificar que existe el template
    if not os.path.exists(PDF_TEMPLATE):
        raise FileNotFoundError(f"No se encuentra el PDF template: {PDF_TEMPLATE}")

    try:
        # Abrir el PDF template
        doc = fitz.open(PDF_TEMPLATE)

        # Obtener la primera página (asumimos que el formulario está en página 1)
        page = doc[0]

        # Extraer datos del empleado
        cedula = datos_empleado.get('CEDULA', '')
        primer_apellido = datos_empleado.get('PRIMER_APELLIDO', '')
        segundo_apellido = datos_empleado.get('SEGUNDO_APELLIDO', '')
        nombres_completos = datos_empleado.get('NOMBRES', '')
        fecha_nacimiento = datos_empleado.get('FECHA_NACIMIENTO', '')
        pais_nacimiento = datos_empleado.get('PAIS_NACIMIENTO', '')
        codigo_sexo = datos_empleado.get('CODIGO_SEXO', '')
        departamento_nacimiento = datos_empleado.get('DEPARTAMENTO_NACIMIENTO', '')
        ciudad_nacimiento = datos_empleado.get('CIUDAD_NACIMIENTO', '')

        # Dividir nombres
        primer_nombre, segundo_nombre = split_nombres(nombres_completos)

        # Insertar CEDULA
        coords = COORDENADAS_CAMPOS['CEDULA']
        insertar_texto_en_pdf(page, cedula, coords['x'], coords['y'], fontsize=10)

        # Insertar PRIMER APELLIDO
        coords = COORDENADAS_CAMPOS['PRIMER_APELLIDO']
        insertar_texto_en_pdf(page, primer_apellido, coords['x'], coords['y'], fontsize=10)

        # Insertar SEGUNDO APELLIDO
        coords = COORDENADAS_CAMPOS['SEGUNDO_APELLIDO']
        insertar_texto_en_pdf(page, segundo_apellido, coords['x'], coords['y'], fontsize=10)

        # Insertar PRIMER NOMBRE
        coords = COORDENADAS_CAMPOS['PRIMER_NOMBRE']
        insertar_texto_en_pdf(page, primer_nombre, coords['x'], coords['y'], fontsize=10)

        # Insertar SEGUNDO NOMBRE (si existe)
        if segundo_nombre:
            coords = COORDENADAS_CAMPOS['SEGUNDO_NOMBRE']
            insertar_texto_en_pdf(page, segundo_nombre, coords['x'], coords['y'], fontsize=10)

        # Insertar FECHA DE NACIMIENTO (distribuyendo cada dígito)
        if fecha_nacimiento:
            insertar_fecha_nacimiento(page, fecha_nacimiento)

        # Insertar PAIS DE NACIMIENTO
        if pais_nacimiento:
            coords = COORDENADAS_CAMPOS['PAIS_NACIMIENTO']
            insertar_texto_en_pdf(page, pais_nacimiento, coords['x'], coords['y'], fontsize=10)

        # Marcar SEXO con X
        if codigo_sexo in COORDENADAS_SEXO:
            coords = COORDENADAS_SEXO[str(codigo_sexo)]
            marcar_x_en_pdf(page, coords['x'], coords['y'], size=7)

        # Insertar DEPARTAMENTO DE NACIMIENTO
        if departamento_nacimiento:
            coords = COORDENADAS_CAMPOS['DEPARTAMENTO_NACIMIENTO']
            insertar_texto_en_pdf(page, departamento_nacimiento, coords['x'], coords['y'], fontsize=10)

        # Insertar CIUDAD DE NACIMIENTO
        if ciudad_nacimiento:
            coords = COORDENADAS_CAMPOS['CIUDAD_NACIMIENTO']
            insertar_texto_en_pdf(page, ciudad_nacimiento, coords['x'], coords['y'], fontsize=10)

        # Guardar el PDF generado
        doc.save(output_path)
        doc.close()

        return output_path

    except Exception as e:
        raise Exception(f"Error al generar el PDF: {str(e)}")


def generar_nombre_archivo_pdf(cedula):
    """
    Genera un nombre de archivo único para el PDF.

    Args:
        cedula (str): Número de cédula del empleado

    Returns:
        str: Nombre del archivo (ej: "formulario_1234567890.pdf")
    """
    return f"formulario_eps_{cedula}.pdf"


# Función de prueba
if __name__ == "__main__":
    # Datos de prueba
    datos_prueba = {
        'CEDULA': '1234567890',
        'PRIMER_APELLIDO': 'GARCÍA',
        'SEGUNDO_APELLIDO': 'LÓPEZ',
        'NOMBRES': 'JUAN CARLOS',
    }

    output_test = "test_formulario_generado.pdf"

    try:
        resultado = rellenar_pdf_empleado(datos_prueba, output_test)
        print(f"✓ PDF generado exitosamente: {resultado}")
    except Exception as e:
        print(f"✗ Error: {e}")
