# recruitment/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Замени views.employer_analysis_view на views.analyze_view
    path('analyze/', views.analyze_view, name='analyze'),
]