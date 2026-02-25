from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import User, StudentProfile, EmployerProfile

class StudentSignUpForm(UserCreationForm):
    github_link = forms.URLField(required=False, label='Ссылка на GitHub')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.save()
        
        student_profile = user.student_profile
        student_profile.github_link = self.cleaned_data.get('github_link')
        student_profile.save()
        return user


class EmployerSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True, label='Название компании')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = User.Role.EMPLOYER
        user.save()
        
        employer_profile = user.employer_profile
        employer_profile.company_name = self.cleaned_data.get('company_name')
        employer_profile.save()
        return user