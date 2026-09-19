# AI Research Assistant Agent

A multi-agent system that takes a research question, autonomously searches academic papers, summarizes them, identifies gaps in the literature, and produces a structured literature review draft — built to run entirely on free-tier resources.

## Why this exists

Doing a literature review manually — searching, reading abstracts, clustering papers by theme, spotting what's missing — takes days. This project automates that pipeline end-to-end using an agentic architecture (LangGraph), turning a single research question into a structured, citation-backed draft in minutes.

## Expected Features

- **Autonomous paper search** across Semantic Scholar and arXiv, with on-disk caching to stay within free API rate limits.
- **Multi-step agent pipeline** (LangGraph): search → per-paper summarization → thematic clustering → gap analysis → structured synthesis.
- **Structured output**, not free-text — the final review is generated as a schema-validated JSON object (clusters, per-cluster findings, identified gaps, references) so the frontend can render real sections instead of parsing markdown.
- **Provider-agnostic LLM layer** — swappable between free-tier providers (Groq, Gemini Flash) via config, with retry/backoff for rate-limit handling and automatic failover.
- **Async job handling** — long-running pipeline executions are submitted as background jobs and polled for status, so the API never blocks on a multi-minute LLM run.
- **React frontend** with live pipeline status (searching → summarizing → clustering → synthesizing) and a structured, readable review output with links back to source papers.
- **Evaluation suite** — pipeline outputs are scored against manually-written reviews on citation accuracy, gap quality, and hallucination rate, with cost/latency tracked per run. 

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python) |
| Orchestration | LangGraph |
| LLM providers | Groq (Llama 3.1/3.3), Google Gemini Flash — both free-tier |
| Paper sources | Semantic Scholar API, arXiv API |
| Frontend | React (Vite) |
| Caching / job state | SQLite / in-memory |
| Deployment (optional) | Render/Railway (backend), Vercel/Netlify (frontend) — free tiers |

No paid APIs are used anywhere in this project; all LLM and data calls run on free-tier quotas with caching and backoff to stay within limits.

## Project organization

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app, endpoint definitions
│   │   ├── tools/
│   │   │   ├── semantic_scholar.py  # Paper search via Semantic Scholar
│   │   │   └── arxiv.py             # Paper search via arXiv (fallback)
│   │   ├── llm/
│   │   │   └── provider.py          # Provider-agnostic LLM interface (Groq / Gemini)
│   │   ├── graph/
│   │   │   ├── state.py             # LangGraph state schema
│   │   │   └── pipeline.py          # Node definitions + graph wiring
│   │   └── jobs.py                  # Async job submission/polling logic
│   ├── cache/                       # On-disk cache for API/LLM responses
│   ├── .env                         # API keys (gitignored)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Search input, polling logic, results view
│   │   └── components/              # Review sections, loading states, error states
│   └── package.json
├── EVALUATION.md                    # Evaluation methodology + results (to be added)
└── README.md
```

## How it works

1. **Search** — the user's query is sent to Semantic Scholar (with arXiv as fallback), returning a set of candidate papers with abstracts and metadata.
2. **Summarize** — each paper's abstract is summarized individually via a fast, cheap model (Groq Llama 3.1 8B or Gemini Flash), extracting method, key finding, and limitation.
3. **Cluster** — summaries are grouped into thematic clusters rather than treated as a flat list, so the gap-analysis step reasons over themes instead of individual papers.
4. **Gap analysis** — a prompt over the clustered summaries identifies what's under-explored across the retrieved literature.
5. **Synthesize** — a stronger model produces the final structured review: clusters, findings, gaps, and references, validated against a fixed schema.

## Setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your free Groq / Gemini / Semantic Scholar keys
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default (configurable via `frontend/.env`).

## API

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /papers/search?q=...` | Raw paper search (debugging/inspection) |
| `POST /research` | Submit a research question; returns a `job_id` |
| `GET /research/{job_id}` | Poll job status; returns the structured review once complete |

## Evaluation

Pipeline outputs were tested against manually-written literature reviews on a set of research questions from the LLM/agentic-AI domain, scored on citation accuracy, gap-identification quality, and hallucination rate, with per-run cost and latency tracked. Full methodology and results in [`EVALUATION.md`](./EVALUATION.md).

## Limitations

- Running entirely on free-tier LLM quotas means throughput is rate-limited; large batch queries may take longer than a paid setup.
- Paper coverage is limited to what Semantic Scholar and arXiv index — some fields (or non-English literature) are underrepresented.
- Gap analysis quality depends on cluster quality; sparse or highly heterogeneous result sets can produce weaker clusters.

## Roadmap

- [ ] Add a lightweight vector store for follow-up Q&A over retrieved papers (RAG on top of the search results).
- [ ] Support user-uploaded PDFs alongside API-retrieved papers.
- [ ] Multi-language support for non-English literature search.