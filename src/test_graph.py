from agents.graph import bi_graph

initial_state = {
    "query": "What are the growth trends in the Indian EdTech market?",
    "research_findings": None,
    "analysis": None,
    "final_report": None
}

final_state = bi_graph.invoke(initial_state)

print("=== FINAL REPORT ===")
print(final_state["final_report"])