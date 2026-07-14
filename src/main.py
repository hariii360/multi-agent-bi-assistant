from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Multi-Agent BI Assistant")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "BI Assistant is running"}

@app.post("/analyze")
def analyze(request: QueryRequest):
    # Placeholder — agent logic will plug in here in Task 4/5
    return {"query": request.query, "result": "pipeline not yet connected"}