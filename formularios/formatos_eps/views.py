from django.shortcuts import render
from .google_sheets import find_row_by_cedula

def login_view(request):
    return render(request, 'formatos_eps/login.html')

def search_view(request):
    return render(request, 'formatos_eps/search.html')

def search_results_view(request):
    cedula = request.GET.get('cedula')
    results = None
    if cedula:
        results = find_row_by_cedula(cedula)
    return render(request, 'formatos_eps/search_results.html', {'results': [results] if results else [], 'cedula': cedula})
