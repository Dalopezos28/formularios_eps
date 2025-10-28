#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener las credenciales de Google en formato para Railway.

Uso:
    python get_credentials_for_railway.py

Esto mostrará el contenido del service_account.json en una sola línea
que puedes copiar y pegar en Railway como variable de entorno.
"""

import json
import os

SERVICE_ACCOUNT_FILE = 'formularios/service_account.json'

print("=" * 80)
print("CREDENCIALES DE GOOGLE PARA RAILWAY")
print("=" * 80)

if not os.path.exists(SERVICE_ACCOUNT_FILE):
    print(f"\n❌ ERROR: No se encontró el archivo: {SERVICE_ACCOUNT_FILE}")
    print("\nAsegúrate de que el archivo existe en la ruta correcta.")
    exit(1)

try:
    # Leer el archivo JSON
    with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as f:
        credentials = json.load(f)

    # Convertir a string JSON compacto (una sola línea)
    credentials_str = json.dumps(credentials, separators=(',', ':'))

    print("\n✅ Archivo leído correctamente")
    print(f"\nProject ID: {credentials.get('project_id')}")
    print(f"Client Email: {credentials.get('client_email')}")

    print("\n" + "-" * 80)
    print("INSTRUCCIONES PARA RAILWAY:")
    print("-" * 80)

    print("\n1. Ve a tu proyecto en Railway")
    print("2. Click en 'Variables' (pestaña)")
    print("3. Click en 'New Variable'")
    print("4. Nombre de la variable: GOOGLE_CREDENTIALS")
    print("5. Valor: Copia TODO el texto de abajo (entre las líneas de ===)")

    print("\n" + "=" * 80)
    print("COPIAR DESDE AQUÍ (SIN INCLUIR ESTA LÍNEA)")
    print("=" * 80)
    print(credentials_str)
    print("=" * 80)
    print("HASTA AQUÍ (SIN INCLUIR ESTA LÍNEA)")
    print("=" * 80)

    print("\n6. Click en 'Add'")
    print("7. Railway redesplegará automáticamente tu aplicación")

    print("\n" + "=" * 80)
    print("✅ COMPLETADO")
    print("=" * 80)

    # Guardar también en un archivo temporal por si acaso
    output_file = 'google_credentials_for_railway.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(credentials_str)

    print(f"\n💾 También guardado en: {output_file}")
    print("   (Puedes abrirlo y copiar desde ahí si prefieres)")

except json.JSONDecodeError as e:
    print(f"\n❌ ERROR: El archivo JSON tiene formato inválido: {e}")
    print("\nVerifica que service_account.json sea un JSON válido.")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
