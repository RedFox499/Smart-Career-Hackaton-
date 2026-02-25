from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView
from ..forms import EmployerSignUpForm
from ..models import User

class EmployerSignUpView(CreateView):
    model = User
    form_class = EmployerSignUpForm
    template_name = 'users/register_employer.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')