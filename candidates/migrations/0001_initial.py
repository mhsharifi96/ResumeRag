from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("jobs", "0001_initial"),
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CandidateCV",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("file", models.FileField(upload_to="cvs/")),
                ("raw_text", models.TextField(blank=True)),
                ("language", models.CharField(blank=True, max_length=8)),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("READY", "Ready"), ("FAILED", "Failed")],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cvs",
                        to="jobs.jobposition",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cvs",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CVScore",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("score", models.PositiveSmallIntegerField(default=0)),
                ("pros", models.JSONField(default=list)),
                ("cons", models.JSONField(default=list)),
                ("language_detected", models.CharField(blank=True, max_length=8)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "candidate_cv",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="score",
                        to="candidates.candidatecv",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scores",
                        to="jobs.jobposition",
                    ),
                ),
            ],
            options={"ordering": ["-score", "-created_at"]},
        ),
    ]
