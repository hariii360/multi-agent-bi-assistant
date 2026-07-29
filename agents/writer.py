import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from agents.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def writer_node(state: AgentState) -> AgentState:
    query = state["query"]
    analysis = state["analysis"]

    prompt = f"""You are a Business Report Writer.

Original question: "{query}"

Analyst's findings:
\"\"\"{analysis}\"\"\"

Write a clean, professional business report summarizing this for a
non-technical stakeholder. Use a short title, an executive summary
(2-3 sentences), and bullet points for key takeaways. Keep it concise.
"""

    response = llm.invoke(prompt)
    state["final_report"] = response.content
    return state