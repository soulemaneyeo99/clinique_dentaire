# ==========================================
# 4. SERIALIZERS.PY
# ==========================================
from rest_framework import serializers
from .models import Service, Dentiste, Horaire, RendezVous, Contact
from django.utils import timezone
from datetime import date

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
    service_nom = serializers.CharField(source='service.nom', read_only=True)
    
    class Meta:
        model = RendezVous
        fields = ['nom', 'prenom', 'telephone', 'email', 'date_souhaitee', 
                 'service', 'service_nom', 'message']
        extra_kwargs = {
            'service': {'write_only': True}
        }

    def validate_date_souhaitee(self, value):
        """Valider que la date n'est pas dans le passé"""
        if value < date.today():
            raise serializers.ValidationError("La date ne peut pas être dans le passé.")
        return value

    def validate_telephone(self, value):
        """Validation personnalisée du téléphone"""
        import re
        if not re.match(r'^\+?225?[0-9]{8,10}$', value):
            raise serializers.ValidationError("Format de téléphone invalide pour la Côte d'Ivoire.")
        return value

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'email', 'telephone', 'sujet', 'message']

# ==========================================
# 5. VIEWS.PY
# ==========================================
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)

class ServiceListView(generics.ListAPIView):
    """API pour lister tous les services actifs"""
    queryset = Service.objects.filter(actif=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

class EquipeListView(generics.ListAPIView):
    """API pour lister tous les membres de l'équipe actifs"""
    queryset = Dentiste.objects.filter(actif=True)
    serializer_class = DentisteSerializer
    permission_classes = [AllowAny]

class HoraireListView(generics.ListAPIView):
    """API pour lister les horaires de la clinique"""
    queryset = Horaire.objects.all()
    serializer_class = HoraireSerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([AllowAny])
def prendre_rendez_vous(request):
    """
    Endpoint principal pour la prise de rendez-vous
    Gère la validation, l'enregistrement et l'envoi d'email
    """
    try:
        # Récupération des données
        data = request.data
        
        # Validation des champs requis
        required_fields = ['nom', 'prenom', 'telephone', 'email', 'date', 'service']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return Response({
                'status': 'error',
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Récupération du service
        try:
            service = Service.objects.get(nom=data['service'], actif=True)
        except Service.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Service non disponible'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Préparation des données pour le serializer
        rdv_data = {
            'nom': data['nom'].strip(),
            'prenom': data['prenom'].strip(),
            'telephone': data['telephone'].strip(),
            'email': data['email'].strip(),
            'date_souhaitee': data['date'],
            'service': service.id,
            'message': data.get('message', '').strip()
        }

        # Validation et création
        serializer = RendezVousSerializer(data=rdv_data)
        if serializer.is_valid():
            rendez_vous = serializer.save()
            
            # Envoi de l'email de confirmation
            try:
                send_confirmation_email(rendez_vous)
                send_admin_notification(rendez_vous)
            except Exception as e:
                logger.error(f"Erreur envoi email: {e}")
                # On continue même si l'email échoue
            
            return Response({
                'status': 'ok',
                'message': 'Votre demande de rendez-vous a été enregistrée avec succès. Nous vous contacterons bientôt pour confirmer.'
            }, status=status.HTTP_201_CREATED)
        else:
            # Formatage des erreurs de validation
            errors = []
            for field, field_errors in serializer.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            return Response({
                'status': 'error',
                'message': f'Erreurs de validation: {", ".join(errors)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur dans prendre_rendez_vous: {e}")
        return Response({
            'status': 'error',
            'message': 'Une erreur interne est survenue. Veuillez réessayer.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_message(request):
    """Endpoint pour les messages de contact"""
    try:
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            
            # Envoi de l'email de notification
            try:
                send_contact_notification(contact)
            except Exception as e:
                logger.error(f"Erreur envoi email contact: {e}")
            
            return Response({
                'status': 'ok',
                'message': 'Votre message a été envoyé avec succès. Nous vous répondrons rapidement.'
            }, status=status.HTTP_201_CREATED)
        else:
            errors = []
            for field, field_errors in serializer.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            return Response({
                'status': 'error',
                'message': f'Erreurs de validation: {", ".join(errors)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Erreur dans contact_message: {e}")
        return Response({
            'status': 'error',
            'message': 'Une erreur interne est survenue. Veuillez réessayer.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Fonctions utilitaires pour les emails
def send_confirmation_email(rendez_vous):
    """Envoie un email de confirmation au patient"""
    subject = f'Confirmation de votre demande de rendez-vous - Clinique Ivoire Dentaire'
    
    message = f"""
    Bonjour {rendez_vous.nom_complet},

    Nous avons bien reçu votre demande de rendez-vous pour le {rendez_vous.date_souhaitee.strftime('%d/%m/%Y')}.

    Détails de votre demande:
    - Service: {rendez_vous.service.nom}
    - Date souhaitée: {rendez_vous.date_souhaitee.strftime('%d/%m/%Y')}
    - Téléphone: {rendez_vous.telephone}
    {f"- Message: {rendez_vous.message}" if rendez_vous.message else ""}

    Notre équipe vous contactera dans les plus brefs délais pour confirmer votre rendez-vous.

    Cordialement,
    L'équipe de la Clinique Ivoire Dentaire
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [rendez_vous.email],
        fail_silently=False,
    )

def send_admin_notification(rendez_vous):
    """Envoie une notification à l'admin"""
    subject = f'Nouvelle demande de rendez-vous - {rendez_vous.nom_complet}'
    
    message = f"""
    Nouvelle demande de rendez-vous reçue:

    Patient: {rendez_vous.nom_complet}
    Email: {rendez_vous.email}
    Téléphone: {rendez_vous.telephone}
    Service: {rendez_vous.service.nom}
    Date souhaitée: {rendez_vous.date_souhaitee.strftime('%d/%m/%Y')}
    Message: {rendez_vous.message or "Aucun message"}

    Reçu le: {rendez_vous.created_at.strftime('%d/%m/%Y à %H:%M')}
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],  # Ou une liste d'emails admin
        fail_silently=False,
    )

def send_contact_notification(contact):
    """Envoie une notification pour les messages de contact"""
    subject = f'Nouveau message de contact - {contact.nom_complet}'
    
    message = f"""
    Nouveau message de contact reçu:

    Nom: {contact.nom_complet}
    Email: {contact.email}
    Téléphone: {contact.telephone}
    Sujet: {contact.sujet}
    
    Message:
    {contact.message}

    Reçu le: {contact.created_at.strftime('%d/%m/%Y à %H:%M')}
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )
