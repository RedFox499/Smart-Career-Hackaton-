import os
import json
import google.generativeai as genai
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

# Настраиваем Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_skills_json(text):
    prompt = f"""
    Проанализируй текст и выпиши ИТ-навыки.
    Верни ответ СТРОГО в формате JSON-массива строк.
    {text}
    """
    try:
        response = model.generate_content(prompt)
        # Очистка от markdown если он есть
        text_data = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text_data)
    except:
        return []

def calculate_match(resume_text, vacancy_text):
    candidate_skills = set(extract_skills_json(resume_text))
    required_skills = set(extract_skills_json(vacancy_text))
    
    if not required_skills:
        return 0, list(candidate_skills), [], "В вакансии не найдены навыки."
        
    matched = candidate_skills.intersection(required_skills)
    missing = required_skills.difference(candidate_skills)
    
    match_percentage = int((len(matched) / len(required_skills)) * 100)
    
    # Промпт для совета
    prompt = f"Студенту не хватает: {', '.join(missing)}. Дай план обучения из 2 предложений."
    recommendation = model.generate_content(prompt).text

    return match_percentage, list(matched), list(missing), recommendation