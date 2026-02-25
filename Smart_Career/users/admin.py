from django.contrib import admin
from .models import *
from  career.models import Vacancy

admin.site.register(StudentProfile)

class VacancyInline(admin.TabularInline): # TabularInline — это компактный вид таблицей
    model = Vacancy
    extra = 0  # Сколько пустых строк для новых вакансий показать сразу
    fields = ['title', 'description', 'salary_range'] # Какие поля вакансии показывать

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    # Добавляем вставку вакансий на страницу работодателя
    inlines = [VacancyInline]
# Register your models here.
