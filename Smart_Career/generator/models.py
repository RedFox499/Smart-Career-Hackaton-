from django.db import models

class Candidate(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    position = models.CharField(max_length=150, verbose_name="Должность")
    resume_text = models.TextField(verbose_name="Текст резюме")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Кандидат"
        verbose_name_plural = "Кандидаты"