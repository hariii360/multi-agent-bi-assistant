import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from src.chroma_client import collection

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY")
)


class AgentState(TypedDict):
    query: str
    research_findings: Optional[str]
    analysis: Optional[str]
    final_report: Optional[str]


def retrieve_context(query: str, n_results: int = 2) -> str:
    results = collection.query(query_texts=[query], n_results=n_results)
    documents = results.get("documents", [[]])[0]
    return "\n\n".join(documents) if documents else "No relevant documents found in knowledge base."


def researcher_node(state: AgentState) -> dict:
    query = state["query"]
    retrieved_context = retrieve_context(query)

    prompt = f"""You are a Business Research Analyst.

Retrieved knowledge base context:
\"\"\"{retrieved_context}\"\"\"

Given this business question: "{query}"

Using the retrieved context above as your primary source, summarize
relevant background information, key facts, and context that would
help analyze this topic. If the context doesn't fully cover the question,
you may supplement with general knowledge, but prioritize the retrieved
context and note when you're doing so.
"""
    response = llm.invoke(prompt)
    return {"research_findings": response.content}


def analyst_node(state: AgentState) -> dict:
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
    return {"analysis": response.content}


def writer_node(state: AgentState) -> dict:
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
    return {"final_report": response.content}


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()


bi_graph = build_graph()