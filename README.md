# Multi-Agent BI Assistant

A hybrid multi-agent Business Intelligence assistant. Combines two Python-based agent reasoning cores — a fast LangGraph pipeline and a deep, self-critiquing CrewAI crew — with n8n as the orchestration/delivery layer.

## Architecture
- **Orchestration/UI Layer:** n8n (local, via `npx`, http://localhost:5678)
- **Core Agent Brain (Fast):** FastAPI + LangGraph (Researcher → Analyst → Writer pipeline)
- **Core Agent Brain (Deep):** FastAPI + CrewAI (Researcher → Adversarial Critic → Strategist crew)
- **Vector DB:** ChromaDB (local, persistent, RAG-grounded LangGraph Researcher agent)
- **LLM:** Groq (llama-3.3-70b-versatile, free tier) via LiteLLM for CrewAI compatibility
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2, free/local)
- **Delivery:** Slack or Email, selected per-request via an n8n Switch node

![Architecture Diagram](docs/architecture-diagram.svg)

## Why Two Agent Frameworks?
This project intentionally uses LangGraph and CrewAI for different jobs, mirroring *System 1 / System 2* thinking:

| | LangGraph (`/analyze`) | CrewAI (`/deep-analyze`) |
|---|---|---|
| **Style** | Fast, linear, low latency | Deep, multi-perspective, adversarial |
| **Pattern** | Fixed state machine (DAG) | Role-playing crew with dynamic context |
| **Best for** | Routine queries, quick summaries | High-stakes strategy, due diligence |
| **Cost/Time** | Seconds, low token usage | Minutes, higher token usage |

See a full worked comparison in [`data/sample_outputs/fast_vs_deep_comparison.md`](data/sample_outputs/fast_vs_deep_comparison.md).

## Pipelines

**Fast (LangGraph):**
User Query → Researcher (RAG via ChromaDB) → Analyst (trends/risks/opportunities) → Writer (stakeholder report)

**Deep (CrewAI):**
User Query → Researcher (tags claims as Fact/Estimate/Open Question) → Adversarial Critic (per-claim review + Confidence Verdict) → Strategist (report with explicit Confidence & Caveats section)

Both converge into n8n, which routes the final report to Slack or Email.

## Setup
1. `python -m venv venv` and activate it
2. `pip install -r requirements.txt`
3. Add `GROQ_API_KEY` to `.env`
4. `python src/ingest.py` to load the knowledge base into ChromaDB
5. `uvicorn src.main:app --reload` to start the API (http://localhost:8000)
6. `npx n8n@2.33.3` to start the orchestration layer (version pinned for reproducibility)

## API
- `GET /` — health check
- `POST /analyze` — runs the fast LangGraph pipeline
```json
  { "query": "<type your business question here>" }
```
  Returns `mode: "fast"`, `research_findings`, `analysis`, and `final_report`.

- `POST /deep-analyze` — runs the deep CrewAI crew
```json
  { "query": "<type your business question here>" }
```
  Returns `mode: "deep"`, `research_findings`, `critique`, and `final_report`.

## n8n Webhook
- `POST http://localhost:5678/webhook-test/bi-assistant`
```json
  { "query": "<your business question>", "channel": "slack" }
```
  `channel` accepts `"slack"` or `"email"` and routes the final report to the corresponding delivery path via a Switch node. Defaults to Slack if omitted.

## Delivery
Two delivery channels are supported, chosen per-request:

**Slack** — posted via an Incoming Webhook, with a Code node converting standard markdown (`**bold**`, `# headers`) into Slack's mrkdwn syntax before sending.
To reproduce: create a Slack app → enable Incoming Webhooks → add the webhook URL into the "Send to Slack" node's URL field in n8n (not committed to this repo for security — see the placeholder in `n8n-workflow.json`).

**Email** — sent via Gmail SMTP using an n8n-native "Send an Email" node.
To reproduce: enable 2-Step Verification on your Google account → generate an App Password → add it as an SMTP credential in n8n (Host: `smtp.gmail.com`, Port: `465`, SSL on). Credentials are stored encrypted in n8n's local credential store and are never included in the exported workflow JSON.

## APIs & External Services Used
| Service | Purpose | Type |
|---|---|---|
| **Groq API** | LLM inference for all agents in both pipelines — `llama-3.3-70b-versatile` | REST API (OpenAI-compatible) |
| **Slack Incoming Webhooks API** | Delivers the final report to a Slack channel | REST Webhook |
| **Gmail SMTP** | Delivers the final report via email | SMTP protocol (via n8n's native Send Email node) |

### Local/self-hosted (not external APIs, but core to the stack)
| Component | Purpose |
|---|---|
| **ChromaDB** | Local persistent vector store for RAG retrieval |
| **sentence-transformers** (`all-MiniLM-L6-v2`) | Local embedding model — runs on-device, no external calls |
| **n8n** | Local orchestration engine (webhook trigger, routing, delivery) |
| **FastAPI** | Local Python microservice exposing `/analyze` and `/deep-analyze` |
| **LangGraph** | Fast, deterministic agent pipeline |
| **CrewAI** | Deep, role-based, self-critiquing agent crew |

## Known Compatibility Notes
`agents/deep_crew.py` includes a scoped patch for a CrewAI/Groq caching conflict via LiteLLM (see inline comment for details and pinned versions). If upgrading `crewai` or `litellm`, verify this is still needed.

## Sample Outputs
See real pipeline outputs in [`data/sample_outputs/`](data/sample_outputs/), including a [fast vs. deep mode comparison](data/sample_outputs/fast_vs_deep_comparison.md) showing why the project uses two agent frameworks.

## Scaling this project
- **New agents:** add a `<agent_name>.py` file in `agents/`, wire it into `agents/graph.py` (fast) or `agents/deep_crew.py` (deep)
- **New use cases:** add new endpoints in `src/main.py`, or parameterize existing endpoints with a `use_case` field
- **New knowledge sources:** drop files into `data/knowledge_base/` and re-run `python src/ingest.py`
- **New delivery channels:** add another branch off the "Choose Channel" Switch node in n8n (e.g. WhatsApp, Teams, SMS)

## Status
- [x] Core fast pipeline (Researcher, Analyst, Writer) wired with LangGraph
- [x] FastAPI integration, ChromaDB RAG, logging & error handling
- [x] n8n workflow (webhook → FastAPI → delivery channel)
- [x] Dual delivery channels (Slack, Gmail) with per-request routing
- [x] Deep pipeline (Researcher, Critic, Strategist) built with CrewAI
- [x] `/deep-analyze` endpoint exposing the CrewAI crew
- [ ] n8n mode routing between `/analyze` and `/deep-analyze`