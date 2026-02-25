from django.urls import path
from . import views

urlpatterns = [
    # Возвращаем простой путь без всяких ID
    path('analyze/', views.analyze_view, name='analyze'),
]