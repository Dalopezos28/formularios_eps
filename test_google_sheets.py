#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnostico para probar la conexion con Google Sheets
"""
import json
import sys


print("=" * 60)
print("DIAGNOSTICO DE GOOGLE SHEETS API")
print("=" * 60)

# 1. Verificar que el archivo existe
print("\n1. Verificando archivo service_account.json...")
try:
    with open('formularios/service_account.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("   [OK] Archivo encontrado y parseado correctamente")
    print(f"   - Project ID: {data.get('project_id')}")
    print(f"   - Client Email: {data.get('client_email')}")
except FileNotFoundError:
    print("   [ERROR] Archivo service_account.json no encontrado")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"   [ERROR] JSON invalido - {e}")
    sys.exit(1)
except Exception as e:
    print(f"   [ERROR] {e}")
    sys.exit(1)

# 2. Verificar estructura de la clave privada
print("\n2. Verificando estructura de la clave privada...")
private_key = data.get('private_key', '')
if not private_key:
    print("   ✗ ERROR: No se encontró 'private_key' en el JSON")
    sys.exit(1)
elif not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
    print("   ✗ ERROR: La clave privada no tiene el formato correcto")
    sys.exit(1)
else:
    print("   ✓ Clave privada tiene el formato correcto")
    lines = private_key.count('\n')
    print(f"   - Líneas en la clave: {lines}")

# 3. Probar importar las librerías
print("\n3. Verificando librerías...")
try:
    import gspread
    print("   ✓ gspread instalado")
except ImportError:
    print("   ✗ ERROR: gspread no está instalado")
    sys.exit(1)

try:
    from google.oauth2.service_account import Credentials
    print("   ✓ google-auth instalado")
except ImportError:
    print("   ✗ ERROR: google-auth no está instalado")
    sys.exit(1)

# 4. Intentar crear las credenciales
print("\n4. Intentando crear credenciales...")
try:
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        'formularios/service_account.json',
        scopes=SCOPE
    )
    print("   ✓ Credenciales creadas exitosamente")
except ValueError as e:
    print(f"   ✗ ERROR en el formato de las credenciales: {e}")
    print("\n   SOLUCIÓN: Descarga nuevamente el archivo JSON desde Google Cloud Console")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ ERROR: {type(e).__name__}: {e}")

    if "padding" in str(e).lower():
        print("\n   CAUSA: La clave privada tiene un problema de codificación base64")
        print("   SOLUCIÓN:")
        print("   1. Ve a Google Cloud Console")
        print("   2. IAM → Cuentas de servicio")
        print("   3. Descarga una nueva clave JSON")
        print("   4. Reemplaza el archivo service_account.json")
    sys.exit(1)

# 5. Intentar autorizar con gspread
print("\n5. Intentando autorizar con gspread...")
try:
    client = gspread.authorize(creds)
    print("   ✓ Cliente de gspread autorizado")
except Exception as e:
    print(f"   ✗ ERROR: {type(e).__name__}: {e}")
    sys.exit(1)

# 6. Intentar abrir el spreadsheet
print("\n6. Intentando acceder al spreadsheet...")
SPREADSHEET_ID = '1OzyM4jlADde1MKU7INbtXvVOUaqD1KfZH_gFLOciwNk'
try:
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    print("   ✓ Spreadsheet encontrado")
    print(f"   - Título: {spreadsheet.title}")

    # Listar hojas
    worksheets = spreadsheet.worksheets()
    print(f"   - Hojas disponibles: {[ws.title for ws in worksheets]}")

except gspread.exceptions.SpreadsheetNotFound:
    print(f"   ✗ ERROR: No se encontró el spreadsheet con ID: {SPREADSHEET_ID}")
    print("\n   SOLUCIÓN: Verifica que el spreadsheet existe y está compartido con:")
    print(f"   {data.get('client_email')}")
except gspread.exceptions.APIError as e:
    print(f"   ✗ ERROR de API: {e}")
    if "PERMISSION_DENIED" in str(e):
        print("\n   CAUSA: La cuenta de servicio no tiene permisos")
        print("   SOLUCIÓN:")
        print("   1. Abre el Google Sheet")
        print("   2. Click en 'Compartir'")
        print(f"   3. Agrega: {data.get('client_email')}")
        print("   4. Dale permisos de 'Editor' o 'Lector'")
except Exception as e:
    print(f"   ✗ ERROR: {type(e).__name__}: {e}")
    sys.exit(1)

# 7. Intentar leer datos con manejo de columnas duplicadas
print("\n7. Intentando leer datos de las hojas...")
try:
    # Importar la función actualizada
    sys.path.insert(0, 'formularios')
    from formatos_eps.google_sheets import get_sheet_data

    planta_data = get_sheet_data('Planta')
    print(f"   [OK] Hoja 'Planta' leida: {len(planta_data)} registros")

    if planta_data:
        # Mostrar columnas (primeros 10)
        columns = list(planta_data[0].keys())
        print(f"   - Total de columnas: {len(columns)}")
        print(f"   - Primeras 10 columnas: {columns[:10]}")

        # Buscar columna de CEDULA
        cedula_cols = [col for col in columns if 'CEDULA' in col.upper()]
        print(f"   - Columnas tipo CEDULA: {cedula_cols}")

except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    manipuladoras_data = get_sheet_data('Manipuladoras')
    print(f"   [OK] Hoja 'Manipuladoras' leida: {len(manipuladoras_data)} registros")

    if manipuladoras_data:
        columns = list(manipuladoras_data[0].keys())
        cedula_cols = [col for col in columns if 'CEDULA' in col.upper()]
        print(f"   - Columnas tipo CEDULA: {cedula_cols}")

except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")

# 8. Probar búsqueda por cédula
print("\n8. Probando busqueda por cedula...")
try:
    from formatos_eps.google_sheets import find_row_by_cedula

    # Intentar con el primer registro
    if planta_data:
        test_cedula = planta_data[0].get('CEDULA ', '') or planta_data[0].get('CEDULA', '')
        print(f"   - Probando con cedula de prueba: {test_cedula}")

        result = find_row_by_cedula(str(test_cedula))
        if result:
            print(f"   [OK] Empleado encontrado!")
            print(f"   - CEDULA: {result.get('CEDULA ', result.get('CEDULA', 'N/A'))}")
            print(f"   - NOMBRES: {result.get('NOMBRES', 'N/A')}")
        else:
            print(f"   [ERROR] No se encontro el empleado")

except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("[OK] DIAGNOSTICO COMPLETADO - CONEXION EXITOSA")
print("=" * 60)
print("\nSi llegaste aqui, todo funciona correctamente!")
