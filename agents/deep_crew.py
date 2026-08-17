import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from groq import RateLimitError

import crewai.llms.cache as _crewai_cache
# Workaround: CrewAI's cache-breakpoint marker conflicts with Groq's response
# format via LiteLLM, causing a crash during multi-agent execution.
# This no-ops the marker function until upstream CrewAI/LiteLLM fixes Groq compatibility.
# Verified working with crewai==1.15.12, litellm==1.95.0 as of Aug 2026.
_crewai_cache.mark_cache_breakpoint = lambda msg: msg


load_dotenv()

llm = LLM(
    model="groq/openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY")
)

researcher = Agent(
    role="Senior Research Analyst",
    goal=(
        "Produce rigorous, well-structured research that clearly separates "
        "established facts from estimates, and never presents a guess as a certainty"
    ),
    backstory=(
        "You are a former equity research analyst who was taught to never let a "
        "number into a report without knowing where it came from. You are allergic "
        "to vague claims like 'growing rapidly' without a timeframe or magnitude. "
        "When you don't have a hard figure, you say so explicitly rather than "
        "inventing one. You always distinguish between what is widely reported "
        "industry consensus versus what is a single-source or speculative claim."
    ),
    llm=llm,
    verbose=True
)

critic = Agent(
    role="Adversarial Fact-Checker",
    goal=(
        "Stress-test the research like a hostile due-diligence reviewer would — "
        "assume every unsupported claim is wrong until proven otherwise, and force "
        "precision where the research is vague"
    ),
    backstory=(
        "You built your career catching bad numbers in investment memos before they "
        "reached a board. You are not here to be agreeable. For every claim in the "
        "research, you ask: what is this based on, is it still current, and what "
        "would have to be true for this to be wrong. You explicitly separate "
        "'high confidence' findings from 'low confidence / unverifiable' ones, and "
        "you flag anything that sounds like it was invented to fill a gap."
    ),
    llm=llm,
    verbose=True
)

strategist = Agent(
    role="Business Strategist",
    goal="Synthesize research and critique into clear, actionable strategic recommendations",
    backstory=(
        "You are a seasoned consultant who turns raw analysis into decisions "
        "executives can act on. You never smooth over disagreement between your "
        "research and fact-checking teams — you surface it, because executives "
        "make worse decisions when uncertainty is hidden from them."
    ),
    llm=llm,
    verbose=True
)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    retry=retry_if_exception_type(RateLimitError)
)
def _run_crew_with_retry(crew: Crew):
    """Runs the crew, automatically retrying with exponential backoff if
    Groq's free-tier TPM/RPM rate limit is hit mid-execution."""
    return crew.kickoff()


def run_deep_analysis(query: str) -> dict:
    research_task = Task(
        description=(
            f"Research this business question thoroughly: '{query}'\n\n"
            "Structure your output with these exact sections:\n"
            "1. **Established Facts** — widely reported, high-confidence information\n"
            "2. **Estimates & Projections** — figures that are forecasts, not facts; "
            "state the source type (e.g. 'industry report estimate') and the range "
            "of uncertainty if known\n"
            "3. **Key Players** — named companies/entities relevant to the question\n"
            "4. **Open Questions** — anything relevant you genuinely don't have "
            "reliable information on; do not fill these with speculation\n\n"
            "Do not present any number without indicating whether it is a fact, "
            "an estimate, or your own inference.\n\n"
            "Output ONLY the four labeled sections above — do not include step-by-step "
            "reasoning, meta-commentary, or a 'Step 1/2/3' narration of your process."
        ),
        expected_output=(
            "A structured research summary with the four labeled sections above, "
            "each claim tagged by confidence type."
        ),
        agent=researcher
    )

    critique_task = Task(
        description=(
            "Critically review the research findings above as an adversarial "
            "fact-checker. For each major claim:\n"
            "1. Assess whether it is adequately supported or unverifiable\n"
            "2. Flag anything stated as fact that should be an estimate\n"
            "3. Identify what's missing that a rigorous analysis would need\n"
            "4. Note any internal contradictions or outdated-sounding claims\n\n"
            "Conclude with a **Confidence Verdict**: rate the overall research as "
            "High / Medium / Low confidence, and justify the rating in 1-2 sentences."
        ),
        expected_output=(
            "A structured critique with per-claim assessments and a final "
            "Confidence Verdict with justification."
        ),
        agent=critic,
        context=[research_task]
    )

    strategy_task = Task(
        description=(
            f"Using the research findings and the critic's review above, produce a "
            f"final strategic recommendation report for a business stakeholder "
            f"answering: '{query}'.\n\n"
            "Required sections:\n"
            "1. **Executive Summary** (2-3 sentences)\n"
            "2. **Key Insights** — grounded in the research's Established Facts\n"
            "3. **Risks & Opportunities**\n"
            "4. **Confidence & Caveats** — explicitly state the critic's Confidence "
            "Verdict and which specific recommendations below depend on the weaker, "
            "lower-confidence findings\n"
            "5. **Recommendations** — clearly mark any recommendation that hinges "
            "on an estimate rather than an established fact\n\n"
            "You must not present a unanimous, clean narrative if the critique found "
            "real gaps — surface the disagreement instead of resolving it artificially."
        ),
        expected_output=(
            "A structured report with all five sections above, explicitly "
            "referencing the critic's confidence assessment."
        ),
        agent=strategist,
        context=[research_task, critique_task]
    )

    crew = Crew(
        agents=[researcher, critic, strategist],
        tasks=[research_task, critique_task, strategy_task],
        process=Process.sequential,
        verbose=True
    )

    result = _run_crew_with_retry(crew)

    return {
        "research": research_task.output.raw if research_task.output else None,
        "critique": critique_task.output.raw if critique_task.output else None,
        "final_report": str(result)
    }