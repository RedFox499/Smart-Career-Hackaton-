import os
import PyPDF2
import docx
from google import genai
from django.conf import settings
from sentence_transformers import SentenceTransformer, util
import requests
from bs4 import BeautifulSoup

class SmartMatcher:
    def __init__(self):
        # Загружаем легкую и быструю модель для процентов
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def extract_text(self, file):
        """Извлекает текст из PDF, DOCX или TXT"""
        ext = os.path.splitext(file.name)[1].lower()
        if ext == '.pdf':
            reader = PyPDF2.PdfReader(file)
            return " ".join([page.extract_text() for page in reader.pages])
        elif ext == '.docx':
            doc = docx.Document(file)
            return " ".join([p.text for p in doc.paragraphs])
        return file.read().decode('utf-8')

    def get_match_percentage(self, resume, reqs):
        emb1 = self.model.encode(resume, convert_to_tensor=True)
        emb2 = self.model.encode(reqs, convert_to_tensor=True)
        score = util.cos_sim(emb1, emb2).item()
        return max(0, int(score * 100))

    def get_ai_analysis(self, resume, reqs):
        prompt = f"""
        Сравни резюме и вакансию. 
        1. Выдай подробный список недостатков (почему не подходит).
        2. Оцени соответствие рынку Алматы на 2026 год.
        3. Дай вердикт работодателю.
        
        ВАКАНСИЯ: {reqs}
        РЕЗЮМЕ: {resume}
        Оформляй в чистом HTML (без Markdown).
        """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text
    
def fetch_hh_vacancy(url):
    """Парсит требования вакансии прямо с hh.kz"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем описание вакансии (на HH это обычно класс vacancy-description)
        description = soup.find('div', {'data-qa': 'vacancy-description'})
        return description.get_text(separator=' ') if description else "Не удалось найти описание."
    except Exception as e:
        return f"Ошибка при загрузке: {e}"

matcher = SmartMatcher()