from django.contrib import admin
from .models import AnalysisHistory


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    # Список полей, которые будут видны в таблице админки
    list_display = ('candidate_name', 'vacancy_title', 'market_fit_score', 'created_at')
    # Фильтры справа
    list_filter = ('created_at', 'market_fit_score')
    # Поиск по имени и вакансии
    search_fields = ('candidate_name', 'vacancy_title')