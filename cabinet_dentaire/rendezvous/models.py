from django.db import models

# Create your models here.
from django.db import models

class RendezVous(models.Model):
    SERVICES = [
        ('consultation', 'Consultation générale'),
        ('urgence', 'Urgence dentaire'),
        ('detartrage', 'Détartrage'),
        ('orthodontie', 'Orthodontie'),
        ('implant', 'Implantologie'),
        ('blanchiment', 'Blanchiment'),
        ('esthetique', 'Esthétique dentaire'),
        ('pediatrie', 'Dentisterie pédiatrique'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    date = models.DateField()
    service = models.CharField(max_length=20, choices=SERVICES)
    message = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.service} - {self.date}"

from django.db import models

class Patient(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.nom
