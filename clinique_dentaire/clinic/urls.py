# ==========================================
# URLS.PY - Configuration des URLs Django
# ==========================================
from .views import PrendreRendezVousView

from django.urls import path
from . import views

# Configuration des URLs pour l'application clinique
urlpatterns = [
    # Page principale
    path('', views.home, name='home'),
    
    # APIs pour récupérer les données
    path('api/services/', views.get_services, name='get_services'),
    path('api/equipe/', views.get_equipe, name='get_equipe'),
    path('api/horaires/', views.get_horaires, name='get_horaires'),
    
    # Endpoints pour les formulaires
    path('prendre-rendez-vous/', PrendreRendezVousView.as_view(), name='prendre_rendezvous'),

    path('contact/', views.contact_message, name='contact_message'),
]

