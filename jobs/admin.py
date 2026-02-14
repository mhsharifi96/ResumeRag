from django.contrib import admin
from .models import JobPosition


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organization", "created_at")
    search_fields = ("title", "requirements")
    list_filter = ("organization",)
