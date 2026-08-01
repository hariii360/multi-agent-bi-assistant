from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.graph import bi_graph
from src.logger import logger

app = FastAPI(title="Multi-Agent BI Assistant")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "BI Assistant is running"}

@app.post("/analyze")
def analyze(request: QueryRequest):
    if not request.query or not request.query.strip():
        logger.warning("Empty query received")
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"Received query: {request.query}")

    initial_state = {
        "query": request.query,
        "research_findings": None,
        "analysis": None,
        "final_report": None
    }

    try:
        final_state = bi_graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"Pipeline failed for query '{request.query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    logger.info(f"Successfully processed query: {request.query}")

    return {
        "query": request.query,
        "research_findings": final_state["research_findings"],
        "analysis": final_state["analysis"],
        "final_report": final_state["final_report"]
    }