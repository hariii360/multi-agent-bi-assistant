# Sample Comparison — Fast Mode vs Deep Mode

**Query:** `What are the growth trends in the Indian EdTech market?`

This comparison demonstrates why the project offers two reasoning pipelines instead of one.

---

## `/analyze` (LangGraph — fast mode)

**Runtime:** ~10-15 seconds (3 sequential LLM calls)

**Characteristics:**
- Clean, readable prose
- No distinction between established facts and estimates
- No adversarial review step — the Analyst builds directly on Researcher output with no challenge
- Good for quick, low-stakes questions where speed matters more than epistemic rigor

**Final Report (excerpt):**
> The Indian EdTech market is experiencing a shift towards stable growth, with companies adapting to changing dynamics by innovating and evolving their business models. Key trends include a focus on profitability, hybrid models, and increased adoption in tier-2 and tier-3 cities.

*(Full output: see `fast_analyze_sample.json`)*

---

## `/deep-analyze` (CrewAI — deep mode)

**Runtime:** ~45-90 seconds (3 agents, adversarial review loop)

**Characteristics:**
- Researcher tags every claim as **Established Fact**, **Estimate & Projection**, **Key Player**, or **Open Question**
- Critic performs a claim-by-claim adversarial review and issues a **Confidence Verdict**
- Strategist is required to surface the critique's concerns rather than smoothing them over — includes an explicit **Confidence & Caveats** section
- Individual recommendations are tagged with their supporting confidence level (e.g. "based on established facts" vs "based on medium-confidence estimates")
- Better suited for higher-stakes business decisions where knowing *how sure* the system is matters as much as the answer itself

**Final Report (excerpt):**
> **Confidence & Caveats**
> The critic's confidence verdict is medium due to the lack of specificity in some established facts, the inherent uncertainty in estimates and projections... Specifically, recommendations related to the market's potential value by 2025 and the CAGR from 2020 to 2025 are based on estimates rather than established facts and should be considered with caution.

*(Full output: see `deep_analyze_sample.json`)*

---

## Why this matters

`/analyze` states figures like market growth percentages with the same confidence as verifiable facts. `/deep-analyze` explicitly separates the two and forces the final report to acknowledge which recommendations rest on shakier ground — a meaningful difference for real business decision-making, at the cost of ~4-6x more latency and LLM calls.

This is the core design rationale for using **two different agent frameworks** in this project: LangGraph for deterministic, fast pipelines, and CrewAI for open-ended, self-critiquing research where agent collaboration and adversarial review add real value.

---

## Why Have 2 Systems? (System 1 vs. System 2 Thinking)

Using both LangGraph (`/analyze`) and CrewAI (`/deep-analyze`) in the same system mirrors how human cognitive processing works — often referred to as *Thinking, Fast and Slow*:

| Feature | System 1: LangGraph (`/analyze`) | System 2: CrewAI (`/deep-analyze`) |
|---|---|---|
| **Cognitive Style** | Fast, linear, low latency | Deep, multi-perspective, adversarial |
| **Execution Pattern** | Fixed Directed Acyclic Graph (DAG) state machine | Role-playing crew with dynamic context pass-throughs |
| **Best Used For** | Routine BI queries, straightforward summaries, quick checks | High-stakes strategy, market research, due diligence |
| **Cost & Time** | Seconds, low API cost | Minutes, higher token usage |

Having both endpoints gives the user (or an upstream system) choice:
- If a user asks *"What is the market size of EdTech?"*, they don't need a 3-agent debate — the fast LangGraph pipeline gives an instant answer.
- If a user asks *"Should we invest $5M into Indian EdTech in Q4?"*, the fast pipeline is dangerous because it lacks stress-testing. They need the deep CrewAI pipeline with an adversarial Critic.
