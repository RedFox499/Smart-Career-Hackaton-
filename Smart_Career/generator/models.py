from django.db import models
from django.conf import settings # Чтобы подтянуть твою кастомную модель User

class Candidate(models.Model):
    # Привязываем кандидата к пользователю
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='candidate_data'
    )
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    resume_text = models.TextField()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Кандидат"
        verbose_name_plural = "Кандидаты"