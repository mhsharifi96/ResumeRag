from __future__ import annotations

from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from candidates.models import CandidateCV
from rag.services.embedding import split_documents, load_pdf


def _sqlalchemy_connection_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def sync_to_langchain_pgvector(candidate_cv: CandidateCV) -> None:
    """Keep LangChain PGVector collection in sync for compatibility with tooling."""
    docs = split_documents(load_pdf(candidate_cv))
    for doc in docs:
        doc.metadata.update(
            {
                "job_id": str(candidate_cv.job_id),
                "candidate_cv_id": str(candidate_cv.id),
                "organization_id": str(candidate_cv.organization_id),
            }
        )
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required for embeddings.")
    embeddings = OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
        dimensions=1024,
    )
    PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=settings.LANGCHAIN_PG_COLLECTION,
        connection=_sqlalchemy_connection_url(settings.DATABASE_URL),
        pre_delete_collection=False,
    )
