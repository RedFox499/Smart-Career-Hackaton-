from django.shortcuts import render
from .services import matcher, fetch_hh_vacancy # Добавь импорт нашей новой функции

def analyze_view(request):
    context = {}
    if request.method == "POST":
        vacancy_input = request.POST.get('vacancy')
        resume_text = request.POST.get('resume_text')
        resume_file = request.FILES.get('resume_file')

        # 1. Проверяем, не ссылка ли это на HH.kz
        if "hh.kz" in vacancy_input:
            vacancy_text = fetch_hh_vacancy(vacancy_input)
        else:
            vacancy_text = vacancy_input

        # 2. Обрабатываем файл резюме, если он есть
        if resume_file:
            resume_text = matcher.extract_text(resume_file)

        # 3. Считаем проценты и делаем ИИ-анализ
        percentage = matcher.get_match_percentage(resume_text, vacancy_text)
        report = matcher.get_ai_analysis(resume_text, vacancy_text)

        context = {
            'percentage': percentage,
            'report': report,
            'vacancy_used': vacancy_text[:200] + "..." # Для отладки
        }
    
    return render(request, 'recruitment/analyze.html', context)