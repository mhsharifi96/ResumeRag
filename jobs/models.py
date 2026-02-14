import uuid
from django.conf import settings
from django.db import models


class JobPosition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    job_description = models.TextField(blank=True, default="")
    requirements = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_jobs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "title")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.organization.name} - {self.title}"
