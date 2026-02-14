import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from candidates.models import CVScore, CandidateCV
from jobs.models import JobPosition
from organizations.models import Organization


@pytest.mark.django_db
def test_create_job_scoped_by_header():
    client = APIClient()
    org = Organization.objects.create(name="Acme")
    response = client.post(
        "/api/jobs/",
        {"title": "Backend Engineer", "requirements": "Python, Django"},
        format="json",
        HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert response.status_code == 201
    assert response.data["organization"] == str(org.id)


@pytest.mark.django_db
def test_create_job_generates_requirements_from_description(monkeypatch):
    client = APIClient()
    org = Organization.objects.create(name=f"Org-{uuid.uuid4()}")

    monkeypatch.setattr(
        "jobs.serializers.extract_requirements",
        lambda _: "- Python\n- Django\n- Automation systems",
    )

    response = client.post(
        "/api/jobs/",
        {
            "title": "Automation Expert",
            "job_description": "Long role description without explicit requirement field.",
        },
        format="json",
        HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert response.status_code == 201
    assert "Python" in response.data["requirements"]


@pytest.mark.django_db
def test_create_job_requires_requirements_or_description():
    client = APIClient()
    org = Organization.objects.create(name=f"Org-{uuid.uuid4()}")
    response = client.post(
        "/api/jobs/",
        {"title": "Empty Spec"},
        format="json",
        HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_job_duplicate_title_returns_400():
    client = APIClient()
    org = Organization.objects.create(name=f"Org-{uuid.uuid4()}")
    JobPosition.objects.create(
        organization=org,
        title="Backend Engineer",
        requirements="Django",
        job_description="desc",
    )

    response = client.post(
        "/api/jobs/",
        {"title": "Backend Engineer", "requirements": "Python"},
        format="json",
        HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert response.status_code == 400
    assert "title" in response.data


@pytest.mark.django_db
def test_rankings_are_job_scoped():
    client = APIClient()
    org = Organization.objects.create(name=f"Acme-{uuid.uuid4()}")
    job = JobPosition.objects.create(organization=org, title="Data Engineer", requirements="SQL")
    cv = CandidateCV.objects.create(organization=org, job=job, file=SimpleUploadedFile("cv.txt", b"hello"))
    CVScore.objects.create(candidate_cv=cv, job=job, score=85, pros=["SQL"], cons=[], language_detected="en")

    response = client.get(f"/api/jobs/{job.id}/rankings/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["score"] == 85
