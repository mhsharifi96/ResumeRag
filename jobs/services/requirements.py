from __future__ import annotations

from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class RequirementsOutput(BaseModel):
    requirements: list[str] = Field(default_factory=list)


def _fallback_requirements(job_description: str) -> str:
    lines = [line.strip(" -•\t") for line in job_description.splitlines() if line.strip()]
    preferred = [line for line in lines if line and len(line.split()) >= 4]
    selected = preferred[:10] if preferred else lines[:10]
    if not selected:
        return ""
    return "\n".join(f"- {item}" for item in selected)


def extract_requirements(job_description: str) -> str:
    text = (job_description or "").strip()
    if not text:
        return ""

    if not settings.OPENAI_API_KEY:
        return _fallback_requirements(text)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract concrete hiring requirements from the job description. "
                "Return concise requirement items only.",
            ),
            ("human", "Job description:\n{job_description}"),
        ]
    )

    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0)
    chain = prompt | llm.with_structured_output(RequirementsOutput)
    try:
        output = chain.invoke({"job_description": text})
        reqs = [item.strip() for item in output.requirements if item.strip()]
        return "\n".join(f"- {item}" for item in reqs)
    except Exception:
        return _fallback_requirements(text)
