from src.n8n_client import get_workflow_status, activate_workflow, get_execution_history

print("=== Workflow Status ===")
print(get_workflow_status())

print("\n=== Activating Workflow ===")
print(activate_workflow())

print("\n=== Recent Executions ===")
for ex in get_execution_history(limit=5):
    print(ex)