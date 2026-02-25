import re
from sentence_transformers import SentenceTransformer, util
from generator.models import Candidate

class LocalMatcher:  # <-- ПРОВЕРЬ, ЧТО ИМЯ ТАКОЕ ЖЕ
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_matches(self, vacancy_text, top_n=3):
        candidates = Candidate.objects.all()
        if not candidates.exists(): 
            return "EMPTY"

        vac_emb = self.model.encode(vacancy_text, convert_to_tensor=True)
        results = []
        
        # Стек для поиска совпадений
        tech_stack = ['Python', 'Go', 'Kotlin', 'Android', 'Docker', 'SQL', 'Git', 'Kafka', 'PostgreSQL']

        for cand in candidates:
            cand_emb = self.model.encode(cand.resume_text, convert_to_tensor=True)
            score = int(util.cos_sim(vac_emb, cand_emb).item() * 100)
            
            if score < 15: 
                continue

            found = [t for t in tech_stack if t.lower() in cand.resume_text.lower() and t.lower() in vacancy_text.lower()]
            
            results.append({
                "id": cand.id,
                "name": f"{cand.full_name} ({cand.position})",
                "score": score,
                "text": cand.resume_text,
                "pros": "<ul>" + "".join([f"<li>Стек: <b>{s}</b></li>" for s in found]) + "<li>Локальный ML-скоринг</li></ul>",
                "cons": "<ul><li>AI-анализ не проводился</li></ul>",
                "conclusion": f"Локальный поиск (сходство {score}%)."
            })
        
        if not results: 
            return "NONE"
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]