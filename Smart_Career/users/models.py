from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Кастомная базовая модель пользователя с жесткой типизацией ролей."""
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Студент'
        EMPLOYER = 'EMPLOYER', 'Работодатель'
        ADMIN = 'ADMIN', 'Администратор'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STUDENT,
        verbose_name='Роль'
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    """Специфичные данные для студента."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    bio = models.TextField(blank=True, verbose_name='Общий опыт')
    github_link = models.URLField(blank=True, max_length=255)
    raw_resume_text = models.TextField(blank=True, verbose_name='Сырой текст резюме')
    market_readiness_score = models.IntegerField(default=0, help_text='Скор готовности (от ИИ)')
    
    def __str__(self):
        return f"Студент: {self.user.username}"


class EmployerProfile(models.Model):
    """Специфичные данные для HR/Работодателя."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255, verbose_name='Название компании')
    website = models.URLField(blank=True, max_length=255)

    def __str__(self):
        return f"Компания: {self.company_name}"


# --- SIGNALS ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Гарантирует существование профиля при создании User."""
    if created:
        if instance.role == User.Role.STUDENT:
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == User.Role.EMPLOYER:
            EmployerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == User.Role.STUDENT and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == User.Role.EMPLOYER and hasattr(instance, 'employer_profile'):
        instance.employer_profile.save()
