"""Python helper for n8n REST API — workflow control and execution history.
Uses n8n's public REST API v1 to activate/deactivate the BI Assistant
workflow and retrieve recent execution history for the Streamlit status panel.
"""
import os
import httpx
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
N8N_WORKFLOW_ID = os.getenv("N8N_WORKFLOW_ID", "")

_headers = {"X-N8N-API-KEY": N8N_API_KEY}


def get_workflow_status() -> dict:
    """Fetch the workflow metadata including active/inactive status."""
    try:
        resp = httpx.get(
            f"{N8N_BASE_URL}/api/v1/workflows/{N8N_WORKFLOW_ID}",
            headers=_headers, timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        return {"id": data["id"], "name": data["name"], "active": data["active"]}
    except httpx.ConnectError:
        logger.warning("[n8n] Cannot connect — is n8n running?")
        return {"id": N8N_WORKFLOW_ID, "name": "unknown", "active": None, "error": "n8n unreachable"}
    except Exception as e:
        logger.error(f"[n8n] Failed to fetch workflow status: {e}")
        return {"id": N8N_WORKFLOW_ID, "name": "unknown", "active": None, "error": str(e)}


def activate_workflow() -> dict:
    """Activate the BI Assistant workflow via n8n's dedicated activate endpoint."""
    try:
        resp = httpx.post(
            f"{N8N_BASE_URL}/api/v1/workflows/{N8N_WORKFLOW_ID}/activate",
            headers=_headers, timeout=5
        )
        resp.raise_for_status()
        logger.info("[n8n] Workflow activated")
        return resp.json()
    except Exception as e:
        logger.error(f"[n8n] Failed to activate workflow: {e}")
        return {"active": None, "error": str(e)}


def deactivate_workflow() -> dict:
    """Deactivate the BI Assistant workflow via n8n's dedicated deactivate endpoint."""
    try:
        resp = httpx.post(
            f"{N8N_BASE_URL}/api/v1/workflows/{N8N_WORKFLOW_ID}/deactivate",
            headers=_headers, timeout=5
        )
        resp.raise_for_status()
        logger.info("[n8n] Workflow deactivated")
        return resp.json()
    except Exception as e:
        logger.error(f"[n8n] Failed to deactivate workflow: {e}")
        return {"active": None, "error": str(e)}


def get_execution_history(limit: int = 5) -> list[dict]:
    """Fetch the most recent workflow executions.
    Returns a list of dicts with: id, status, started_at, stopped_at, mode.
    """
    try:
        resp = httpx.get(
            f"{N8N_BASE_URL}/api/v1/executions",
            headers=_headers,
            params={"workflowId": N8N_WORKFLOW_ID, "limit": limit},
            timeout=5,
        )
        resp.raise_for_status()
        executions = resp.json().get("data", [])
        return [
            {
                "id": ex["id"],
                "status": ex.get("status", ex.get("finished", "unknown")),
                "started_at": ex.get("startedAt"),
                "stopped_at": ex.get("stoppedAt"),
                "mode": ex.get("mode"),
            }
            for ex in executions
        ]
    except httpx.ConnectError:
        return []
    except Exception as e:
        logger.error(f"[n8n] Failed to fetch execution history: {e}")
        return []