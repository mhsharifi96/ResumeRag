import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from candidates.models import CandidateCV
from jobs.models import JobPosition
from organizations.models import Organization
from rag.models import CVEmbeddingChunk


@pytest.mark.django_db
def test_cv_delete_cleans_vector_chunks():
    org = Organization.objects.create(name="Org")
    job = JobPosition.objects.create(organization=org, title="ML", requirements="Python")
    cv = CandidateCV.objects.create(organization=org, job=job, file=SimpleUploadedFile("cv.txt", b"text"))

    CVEmbeddingChunk.objects.create(
        organization=org,
        job=job,
        candidate_cv=cv,
        chunk_index=0,
        content="sample",
        metadata={"job_id": str(job.id)},
        embedding=[0.0] * 1024,
    )

    cv.delete()
    assert CVEmbeddingChunk.objects.count() == 0
