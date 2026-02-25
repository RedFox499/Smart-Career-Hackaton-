from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from career.models import Vacancy
from .services import extract_text_from_file, auto_match_vacancies

@login_required
def student_analysis_view(request):
    if request.user.role != 'STUDENT': # Поправь на свою проверку роли
        return redirect('profile')

    context = {}
    
    if request.method == 'POST':
        resume_file = request.FILES.get('resume_file')
        resume_text = request.POST.get('resume_text')

        # Если загружен файл — приоритет ему
        if resume_file:
            resume_text = extract_text_from_file(resume_file)
        
        if resume_text:
            active_vacancies = Vacancy.objects.filter(is_active=True)
            # Запускаем автоподбор
            recommendations = auto_match_vacancies(resume_text, active_vacancies)
            context['recommendations'] = recommendations
            context['analyzed'] = True
        else:
            context['error'] = "Загрузите файл или вставьте текст резюме."

    return render(request, 'matching/analyze.html', context)