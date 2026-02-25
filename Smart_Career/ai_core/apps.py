import os
from django.apps import AppConfig
from django.conf import settings

class AiCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'

    def ready(self):
        # RUN_MAIN проверяет, что это основной процесс, а не релоадер
        if os.environ.get('RUN_MAIN') == 'true':
            self.check_gemini_connection()

    def check_gemini_connection(self):
        from google import genai
        print("\n" + "="*30)
        print("🤖 ПРОВЕРКА GEMINI 2.5 FLASH...")
        
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        
        if not api_key:
            print("❌ ОШИБКА: API ключ не найден в settings.py!")
            return

        try:
            client = genai.Client(api_key=api_key)
            # Короткий тестовый запрос
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="test"
            )
            if response.text:
                print("✅ СВЯЗЬ УСТАНОВЛЕНА! Нейронка готова к работе.")
        except Exception as e:
            print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
        
        print("="*30 + "\n")