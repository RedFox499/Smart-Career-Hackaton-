import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Career.settings')
django.setup()

from career.models import Vacancy
from users.models import User, EmployerProfile

def seed():
    # 1. Находим или создаем тестового работодателя
    user, _ = User.objects.get_or_create(
        username='tech_boss', 
        defaults={'email': 'boss@tech.kz', 'role': 'EMPLOYER'}
    )
    if _: user.set_password('hackathon2026'); user.save()
    
    employer, _ = EmployerProfile.objects.get_or_create(user=user, defaults={'company_name': 'Tech Giants KZ'})

    # 2. Список вакансий для загрузки
    vacancies_data = [
        {
            'title': 'Middle Python Developer (Backend)',
            'description': 'Требования: Python 3.12, Django, DRF, PostgreSQL, Docker, Redis, Git.'
        },
        {
            'title': 'Junior+ Data Scientist',
            'description': 'Нужно знание pandas, NumPy и опыт работы с Big Data Analysis.'
        },
        {
            'title': 'Android Developer (Kotlin)',
            'description': 'Стек: Kotlin, Android SDK, MVVM, Retrofit 2, Jetpack Compose. Интерес к Flutter приветствуется.'
        }
    ]

    for data in vacancies_data:
        v, created = Vacancy.objects.get_or_create(
            employer=employer,
            title=data['title'],
            defaults={'description': data['description'], 'is_active': True}
        )
        print(f"Вакансия '{v.title}' {'создана' if created else 'уже есть'}")

if __name__ == '__main__':
    seed()