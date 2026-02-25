from django.urls import path
from .views import *
from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),
    path('', index, name='index'), 
    path('profile/', profile, name='profile'),
]