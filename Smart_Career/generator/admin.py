from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    # Убери created_at из этого списка
    list_display = ('full_name', 'position')