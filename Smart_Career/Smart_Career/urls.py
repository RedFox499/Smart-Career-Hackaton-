from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')), 
    path('career/', include('career.urls')),
    path('', include('career.urls')),
    path('admin/', admin.site.urls),
    path('arr/', include('recruitment.urls')),
    path('match/', include('matching.urls')),
    path('gen/', include('generator.urls')), # Не забудь про генератор!
]