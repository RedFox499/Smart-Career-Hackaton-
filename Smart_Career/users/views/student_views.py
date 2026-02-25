from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView
from users.forms import StudentSignUpForm
from users.models import User

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'users/register_student.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')