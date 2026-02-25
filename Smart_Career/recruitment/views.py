from django.shortcuts import render
from .services import matcher
from generator.models import Candidate

def analyze_view(request):
    candidates = []
    error = None

    if request.method == "POST":
        # 1. Проверка: Выбрал ли пользователь файл вообще
        files = request.FILES.getlist('resumes')
        use_gemini = request.POST.get('use_gemini') == 'on'
        
        if not files:
            error = "Файл не выбран! Дядя, прикрепи документ для анализа."
        else:
            # 2. Проверка: Есть ли кто-то в базе кандидатов
            if not Candidate.objects.exists():
                error = "База кандидатов пуста! Сначала нагенерируй челиков в генераторе."
            else:
                vacancy_file = files[0]
                vacancy_text = matcher.extract_text(vacancy_file)
                
                # 3. Проверка: Удалось ли прочитать текст (не пустой ли файл)
                if not vacancy_text or len(vacancy_text.strip()) < 10:
                    error = "Не удалось прочитать текст. Файл пустой, поврежден или слишком короткий."
                else:
                    # Запускаем основной процесс
                    results = matcher.process_vacancy(vacancy_text, use_gemini=use_gemini)
                    
                    if results == "NO_MATCHES" or not results:
                        error = "🔍 Подходящих кандидатов не найдено. Попробуй другую вакансию или добавь новых людей."
                    else:
                        # Формируем список для вывода
                        for c in results:
                            score = int(c.get('score', 0))
                            # Твои цвета из HTML
                            c['status_color'] = "success" if score > 70 else "warning" if score > 40 else "danger"
                            candidates.append(c)

    return render(request, 'recruitment/analyze.html', {
        'candidates': candidates, 
        'error': error
    })