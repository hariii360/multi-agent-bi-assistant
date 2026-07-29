from agents.researcher import researcher_node

test_state = {
    "query": "What are the growth trends in the Indian EdTech market?",
    "research_findings": None,
    "analysis": None,
    "final_report": None
}

result = researcher_node(test_state)
print(result["research_findings"])