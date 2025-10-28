import gspread
from google.oauth2.service_account import Credentials
import logging
import os
import json

# Google Sheets API setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = '1OzyM4jlADde1MKU7INbtXvVOUaqD1KfZH_gFLOciwNk'

# Lazy loading del client para evitar errores al importar
_client = None

logger = logging.getLogger(__name__)

def get_credentials():
    """
    Obtiene las credenciales de Google desde variable de entorno o archivo.

    Prioridad:
    1. Variable de entorno GOOGLE_CREDENTIALS (JSON string) - Para producción
    2. Archivo service_account.json - Para desarrollo local
    """
    # Intentar obtener desde variable de entorno (Railway, producción)
    google_creds_env = os.environ.get('GOOGLE_CREDENTIALS')

    if google_creds_env:
        logger.info("Usando credenciales desde variable de entorno GOOGLE_CREDENTIALS")
        try:
            # Parsear el JSON desde la variable de entorno
            creds_dict = json.loads(google_creds_env)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
            return creds
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear GOOGLE_CREDENTIALS: {str(e)}")
            raise ValueError("Variable GOOGLE_CREDENTIALS tiene formato JSON inválido")
        except Exception as e:
            logger.error(f"Error al crear credenciales desde variable de entorno: {str(e)}")
            raise

    # Fallback: usar archivo local (desarrollo)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')

    if os.path.exists(SERVICE_ACCOUNT_FILE):
        logger.info(f"Usando credenciales desde archivo: {SERVICE_ACCOUNT_FILE}")
        try:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
            return creds
        except Exception as e:
            logger.error(f"Error al leer archivo de credenciales: {str(e)}")
            raise

    # No hay credenciales disponibles
    raise FileNotFoundError(
        "No se encontraron credenciales de Google. "
        "Configure la variable GOOGLE_CREDENTIALS o agregue service_account.json"
    )

def get_client():
    global _client
    if _client is None:
        try:
            creds = get_credentials()
            _client = gspread.authorize(creds)
            logger.info("Cliente de Google Sheets autorizado exitosamente")
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
