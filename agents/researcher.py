import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from agents.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def researcher_node(state: AgentState) -> AgentState:
    query = state["query"]

    prompt = f"""You are a Business Research Analyst.
Given this business question: "{query}"

Provide relevant background information, key facts, and context
that would help analyze this topic. Be factual and concise.
Do not make up specific statistics — focus on structure and known context.
"""

    response = llm.invoke(prompt)
    state["research_findings"] = response.content
    return state