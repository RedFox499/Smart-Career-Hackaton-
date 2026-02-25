from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_db_view, name='generate_home'),
]