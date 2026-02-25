from django.contrib import admin
from django.urls import path
from django.conf import settings
from google import genai
import os

# Функция проверки нейронки
def check_gemini_status():
    # Проверка RUN_MAIN нужна, чтобы код не запускался дважды из-за авто-перезагрузки Django
    if os.environ.get('RUN_MAIN') == 'true':
        print("\n" + "—" * 40)
        print("🔍 ПРОВЕРКА ПОДКЛЮЧЕНИЯ К GEMINI...")
        
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        
        if not api_key:
            print("❌ ОШИБКА: API_KEY не найден! Проверь файл .env")
            print("—" * 40 + "\n")
            return

        try:
            # Инициализируем клиент
            client = genai.Client(api_key=api_key)
            # Отправляем микро-запрос для проверки ключа и модели
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents="ping"
            )
            
            if response:
                print("✅ СТАТУС: Gemini 2.5 Flash на связи!")
                print(f"📡 API КЛЮЧ: {api_key[:8]}*** (скрыто)")
            
        except Exception as e:
            print(f"❌ ОШИБКА API: {e}")
            print("Совет: проверь интернет или валидность ключа.")
            
        print("—" * 40 + "\n")

# Запускаем проверку
check_gemini_status()

# Твои стандартные маршруты
urlpatterns = [
    path('admin/', admin.site.urls),
]