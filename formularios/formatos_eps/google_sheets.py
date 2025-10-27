import gspread
from google.oauth2.service_account import Credentials
import logging
import os

# Google Sheets API setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

# Ruta absoluta al archivo de credenciales
# El archivo está en la carpeta del proyecto Django (un nivel arriba de formatos_eps)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')

SPREADSHEET_ID = '1OzyM4jlADde1MKU7INbtXvVOUaqD1KfZH_gFLOciwNk'

# Lazy loading del client para evitar errores al importar
_client = None

logger = logging.getLogger(__name__)

def get_client():
    global _client
    if _client is None:
        try:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
            _client = gspread.authorize(creds)
        except Exception as e:
            logger.error(f"Error al conectar con Google Sheets: {str(e)}")
            raise ConnectionError(f"No se pudo conectar con Google Sheets. Verifique las credenciales: {str(e)}")
    return _client

def get_sheet_data(sheet_name):
    try:
        client = get_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

        # Obtener todos los valores como lista (no diccionario)
        all_values = sheet.get_all_values()

        if not all_values:
            return []

        # Primera fila son los encabezados
        headers = all_values[0]

        # Manejar columnas duplicadas agregando sufijos
        seen = {}
        unique_headers = []
        for header in headers:
            if header in seen:
                seen[header] += 1
                unique_headers.append(f"{header}_{seen[header]}")
            else:
                seen[header] = 0
                unique_headers.append(header)

        # Convertir las filas a diccionarios
        records = []
        for row in all_values[1:]:  # Saltar encabezados
            # Asegurar que la fila tenga la misma longitud que los encabezados
            row_data = row + [''] * (len(unique_headers) - len(row))
            record = dict(zip(unique_headers, row_data))
            records.append(record)

        return records
    except Exception as e:
        logger.error(f"Error al obtener datos de la hoja '{sheet_name}': {str(e)}")
        raise

def find_row_by_cedula(cedula):
    try:
        planta_data = get_sheet_data('Planta')
        manipuladoras_data = get_sheet_data('Manipuladoras')

        # Limpiar la cédula de búsqueda (eliminar espacios)
        cedula_limpia = str(cedula).strip()

        for row in planta_data:
            # Comparar limpiando espacios en blanco
            cedula_row = str(row.get('CEDULA', '')).strip()
            if cedula_row == cedula_limpia:
                return row

        for row in manipuladoras_data:
            # Comparar limpiando espacios en blanco
            cedula_row = str(row.get('CEDULA', '')).strip()
            if cedula_row == cedula_limpia:
                return row

        return None
    except ConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error al buscar cédula {cedula}: {str(e)}")
        raise
