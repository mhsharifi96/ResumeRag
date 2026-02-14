from django.apps import AppConfig


class CandidatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "candidates"

    def ready(self) -> None:
        from . import signals  # noqa: F401
