# ==========================================
# 8. ADMIN.PY
# ==========================================
from django.contrib import admin
from .models import Service, Dentiste, Horaire, RendezVous, Contact

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix_min', 'prix_max', 'duree_minutes', 'actif', 'ordre']
    list_filter = ['actif', 'created_at']
    search_fields = ['nom', 'description']
    ordering = ['ordre', 'nom']
    list_editable = ['ordre', 'actif']

@admin.register(Dentiste)
class DentisteAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'specialite', 'actif', 'ordre']
    list_filter = ['actif', 'created_at']
    search_fields = ['nom', 'prenom', 'specialite']
    ordering = ['ordre', 'nom']
    list_editable = ['ordre', 'actif']

@admin.register(Horaire)
class HoraireAdmin(admin.ModelAdmin):
    list_display = ['jour', 'ouverture_matin', 'fermeture_matin', 'ouverture_apres_midi', 'fermeture_apres_midi', 'ferme']
    ordering = ['id']

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'service', 'date_souhaitee', 'telephone', 'status', 'created_at']
    list_filter = ['status', 'service', 'date_souhaitee', 'created_at']
    search_fields = ['nom', 'prenom', 'telephone', 'email']
    ordering = ['-created_at']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations Patient', {
            'fields': ('nom', 'prenom', 'telephone', 'email')
        }),
        ('Détails du Rendez-vous', {
            'fields': ('service', 'date_souhaitee', 'message')
        }),
        ('Gestion', {
            'fields': ('status', 'notes_admin', 'date_confirmation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'email', 'sujet', 'lu', 'created_at']
    list_filter = ['lu', 'created_at']
    search_fields = ['nom', 'prenom', 'email', 'sujet']
    ordering = ['-created_at']
    list_editable = ['lu']
    readonly_fields = ['created_at', 'updated_at']
