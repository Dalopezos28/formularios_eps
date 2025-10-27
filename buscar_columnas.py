#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para buscar columnas específicas en las hojas de Google Sheets
"""
import sys
import os

# Agregar el directorio de Django al path
sys.path.insert(0, 'formularios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formularios.settings')

# Configurar Django
import django
django.setup()

from formatos_eps.google_sheets import get_sheet_data

print("=" * 80)
print("BÚSQUEDA DE COLUMNAS EN GOOGLE SHEETS")
print("=" * 80)

# Palabras clave a buscar
keywords = ['PAIS', 'SEXO', 'DEPARTAMENTO', 'CIUDAD', 'NACIMIENTO']

print("\nBuscando columnas relacionadas con:")
for kw in keywords:
    print(f"  - {kw}")

print("\n" + "-" * 80)

# Buscar en hoja Planta
print("\n1. HOJA 'PLANTA':")
print("-" * 80)

try:
    planta_data = get_sheet_data('Planta')
    if planta_data:
        columns = list(planta_data[0].keys())
        print(f"Total de columnas: {len(columns)}\n")

        # Buscar columnas que contengan las palabras clave
        found_columns = {}
        for keyword in keywords:
            matching = [col for col in columns if keyword.upper() in col.upper()]
            if matching:
                found_columns[keyword] = matching

        if found_columns:
            print("Columnas encontradas:")
            for keyword, cols in found_columns.items():
                print(f"\n  {keyword}:")
                for col in cols:
                    print(f"    - '{col}'")
        else:
            print("No se encontraron columnas con esas palabras clave")

        # Mostrar todas las columnas para referencia
        print("\n\nTODAS LAS COLUMNAS (primeras 30):")
        for i, col in enumerate(columns[:30], 1):
            print(f"  {i:2}. '{col}'")

        if len(columns) > 30:
            print(f"  ... y {len(columns) - 30} más")

except Exception as e:
    print(f"Error al leer hoja Planta: {e}")

print("\n" + "-" * 80)

# Buscar en hoja Manipuladoras
print("\n2. HOJA 'MANIPULADORAS':")
print("-" * 80)

try:
    manipuladoras_data = get_sheet_data('Manipuladoras')
    if manipuladoras_data:
        columns = list(manipuladoras_data[0].keys())
        print(f"Total de columnas: {len(columns)}\n")

        # Buscar columnas que contengan las palabras clave
        found_columns = {}
        for keyword in keywords:
            matching = [col for col in columns if keyword.upper() in col.upper()]
            if matching:
                found_columns[keyword] = matching

        if found_columns:
            print("Columnas encontradas:")
            for keyword, cols in found_columns.items():
                print(f"\n  {keyword}:")
                for col in cols:
                    print(f"    - '{col}'")
        else:
            print("No se encontraron columnas con esas palabras clave")

        # Mostrar todas las columnas para referencia
        print("\n\nTODAS LAS COLUMNAS (primeras 30):")
        for i, col in enumerate(columns[:30], 1):
            print(f"  {i:2}. '{col}'")

        if len(columns) > 30:
            print(f"  ... y {len(columns) - 30} más")

except Exception as e:
    print(f"Error al leer hoja Manipuladoras: {e}")

print("\n" + "=" * 80)
print("BÚSQUEDA COMPLETADA")
print("=" * 80)
