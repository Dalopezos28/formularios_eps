from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from .google_sheets import find_row_by_cedula
from .pdf_generator import rellenar_pdf_empleado, generar_nombre_archivo_pdf
import os
import tempfile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('formatos_eps:search')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('formatos_eps:search')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'formatos_eps/login.html')

@login_required(login_url='formatos_eps:login')
def search_view(request):
    return render(request, 'formatos_eps/search.html')

@login_required(login_url='formatos_eps:login')
def search_results_view(request):
    cedula = request.GET.get('cedula')
    results = None
    error_message = None

    if cedula:
        try:
            result_data = find_row_by_cedula(cedula)
            if result_data:
                # Normalizar las claves del diccionario (reemplazar espacios con guiones bajos)
                normalized_result = {
                    'CEDULA': result_data.get('CEDULA', ''),
                    'PRIMER_APELLIDO': result_data.get('PRIMER APELLIDO', ''),
                    'SEGUNDO_APELLIDO': result_data.get('SEGUNDO APELLIDO', ''),
                    'NOMBRES': result_data.get('NOMBRES', ''),
                    # Puedes agregar más campos aquí si los necesitas
                }
                results = normalized_result
        except ConnectionError as e:
            error_message = "Error de conexión con Google Sheets. Por favor, verifique la configuración de credenciales."
            messages.error(request, error_message)
        except Exception as e:
            error_message = f"Error al buscar la cédula: {str(e)}"
            messages.error(request, error_message)

    return render(request, 'formatos_eps/search_results.html', {
        'results': [results] if results else [],
        'cedula': cedula,
        'error_message': error_message
    })

@login_required(login_url='formatos_eps:login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('formatos_eps:login')

@login_required(login_url='formatos_eps:login')
def generar_pdf_view(request, cedula):
    """
    Vista para generar y descargar el PDF del formulario EPS con los datos del empleado.
    """
    try:
        # Buscar datos del empleado
        datos_empleado = find_row_by_cedula(cedula)

        if not datos_empleado:
            messages.error(request, f'No se encontró empleado con cédula {cedula}')
            return redirect('formatos_eps:search_results') + f'?cedula={cedula}'

        # Normalizar datos (igual que en search_results_view)
        datos_normalizados = {
            'CEDULA': datos_empleado.get('CEDULA', ''),
            'PRIMER_APELLIDO': datos_empleado.get('PRIMER APELLIDO', ''),
            'SEGUNDO_APELLIDO': datos_empleado.get('SEGUNDO APELLIDO', ''),
            'NOMBRES': datos_empleado.get('NOMBRES', ''),
        }

        # Generar nombre del archivo
        nombre_archivo = generar_nombre_archivo_pdf(cedula)

        # Crear archivo temporal para el PDF
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, nombre_archivo)

        # Generar PDF
        rellenar_pdf_empleado(datos_normalizados, output_path)

        # Retornar el PDF como descarga
        response = FileResponse(
            open(output_path, 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=nombre_archivo
        )

        return response

    except ConnectionError as e:
        messages.error(request, 'Error de conexión con Google Sheets')
        return redirect('formatos_eps:search')
    except FileNotFoundError as e:
        messages.error(request, 'No se encontró el archivo PDF template')
        return redirect('formatos_eps:search')
    except Exception as e:
        messages.error(request, f'Error al generar el PDF: {str(e)}')
        return redirect('formatos_eps:search')
