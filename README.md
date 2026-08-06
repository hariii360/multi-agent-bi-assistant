# Multi-Agent BI Assistant

A hybrid multi-agent Business Intelligence assistant. Combines a Python-based agent reasoning core (LangGraph + Groq + ChromaDB) with n8n as the orchestration/delivery layer.

## Architecture
- **Orchestration/UI Layer:** n8n (local, via `npx`, http://localhost:5678)
- **Core Agent Brain:** FastAPI + LangGraph (Researcher → Analyst → Writer pipeline)
- **Vector DB:** ChromaDB (local, persistent, RAG-grounded Researcher agent)
- **LLM:** Groq (llama-3.3-70b-versatile, free tier)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2, free/local)
- **Delivery:** Slack/Email/WhatsApp via n8n (in progress)

## Pipeline
User Query → Researcher (RAG via ChromaDB) → Analyst (trends/risks/opportunities) → Writer (stakeholder report)

## Setup
1. `python -m venv venv` and activate it
2. `pip install -r requirements.txt`
3. Add `GROQ_API_KEY` to `.env`
4. `python src/ingest.py` to load the knowledge base into ChromaDB
5. `uvicorn src.main:app --reload` to start the API (http://localhost:8000)
6. `npx n8n@2.33.3` to start the orchestration layer (version pinned for reproducibility)

## API
- `GET /` — health check
- `POST /analyze` — runs the full agent pipeline
```json
  { "query": "<type your business question here>" }
```
  Returns `research_findings`, `analysis`, and `final_report`.

## Scaling this project
- **New agents:** add a `<agent_name>.py` file in `agents/`, wire it into `agents/graph.py` as a new node + edge
- **New use cases:** add new endpoints in `src/main.py` calling different graphs, or parameterize `/analyze` with a `use_case` field
- **New knowledge sources:** drop files into `data/knowledge_base/` and re-run `python src/ingest.py`

## Status
- [x] Core agent pipeline (Researcher, Analyst, Writer) wired with LangGraph
- [x] FastAPI integration, ChromaDB RAG, logging & error handling
- [x] n8n workflow (webhook → FastAPI → delivery channel)

## Delivery
Final reports are posted to Slack via an Incoming Webhook.
To reproduce: create a Slack app → enable Incoming Webhooks → add the
webhook URL into the "Send to Slack" node's URL field in n8n
(not committed to this repo for security — see n8n-workflow.json placeholder).