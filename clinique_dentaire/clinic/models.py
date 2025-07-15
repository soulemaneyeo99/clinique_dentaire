# ==========================================
# MODELS.PY - Modèles Django pour la clinique dentaire
# ==========================================

from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone
from datetime import date

class Service(models.Model):
    """Modèle pour les services dentaires proposés"""
    nom = models.CharField(max_length=100, verbose_name="Nom du service")
    description = models.TextField(verbose_name="Description")
    ordre = models.PositiveIntegerField(default=0)

    prix_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Prix minimum"
    )
    prix_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Prix maximum"
    )
    duree_minutes = models.PositiveIntegerField(
        default=30, 
        verbose_name="Durée en minutes"
    )
    actif = models.BooleanField(default=True, verbose_name="Service actif")
    icone = models.CharField(
        max_length=50, 
        default="ri-health-book-line",
        verbose_name="Icône Remix"
    )
    image = models.ImageField(
        upload_to='services/', 
        null=True, 
        blank=True,
        verbose_name="Image du service"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Dentiste(models.Model):
    """Modèle pour les dentistes de la clinique"""
    nom = models.CharField(max_length=50, verbose_name="Nom")
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    specialite = models.CharField(max_length=100, verbose_name="Spécialité")
    bio = models.TextField(verbose_name="Biographie")
    ordre = models.PositiveIntegerField(default=0)

    photo = models.ImageField(
        upload_to='dentistes/', 
        null=True, 
        blank=True,
        verbose_name="Photo"
    )
    linkedin = models.URLField(blank=True, verbose_name="Profil LinkedIn")
    actif = models.BooleanField(default=True, verbose_name="Dentiste actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dentiste"
        verbose_name_plural = "Dentistes"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"Dr. {self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class Horaire(models.Model):
    """Modèle pour les horaires de la clinique"""
    JOURS_SEMAINE = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    jour = models.IntegerField(choices=JOURS_SEMAINE, unique=True)
    ouverture_matin = models.TimeField(null=True, blank=True)
    fermeture_matin = models.TimeField(null=True, blank=True)
    ouverture_apres_midi = models.TimeField(null=True, blank=True)
    fermeture_apres_midi = models.TimeField(null=True, blank=True)
    ferme = models.BooleanField(default=False, verbose_name="Fermé ce jour")

    class Meta:
        verbose_name = "Horaire"
        verbose_name_plural = "Horaires"
        ordering = ['jour']

    def __str__(self):
        return f"{self.get_jour_display()}"


class RendezVous(models.Model):
    """Modèle principal pour les rendez-vous"""
    # Statuts possibles
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('completed', 'Terminé'),
    ]
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    
    # Validation du téléphone ivoirien
    phone_regex = RegexValidator(
        regex=r'^\+225\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}$|^\d{10}$',
        message="Format téléphone invalide. Exemple: +225 07 08 09 10"
    )
    telephone = models.CharField(
        validators=[phone_regex], 
        max_length=20, 
        verbose_name="Téléphone"
    )
    
    email = models.EmailField(verbose_name="Email")
    
    # Informations du rendez-vous
    date_souhaitee = models.DateField(verbose_name="Date souhaitée")
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        verbose_name="Service demandé"
    )
    message = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Message complémentaire"
    )
    
    # Statut et métadonnées
    statut = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="Statut"
    )
    
    # Dates système
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    # Champ pour la date/heure confirmée par l'admin
    date_confirmee = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Date et heure confirmées"
    )
    
    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.service.nom} ({self.date_souhaitee})"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        # Vérifier que la date n'est pas dans le passé
        if self.date_souhaitee and self.date_souhaitee < timezone.now().date():
            raise ValidationError({
                'date_souhaitee': 'La date ne peut pas être dans le passé.'
            })
class Contact(models.Model):
    """Modèle pour les messages de contact"""
    nom = models.CharField(max_length=50, verbose_name="Nom")
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    email = models.EmailField(verbose_name="Email")
    lu = models.BooleanField(default=False)
    telephone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?225?[0-9]{8,10}$',
            message="Format: +225XXXXXXXX"
        )],
        verbose_name="Téléphone"
    )
    sujet = models.CharField(max_length=100, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    traite = models.BooleanField(default=False, verbose_name="Traité")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom_complet} - {self.sujet}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"