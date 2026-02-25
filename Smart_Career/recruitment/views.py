from django.shortcuts import render, redirect
from .services import matcher
from .models import AnalysisHistory  # ИСПРАВИЛИ ИМПОРТ
from career.models import Vacancy

def analyze_view(request):
    candidates = []
    error = None

    if request.method == "POST":
        # ЛОГИКА СОХРАНЕНИЯ (срабатывает при нажатии кнопки "Сохранить")
        if 'save_results' in request.POST:
            current_employer = request.user.employer_profile
            candidate_ids = request.POST.getlist('cand_ids')
            scores = request.POST.getlist('cand_scores')
            v_title = request.POST.get('vacancy_name', 'Анализ')
            v_text = request.POST.get('vacancy_text', 'Текст вакансии не указан')
            Vacancy.objects.create(
                    employer=current_employer,
                    title = v_title,
                    description = v_text,
                    salary_range = 0
                )
            for i in range(len(candidate_ids)):
                c_id = candidate_ids[i]
    
                # Создаем запись в твоей модели AnalysisHistory
                AnalysisHistory.objects.create(
                    employer=request.user, 
                    candidate_name=request.POST.get(f'name_{c_id}'),
                    vacancy_title=v_title,
                    requirements_text=v_text,
                    resume_text=request.POST.get(f'text_{c_id}', 'Текст резюме'),
                    analysis_report=request.POST.get(f'conclusion_{c_id}', 'Без отчета'),
                    market_fit_score=int(scores[i])
                )
            return redirect('/career/') # Уводим работодателя в личный кабинет

        # ЛОГИКА АНАЛИЗА (твоя основная часть)
        files = request.FILES.getlist('resumes')
        use_gemini = request.POST.get('use_gemini') == 'on'
        
        if files:
            vacancy_text = matcher.extract_text(files[0])
            results = matcher.process_vacancy(vacancy_text, use_gemini=use_gemini)
            if isinstance(results, list):
                for c in results:
                    c['status_color'] = "success" if c['score'] > 70 else "warning" if c['score'] > 40 else "danger"
                    candidates.append(c)
                # Передаем текст вакансии в контекст для скрытых полей
                return render(request, 'recruitment/analyze.html', {
                    'candidates': candidates, 
                    'vacancy_text': vacancy_text,
                    'vacancy_name': files[0].name
                })
            else:
                error = "База пуста или совпадений нет."
        else:
            error = "Файл не выбран!"

    return render(request, 'recruitment/analyze.html', {'candidates': candidates, 'error': error})