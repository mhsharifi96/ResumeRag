from __future__ import annotations

from django.conf import settings
import psycopg
import uuid
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_postgres import PostgresChatMessageHistory

from jobs.models import JobPosition
from rag.services.retrieval import JobScopedRetriever

try:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
except ModuleNotFoundError:  # LangChain v1 compatibility path
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory


def run_job_chat(*, question: str, session_id: str, job_id: str, organization_id: str) -> str:
    if not settings.OPENAI_API_KEY:
        return "I don't know."

    connection_url = settings.DATABASE_URL
    if connection_url.startswith("postgres://"):
        connection_url = connection_url.replace("postgres://", "postgresql://", 1)
    if connection_url.startswith("postgresql+psycopg://"):
        connection_url = connection_url.replace("postgresql+psycopg://", "postgresql://", 1)

    conn = psycopg.connect(connection_url)
    table_name = "chat_history"
    PostgresChatMessageHistory.create_tables(conn, table_name)
    scoped_session_key = f"{organization_id}:{job_id}:{session_id}"
    history_session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, scoped_session_key))
    history = PostgresChatMessageHistory(
        table_name,
        history_session_id,
        sync_connection=conn,
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=history,
        input_key="question",
        return_messages=True,
        output_key="answer",
    )

    retriever = JobScopedRetriever(job_id=str(job_id), organization_id=str(organization_id), k=6)
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0)
    job = JobPosition.objects.filter(id=job_id, organization_id=organization_id).first()
    job_requirements = (job.requirements if job else "").strip() or "Not provided."
    prompt = PromptTemplate.from_template(
        "You are an HR assistant. Answer based ONLY on the provided CVs for this specific job. "
        "Use the job requirements as the primary evaluation criteria.\n"
        "If the answer is not present, say you don't know.\n\n"
        "Job Requirements:\n{job_requirements}\n\n"
        "CV Context:\n{context}\n\nQuestion:\n{question}"
    ).partial(job_requirements=job_requirements)

    try:
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=False,
            combine_docs_chain_kwargs={"prompt": prompt},
        )
        result = chain.invoke({"question": question})
        return result.get("answer", "I don't know.")
    finally:
        conn.close()
