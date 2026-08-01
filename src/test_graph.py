from agents.graph import bi_graph

initial_state = {
    "query": "How is Tier-2 and Tier-3 city adoption affecting Indian EdTech growth?",
    "research_findings": None,
    "analysis": None,
    "final_report": None
}

final_state = bi_graph.invoke(initial_state)

print("=== FINAL REPORT ===")
print(final_state["final_report"])