import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.environ.get('GEMINI_API_KEY')


client = genai.Client(api_key=API_KEY) if API_KEY else None

API_KEY = os.environ.get('GEMINI_API_KEY', '')
client = genai.Client(api_key=API_KEY) if API_KEY else None

def _fallback_analysis():
    """Возвращается, если нет ключа или API упал"""
    return {
        "summary": "AI-анализ недоступен. Проверьте API-ключ.",
        "errors": ["Не удалось связаться с Gemini."],
        "missing_skills": ["Неизвестно"],
        "action_plan": []
    }

def analyze_resume_with_gemini(text: str) -> dict:
    if not client or not text.strip():
        return _fallback_analysis()


    prompt = f"""
    Ты — Senior IT-рекрутер и опытный Tech Lead. Твоя задача — провести жесткое, но конструктивное ревью резюме кандидата.
    
    Определи предполагаемую должность кандидата (например, Backend Developer, QA Engineer, Data Scientist) и проанализируй текст на основе требований к этой роли на уровне Middle/Senior.

    Проанализируй текст и верни результат СТРОГО в формате валидного JSON без Markdown-разметки:
    {{
        "summary": "Краткий вывод о профиле кандидата, его сильных сторонах и предполагаемой должности.",
        "errors": [
            "Список логических, структурных или стилистических ошибок в резюме (например: 'Опыт работы описан процессами, а не результатами', 'Не указан стек технологий в последнем проекте')"
        ],
        "missing_skills": [
            "Список хард-скиллов или технологий, которых не хватает для его должности"
        ],
        "action_plan": [
            {{
                "step": "Название шага (например: 'Изучить паттерны проектирования')",
                "description": "Краткая лекция/гайд, почему это важно и как это закрывает пробел в резюме.",
                "resource": "Конкретная книга, документация или тема для гугления"
            }}
        ]
    }}

    Резюме кандидата:
    {text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        # Очищаем ответ от возможных Markdown-тегов (```json ... ```)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        return json.loads(raw_text.strip())
        
    except Exception as e:
        print(f"Ошибка Gemini API: {e}")
        return _fallback_analysis()