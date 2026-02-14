from django.contrib import admin
from .models import CVEmbeddingChunk


@admin.register(CVEmbeddingChunk)
class CVEmbeddingChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "candidate_cv", "job", "chunk_index", "created_at")
    list_filter = ("organization", "job")
