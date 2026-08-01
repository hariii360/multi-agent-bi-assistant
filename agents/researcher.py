import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import chromadb
from chromadb.utils import embedding_functions
from agents.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

CHROMA_PATH = "chroma_db"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name="bi_knowledge_base",
    embedding_function=embedding_fn
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