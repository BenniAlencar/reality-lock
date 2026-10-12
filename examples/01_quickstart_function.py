"""
Example 01: Quickstart Function Guard with @reality_locked.

Demonstrates how to protect any Python function with zero boilerplate.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reality_lock import RiskLevel, reality_locked


# 1. Protect a read-only inspection function (allowed automatically)
@reality_locked(risk=RiskLevel.READ_ONLY, intent="Read system telemetry")
def fetch_telemetry():
    return {"cluster_health": "nominal", "active_nodes": 4}


# 2. Protect a side-effecting action (requires explicit approval or policy clearance)
@reality_locked(risk=RiskLevel.EXTERNAL_MUTATION, intent="Notify team channel")
def dispatch_slack_alert(message: str):
    print(f"[SLACK BOT] Sent message: {message}")
    return {"delivered": True}


if __name__ == "__main__":
    print("--- Running Quickstart Example ---")
    data = fetch_telemetry()
    print("Telemetry result:", data)

    # In interactive environments, this triggers an operator confirmation prompt
    result = dispatch_slack_alert("Production deploy successful!")
    print("Alert result:", result)
