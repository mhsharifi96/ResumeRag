import uuid
from django.db import models
from pgvector.django import VectorField


class CVEmbeddingChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="embedding_chunks")
    job = models.ForeignKey("jobs.JobPosition", on_delete=models.CASCADE, related_name="embedding_chunks")
    candidate_cv = models.ForeignKey("candidates.CandidateCV", on_delete=models.CASCADE, related_name="embedding_chunks")
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    embedding = VectorField(dimensions=1024)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["chunk_index"]
        indexes = [
            models.Index(fields=["job"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["candidate_cv"]),
        ]
        unique_together = ("candidate_cv", "chunk_index")
