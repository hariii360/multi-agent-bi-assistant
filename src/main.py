from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.fast_graph import bi_graph
from agents.deep_crew import run_deep_analysis
from src.logger import logger
from src.kb_routes import router as kb_router

app = FastAPI(title="Multi-Agent BI Assistant")

app.include_router(kb_router)

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

    logger.info(f"[LangGraph] Received query: {request.query}")

    initial_state = {
        "query": request.query,
        "research_findings": None,
        "analysis": None,
        "final_report": None
    }

    try:
        final_state = bi_graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"[LangGraph] Pipeline failed for query '{request.query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    logger.info(f"[LangGraph] Successfully processed query: {request.query}")

    return {
        "query": request.query,
        "mode": "fast",
        "research_findings": final_state["research_findings"],
        "analysis": final_state["analysis"],
        "final_report": final_state["final_report"]
    }

@app.post("/deep-analyze")
def deep_analyze(request: QueryRequest):
    if not request.query or not request.query.strip():
        logger.warning("Empty query received")
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"[CrewAI] Received deep-analysis query: {request.query}")

    try:
        result = run_deep_analysis(request.query)
    except Exception as e:
        logger.error(f"[CrewAI] Deep analysis failed for query '{request.query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deep analysis error: {str(e)}")

    logger.info(f"[CrewAI] Successfully processed deep-analysis query: {request.query}")

    return {
        "query": request.query,
        "mode": "deep",
        "research_findings": result["research"],
        "critique": result["critique"],
        "final_report": result["final_report"]
    }