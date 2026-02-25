from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Добавляем роли
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Студент'
        EMPLOYER = 'EMPLOYER', 'Работодатель'
        ADMIN = 'ADMIN', 'Администратор'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)