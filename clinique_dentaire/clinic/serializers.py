# ==========================================
# 4. SERIALIZERS.PY
# ==========================================
from rest_framework import serializers
from .models import Service, Dentiste, Horaire, RendezVous, Contact
from django.utils import timezone
from datetime import date
from django.core.validators import RegexValidator  # Import ajouté
from datetime import date, datetime, timedelta

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'nom', 'description', 'prix_min', 'prix_max', 
                 'duree_minutes', 'icone', 'image']

class DentisteSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()
    
    class Meta:
        model = Dentiste
        fields = ['id', 'nom', 'prenom', 'nom_complet', 'specialite', 
                 'bio', 'photo', 'linkedin']

class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ['jour', 'ouverture_matin', 'fermeture_matin', 
                 'ouverture_apres_midi', 'fermeture_apres_midi', 'ferme']

class RendezVousSerializer(serializers.ModelSerializer):
    """Serializer pour les rendez-vous avec validation complète"""
    
    # Relation avec le service
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(actif=True),
        error_messages={
            'required': 'Le service est obligatoire.',
            'does_not_exist': 'Le service sélectionné n\'existe pas.',
            'incorrect_type': 'Type de service invalide.'
        }
    )
    
    # Champ en lecture seule pour afficher le nom du service
    service_nom = serializers.CharField(source='service.nom', read_only=True)
    
    # Validation du téléphone avec regex pour la Côte d'Ivoire
    telephone = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?225?[0-9]{8,10}$',
                message="Format de téléphone invalide pour la Côte d'Ivoire. Exemple: +22507123456 ou 07123456"
            )
        ]
    )
    
    # Validation de l'email
    email = serializers.EmailField(
        error_messages={
            'invalid': 'Adresse email invalide.',
            'required': 'L\'adresse email est obligatoire.'
        }
    )
    
    # Validation des noms
    nom = serializers.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZÀ-ÿ\s\-\']+$',
                message="Le nom ne peut contenir que des lettres, espaces, tirets et apostrophes."
            )
        ]
    )
    
    prenom = serializers.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZÀ-ÿ\s\-\']+$',
                message="Le prénom ne peut contenir que des lettres, espaces, tirets et apostrophes."
            )
        ]
    )
    
    # Champ message optionnel
    message = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Message optionnel (max 500 caractères)"
    )

    class Meta:
        model = RendezVous
        fields = [
            'id', 'nom', 'prenom', 'telephone', 'email', 
            'date_souhaitee', 'service', 'service_nom', 
            'message', 'statut',
        ]
        read_only_fields = ['id', 'statut', 'date_creation', 'service_nom']
        
    def validate_date_souhaitee(self, value):
        """Validation de la date souhaitée"""
        today = date.today()
        
        # Vérifier que la date n'est pas dans le passé
        if value < today:
            raise serializers.ValidationError(
                "La date ne peut pas être dans le passé."
            )
        
        # Vérifier que la date n'est pas trop éloignée (max 6 mois)
        max_date = today + timedelta(days=180)
        if value > max_date:
            raise serializers.ValidationError(
                "La date ne peut pas être supérieure à 6 mois."
            )
        
        # Vérifier que ce n'est pas un dimanche (clinique fermée)
        if value.weekday() == 6:  # 6 = dimanche
            raise serializers.ValidationError(
                "La clinique est fermée le dimanche. Veuillez choisir une autre date."
            )
        
        return value

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'email', 'telephone', 'sujet', 'message']
