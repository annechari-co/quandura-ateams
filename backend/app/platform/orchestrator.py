"""LangGraph-based orchestrator for agent teams."""

from dataclasses import dataclass, field
from typing import Any, Literal

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from app.agents.base import Agent
from app.models.passport import Passport


@dataclass
class TeamConfig:
    """Configuration for an agent team."""

    team_id: str
    team_type: str
    agents: dict[str, Agent]
    entry_point: str
    routing_rules: dict[str, dict[str, str]] = field(default_factory=dict)


class PassportState(BaseModel):
    """State wrapper for LangGraph."""

    passport: Passport
    iteration: int = 0
    max_iterations: int = 10


class Orchestrator:
    """Hub-and-spoke orchestrator using LangGraph."""

    def __init__(
        self,
        config: TeamConfig,
        checkpointer: BaseCheckpointSaver | None = None,
    ):
        self.config = config
        self.checkpointer = checkpointer
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        # Define state schema
        graph = StateGraph(PassportState)

        # Add node for each agent
        for agent_id, agent in self.config.agents.items():
            graph.add_node(agent_id, self._create_agent_node(agent))

        # Add routing node
        graph.add_node("router", self._route_passport)

        # Set entry point
        graph.set_entry_point(self.config.entry_point)

        # Add edges from entry point to router after processing
        graph.add_edge(self.config.entry_point, "router")

        # Add conditional edges from router
        for agent_id in self.config.agents:
            if agent_id != self.config.entry_point:
                graph.add_edge(agent_id, "router")

        # Add conditional routing from router to agents or END
        graph.add_conditional_edges(
            "router",
            self._determine_next,
            {
                **{agent_id: agent_id for agent_id in self.config.agents},
                "end": END,
            },
        )

        return graph.compile(checkpointer=self.checkpointer)

    def _create_agent_node(self, agent: Agent):
        """Create a node function for an agent."""

        async def node(state: PassportState) -> PassportState:
            passport = await agent.execute(state.passport)
            return PassportState(
                passport=passport,
                iteration=state.iteration + 1,
                max_iterations=state.max_iterations,
            )

        return node

    async def _route_passport(self, state: PassportState) -> PassportState:
        """Routing decision node (no-op, logic in _determine_next)."""
        return state

    def _determine_next(
        self, state: PassportState
    ) -> Literal["end"] | str:
        """Determine next agent based on passport state."""
        passport = state.passport

        # Check termination conditions
        if state.iteration >= state.max_iterations:
            return "end"

        if passport.status in ("completed", "failed", "escalated"):
            return "end"

        if passport.routing.escalation_required:
            return "end"

        # Use routing info from passport
        next_agent = passport.routing.next_agent
        if next_agent and next_agent in self.config.agents:
            return next_agent

        # Use team routing rules
        current_agent = passport.current_agent
        if current_agent and current_agent in self.config.routing_rules:
            rules = self.config.routing_rules[current_agent]
            # Simple status-based routing
            status_key = f"status:{passport.status}"
            if status_key in rules:
                return rules[status_key]
            if "default" in rules:
                return rules["default"]

        return "end"

    async def run(
        self,
        passport: Passport,
        thread_id: str | None = None,
    ) -> Passport:
        """Execute the team workflow on a passport."""
        initial_state = PassportState(passport=passport)

        config: dict[str, Any] = {}
        if thread_id and self.checkpointer:
            config["configurable"] = {"thread_id": thread_id}

        final_state = await self.graph.ainvoke(initial_state, config)
        return final_state.passport

    async def resume(
        self,
        thread_id: str,
        updates: dict[str, Any] | None = None,
    ) -> Passport:
        """Resume a paused workflow from checkpoint."""
        if not self.checkpointer:
            raise ValueError("Checkpointer required for resume")

        config = {"configurable": {"thread_id": thread_id}}

        if updates:
            # Get current state and apply updates
            state = await self.graph.aget_state(config)
            if state and state.values:
                current = state.values
                current.passport.context.update(updates)
                await self.graph.aupdate_state(config, current)

        final_state = await self.graph.ainvoke(None, config)
        return final_state.passport
