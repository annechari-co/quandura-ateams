"""Basic 2-agent team (Triage + Executor) for validation."""

from app.agents.executor import ExecutorAgent
from app.agents.triage import TriageAgent
from app.platform.orchestrator import Orchestrator, TeamConfig


def create_basic_team(team_id: str = "basic") -> Orchestrator:
    """Create a basic 2-agent team for testing."""
    triage = TriageAgent()
    executor = ExecutorAgent()

    config = TeamConfig(
        team_id=team_id,
        team_type="basic",
        agents={
            "triage": triage,
            "executor": executor,
        },
        entry_point="triage",
        routing_rules={
            "triage": {
                "default": "executor",
            },
            "executor": {
                "status:completed": "end",
                "status:failed": "end",
                "default": "end",
            },
        },
    )

    return Orchestrator(config)
