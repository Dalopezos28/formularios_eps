#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para generar un PDF con datos de ejemplo
"""
import sys
import os

# Agregar el directorio de Django al path
sys.path.insert(0, 'formularios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formularios.settings')

# Configurar Django
import django
django.setup()

from formatos_eps.pdf_generator import rellenar_pdf_empleado

print("=" * 60)
print("PRUEBA DE GENERACION DE PDF")
print("=" * 60)

# Datos de prueba
datos_prueba = {
    'CEDULA': '1234567890',
    'PRIMER_APELLIDO': 'GARCIA',
    'SEGUNDO_APELLIDO': 'LOPEZ',
    'NOMBRES': 'JUAN CARLOS',
}

print("\n1. Datos de prueba:")
print(f"   - CEDULA: {datos_prueba['CEDULA']}")
print(f"   - PRIMER APELLIDO: {datos_prueba['PRIMER_APELLIDO']}")
print(f"   - SEGUNDO APELLIDO: {datos_prueba['SEGUNDO_APELLIDO']}")
print(f"   - NOMBRES: {datos_prueba['NOMBRES']}")

output_path = "formulario_generado_prueba.pdf"

print(f"\n2. Generando PDF: {output_path}")

try:
    resultado = rellenar_pdf_empleado(datos_prueba, output_path)
    print(f"   [OK] PDF generado exitosamente!")
    print(f"   - Archivo: {os.path.abspath(resultado)}")
    print(f"\n3. Abre el archivo para verificar las coordenadas:")
    print(f"   - CEDULA debe estar en (x:120, y:190)")
    print(f"   - PRIMER APELLIDO en (x:100, y:175)")
    print(f"   - SEGUNDO APELLIDO en (x:150, y:175)")
    print(f"   - PRIMER NOMBRE (JUAN) en (x:180, y:175)")
    print(f"   - SEGUNDO NOMBRE (CARLOS) en (x:200, y:175)")

    print("\n" + "=" * 60)
    print("[OK] PRUEBA COMPLETADA")
    print("=" * 60)
    print(f"\nSi las coordenadas no coinciden, ajusta los valores en:")
    print("formularios/formatos_eps/pdf_generator.py")

except FileNotFoundError as e:
    print(f"   [ERROR] No se encontro el PDF template")
    print(f"   - Verifica que exista: formatos/formulario_de_afiliacion_eps_delagente_comfenalco_valle.pdf")
except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
