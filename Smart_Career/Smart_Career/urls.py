from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')), 
    path('career/', include('career.urls')),
    path('', include('career.urls')),
]