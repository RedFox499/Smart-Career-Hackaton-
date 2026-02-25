from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('career.urls')),

    path('auth/', include('users.urls')),
 
 
]