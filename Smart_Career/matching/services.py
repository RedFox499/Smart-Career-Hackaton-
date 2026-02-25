import os
import json
import PyPDF2
import docx
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_file(file):
    """Извлекает текст из PDF или DOCX."""
    ext = os.path.splitext(file.name)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        elif ext == '.docx':
            doc = docx.Document(file)
            text = " ".join([p.text for p in doc.paragraphs])
        else:
            text = file.read().decode('utf-8')
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
    return text

def get_skills(text):
    """Вытаскивает навыки через ИИ."""
    prompt = f"Извлеки из текста все ИТ-технологии и навыки. Верни СТРОГО JSON список строк. Текст: {text}"
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return set(json.loads(clean_json))
    except:
        return set()

def auto_match_vacancies(resume_text, vacancies_qs):
    """Ищет лучшие вакансии для данного текста резюме."""
    resume_skills = get_skills(resume_text)
    recommendations = []

    for vacancy in vacancies_qs:
        # Для каждой вакансии вытаскиваем навыки (в идеале их надо хранить в базе заранее)
        vacancy_skills = get_skills(vacancy.description)
        
        if not vacancy_skills: continue
        
        matched = resume_skills.intersection(vacancy_skills)
        score = int((len(matched) / len(vacancy_skills)) * 100)
        
        if score > 10: # Показываем только если есть хоть какое-то совпадение
            recommendations.append({
                'vacancy': vacancy,
                'score': score,
                'matched_skills': list(matched),
                'missing_skills': list(vacancy_skills.difference(resume_skills))
            })
    
    # Сортируем: самые подходящие вверху
    return sorted(recommendations, key=lambda x: x['score'], reverse=True)