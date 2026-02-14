from django.db import transaction
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from candidates.models import CVScore, CandidateCV
from jobs.models import JobPosition
from jobs.serializers import (
    ChatSerializer,
    CVUploadSerializer,
    JobCreateSerializer,
    OrganizationCreateSerializer,
    RankingSerializer,
)
from jobs.tenant import get_org_id
from rag.services.chat import run_job_chat
from rag.tasks import process_candidate_cv


class OrganizationCreateAPIView(generics.CreateAPIView):
    serializer_class = OrganizationCreateSerializer


class JobCreateAPIView(generics.CreateAPIView):
    serializer_class = JobCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization_id"] = get_org_id(self.request)
        return context

    def perform_create(self, serializer):
        org_id = get_org_id(self.request)
        try:
            serializer.save(
                organization_id=org_id,
                created_by=self.request.user if self.request.user.is_authenticated else None,
            )
        except IntegrityError as exc:
            raise ValidationError(
                {"title": ["A job with this title already exists for the selected organization."]}
            ) from exc


class JobUploadAPIView(APIView):
    def post(self, request, job_id):
        org_id = get_org_id(request)
        job = get_object_or_404(JobPosition, pk=job_id, organization_id=org_id)
        serializer = CVUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_ids = []
        with transaction.atomic():
            for file_obj in serializer.validated_data["files"]:
                candidate = CandidateCV.objects.create(
                    organization_id=org_id,
                    job=job,
                    file=file_obj,
                    status=CandidateCV.Status.PENDING,
                )
                process_candidate_cv.delay(str(candidate.id))
                created_ids.append(str(candidate.id))

        return Response({"candidate_ids": created_ids}, status=status.HTTP_202_ACCEPTED)


class JobRankingsAPIView(generics.ListAPIView):
    serializer_class = RankingSerializer

    def get_queryset(self):
        org_id = get_org_id(self.request)
        job_id = self.kwargs["job_id"]
        get_object_or_404(JobPosition, pk=job_id, organization_id=org_id)
        return CVScore.objects.filter(job_id=job_id, job__organization_id=org_id).select_related("candidate_cv")


class JobChatAPIView(APIView):
    def post(self, request, job_id):
        org_id = get_org_id(request)
        get_object_or_404(JobPosition, pk=job_id, organization_id=org_id)

        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = run_job_chat(
            question=serializer.validated_data["question"],
            session_id=serializer.validated_data["session_id"],
            job_id=job_id,
            organization_id=str(org_id),
        )
        return Response({"answer": answer})
