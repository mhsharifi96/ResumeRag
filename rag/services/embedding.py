from __future__ import annotations

import os
from typing import Iterable

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from django.conf import settings

from candidates.models import CandidateCV
from rag.models import CVEmbeddingChunk


def detect_language(text: str) -> str:
    return "fa" if any("\u0600" <= ch <= "\u06FF" for ch in text) else "en"


def load_pdf(candidate_cv: CandidateCV) -> list[Document]:
    file_path = candidate_cv.file.path
    if not file_path or not os.path.isfile(file_path):
        raise ValueError(
            f"CV file is not accessible at {file_path}. "
            "Ensure web and worker share the same /app/media volume."
        )
    loader = PyMuPDFLoader(file_path)
    return loader.load()


def split_documents(documents: Iterable[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_documents(list(documents))


def _embedder() -> OpenAIEmbeddings:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required for embeddings.")
    # Keep dimensions aligned with VectorField(dimensions=1024).
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
        dimensions=1024,
    )


def store_embeddings(candidate_cv: CandidateCV) -> int:
    docs = load_pdf(candidate_cv)
    chunks = split_documents(docs)
    merged_text = "\n".join(doc.page_content for doc in docs)
    candidate_cv.raw_text = merged_text
    candidate_cv.language = detect_language(merged_text)
    candidate_cv.save(update_fields=["raw_text", "language", "updated_at"])

    embeddings = _embedder().embed_documents([doc.page_content for doc in chunks])

    CVEmbeddingChunk.objects.filter(candidate_cv=candidate_cv).delete()

    for idx, (doc, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
        CVEmbeddingChunk.objects.create(
            organization=candidate_cv.organization,
            job=candidate_cv.job,
            candidate_cv=candidate_cv,
            chunk_index=idx,
            content=doc.page_content,
            metadata={
                "job_id": str(candidate_cv.job_id),
                "candidate_cv_id": str(candidate_cv.id),
                "organization_id": str(candidate_cv.organization_id),
                **(doc.metadata or {}),
            },
            embedding=embedding,
        )
    return len(chunks)


def embed_query(text: str) -> list[float]:
    return _embedder().embed_query(text)
