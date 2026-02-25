from django.db import models
from .utils import preprocess_text

class Vacancy(models.Model):
    # Твои существующие поля...
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Новое скрытое поле для ML-поиска
    cleaned_description = models.TextField(blank=True, editable=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Автоматическая очистка перед сохранением в БД
        self.cleaned_description = preprocess_text(self.description)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title