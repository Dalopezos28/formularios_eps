import gspread
from google.oauth2.service_account import Credentials

# Google Sheets API setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"] 
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1OzyM4jlADde1MKU7INbtXvVOUaqD1KfZH_gFLOciwNk'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
client = gspread.authorize(creds)

def get_sheet_data(sheet_name):
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    return sheet.get_all_records()

def find_row_by_cedula(cedula):
    planta_data = get_sheet_data('Planta')
    manipuladoras_data = get_sheet_data('Manipuladoras')

    for row in planta_data:
        if str(row['CEDULA']) == cedula:
            return row

    for row in manipuladoras_data:
        if str(row['CEDULA']) == cedula:
            return row

    return None
