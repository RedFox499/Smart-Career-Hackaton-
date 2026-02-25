from django.urls import path
from .views import auth_views, employer_views, student_views

urlpatterns = [

    path('', auth_views.MyLoginView.as_view(), name='login'),
]