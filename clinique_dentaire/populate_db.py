# ==========================================
# 12. SCRIPT DE DONNÉES DE TEST
# ==========================================
"""
# Fichier: populate_db.py
# À exécuter avec: python manage.py shell < populate_db.py
"""
from clinic.models import Service, Dentiste, Horaire

# Créer des services
services_data = [
    {
        'nom': 'Consultation générale',
        'description': 'Examen complet de la bouche et des dents',
        'prix_min': 25000,
        'prix_max': 35000,
        'duree_minutes': 30,
        'icone': 'stethoscope',
        'ordre': 1
    },
    {
        'nom': 'Détartrage',
        'description': 'Nettoyage professionnel des dents',
        'prix_min': 15000,
        'prix_max': 25000,
        'duree_minutes': 45,
        'icone': 'sparkles',
        'ordre': 2
    },
    {
        'nom': 'Soins dentaires',
        'description': 'Traitement des caries et obturations',
        'prix_min': 20000,
        'prix_max': 50000,
        'duree_minutes': 60,
        'icone': 'tooth',
        'ordre': 3
    },
    {
        'nom': 'Orthodontie',
        'description': 'Correction de l\'alignement des dents',
        'prix_min': 500000,
        'prix_max': 1500000,
        'duree_minutes': 90,
        'icone': 'braces',
        'ordre': 4
    },
    {
        'nom': 'Prothèses dentaires',
        'description': 'Couronnes, bridges et prothèses',
        'prix_min': 100000,
        'prix_max': 300000,
        'duree_minutes': 120,
        'icone': 'crown',
        'ordre': 5
    },
    {
        'nom': 'Implants dentaires',
        'description': 'Remplacement de dents manquantes',
        'prix_min': 200000,
        'prix_max': 500000,
        'duree_minutes': 150,
        'icone': 'implant',
        'ordre': 6
    }
]

for service_data in services_data:
    Service.objects.get_or_create(
        nom=service_data['nom'],
        defaults=service_data
    )

# Créer des dentistes
dentistes_data = [
    {
        'nom': 'KOUAME',
        'prenom': 'Marie',
        'specialite': 'Dentisterie générale',
        'bio': 'Diplômée de l\'Université d\'Abidjan, spécialisée en soins dentaires généraux avec 10 ans d\'expérience.',
        'ordre': 1
    },
    {
        'nom': 'DIABATE',
        'prenom': 'Seydou',
        'specialite': 'Orthodontie',
        'bio': 'Orthodontiste certifié avec une expertise en correction dentaire moderne.',
        'ordre': 2
    },
    {
        'nom': 'OUATTARA',
        'prenom': 'Aminata',
        'specialite': 'Chirurgie dentaire',
        'bio': 'Chirurgienne dentaire spécialisée en implantologie et extractions complexes.',
        'ordre': 3
    }
]

for dentiste_data in dentistes_data:
    Dentiste.objects.get_or_create(
        nom=dentiste_data['nom'],
        prenom=dentiste_data['prenom'],
        defaults=dentiste_data
    )

# Créer les horaires
horaires_data = [
    {'jour': 'lundi', 'ouverture_matin': '08:00', 'fermeture_matin': '12:00', 'ouverture_apres_midi': '14:00', 'fermeture_apres_midi': '18:00'},
    {'jour': 'mardi', 'ouverture_matin': '08:00', 'fermeture_matin': '12:00', 'ouverture_apres_midi': '14:00', 'fermeture_apres_midi': '18:00'},
    {'jour': 'mercredi', 'ouverture_matin': '08:00', 'fermeture_matin': '12:00', 'ouverture_apres_midi': '14:00', 'fermeture_apres_midi': '18:00'},
    {'jour': 'jeudi', 'ouverture_matin': '08:00', 'fermeture_matin': '12:00', 'ouverture_apres_midi': '14:00', 'fermeture_apres_midi': '18:00'},
    {'jour': 'vendredi', 'ouverture_matin': '08:00', 'fermeture_matin': '12:00', 'ouverture_apres_midi': '14:00', 'fermeture_apres_midi': '18:00'},
    {'jour': 'samedi', 'ouverture_matin': '08:00', 'fermeture_matin': '12:00', 'ferme': False},
    {'jour': 'dimanche', 'ferme': True}
]

for horaire_data in horaires_data:
    Horaire.objects.get_or_create(
        jour=horaire_data['jour'],
        defaults=horaire_data
    )

print("Base de données peuplée avec succès!")