import os, json, re, PyPDF2, docx, socket
from django.conf import settings
from google import genai
from sentence_transformers import SentenceTransformer, util
from users.models import StudentProfile # Теперь работаем с профилями студентов

class SmartRecruiter:
    def __init__(self):
        # Инициализация локальной модели SBERT
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Инициализация клиента Gemini
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.client = genai.Client(api_key=api_key) if api_key else None

    def extract_text(self, file):
        """Извлекает текст из вакансии (PDF, DOCX, TXT)."""
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
        """Проверка наличия сети для работы с Gemini."""
        try:
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except socket.error:
            return False

    def process_vacancy(self, vacancy_text, use_gemini=False, top_n=5):
        """
        Основной метод анализа. 
        Ищет совпадения между текстом вакансии и StudentProfile.
        """
        # 1. Берем только тех студентов, у которых заполнено резюме
        profiles = StudentProfile.objects.exclude(raw_resume_text="")
        
        if not profiles.exists():
            return "EMPTY_DATABASE"

        # Кодируем текст вакансии локально
        vac_emb = self.model.encode(vacancy_text, convert_to_tensor=True)
        scored_students = []

        # 2. Локальный семантический поиск по всем профилям
        for profile in profiles:
            resume_emb = self.model.encode(profile.raw_resume_text, convert_to_tensor=True)
            sim_score = int(util.cos_sim(vac_emb, resume_emb).item() * 100)
            
            # Отсекаем совсем нерелевантных
            if sim_score < 15:
                continue

            scored_students.append({
                "id": profile.user.id,
                "name": profile.user.get_full_name() or profile.user.username,
                "text": profile.raw_resume_text,
                "score": sim_score,
                "pros": "<ul><li>Семантическое соответствие профилю</li></ul>",
                "cons": "<ul><li>Требуется детальное ревью</li></ul>",
                "conclusion": f"Профиль студента соответствует вакансии на {sim_score}%."
            })
            
        # Сортируем и берем ТОП
        scored_students.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_students[:top_n]
        
        if not top_candidates:
            return "NO_MATCHES"

        # 3. Углубленный анализ через Gemini (если включено и есть сеть)
        if use_gemini and self.client:
            if not self.is_internet_available():
                print("--- Сеть недоступна, возврат локальных результатов ---")
                return top_candidates

            # Формируем данные для Промпта
            candidates_info = ""
            for c in top_candidates:
                candidates_info += f"ID: {c['id']}\nРезюме: {c['text'][:1000]}\n\n"

            prompt = f"""
            Проанализируй соответствие студентов вакансии.
            Вакансия: {vacancy_text[:1000]}
            
            Студенты:
            {candidates_info}
            
            Верни ответ строго в формате JSON массива объектов с полями: 
            id, pros (HTML список li), cons (HTML список li), conclusion.
            """

            try:
                res = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                clean_json = re.sub(r'```json|```', '', res.text).strip()
                ai_results = json.loads(clean_json)
                
                # Обновляем локальные данные ответами от ИИ
                for c in top_candidates:
                    ai_data = next((item for item in ai_results if str(item.get('id')) == str(c['id'])), None)
                    if ai_data:
                        c.update({
                            "pros": ai_data.get('pros', c['pros']),
                            "cons": ai_data.get('cons', c['cons']),
                            "conclusion": ai_data.get('conclusion', c['conclusion'])
                        })
                return top_candidates
            except Exception as e:
                print(f"--- Ошибка Gemini: {e} ---")
                return top_candidates

        return top_candidates

# Создаем экземпляр для использования во вьюхах
matcher = SmartRecruiter()