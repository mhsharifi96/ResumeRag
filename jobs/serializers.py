from rest_framework import serializers

from candidates.models import CandidateCV, CVScore
from jobs.models import JobPosition
from jobs.services.requirements import extract_requirements
from organizations.models import Organization


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class JobCreateSerializer(serializers.ModelSerializer):
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")
    job_description = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")

    class Meta:
        model = JobPosition
        fields = ["id", "organization", "title", "job_description", "requirements", "created_at"]
        read_only_fields = ["id", "organization", "created_at"]

    def validate_title(self, value: str) -> str:
        org_id = self.context.get("organization_id")
        if org_id and JobPosition.objects.filter(organization_id=org_id, title=value).exists():
            raise serializers.ValidationError(
                "A job with this title already exists for the selected organization."
            )
        return value

    def validate(self, attrs):
        requirements = (attrs.get("requirements") or "").strip()
        job_description = (attrs.get("job_description") or "").strip()
        if not requirements and not job_description:
            raise serializers.ValidationError(
                {"detail": "Provide at least one of: requirements or job_description."}
            )
        return attrs

    def create(self, validated_data):
        requirements = (validated_data.get("requirements") or "").strip()
        job_description = (validated_data.get("job_description") or "").strip()
        if not requirements and job_description:
            validated_data["requirements"] = extract_requirements(job_description)
        return super().create(validated_data)


class CVUploadSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)


class RankingSerializer(serializers.ModelSerializer):
    candidate_cv_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = CVScore
        fields = [
            "candidate_cv_id",
            "score",
            "pros",
            "cons",
            "language_detected",
            "created_at",
        ]


class ChatSerializer(serializers.Serializer):
    question = serializers.CharField()
    session_id = serializers.CharField()


class CandidateCVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateCV
        fields = ["id", "job", "status", "language", "created_at"]
