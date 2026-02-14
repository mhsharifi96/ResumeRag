from celery import shared_task
from django.db import transaction

from candidates.models import CandidateCV
from rag.services.embedding import store_embeddings
from rag.services.ingestion import sync_to_langchain_pgvector
from rag.services.scoring import score_candidate


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, max_retries=3)
def process_candidate_cv(self, candidate_cv_id: str) -> None:
    candidate_cv = CandidateCV.objects.select_related("job", "organization").get(pk=candidate_cv_id)
    try:
        with transaction.atomic():
            store_embeddings(candidate_cv)
            sync_to_langchain_pgvector(candidate_cv)
            score_candidate(candidate_cv)
            candidate_cv.status = CandidateCV.Status.READY
            candidate_cv.error_message = ""
            candidate_cv.save(update_fields=["status", "error_message", "updated_at"])
    except Exception as exc:
        candidate_cv.status = CandidateCV.Status.FAILED
        candidate_cv.error_message = str(exc)
        candidate_cv.save(update_fields=["status", "error_message", "updated_at"])
        raise
