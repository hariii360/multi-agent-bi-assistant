import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.chroma_client import collection
from agents.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def retrieve_context(query: str, n_results: int = 2) -> str:
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    documents = results.get("documents", [[]])[0]
    return "\n\n".join(documents) if documents else "No relevant documents found in knowledge base."

def researcher_node(state: AgentState) -> AgentState:
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
    state["research_findings"] = response.content
    return state