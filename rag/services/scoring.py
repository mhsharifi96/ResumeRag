from __future__ import annotations

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from django.conf import settings

from candidates.models import CVScore, CandidateCV


class CVScoreOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    pros: list[str]
    cons: list[str]
    language_detected: str


def score_candidate(candidate_cv: CandidateCV) -> CVScore:
    if not settings.OPENAI_API_KEY:
        output = CVScoreOutput(
            score=0,
            pros=[],
            cons=["OpenAI API key is not configured; AI scoring skipped."],
            language_detected=candidate_cv.language or "en",
        )
    else:
        prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict, evidence-based HR evaluator. "
            "Evaluate the candidate ONLY against the provided job requirements and the CV text. "
            "Do not infer or assume missing information. If something is not explicitly in the CV, treat it as not met. "
            "Be concise and specific. Every pro/con MUST reference concrete evidence from the CV (skills, tools, years, titles, achievements). "
            "Score from 0 to 100 using this rubric: "
            "60% requirement match (must-have skills/experience), "
            "25% seniority/impact evidence (scope, results, metrics), "
            "15% clarity/communication (structure, readability, typos). "
            "If must-have requirements are clearly missing, cap the score at 49. "
            "If requirements are met strongly with clear evidence, score 80+. "
            "Detect the language of the CV text and set language_detected as an ISO-like code (e.g., en, fa, fr). "
            "Return ONLY the structured output",
        ),
        (
            "human",
            "Job requirements:\n{requirements}\n\nCandidate CV:\n{cv_text}",
        ),
    ]
)

        llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0)
        chain = prompt | llm.with_structured_output(CVScoreOutput)
        output = chain.invoke(
            {
                "requirements": candidate_cv.job.requirements,
                "cv_text": candidate_cv.raw_text,
            }
        )

    score_obj, _ = CVScore.objects.update_or_create(
        candidate_cv=candidate_cv,
        defaults={
            "job": candidate_cv.job,
            "score": max(0, min(int(output.score), 100)),
            "pros": output.pros,
            "cons": output.cons,
            "language_detected": output.language_detected,
        },
    )
    return score_obj
