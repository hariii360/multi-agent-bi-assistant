from fastapi import FastAPI
from pydantic import BaseModel
from agents.graph import bi_graph

app = FastAPI(title="Multi-Agent BI Assistant")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "BI Assistant is running"}

@app.post("/analyze")
def analyze(request: QueryRequest):
    initial_state = {
        "query": request.query,
        "research_findings": None,
        "analysis": None,
        "final_report": None
    }

    final_state = bi_graph.invoke(initial_state)

    return {
        "query": request.query,
        "research_findings": final_state["research_findings"],
        "analysis": final_state["analysis"],
        "final_report": final_state["final_report"]
    }