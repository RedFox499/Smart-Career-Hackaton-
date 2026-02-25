from django.db import models
from .utils import preprocess_text
from users.models import EmployerProfile


class Vacancy(models.Model):
    """
    Модель вакансии.
    """
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=255, verbose_name='Название должности')
    description = models.TextField(verbose_name='Описание и требования')
    salary_range = models.CharField(max_length=100, blank=True, verbose_name='Зарплата')

    # Флаг: активна вакансия или в архиве
    is_active = models.BooleanField(default=True)
    
    # Новое скрытое поле для ML-поиска
    cleaned_description = models.TextField(blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # Автоматическая очистка перед сохранением в БД
        self.cleaned_description = preprocess_text(self.description)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        
    def __str__(self):
        return f"{self.title} - {self.employer.company_name}"