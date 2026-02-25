from django.shortcuts import render
from django.http import JsonResponse
#from .services import ask_gemini
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import redirect, get_object_or_404
from matching.models import SkillMatchResult
from django.conf import settings
import os
from .models import Vacancy
from users.models import EmployerProfile
from .models import Verdict
from .gemini import analyze_resume_with_gemini
import docx
import json

def index(request):
    return render(request, 'index.html')

@login_required 
def profile(request):
    last_id = request.GET.get('last_analysis')
    history = []
    if hasattr(request.user, 'student_profile'):
        history = SkillMatchResult.objects.filter(
            student=request.user.student_profile
        ).order_by('created_at')

    context = {
        'history': history,
        'verdicts': Verdict.objects.filter(user=request.user).order_by('-created_at'),
    }
    if last_id:
        # Находим конкретный результат, который только что создали
        context['ai'] = Verdict.objects.filter(id=last_id, user=request.user).first()
    return render(request, 'profile.html', context) 

@login_required
def student_dashboard(request):
    return render(request, 'career/student_dashboard.html')

@login_required
def employer_dashboard(request):
    return render(request, 'career/employer_dashboard.html')

def extract_text_from_memory(file_obj):
    if file_obj.name.endswith('.docx'):
        doc = docx.Document(file_obj)
        return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    return file_obj.read().decode('utf-8', errors='ignore')


 # Добавь импорт в начало файла

@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        text = extract_text_from_memory(file_obj)
        ai_result = analyze_resume_with_gemini(text)
        
        # Если Gemini вернул строку, а не словарь, попробуй распарсить или обернуть
        # Для простоты считаем, что ai_result — это словарь
        
        # Сохраняем вердикт в базу
        verdict = Verdict.objects.create(
            user=request.user,
            filename=file_obj.name,
            ai_data=ai_result # Здесь должен быть JSON или словарь
        )
        
        # Редиректим обратно в профиль и передаем ID нового вердикта в параметрах
        return redirect(f'/profile/?last_analysis={verdict.id}')
    
    return redirect('profile') # Если кто-то просто зашел на /upload/

@login_required
def profile_view(request):
    # Получаем все прошлые вердикты пользователя
    verdicts = Verdict.objects.filter(user=request.user).order_by('-created_at')
    
    # Проверяем, пришел ли пользователь после новой загрузки
    last_id = request.GET.get('last_analysis')
    last_verdict = None
    if last_id:
        last_verdict = Verdict.objects.filter(id=last_id, user=request.user).first()

    return render(request, 'profile.html', {
        'verdicts': verdicts,
        'last_verdict': last_verdict # Это наш свежий результат
    })

@login_required
def verdict_detail(request, pk):
    # Достаем вердикт из базы (только если он принадлежит текущему юзеру)
    verdict = get_object_or_404(Verdict, pk=pk, user=request.user)
    
    # Передаем в шаблон объект verdict и отдельно распаковываем ai_data как ai
    return render(request, 'analyzer/verdict_detail.html', {
        'verdict': verdict,
        'ai': verdict.ai_data 
    })

@login_required
def verdict_list(request):
    # Получаем все вердикты пользователя, отсортированные по дате (новые сверху)
    verdicts = Verdict.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'analyzer/verdict_list.html', {'verdicts': verdicts})
