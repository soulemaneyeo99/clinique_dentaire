# ==========================================
# 3. MODELS.PY
# ==========================================
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Service(models.Model):
    """Modèle pour les services de la clinique"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    prix_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duree_minutes = models.PositiveIntegerField(default=30)
    icone = models.CharField(max_length=50, blank=True)  # Nom de l'icône
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.nom

class Dentiste(models.Model):
    """Modèle pour les membres de l'équipe"""
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    specialite = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='equipe/', null=True, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=15, blank=True)
    linkedin = models.URLField(blank=True)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Dentiste'
        verbose_name_plural = 'Dentistes'

    def __str__(self):
        return f"Dr. {self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"Dr. {self.prenom} {self.nom}"

class Horaire(models.Model):
    """Modèle pour les horaires de la clinique"""
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]
    
    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE, unique=True)
    ouverture_matin = models.TimeField(null=True, blank=True)
    fermeture_matin = models.TimeField(null=True, blank=True)
    ouverture_apres_midi = models.TimeField(null=True, blank=True)
    fermeture_apres_midi = models.TimeField(null=True, blank=True)
    ferme = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Horaire'
        verbose_name_plural = 'Horaires'

    def __str__(self):
        return self.jour.capitalize()

class RendezVous(models.Model):
    """Modèle pour les rendez-vous"""
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('reporte', 'Reporté'),
        ('annule', 'Annulé'),
        ('termine', 'Terminé'),
    ]
    
    # Validation du téléphone ivoirien
    phone_regex = RegexValidator(
        regex=r'^\+?225?[0-9]{8,10}$',
        message="Le numéro de téléphone doit être au format ivoirien (+225xxxxxxxx)"
    )
    
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()
    date_souhaitee = models.DateField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    
    # Champs de gestion
    date_confirmation = models.DateTimeField(null=True, blank=True)
    notes_admin = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.date_souhaitee}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class Contact(models.Model):
    """Modèle pour les messages de contact"""
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=17, blank=True)
    sujet = models.CharField(max_length=100)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'

    def __str__(self):
        return f"{self.nom_complet} - {self.sujet}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
