import random
from django.shortcuts import render
from .models import Candidate

FIRST_NAMES = ["Азамат", "Илья", "Санжар", "Динара", "Елена", "Тимур", "Алишер", "Мадина", "Данияр", "Айгерим"]
LAST_NAMES = ["Ахметов", "Иванов", "Нурланов", "Смагулова", "Ким", "Оспанов", "Цой", "Касымов", "Попова"]
UNIVERSITIES = ["МУИТ", "СДУ", "КазНУ", "КБТУ", "АУЭС", "Самоучка", "Яндекс.Практикум"]

def generate_db_view(request):
    message = None
    
    if request.method == "POST":
        topic = request.POST.get('topic', 'Разработчик')
        count = int(request.POST.get('count', 5))
        
        created_count = 0
        for _ in range(count):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            exp_years = random.randint(1, 7)
            
            topic_lower = topic.lower()
            if "android" in topic_lower or "kotlin" in topic_lower:
                skills_pool = ["Kotlin", "Java", "Android SDK", "MVVM", "Coroutines", "Room", "Retrofit", "Compose"]
            elif "go" in topic_lower or "backend" in topic_lower:
                skills_pool = ["Go", "Golang", "PostgreSQL", "Docker", "Kubernetes", "Redis", "Kafka"]
            elif "python" in topic_lower or "data" in topic_lower:
                skills_pool = ["Python", "Pandas", "NumPy", "Django", "FastAPI", "Machine Learning", "SQL"]
            else:
                skills_pool = ["Git", "Agile", "SQL", "REST API", "Linux"]
            
            skills = random.sample(skills_pool, min(len(skills_pool), random.randint(3, 5)))
            
            resume_text = f"Опыт работы: {exp_years} лет. Специализация: {topic}.\n"
            resume_text += f"Образование: {random.choice(UNIVERSITIES)}.\n"
            resume_text += f"Ключевые навыки: {', '.join(skills)}.\n"
            resume_text += "Готов к сложным задачам."
            
            # Сохраняем в БД генератора
            Candidate.objects.create(
                full_name=name,
                position=topic,
                resume_text=resume_text
            )
            created_count += 1
            
        message = f"✅ Готово! В базу залетело {created_count} новых резюме по профилю «{topic}»."

    total_in_db = Candidate.objects.count()
    return render(request, 'generator/generate.html', {'message': message, 'total_in_db': total_in_db})