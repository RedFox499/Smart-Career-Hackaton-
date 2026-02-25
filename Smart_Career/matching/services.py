import os
import json
import re
import PyPDF2
import docx
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from career.utils import preprocess_text

# Инициализация моделей
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Модель SBERT для семантического поиска (поддерживает RU и EN)
sbert_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def extract_text_from_file(file):
    """Извлекает текст из PDF, DOCX или текстовых файлов."""
    ext = os.path.splitext(file.name)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext == '.docx':
            doc = docx.Document(file)
            text = " ".join([p.text for p in doc.paragraphs])
        else:
            text = file.read().decode('utf-8')
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    return text

def get_top_n_candidates(resume_text, vacancies_qs, top_x=3):
    """Этап 1: Семантическая фильтрация вакансий через SBERT."""
    if not vacancies_qs:
        return []

    clean_resume = preprocess_text(resume_text)
    # Используем заранее очищенные описания из БД для скорости
    clean_vacancies = [v.cleaned_description for v in vacancies_qs]
    
    resume_embedding = sbert_model.encode(clean_resume, convert_to_tensor=True)
    vacancy_embeddings = sbert_model.encode(clean_vacancies, convert_to_tensor=True)

    cosine_scores = util.cos_sim(resume_embedding, vacancy_embeddings)[0]

    scored_vacancies = []
    for i, score in enumerate(cosine_scores):
        scored_vacancies.append({
            'vacancy': vacancies_qs[i],
            'sbert_score': float(score),
        })

    # Сортируем по убыванию сходства
    scored_vacancies.sort(key=lambda x: x['sbert_score'], reverse=True)
    return scored_vacancies[:top_x]

def get_gemini_verdict(resume_text, vacancy_text):
    """Этап 2: Глубокий анализ соответствия и подбор учебных материалов."""
    prompt = f"""
    Твоя роль: Технический эксперт и ментор.
    Сравни резюме и вакансию. Для каждого недостающего навыка предложи: 1 статью, 1 видео и 1 курс.
    
    Верни строго JSON:
    {{
        "score": число_0_100,
        "reason": "краткое пояснение (2 предложения)",
        "roadmap": [
            {{"skill": "название", "article": "ссылка или название", "video": "ссылка или название", "course": "платформа и название"}}
        ]
    }}
    РЕЗЮМЕ: {resume_text}
    ВАКАНСИЯ: {vacancy_text}
    """
    try:
        response = gemini_model.generate_content(prompt)
        clean_json = re.sub(r'```json\s*|```', '', response.text).strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "score": 0, 
            "reason": "Анализ на основе семантического сходства SBERT (лимит ИИ).", 
            "roadmap": []
        }