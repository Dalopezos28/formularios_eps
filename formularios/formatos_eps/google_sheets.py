import gspread
from google.oauth2.service_account import Credentials
import logging

# Google Sheets API setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = 'service_account.json'
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
        return sheet.get_all_records()
    except Exception as e:
        logger.error(f"Error al obtener datos de la hoja '{sheet_name}': {str(e)}")
        raise

def find_row_by_cedula(cedula):
    try:
        planta_data = get_sheet_data('Planta')
        manipuladoras_data = get_sheet_data('Manipuladoras')

        for row in planta_data:
            if str(row.get('CEDULA ', '')) == str(cedula):
                return row

        for row in manipuladoras_data:
            if str(row.get('CEDULA ', '')) == str(cedula):
                return row

        return None
    except ConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error al buscar cédula {cedula}: {str(e)}")
        raise
