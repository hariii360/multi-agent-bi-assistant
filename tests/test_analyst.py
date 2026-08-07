from agents.researcher import researcher_node
from agents.analyst import analyst_node

test_state = {
    "query": "What are the growth trends in the Indian EdTech market?",
    "research_findings": None,
    "analysis": None,
    "final_report": None
}

state_after_research = researcher_node(test_state)
state_after_analysis = analyst_node(state_after_research)

print("=== RESEARCH ===")
print(state_after_research["research_findings"])
print("\n=== ANALYSIS ===")
print(state_after_analysis["analysis"])