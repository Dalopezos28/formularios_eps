from django.urls import path
from . import views

app_name = 'formatos_eps'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_view, name='search'),
    path('search/results/', views.search_results_view, name='search_results'),
    path('generar-pdf/<str:cedula>/', views.generar_pdf_view, name='generar_pdf'),
]