import uuid
from django.db import models


class CandidateCV(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="cvs")
    job = models.ForeignKey("jobs.JobPosition", on_delete=models.CASCADE, related_name="cvs")
    file = models.FileField(upload_to="cvs/")
    raw_text = models.TextField(blank=True)
    language = models.CharField(max_length=8, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class CVScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate_cv = models.OneToOneField(CandidateCV, on_delete=models.CASCADE, related_name="score")
    job = models.ForeignKey("jobs.JobPosition", on_delete=models.CASCADE, related_name="scores")
    score = models.PositiveSmallIntegerField(default=0)
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)
    language_detected = models.CharField(max_length=8, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score", "-created_at"]
