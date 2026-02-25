import os
import json
import re
import PyPDF2
import docx
import socket
from django.conf import settings
from google import genai
from sentence_transformers import SentenceTransformer, util
from generator.models import Candidate 

class SmartRecruiter:
    def __init__(self):
        # Локальная модель — твой фундамент, работает без интернета
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Инициализация Gemini
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.client = genai.Client(api_key=api_key) if api_key else None

    def extract_text(self, file):
        """Извлекает текст из файлов разных форматов."""
        ext = os.path.splitext(file.name)[1].lower()
        try:
            if ext == '.pdf':
                reader = PyPDF2.PdfReader(file)
                text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
            elif ext == '.docx':
                doc = docx.Document(file)
                text = " ".join([p.text for p in doc.paragraphs])
            elif ext == '.txt':
                text = file.read().decode('utf-8', errors='ignore')
            else:
                return ""
            return text.strip()
        except Exception as e:
            print(f"Ошибка при чтении файла {file.name}: {e}")
            return ""

    def is_internet_available(self):
        """Быстрая проверка соединения с серверами Google."""
        try:
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except socket.error:
            return False

    def process_vacancy(self, vacancy_text, use_gemini=False, top_n=3):
        """Основная логика матчинга: Локалка + опционально Gemini."""
        db_candidates = Candidate.objects.all()
        if not db_candidates.exists():
            return "EMPTY_DATABASE"

        # 1. Считаем семантическую близость локально
        vac_emb = self.model.encode(vacancy_text, convert_to_tensor=True)
        scored_candidates = []

        for cand in db_candidates:
            cand_emb = self.model.encode(cand.resume_text, convert_to_tensor=True)
            score = int(util.cos_sim(vac_emb, cand_emb).item() * 100)
            
            # Порог отсечения, чтобы не показывать мусор
            if score < 15:
                continue

            scored_candidates.append({
                "id": cand.id,
                "name": f"{cand.full_name} ({cand.position})",
                "text": cand.resume_text,
                "score": score,
                "pros": "<ul><li>Математическое соответствие стеку</li></ul>",
                "cons": "<ul><li>AI-анализ не проводился</li></ul>",
                "conclusion": f"Кандидат отобран локальной моделью (уверенность {score}%)."
            })

        # Сортируем по убыванию скора
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_candidates[:top_n]

        if not top_candidates:
            return "NO_MATCHES"

        # 2. Если включен Gemini и есть интернет — "прокачиваем" результаты
        if use_gemini and self.client:
            if not self.is_internet_available():
                print("Gemini пропущена: нет интернета.")
                return top_candidates

            candidates_info = ""
            for c in top_candidates:
                candidates_info += f"ID: {c['id']}\nОпыт: {c['text'][:500]}\n\n"

            prompt = f"""
            Проанализируй кандидатов для вакансии: {vacancy_text[:500]}
            
            Кандидаты:
            {candidates_info}
            
            Верни ответ строго в формате JSON массива:
            [
              {{
                "id": ID,
                "pros": "<ul><li>Плюс в HTML</li></ul>",
                "cons": "<ul><li>Минус в HTML</li></ul>",
                "conclusion": "Твой вердикт"
              }}
            ]
            """

            try:
                # Пробуем разные варианты имени модели для стабильности
                model_name = "models/gemini-1.5-flash"
                res = self.client.models.generate_content(model=model_name, contents=prompt)
                
                # Чистим JSON от Markdown-разметки
                clean_json = re.sub(r'```json|```', '', res.text).strip()
                ai_data = json.loads(clean_json)
                
                for c in top_candidates:
                    match = next((item for item in ai_data if str(item.get('id')) == str(c['id'])), None)
                    if match:
                        c.update({
                            "pros": match.get('pros', c['pros']),
                            "cons": match.get('cons', c['cons']),
                            "conclusion": match.get('conclusion', c['conclusion'])
                        })
                return top_candidates
            except Exception as e:
                print(f"Gemini Error: {e}")
                return top_candidates # Если ИИ упал, отдаем локальный результат

        return top_candidates

# Создаем один экземпляр для использования во вьюхах
matcher = SmartRecruiter()