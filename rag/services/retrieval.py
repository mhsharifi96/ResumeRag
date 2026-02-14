from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pgvector.django import CosineDistance

from rag.models import CVEmbeddingChunk
from rag.services.embedding import embed_query


class JobScopedRetriever(BaseRetriever):
    job_id: str
    organization_id: str
    k: int = 6

    def _get_relevant_documents(self, query: str, *args, **kwargs) -> list[Document]:
        query_vector = embed_query(query)
        chunks = (
            CVEmbeddingChunk.objects.filter(job_id=self.job_id, organization_id=self.organization_id)
            .annotate(distance=CosineDistance("embedding", query_vector))
            .order_by("distance")[: self.k]
        )
        return [
            Document(page_content=chunk.content, metadata=chunk.metadata)
            for chunk in chunks
        ]
