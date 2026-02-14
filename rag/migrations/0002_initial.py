from django.db import migrations, models
import django.db.models.deletion
import pgvector.django
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("candidates", "0001_initial"),
        ("jobs", "0001_initial"),
        ("organizations", "0001_initial"),
        ("rag", "0001_enable_pgvector"),
    ]

    operations = [
        migrations.CreateModel(
            name="CVEmbeddingChunk",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("chunk_index", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("metadata", models.JSONField(default=dict)),
                ("embedding", pgvector.django.VectorField(dimensions=1024)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "candidate_cv",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="embedding_chunks",
                        to="candidates.candidatecv",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="embedding_chunks",
                        to="jobs.jobposition",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="embedding_chunks",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "ordering": ["chunk_index"],
                "unique_together": {("candidate_cv", "chunk_index")},
            },
        ),
        migrations.AddIndex(
            model_name="cvembeddingchunk",
            index=models.Index(fields=["job"], name="rag_cvembed_job_id_2ec5da_idx"),
        ),
        migrations.AddIndex(
            model_name="cvembeddingchunk",
            index=models.Index(fields=["organization"], name="rag_cvembed_organiz_327890_idx"),
        ),
        migrations.AddIndex(
            model_name="cvembeddingchunk",
            index=models.Index(fields=["candidate_cv"], name="rag_cvembed_candida_a2c4e4_idx"),
        ),
    ]
