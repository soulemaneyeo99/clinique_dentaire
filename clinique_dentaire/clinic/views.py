# ==========================================
# VIEWS.PY - Vues Django pour la clinique dentaire
# ==========================================
from rest_framework import status
from rest_framework.response import Response
from .serializers import RendezVousSerializer
from rest_framework.views import APIView

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from datetime import date

# Import des modèles
from .models import Service, Dentiste, Horaire, RendezVous, Contact

# Configuration du logging
logger = logging.getLogger(__name__)

# ==========================================
# VUES API POUR LE FRONTEND
# ==========================================

def home(request):
    """Vue principale - rendu de la page d'accueil"""
    return render(request, 'index.html')

def get_services(request):
    """API pour récupérer tous les services actifs"""
    try:
        services = Service.objects.filter(actif=True).values(
            'id', 'nom', 'description', 'prix_min', 'prix_max', 
            'duree_minutes', 'icone'
        )
        return JsonResponse({
            'status': 'success',
            'services': list(services)
        })
    except Exception as e:
        logger.error(f"Erreur get_services: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur lors de la récupération des services'
        }, status=500)

def get_equipe(request):
    """API pour récupérer l'équipe de dentistes"""
    try:
        dentistes = Dentiste.objects.filter(actif=True).values(
            'id', 'nom', 'prenom', 'specialite', 'bio', 'photo', 'linkedin'
        )
        return JsonResponse({
            'status': 'success',
            'dentistes': list(dentistes)
        })
    except Exception as e:
        logger.error(f"Erreur get_equipe: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur lors de la récupération de l\'équipe'
        }, status=500)

def get_horaires(request):
    """API pour récupérer les horaires de la clinique"""
    try:
        horaires = Horaire.objects.all().values(
            'jour', 'ouverture_matin', 'fermeture_matin',
            'ouverture_apres_midi', 'fermeture_apres_midi', 'ferme'
        )
        return JsonResponse({
            'status': 'success',
            'horaires': list(horaires)
        })
    except Exception as e:
        logger.error(f"Erreur get_horaires: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur lors de la récupération des horaires'
        }, status=500)

# ==========================================
# VUE PRINCIPALE POUR PRENDRE RENDEZ-VOUS
# ==========================================
class PrendreRendezVousView(APIView):
    def post(self, request):
        serializer = RendezVousSerializer(data=request.data)
        
        if serializer.is_valid():
            # Vérifier que le service existe et est actif
            try:
                service = Service.objects.get(id=serializer.validated_data['service'].id, actif=True)
            except Service.DoesNotExist:
                return Response(
                    {'status': 'error', 'message': 'Service non disponible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Créer le rendez-vous
            rdv = serializer.save(service=service)
            
            return Response({
                'status': 'ok',
                'message': 'Rendez-vous enregistré avec succès',
                'data': RendezVousSerializer(rdv).data
            })
        
        return Response({
            'status': 'error',
            'message': 'Données invalides',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    
    def test_email(request):
        try:
            send_mail(
                subject='Test email',
                message='Ceci est un test.',
                from_email='Clinique <soulemaneyeo99@gmail.com>',
                recipient_list=['tonemailperso@gmail.com'],
                fail_silently=False,
            )
            return JsonResponse({'status': 'envoyé'})
        except Exception as e:
            return JsonResponse({'status': 'échec', 'erreur': str(e)})
            
# ==========================================
# VUE POUR LES MESSAGES DE CONTACT
# ==========================================

@csrf_exempt
@require_http_methods(["POST"])
def contact_message(request):
    """Vue pour gérer les messages de contact"""
    try:
        data = json.loads(request.body)
        
        # Validation des champs requis
        required_fields = ['nom', 'prenom', 'email', 'telephone', 'sujet', 'message']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return JsonResponse({
                'status': 'error',
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }, status=400)

        # Validation du téléphone
        import re
        telephone = data['telephone'].strip()
        if not re.match(r'^\+?225?[0-9]{8,10}$', telephone):
            return JsonResponse({
                'status': 'error',
                'message': 'Format de téléphone invalide'
            }, status=400)

        # Validation de l'email
        from django.core.validators import validate_email
        try:
            validate_email(data['email'])
        except ValidationError:
            return JsonResponse({
                'status': 'error',
                'message': 'Format d\'email invalide'
            }, status=400)

        # Création du message de contact
        contact = Contact.objects.create(
            nom=data['nom'].strip(),
            prenom=data['prenom'].strip(),
            email=data['email'].strip(),
            telephone=telephone,
            sujet=data['sujet'].strip(),
            message=data['message'].strip()
        )

        # Envoi de l'email de notification
        try:
            send_contact_notification(contact)
        except Exception as e:
            logger.error(f"Erreur envoi email contact: {e}")

        return JsonResponse({
            'status': 'ok',
            'message': 'Votre message a été envoyé avec succès. Nous vous répondrons rapidement.'
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Données JSON invalides'
        }, status=400)
    except Exception as e:
        logger.error(f"Erreur dans contact_message: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Une erreur interne est survenue. Veuillez réessayer.'
        }, status=500)

# ==========================================
# FONCTIONS UTILITAIRES POUR LES EMAILS
# ==========================================

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

---
Clinique Ivoire Dentaire
Rue des Jardins, Marcory Zone 4
Abidjan, Côte d'Ivoire
Tél: +225 07 00 00 08 41
Email: contact@cliniqueivoiredentaire.ci
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [rendez_vous.email],
            fail_silently=False,
        )
        logger.info(f"Email de confirmation envoyé à {rendez_vous.email}")
    except Exception as e:
        logger.error(f"Erreur envoi email confirmation: {e}")
        raise

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

Statut: {rendez_vous.get_status_display()}

---
Accédez à l'administration pour gérer ce rendez-vous.
"""
    
    try:
        # Vous pouvez configurer une liste d'emails admin dans settings
        admin_emails = getattr(settings, 'ADMIN_EMAILS', [settings.DEFAULT_FROM_EMAIL])
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=False,
        )
        logger.info(f"Notification admin envoyée pour RDV {rendez_vous.id}")
    except Exception as e:
        logger.error(f"Erreur envoi notification admin: {e}")
        raise

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

---
Répondez directement à {contact.email}
"""
    
    try:
        admin_emails = getattr(settings, 'ADMIN_EMAILS', [settings.DEFAULT_FROM_EMAIL])
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=False,
        )
        logger.info(f"Notification contact envoyée pour {contact.email}")
    except Exception as e:
        logger.error(f"Erreur envoi notification contact: {e}")
        raise