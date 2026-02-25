import re

NOISE_PHRASES = [
    r'дружный коллектив', r'печеньки', r'кофе', r'офис в центре',
    r'оформление по тк', r'белая зарплата', r'гибкий график',
    r'коммуникабельность', r'ответственность', r'стрессоустойчивость'
]

def preprocess_text(text):
    """Очищает текст от мусора, оставляя суть для SBERT."""
    if not text:
        return ""
    text = text.lower()
    for phrase in NOISE_PHRASES:
        text = re.sub(phrase, '', text)
    text = re.sub(r'[^\w\s\+\#\.]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()