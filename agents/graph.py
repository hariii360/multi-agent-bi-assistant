from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.writer import writer_node

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