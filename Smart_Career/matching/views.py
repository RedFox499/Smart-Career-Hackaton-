import json
import time
from django.shortcuts import render
from career.models import Vacancy
from .services import extract_text_from_file, get_top_n_candidates, get_gemini_verdict

def student_analysis_view(request):
    context = {}
    if request.method == 'POST':
        resume_text = ""
        
        # Обработка файла или текста
        if request.FILES.get('resume_file'):
            resume_text = extract_text_from_file(request.FILES['resume_file'])
        elif request.POST.get('resume_text'):
            resume_text = request.POST.get('resume_text')
        
        if resume_text:
            # Получаем все активные вакансии
            all_vacancies = list(Vacancy.objects.filter(is_active=True))
            
            # Фильтруем ТОП-3 через локальный ML (SBERT)
            top_candidates = get_top_n_candidates(resume_text, all_vacancies, top_x=3)
            
            final_recommendations = []
            for item in top_candidates:
                vac = item['vacancy']
                
                # Запрос к нейросети за подробным разбором
                ai_analysis = get_gemini_verdict(resume_text, vac.description)
                
                # Пауза для обхода лимитов Rate Limit
                time.sleep(1)
                
                # Если ИИ не ответил, используем балл от SBERT
                score = ai_analysis.get('score', 0)
                if score == 0:
                    score = int(item['sbert_score'] * 100)
                
                final_recommendations.append({
                    'vacancy': vac,
                    'score': score,
                    'reason': ai_analysis.get('reason'),
                    'roadmap_json': json.dumps(ai_analysis.get('roadmap', []))
                })
            
            # Сортировка итогового списка
            final_recommendations.sort(key=lambda x: x['score'], reverse=True)
            context.update({'recommendations': final_recommendations, 'analyzed': True})
            
    return render(request, 'matching/analyze.html', context)