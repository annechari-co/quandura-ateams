"""Executor agent - performs the actual work based on triage routing."""

from app.agents.base import Agent, AgentConfig, AgentResult
from app.models.passport import ConfidenceVector, Passport

EXECUTOR_SYSTEM_PROMPT = """You are an execution specialist for a local government platform.

Your job is to:
1. Review the mission objective and triage analysis
2. Break down the work into concrete steps
3. Execute each step methodically
4. Produce a draft deliverable

For each mission, produce:
1. A step-by-step plan
2. Key findings or analysis
3. A draft output appropriate to the mission type

Be thorough but concise. Always cite sources when making factual claims.
If you encounter blockers or need information you don't have, clearly state what's needed.

Output your work in a structured format with sections:
## Plan
## Analysis
## Draft Output
## Confidence Assessment
## Next Steps (if any)"""


class ExecutorAgent(Agent):
    """Executes mission objectives based on triage routing."""

    def __init__(self, agent_id: str = "executor"):
        config = AgentConfig(
            agent_id=agent_id,
            agent_type="executor",
            system_prompt=EXECUTOR_SYSTEM_PROMPT,
            max_tokens=4096,
            temperature=0.7,
            autonomy_level=2,
        )
        super().__init__(config)

    async def process(self, passport: Passport) -> AgentResult:
        """Execute the mission objective."""
        # Get triage context
        triage = passport.context.get("triage_analysis", {})
        category = passport.context.get("category", "general")
        complexity = passport.context.get("complexity", "medium")

        messages = [
            {
                "role": "user",
                "content": f"""Execute this mission:

## Mission
Objective: {passport.mission.objective}
Department: {passport.mission.requester_department}
Matter Type: {passport.mission.matter_type}

## Constraints
{chr(10).join(f'- {c}' for c in passport.mission.constraints) or 'None specified'}

## Success Criteria
{chr(10).join(f'- {c}' for c in passport.mission.success_criteria) or 'None specified'}

## Triage Analysis
Category: {category}
Complexity: {complexity}
Additional Analysis: {triage.get('reasoning', 'N/A')}

## Context
{passport.context}

Execute this mission and provide your structured output.""",
            }
        ]

        try:
            response, tool_calls, tokens = await self.call_llm(messages)

            # Store the draft output
            passport.artifacts["draft_output"] = response
            passport.context["execution_complete"] = True

            # Determine confidence based on complexity and response quality
            base_confidence = {
                "low": 0.9,
                "medium": 0.75,
                "high": 0.6,
            }.get(complexity, 0.7)

            # Adjust based on response length (proxy for thoroughness)
            thoroughness_bonus = min(0.1, len(response) / 10000)

            confidence = self.calculate_confidence(
                base_value=min(0.95, base_confidence + thoroughness_bonus),
                evidence_count=1,
                evidence_quality=0.7,
            )

            # Check if mission can be marked complete
            if confidence.value >= 0.7 and not passport.routing.escalation_required:
                passport.status = "completed"
                passport.routing.next_agent = None
            else:
                # Needs review
                passport.routing.next_agent = "review"
                passport.routing.escalation_reason = "Requires human review before completion"

            return AgentResult(
                success=True,
                output=f"Execution complete. Confidence: {confidence.value:.2f}",
                confidence=confidence,
                tokens_used=tokens,
                artifacts={"draft_output": response},
            )

        except Exception as e:
            return AgentResult(
                success=False,
                output="",
                confidence=ConfidenceVector(value=0.0),
                error=str(e),
            )
