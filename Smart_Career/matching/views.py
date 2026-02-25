from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from career.models import Vacancy # Берем вакансии из приложения career
from .models import SkillMatchResult
from .services import calculate_match

@login_required
def student_analysis_view(request):
    # Защита: пускаем только студентов
    if request.user.role != User.Role.STUDENT:
        return redirect('employer_dashboard')

    # Достаем все активные вакансии для выпадающего списка
    vacancies = Vacancy.objects.filter(is_active=True)
    context = {'vacancies': vacancies}

    if request.method == 'POST':
        vacancy_id = request.POST.get('vacancy_id')
        resume_text = request.POST.get('resume_text')

        if not vacancy_id or not resume_text:
            context['error'] = "Выберите вакансию и вставьте текст резюме."
            return render(request, 'matching/analyze.html', context)

        vacancy = get_object_or_404(Vacancy, id=vacancy_id)

        # Вызываем наш ИИ-движок
        percentage, matched, missing, rec = calculate_match(
            resume_text=resume_text, 
            vacancy_text=vacancy.description
        )

        # Сохраняем слепок в базу (для "Кривой развития")
        result = SkillMatchResult.objects.create(
            student=request.user.student_profile,
            vacancy=vacancy,
            match_percentage=percentage,
            has_skills=matched,
            missing_skills=missing,
            ai_recommendation=rec
        )

        context['result'] = result

    return render(request, 'matching/analyze.html', context)