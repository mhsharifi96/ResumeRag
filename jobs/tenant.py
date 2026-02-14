from uuid import UUID
from rest_framework.exceptions import ValidationError


def get_org_id(request) -> UUID:
    value = request.headers.get("X-Organization-ID")
    if not value:
        raise ValidationError({"detail": "X-Organization-ID header is required."})
    try:
        return UUID(value)
    except ValueError as exc:
        raise ValidationError({"detail": "Invalid organization id."}) from exc
