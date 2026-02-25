from django.db import models
from users.models import StudentProfile
from career.models import Vacancy # Предполагаем, что вакансии у нас лежат в career

class SkillMatchResult(models.Model):
    """
    Результат анализа. Хранит исторические данные, чтобы строить кривую развития.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='match_history')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='match_results')
    
    # Математически точный процент
    match_percentage = models.IntegerField(verbose_name='Процент совпадения')
    
    # JSON списки для графиков (какие навыки есть, каких нет)
    has_skills = models.JSONField(verbose_name='Совпавшие навыки', default=list)
    missing_skills = models.JSONField(verbose_name='Недостающие навыки', default=list)
    
    # Совет ИИ (Gap-анализ)
    ai_recommendation = models.TextField(blank=True, verbose_name='План развития')
    
    # Дата нужна для оси X на "Кривой развития"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # От новых к старым

    def __str__(self):
        return f"{self.student.user.username} -> {self.vacancy.title} ({self.match_percentage}%)"