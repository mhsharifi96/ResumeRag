from django.urls import path

from jobs.views import (
    JobChatAPIView,
    JobCreateAPIView,
    JobRankingsAPIView,
    JobUploadAPIView,
    OrganizationCreateAPIView,
)

urlpatterns = [
    path("organizations/", OrganizationCreateAPIView.as_view(), name="organization-create"),
    path("jobs/", JobCreateAPIView.as_view(), name="job-create"),
    path("jobs/<uuid:job_id>/upload/", JobUploadAPIView.as_view(), name="job-upload"),
    path("jobs/<uuid:job_id>/rankings/", JobRankingsAPIView.as_view(), name="job-rankings"),
    path("jobs/<uuid:job_id>/chat/", JobChatAPIView.as_view(), name="job-chat"),
]
