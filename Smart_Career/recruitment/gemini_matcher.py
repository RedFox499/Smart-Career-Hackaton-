import os
import json
import re
import PyPDF2
import docx
from django.conf import settings
from google import genai
from sentence_transformers import SentenceTransformer, util
from generator.models import Candidate 

class SmartRecruiter:
    def __init__(self):
        # Локальная модель для быстрого расчета (бесплатно)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Инициализация клиента Gemini
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.client = genai.Client(api_key=api_key) if api_key else None

    def extract_text(self, file):
        ext = os.path.splitext(file.name)[1].lower()
        try:
            if ext == '.pdf':
                reader = PyPDF2.PdfReader(file)
                return " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
            elif ext == '.docx':
                doc = docx.Document(file)
                return " ".join([p.text for p in doc.paragraphs])
            elif ext == '.txt':
                return file.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Ошибка чтения: {e}")
        return ""

    def process_vacancy(self, vacancy_text, use_gemini=False, top_n=3):
        db_candidates = Candidate.objects.all()
        if not db_candidates:
            return "EMPTY_DATABASE"

        print(f"Сравниваем вакансию с {db_candidates.count()} кандидатами...")
        vac_emb = self.model.encode(vacancy_text, convert_to_tensor=True)
        
        scored_candidates = []
        for cand in db_candidates:
            cand_emb = self.model.encode(cand.resume_text, convert_to_tensor=True)
            sim_score = int(util.cos_sim(vac_emb, cand_emb).item() * 100)
            
            # Порог отсечения, чтобы не показывать совсем левых людей
            if sim_score < 15:
                continue

            scored_candidates.append({
                "id": cand.id,
                "name": f"{cand.full_name} ({cand.position})",
                "text": cand.resume_text,
                "score": sim_score,
                "pros": "<ul><li>Математический подбор</li></ul>",
                "cons": "<ul><li>AI-анализ не запущен</li></ul>",
                "conclusion": f"Кандидат отобран локально (сходство {sim_score}%)."
            })
            
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_candidates[:top_n]

        if not top_candidates:
            return "NO_MATCHES"

        # Если юзер нажал галочку ИИ и у нас есть клиент
        if use_gemini and self.client:
            candidates_info = ""
            for c in top_candidates:
                candidates_info += f"ID: {c['id']}\nИмя: {c['name']}\nОпыт: {c['text']}\n\n"

            prompt = f"""
            Ты HR-директор. Проанализируй кандидатов для вакансии.
            ВАКАНСИЯ: {vacancy_text[:1000]}
            КАНДИДАТЫ:
            {candidates_info}
            
            Верни JSON-массив (без Markdown):
            [
              {{
                "id": ID,
                "pros": "<ul><li>Плюсы</li></ul>",
                "cons": "<ul><li>Минусы</li></ul>",
                "conclusion": "Вердикт"
              }}
            ]
            """

            try:
                # Используем flash-1.5, она стабильнее для бесплатных ключей
                res = self.client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                clean_json = re.sub(r'```json|```', '', res.text).strip()
                ai_results = json.loads(clean_json)
                
                for c in top_candidates:
                    ai_data = next((item for item in ai_results if str(item.get('id')) == str(c['id'])), None)
                    if ai_data:
                        c.update(ai_data)
                    else:
                        c.update({"pros": "Нет данных", "cons": "Нет данных", "conclusion": "Ошибка ИИ"})
                return top_candidates
            except Exception as e:
                print(f"Ошибка API: {e}")
                # Если Gemini сбоит (403/404), просто возвращаем локальный расчет
                for c in top_candidates:
                    c.update({"pros": "<ul><li>Лимит API Google</li></ul>", "cons": "<ul><li>Нужен новый ключ</li></ul>"})
                return top_candidates

        return top_candidates

matcher = SmartRecruiter()