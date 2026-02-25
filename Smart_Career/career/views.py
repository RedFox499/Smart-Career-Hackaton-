from django.shortcuts import render
from django.http import JsonResponse
#from .services import ask_gemini
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from matching.models import SkillMatchResult

def index(request):
    return render(request, 'index.html')

@login_required # Используем декоратор вместо ручной проверки if
def profile(request):
    # Получаем историю анализов этого студента
    history = []
    if hasattr(request.user, 'student_profile'):
        history = SkillMatchResult.objects.filter(
            student=request.user.student_profile
        ).order_by('created_at')

    context = {
        'history': history,
    }
    return render(request, 'profile.html', context) # Лучше хранить внутри папки приложения

@login_required
def student_dashboard(request):
    return render(request, 'career/student_dashboard.html')

@login_required
def employer_dashboard(request):
    return render(request, 'career/employer_dashboard.html')