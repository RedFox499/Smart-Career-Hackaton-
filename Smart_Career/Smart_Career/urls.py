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
    # Вот этот маршрут создаст путь http://127.0.0.1:8000/auth/...
    path('arr/', include('recruitment.urls')),
    
    # Вакансии ищутся по навыкам
    path('match/', include('matching.urls')),
]