from agents.deep_crew import run_deep_analysis

result = run_deep_analysis("What are the growth trends in the Indian EdTech market?")

print("=== RESEARCH ===")
print(result["research"])
print("\n=== CRITIQUE ===")
print(result["critique"])
print("\n=== FINAL REPORT ===")
print(result["final_report"])