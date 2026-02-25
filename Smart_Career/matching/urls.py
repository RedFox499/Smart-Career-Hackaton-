from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.student_analysis_view, name='analyze_resume'),
]