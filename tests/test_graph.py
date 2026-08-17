from agents.fast_graph import researcher_node, analyst_node, writer_node, bi_graph

test_query = "What are the growth trends in the Indian EdTech market?"

print("=" * 60)
print("TEST 1: Researcher node standalone")
print("=" * 60)

state = {"query": test_query, "research_findings": None, "analysis": None, "final_report": None}
delta = researcher_node(state)
state.update(delta)
print(state["research_findings"])

print("\n" + "=" * 60)
print("TEST 2: Researcher -> Analyst chained")
print("=" * 60)

delta = analyst_node(state)
state.update(delta)
print(state["analysis"])

print("\n" + "=" * 60)
print("TEST 3: Full graph (Researcher -> Analyst -> Writer)")
print("=" * 60)

initial_state = {"query": test_query, "research_findings": None, "analysis": None, "final_report": None}
final_state = bi_graph.invoke(initial_state)

print("\n--- Research ---")
print(final_state["research_findings"])
print("\n--- Analysis ---")
print(final_state["analysis"])
print("\n--- Final Report ---")
print(final_state["final_report"])