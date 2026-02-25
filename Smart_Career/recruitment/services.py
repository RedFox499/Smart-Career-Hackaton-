import os, json, re, PyPDF2, docx, socket
from django.conf import settings
from google import genai
from sentence_transformers import SentenceTransformer, util
from generator.models import Candidate 

class SmartRecruiter:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
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

    def is_internet_available(self):
        # Быстрая проверка: доступен ли сервер Google вообще
        try:
            socket.setdefaulttimeout(2) # Ждем максимум 2 секунды
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except socket.error:
            return False

    def process_vacancy(self, vacancy_text, use_gemini=False, top_n=3):
        db_candidates = Candidate.objects.all()
        if not db_candidates: return "EMPTY_DATABASE"

        # 1. Локальный скоринг (всегда работает быстро)
        vac_emb = self.model.encode(vacancy_text, convert_to_tensor=True)
        scored_candidates = []
        for cand in db_candidates:
            cand_emb = self.model.encode(cand.resume_text, convert_to_tensor=True)
            sim_score = int(util.cos_sim(vac_emb, cand_emb).item() * 100)
            if sim_score < 15: continue
            scored_candidates.append({
                "id": cand.id, "name": f"{cand.full_name} ({cand.position})",
                "text": cand.resume_text, "score": sim_score,
                "pros": "<ul><li>Математический подбор</li></ul>",
                "cons": "<ul><li>AI-анализ не запущен</li></ul>",
                "conclusion": f"Кандидат отобран локально ({sim_score}%)."
            })
            
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_candidates[:top_n]
        if not top_candidates: return "NO_MATCHES"

        # 2. Попытка вызвать Gemini
        if use_gemini and self.client:
            # Сначала проверяем, есть ли интернет вообще
            if not self.is_internet_available():
                print("--- Интернет недоступен, пропускаем Gemini ---")
                return top_candidates

            candidates_info = ""
            for c in top_candidates:
                candidates_info += f"ID: {c['id']}\nОпыт: {c['text']}\n\n"

            prompt = f"Вакансия: {vacancy_text[:500]}\nКандидаты:\n{candidates_info}\nВерни JSON массив (id, pros, cons, conclusion)."

            try:
                # Используем флэш модель с ограничением времени
                res = self.client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                clean_json = re.sub(r'```json|```', '', res.text).strip()
                ai_results = json.loads(clean_json)
                
                for c in top_candidates:
                    ai_data = next((item for item in ai_results if str(item.get('id')) == str(c['id'])), None)
                    if ai_data: c.update(ai_data)
                return top_candidates
            except Exception as e:
                print(f"--- Ошибка Gemini (таймаут или сеть): {e} ---")
                return top_candidates

        return top_candidates

matcher = SmartRecruiter()