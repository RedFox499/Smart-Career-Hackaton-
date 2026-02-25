from django.db import models
from django.conf import settings

class AnalysisHistory(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=100)
    vacancy_title = models.CharField(max_length=100)
    requirements_text = models.TextField()
    resume_text = models.TextField()
    analysis_report = models.TextField() # Ответ от Gemini
    market_fit_score = models.IntegerField(default=0) # Соответствие рынку 0-100
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.vacancy_title}"