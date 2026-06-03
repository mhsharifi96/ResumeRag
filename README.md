# CV RAG (Django + Postgres + pgvector + LangChain) - Resume RAG

## Overview
CV RAG is a resume screening and candidate search platform built with Django, PostgreSQL, pgvector, LangChain, Redis, and OpenAI embeddings. It enables organizations to create job postings, upload candidate CVs, automatically extract and analyze skills, rank applicants against job requirements, and perform natural-language queries across a job's candidate pool using Retrieval-Augmented Generation (RAG).

### Key Features
- Multi-organization support
- Job creation and requirement extraction
- Bulk CV upload and processing
- Vector-based semantic search with pgvector
- AI-powered candidate ranking and scoring
- Natural-language chat over candidate CVs (RAG)
- Asynchronous document processing with Celery and Redis
- Docker and local development support


## Requirements
- Python 3.11+
- `uv` (install from https://docs.astral.sh/uv/)
- PostgreSQL 15+ with UTF-8 database
- Redis

## Setup (uv)
```bash
docker compose up -d db redis
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

## Setup (Docker)
```bash
docker compose up --build
```

Apps:
- Backend API: `http://127.0.0.1:8000`
- Frontend UI (Next.js): `http://127.0.0.1:3000`

## Celery
```bash
uv run celery -A config worker -l info
```

## API Endpoints
Base URL: `http://127.0.0.1:8000`

Required header on job-scoped endpoints:
- `X-Organization-ID: <organization_uuid>`

### 1) Create Organization
- Method: `POST`
- Path: `/api/organizations/`
- Body:
```json
{
  "name": "Acme Inc"
}
```
- Response `201`:
```json
{
  "id": "organization-uuid",
  "name": "Acme Inc",
  "created_at": "2026-02-14T00:00:00Z"
}
```

### 2) Create Job
- Method: `POST`
- Path: `/api/jobs/`
- Notes:
  - `requirements` is optional.
  - If `requirements` is empty and `job_description` is provided, backend extracts requirements via LLM (with fallback heuristic).
- Body:
```json
{
  "title": "Backend Engineer",
  "job_description": "About the role... What you'll do... Required qualifications...",
  "requirements": ""
}
```
- Response `201`:
```json
{
  "id": "job-uuid",
  "organization": "organization-uuid",
  "title": "Backend Engineer",
  "job_description": "About the role...",
  "requirements": "Django, PostgreSQL, REST API design",
  "created_at": "2026-02-14T00:00:00Z"
}
```

### 3) Upload CVs For a Job
- Method: `POST`
- Path: `/api/jobs/{job_id}/upload/`
- Content type: `multipart/form-data`
- Field:
  - `files`: one or multiple files
- Example:
```bash
curl -X POST "http://127.0.0.1:8000/api/jobs/<job_id>/upload/" \
  -H "X-Organization-ID: <organization_uuid>" \
  -F "files=@/path/to/cv1.pdf" \
  -F "files=@/path/to/cv2.pdf"
```
- Response `202`:
```json
{
  "candidate_ids": ["candidate-uuid-1", "candidate-uuid-2"]
}
```

### 4) Get Job Rankings
- Method: `GET`
- Path: `/api/jobs/{job_id}/rankings/`
- Response `200`:
```json
[
  {
    "candidate_cv_id": "candidate-uuid",
    "score": 85,
    "pros": ["Strong Django experience"],
    "cons": ["Limited cloud exposure"],
    "language_detected": "en",
    "created_at": "2026-02-14T00:00:00Z"
  }
]
```

### 5) Chat With Job CV Pool (RAG)
- Method: `POST`
- Path: `/api/jobs/{job_id}/chat/`
- Body:
```json
{
  "session_id": "user-session-1",
  "question": "Which candidates have production Django experience?"
}
```
- Response `200`:
```json
{
  "answer": "..."
}
```

## Notes
- pgvector extension is enabled via migration.
- Retrieval is filtered by `job_id`.
- `CandidateCV` deletion triggers vector cleanup.
- Embeddings use OpenAI (`OPENAI_EMBEDDING_MODEL`, default `text-embedding-3-large`) with `dimensions=1024` to match pgvector schema.

## Frontend (Next.js)
- Location: `/frontend`
- The UI proxies all API calls through Next.js route handlers:
  - `/api/proxy/*` -> Django `/api/*`
- Docker env used by frontend:
  - `BACKEND_URL=http://web:8000`

## Troubleshooting
- If build previously failed with `hatchling ... Unable to determine which files to ship`, it is fixed by disabling package-mode for `uv`.
- If you see `Invalid HTTP_HOST header: 'web:8000'`, ensure `ALLOWED_HOSTS` includes Docker service names (for example: `127.0.0.1,localhost,web,web:8000`).
- If Celery reports `File path /app/media/... is not a valid file or url`, mount shared media on both `web` and `worker` (already configured as `media_data:/app/media`). Re-upload CVs that were uploaded before this change.
- If you see `ModuleNotFoundError: No module named 'psycopg2'` from `langchain_postgres`, this is handled by forcing SQLAlchemy URL to `postgresql+psycopg://` in ingestion code.
- Rebuild from scratch:
```bash
docker compose down
docker compose build --no-cache web worker
docker compose up
```
