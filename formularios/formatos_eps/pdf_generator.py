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
}

# Ruta al PDF original (plantilla)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_TEMPLATE = os.path.join(BASE_DIR, 'formatos', 'formulario_de_afiliacion_eps_delagente_comfenalco_valle.pdf')


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
