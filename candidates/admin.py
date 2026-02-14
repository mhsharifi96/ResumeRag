from django.contrib import admin
from .models import CandidateCV, CVScore


@admin.register(CandidateCV)
class CandidateCVAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "organization", "status", "created_at")
    list_filter = ("organization", "status")


@admin.register(CVScore)
class CVScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "candidate_cv", "job", "score", "language_detected")
    list_filter = ("job",)
