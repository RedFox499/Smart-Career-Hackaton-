from django.core.management.base import BaseCommand
from myapp.services import ask_gemini  # Замени myapp на имя своего приложения
import time

class Command(BaseCommand):
    help = 'Проверка подключения к Gemini API'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Запуск теста Gemini 2.5 Flash ---'))
        
        test_prompt = "Привет! Если ты меня слышишь, ответь: 'Связь установлена!'"
        
        try:
            start_time = time.time()
            
            # Вызываем твою функцию
            response = ask_gemini(test_prompt)
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)

            self.stdout.write(self.style.NOTICE(f"Ответ от нейронки: {response}"))
            self.stdout.write(self.style.SUCCESS(f"✅ Тест пройден успешно за {duration} сек."))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка при обращении к API: {e}"))
            self.stdout.write(self.style.WARNING("Проверь: лимиты ключа, файл .env и наличие интернета."))