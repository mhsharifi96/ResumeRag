from django.db import DatabaseError, connection, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from candidates.models import CandidateCV
from rag.models import CVEmbeddingChunk


@receiver(post_delete, sender=CandidateCV)
def delete_cv_vectors(sender, instance: CandidateCV, **kwargs):
    # Explicit cleanup guarantees atomic consistency even if storage implementation changes.
    CVEmbeddingChunk.objects.filter(candidate_cv_id=instance.id).delete()

    # Best-effort cleanup for LangChain PGVector table synced via metadata.
    try:
        # Run best-effort cleanup in an inner savepoint so failures don't poison
        # the outer transaction used by Django admin bulk delete.
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM langchain_pg_embedding
                    WHERE cmetadata->>'candidate_cv_id' = %s
                    """,
                    [str(instance.id)],
                )
    except DatabaseError:
        # Keep delete path resilient if optional table does not exist yet.
        pass
