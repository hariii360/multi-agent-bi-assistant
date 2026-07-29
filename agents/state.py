from typing import TypedDict, Optional

class AgentState(TypedDict):
    query: str
    research_findings: Optional[str]
    analysis: Optional[str]
    final_report: Optional[str]