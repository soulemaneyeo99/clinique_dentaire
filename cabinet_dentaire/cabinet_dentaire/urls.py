

from django.contrib import admin
from django.urls import path, include  # ✅ n'oublie pas include !

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rendezvous.urls')),  # ✅ ceci permet d'accéder aux urls de l'app
]