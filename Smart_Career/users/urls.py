from django.urls import path
from django.contrib.auth.views import LogoutView
from .views.auth_views import StandardLoginView
from .views.student_views import StudentSignUpView
from .views.employer_views import EmployerSignUpView

urlpatterns = [
    path('login/', StandardLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/auth/login/'), name='logout'),
    path('register/student/', StudentSignUpView.as_view(), name='register_student'),
    path('register/employer/', EmployerSignUpView.as_view(), name='register_employer'),
]