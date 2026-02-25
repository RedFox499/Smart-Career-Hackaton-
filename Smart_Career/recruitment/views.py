from django.shortcuts import render
from .services import matcher

def analyze_view(request):
    candidates = []
    error = None
    if request.method == "POST":
        files = request.FILES.getlist('resumes')
        # Получаем значение чекбокса
        use_gemini = request.POST.get('use_gemini') == 'on'
        
        if not files:
            error = "Файл не выбран!"
        else:
            vacancy_text = matcher.extract_text(files[0])
            # Передаем выбор во флаг
            results = matcher.process_vacancy(vacancy_text, use_gemini=use_gemini)
            
            if results == "EMPTY_DATABASE": error = "База пуста!"
            elif results == "NO_MATCHES": error = "Совпадений нет!"
            else:
                for c in results:
                    c['status_color'] = "success" if c['score'] > 70 else "warning" if c['score'] > 40 else "danger"
                    candidates.append(c)
                    
    return render(request, 'recruitment/analyze.html', {'candidates': candidates, 'error': error})