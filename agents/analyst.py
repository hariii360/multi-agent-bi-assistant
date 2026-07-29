import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from agents.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def analyst_node(state: AgentState) -> AgentState:
    query = state["query"]
    research = state["research_findings"]

    prompt = f"""You are a Senior Business Analyst.

Original question: "{query}"

Research findings to analyze:
\"\"\"{research}\"\"\"

Based on this research, identify:
1. Key trends or patterns
2. Potential risks or challenges
3. Opportunities worth highlighting

Be structured and analytical. Use clear headers for each section.
"""

    response = llm.invoke(prompt)
    state["analysis"] = response.content
    return state