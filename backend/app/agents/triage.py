"""Triage agent - classifies incoming missions and routes them."""

from app.agents.base import Agent, AgentConfig, AgentResult
from app.models.passport import ConfidenceVector, Passport

TRIAGE_SYSTEM_PROMPT = """You are a triage specialist for a local government operations platform.

Your job is to:
1. Analyze incoming mission requests
2. Classify the type of work needed
3. Assess complexity and urgency
4. Determine the appropriate next agent/team

Output your analysis as JSON with these fields:
- category: The type of work (research, document_generation, analysis, communication)
- complexity: low, medium, high
- estimated_steps: Number of steps likely needed
- priority_adjustment: Whether to raise/lower priority based on content
- routing_recommendation: Which agent/team should handle this
- reasoning: Brief explanation of your classification

Be concise and accurate. When uncertain, flag for human review."""


class TriageAgent(Agent):
    """Classifies and routes incoming missions."""

    def __init__(self, agent_id: str = "triage"):
        config = AgentConfig(
            agent_id=agent_id,
            agent_type="triage",
            system_prompt=TRIAGE_SYSTEM_PROMPT,
            temperature=0.3,  # Lower temperature for consistent classification
            autonomy_level=2,
        )
        super().__init__(config)

    async def process(self, passport: Passport) -> AgentResult:
        """Analyze mission and determine routing."""
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this mission request:

Objective: {passport.mission.objective}
Department: {passport.mission.requester_department}
Matter Type: {passport.mission.matter_type}
Constraints: {', '.join(passport.mission.constraints) or 'None specified'}
Success Criteria: {', '.join(passport.mission.success_criteria) or 'None specified'}
Priority: {passport.routing.priority}

Additional Context:
{passport.context}

Provide your triage analysis as JSON.""",
            }
        ]

        try:
            response, tool_calls, tokens = await self.call_llm(messages)

            # Parse response to extract routing
            import json

            try:
                analysis = json.loads(response)
                routing_rec = analysis.get("routing_recommendation", "executor")
                complexity = analysis.get("complexity", "medium")
                category = analysis.get("category", "general")

                # Update passport context with triage results
                passport.context["triage_analysis"] = analysis
                passport.context["category"] = category
                passport.context["complexity"] = complexity

                # Set routing
                passport.routing.next_agent = routing_rec

                # Calculate confidence based on analysis clarity
                evidence_quality = 0.8 if "reasoning" in analysis else 0.5
                base_confidence = 0.85 if complexity != "high" else 0.7

                confidence = self.calculate_confidence(
                    base_value=base_confidence,
                    evidence_count=1,
                    evidence_quality=evidence_quality,
                )

                return AgentResult(
                    success=True,
                    output=f"Classified as {category} ({complexity}). Route: {routing_rec}",
                    confidence=confidence,
                    tokens_used=tokens,
                )

            except json.JSONDecodeError:
                # LLM didn't return valid JSON, try to extract key info
                passport.routing.next_agent = "executor"
                passport.context["triage_raw"] = response

                return AgentResult(
                    success=True,
                    output="Triage complete (fallback parsing). Routing to: executor",
                    confidence=self.calculate_confidence(
                        base_value=0.6,
                        evidence_count=1,
                        evidence_quality=0.4,
                    ),
                    tokens_used=tokens,
                )

        except Exception as e:
            return AgentResult(
                success=False,
                output="",
                confidence=ConfidenceVector(value=0.0),
                error=str(e),
            )
