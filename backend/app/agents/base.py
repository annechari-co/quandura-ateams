"""Base agent class with confidence tracking and tool execution."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from app.core.config import get_settings
from app.models.passport import ConfidenceVector, Passport


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    agent_id: str
    agent_type: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = ""
    tools: list[dict[str, Any]] = []
    autonomy_level: int = 1  # 1-5, per de-scaffolding spec


@dataclass
class AgentResult:
    """Result from agent execution."""

    success: bool
    output: str
    confidence: ConfidenceVector
    tool_calls: list[str] = field(default_factory=list)
    tokens_used: int = 0
    duration_ms: int = 0
    error: str | None = None
    artifacts: dict[str, str] = field(default_factory=dict)


class Agent(ABC):
    """Base class for all agents with confidence tracking."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.settings = get_settings()
        self.client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        self._calibration_history: list[tuple[float, bool]] = []

    @property
    def agent_id(self) -> str:
        return self.config.agent_id

    @abstractmethod
    async def process(self, passport: Passport) -> AgentResult:
        """Process the passport and return results.

        Args:
            passport: Current passport state

        Returns:
            Result of agent processing
        """
        pass

    async def execute(self, passport: Passport) -> Passport:
        """Execute agent logic and update passport."""
        start_time = time.time()
        passport.current_agent = self.agent_id

        try:
            result = await self.process(passport)
            duration_ms = int((time.time() - start_time) * 1000)

            # Update passport with results
            passport.add_ledger_entry(
                agent_id=self.agent_id,
                action=f"{self.config.agent_type}_process",
                inputs_summary=self._summarize_inputs(passport),
                outputs_summary=result.output[:500] if result.output else "",
                duration_ms=duration_ms,
                confidence=result.confidence,
                tokens_used=result.tokens_used,
                tool_calls=result.tool_calls,
            )

            # Update artifacts
            for name, ref in result.artifacts.items():
                passport.artifacts[name] = ref

            # Update overall confidence using weighted average
            self._update_overall_confidence(passport, result.confidence)

            if not result.success:
                passport.status = "blocked" if result.error else "failed"
                passport.routing.escalation_required = True
                passport.routing.escalation_reason = result.error

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            passport.add_ledger_entry(
                agent_id=self.agent_id,
                action=f"{self.config.agent_type}_error",
                inputs_summary=self._summarize_inputs(passport),
                outputs_summary=f"Error: {str(e)}",
                duration_ms=duration_ms,
                confidence=ConfidenceVector(value=0.0),
                notes=str(e),
            )
            passport.status = "failed"
            passport.routing.escalation_required = True
            passport.routing.escalation_reason = str(e)

        return passport

    async def call_llm(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> tuple[str, list[dict[str, Any]], int]:
        """Call the LLM and return response, tool calls, and token count."""
        response = await self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self.config.system_prompt,
            messages=messages,
            tools=tools or self.config.tools or [],
        )

        text_content = ""
        tool_uses = []

        for block in response.content:
            if block.type == "text":
                text_content = block.text
            elif block.type == "tool_use":
                tool_uses.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        return text_content, tool_uses, total_tokens

    def calculate_confidence(
        self,
        base_value: float,
        evidence_count: int = 0,
        evidence_quality: float = 0.5,
    ) -> ConfidenceVector:
        """Calculate confidence vector with historical calibration."""
        # Historical accuracy from past predictions
        historical_accuracy = self._get_historical_accuracy()

        return ConfidenceVector(
            value=base_value,
            evidence_count=evidence_count,
            evidence_quality=evidence_quality,
            historical_accuracy=historical_accuracy,
            calibration_samples=len(self._calibration_history),
        )

    def record_outcome(self, predicted_confidence: float, was_correct: bool) -> None:
        """Record outcome for calibration (called after human review)."""
        self._calibration_history.append((predicted_confidence, was_correct))
        # Keep last 100 samples
        if len(self._calibration_history) > 100:
            self._calibration_history.pop(0)

    def _get_historical_accuracy(self) -> float:
        """Calculate historical accuracy from calibration samples."""
        if not self._calibration_history:
            return 0.5  # Prior

        correct = sum(1 for _, was_correct in self._calibration_history if was_correct)
        return correct / len(self._calibration_history)

    def _summarize_inputs(self, passport: Passport) -> str:
        """Create summary of passport inputs for ledger."""
        return f"Mission: {passport.mission.objective[:100]}; Status: {passport.status}"

    def _update_overall_confidence(
        self, passport: Passport, new_confidence: ConfidenceVector
    ) -> None:
        """Update passport's overall confidence with new agent confidence."""
        current = passport.overall_confidence
        # Weighted average favoring more evidence
        total_evidence = current.evidence_count + new_confidence.evidence_count
        if total_evidence == 0:
            weight = 0.5
        else:
            weight = new_confidence.evidence_count / total_evidence

        passport.overall_confidence = ConfidenceVector(
            value=(1 - weight) * current.value + weight * new_confidence.value,
            evidence_count=total_evidence,
            evidence_quality=(current.evidence_quality + new_confidence.evidence_quality) / 2,
            historical_accuracy=(current.historical_accuracy + new_confidence.historical_accuracy)
            / 2,
            calibration_samples=current.calibration_samples + new_confidence.calibration_samples,
        )

    def can_act_autonomously(self, confidence: float) -> bool:
        """Check if agent can act without human approval based on autonomy level."""
        # De-scaffolding thresholds per architecture doc
        thresholds = {
            1: 0.95,  # Structured - needs high confidence
            2: 0.85,  # Guided
            3: 0.75,  # Collaborative
            4: 0.60,  # Supervised
            5: 0.40,  # Autonomous
        }
        return confidence >= thresholds.get(self.config.autonomy_level, 0.95)
