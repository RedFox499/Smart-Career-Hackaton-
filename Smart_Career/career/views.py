from django.shortcuts import render
from django.http import JsonResponse
#from .services import ask_gemini
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'index.html')

def profile(request):
    return render(request, 'profile.html')

@login_required
def student_dashboard(request):
    return render(request, 'career/student_dashboard.html')

@login_required
def employer_dashboard(request):
    return render(request, 'career/employer_dashboard.html')