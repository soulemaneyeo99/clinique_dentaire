# ==========================================
# 6. URLS.PY (App clinic)
# ==========================================
from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    # API Endpoints
    path('api/services/', views.ServiceListView.as_view(), name='services-list'),
    path('api/equipe/', views.EquipeListView.as_view(), name='equipe-list'),
    path('api/horaires/', views.HoraireListView.as_view(), name='horaires-list'),
    
    # Endpoints pour les formulaires
    path('prendre-rendez-vous/', views.prendre_rendezvous, name='prendre-rendez-vous'),
    path('api/contact/', views.contact_message, name='contact-message'),
]