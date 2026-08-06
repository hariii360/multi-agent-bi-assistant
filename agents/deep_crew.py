import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM


import crewai.llms.cache as _crewai_cache
# Workaround: CrewAI's cache-breakpoint marker conflicts with Groq's response 
# format via LiteLLM, causing a crash during multi-agent execution.
# This no-ops the marker function until upstream CrewAI/LiteLLM fixes Groq compatibility. 
# Verified working with crewai==1.15.12, litellm==1.95.0 as of Aug 2026.
_crewai_cache.mark_cache_breakpoint = lambda msg: msg


load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

researcher = Agent(
    role="Senior Research Analyst",
    goal="Gather thorough, well-grounded background information on the given business topic",
    backstory="You are a meticulous market researcher who prioritizes factual accuracy over speculation.",
    llm=llm,
    verbose=True
)

critic = Agent(
    role="Skeptical Fact-Checker",
    goal="Critically review research findings, flag unsupported claims, and point out gaps or biases",
    backstory="You are a rigorous editor who challenges assumptions and demands evidence before accepting conclusions.",
    llm=llm,
    verbose=True
)

strategist = Agent(
    role="Business Strategist",
    goal="Synthesize research and critique into clear, actionable strategic recommendations",
    backstory="You are a seasoned consultant who turns raw analysis into decisions executives can act on.",
    llm=llm,
    verbose=True
)

def run_deep_analysis(query: str) -> dict:
    research_task = Task(
        description=f"Research this business question thoroughly: {query}",
        expected_output="A detailed research summary with key facts and context.",
        agent=researcher
    )

    critique_task = Task(
        description="Critically review the research findings above. Identify any unsupported claims, missing context, or biases.",
        expected_output="A list of concerns, gaps, or validations regarding the research.",
        agent=critic,
        context=[research_task]
    )

    strategy_task = Task(
        description="Using the research and the critique, produce a final strategic recommendation report for a business stakeholder.",
        expected_output="A structured report with executive summary, key insights, risks, and recommendations.",
        agent=strategist,
        context=[research_task, critique_task]
    )

    crew = Crew(
        agents=[researcher, critic, strategist],
        tasks=[research_task, critique_task, strategy_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return {
        "research": research_task.output.raw if research_task.output else None,
        "critique": critique_task.output.raw if critique_task.output else None,
        "final_report": str(result)
    }