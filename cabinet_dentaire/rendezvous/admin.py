from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RendezVous

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'service', 'date', 'telephone', 'email', 'date_creation')
    list_filter = ('service', 'date')
    search_fields = ('nom', 'prenom', 'email', 'telephone')
from django.contrib import admin
from .models import Patient

admin.site.register(Patient)
