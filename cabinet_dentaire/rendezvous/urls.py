from django.urls import path
from .views import RendezVousCreateView

urlpatterns = [
    path('prendre-rendezvous/', RendezVousCreateView.as_view(), name='prendre_rendezvous'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('rendez-vous/', views.prendre_rendez_vous, name='rendezvous'),
    path('liste-rendez-vous/', views.liste_rendezvous, name='liste_rendezvous'),
]
