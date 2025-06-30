from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import RendezVous
from .serializers import RendezVousSerializer

class RendezVousCreateView(generics.CreateAPIView):
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer
from django.http import HttpResponse

def accueil(request):
    return HttpResponse("<h1>Bienvenue sur le site du Cabinet Dentaire</h1>")
def prendre_rendez_vous(request):
    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'confirmation.html')
    else:
        form = RendezVousForm()
    return render(request, 'rendezvous.html', {'form': form})
from django.shortcuts import render
from .models import RendezVous

def liste_rendezvous(request):
    rendezvous = RendezVous.objects.all().order_by('-date')  # Optionnel : tri par date
    return render(request, 'liste_rendezvous.html', {'rendezvous': rendezvous})
