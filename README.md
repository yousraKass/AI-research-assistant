# AI Research Assistant 

A research assistant that takes a question, searches academic papers, summarizes them, identifies gaps, and returns a structured review draft. The current implementation is a FastAPI backend with LangChain-based LLM utilities and a React frontend for search, polling, and results rendering.

## Why this exists

Doing a literature review manually — searching, reading abstracts, clustering papers by theme, spotting what's missing — takes days. This project automates the repetitive parts of that workflow and presents the results in a structured UI.

## Current status

- **Search tools** for Semantic Scholar, arXiv, web search, and paper lookup, exposed as independent LangChain tools.
- **Research service** that searches, filters, deduplicates, summarizes, and synthesizes paper results into a structured report.
- **Structured LLM output** for synthesis.
- **React frontend** with a home page, result polling, structured result sections, and an about page.
- **On-disk caching** for paper search responses.
- **Backend and frontend tests** covering the current flow.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python) |
| LLM layer | LangChain + OpenRouter-compatible chat model |
| Paper sources | Semantic Scholar API, arXiv API |
| Frontend | React (Vite) |
| Caching / job state | On-disk cache / in-memory polling state |
| Styling | React Bootstrap + Sass |

The backend is intentionally split into routers, services, LLM helpers, and tools so it can be extended later without turning into a single monolith.

## Project organization

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app and routers
│   │   ├── routers/                 # HTTP endpoints
│   │   ├── services/                # Search + research orchestration
│   │   ├── llm/                     # Prompt loading and model helpers
│   │   └── tools/                   # Independent search tools
│   ├── cache/                       # On-disk cache for API responses
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                   # Home, Results, About
│   │   ├── components/              # UI sections and pipeline status
│   │   ├── hooks/                   # Research polling hook
│   │   └── api/                     # API client
│   └── package.json
└── README.md
```

## How it works

1. **Search** — the backend searches Semantic Scholar and, when needed, arXiv or the web through reusable tools.
2. **Normalize** — paper metadata is normalized and cached so the rest of the pipeline works on a stable shape.
3. **Summarize** — each paper abstract is summarized with reusable LangChain prompt templates.
4. **Synthesize** — the service produces structured output for the frontend to render as sections instead of raw markdown.
5. **Poll results** — the frontend starts a research job and polls until the structured result is ready.

## Setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OpenRouter / Semantic Scholar keys
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default.

## API

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /papers/search?q=...` | Raw paper search (debugging/inspection) |
| `POST /research` | Submit a research question; returns a `job_id` |
| `GET /research/{job_id}` | Poll job status; returns the structured review once complete |

## Evaluation

The current repo includes tests for the backend research flow, LangChain prompt templates, tool wrappers, and the frontend build/lint pipeline. A dedicated evaluation report is not yet part of the repository.

## Limitations

- Structured synthesis is intentionally conservative and depends on the quality of the retrieved abstracts.
- Paper coverage is limited to what Semantic Scholar and arXiv index, plus whatever the web search fallback can surface.
- The frontend is functional and clean, but the visual polish/accessibility pass is still ongoing.


## Future direction

The next major architecture step is LangGraph. When that lands, the pipeline will evolve from the current service-oriented flow into a more explicit graph of research planning, evidence extraction, evaluation, and looped refinement. The later phases will also cover reliability, persistence, and deployment hardening.