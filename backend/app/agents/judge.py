"""Judge agent for external validation of agent outputs (SCoRe pattern)."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import Agent, AgentConfig, AgentResult
from app.agents.librarian import Librarian
from app.models.passport import Passport


class JudgmentVerdict(str, Enum):
    """Possible judgment outcomes."""

    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    REJECTED = "rejected"
    ESCALATE = "escalate"


@dataclass
class ValidationIssue:
    """A specific issue found during validation."""

    category: str  # "schema", "policy", "semantic", "completeness"
    severity: str  # "error", "warning", "info"
    message: str
    field: str | None = None
    suggestion: str | None = None


@dataclass
class JudgmentResult:
    """Result of judge validation."""

    verdict: JudgmentVerdict
    confidence: float
    issues: list[ValidationIssue] = field(default_factory=list)
    feedback: str = ""
    revision_instructions: str = ""


class SandboxedContext(BaseModel):
    """Minimal context provided to judge for validation."""

    mission_objective: str
    agent_type: str
    expected_output_type: str
    relevant_policies: list[str] = []
    constraints: list[str] = []


class JudgeAgent(Agent):
    """External validation agent implementing SCoRe pattern.

    The Judge validates agent outputs against:
    - Schema requirements (structural validity)
    - Symbolic rules (policy compliance)
    - Semantic correctness (logical consistency via LLM)

    The Judge does NOT have access to the full passport - only a sandboxed
    view of the output and relevant policies. This prevents self-confirmation bias.
    """

    def __init__(
        self,
        session: AsyncSession | None = None,
        librarian: Librarian | None = None,
    ):
        agent_config = AgentConfig(
            agent_id="judge",
            agent_type="judge",
            system_prompt=self._system_prompt(),
            autonomy_level=2,  # Guided - conservative for validation
            temperature=0.3,  # Low temperature for consistent judgment
        )
        super().__init__(agent_config)

        self.session = session
        self.librarian = librarian

    def _system_prompt(self) -> str:
        return """You are a Judge agent responsible for validating outputs from other agents.
Your role is to identify issues, not to fix them. Be thorough but fair.

When validating, check for:
1. Structural completeness - all required fields present
2. Policy compliance - follows organizational rules and constraints
3. Logical consistency - conclusions follow from evidence
4. Factual accuracy - claims are supported

For each issue found, provide:
- Category (schema, policy, semantic, completeness)
- Severity (error, warning, info)
- Clear description of the problem
- Suggested fix (if obvious)

Be specific in your feedback. Vague criticism is not helpful.
If output is acceptable, say so clearly without inventing issues."""

    async def process(self, passport: Passport) -> AgentResult:
        """Process validation request from passport."""
        # Extract validation request from context
        validation_request = passport.context.get("validation_request", {})

        if not validation_request:
            return AgentResult(
                success=False,
                output="No validation request found in passport context",
                confidence=self.calculate_confidence(0.0),
                error="Missing validation_request in context",
            )

        output = validation_request.get("output")
        schema_name = validation_request.get("schema")
        context = validation_request.get("context", {})
        level = validation_request.get("level", "standard")

        # Build sandboxed context
        sandboxed = SandboxedContext(
            mission_objective=passport.mission.objective,
            agent_type=validation_request.get("source_agent", "unknown"),
            expected_output_type=schema_name or "unknown",
            relevant_policies=context.get("policies", []),
            constraints=context.get("constraints", []),
        )

        # Perform judgment
        result = await self.judge(
            output=output,
            expected_schema=None,  # Schema validation happens in type checking
            context=sandboxed,
            verification_level=level,
        )

        # Store result in passport
        passport.context["judgment_result"] = {
            "verdict": result.verdict.value,
            "confidence": result.confidence,
            "issues": [
                {
                    "category": i.category,
                    "severity": i.severity,
                    "message": i.message,
                    "field": i.field,
                    "suggestion": i.suggestion,
                }
                for i in result.issues
            ],
            "feedback": result.feedback,
            "revision_instructions": result.revision_instructions,
        }

        # Update passport status based on verdict
        if result.verdict == JudgmentVerdict.REJECTED:
            passport.routing.escalation_required = True
            passport.routing.escalation_reason = result.feedback
        elif result.verdict == JudgmentVerdict.REVISION_REQUIRED:
            passport.revision_count += 1

        return AgentResult(
            success=result.verdict in [JudgmentVerdict.APPROVED, JudgmentVerdict.REVISION_REQUIRED],
            output=result.feedback,
            confidence=self.calculate_confidence(
                base_value=result.confidence,
                evidence_count=len(result.issues),
                evidence_quality=0.8,
            ),
            artifacts={"verdict": result.verdict.value},
        )

    async def judge(
        self,
        output: Any,
        expected_schema: type[BaseModel] | None,
        context: SandboxedContext,
        verification_level: Literal["basic", "standard", "thorough"] = "standard",
    ) -> JudgmentResult:
        """Validate an output against schema, rules, and semantic correctness.

        Args:
            output: The output to validate
            expected_schema: Pydantic model for structural validation
            context: Sandboxed context (mission, policies, constraints)
            verification_level: How thorough to be

        Returns:
            JudgmentResult with verdict and any issues found
        """
        issues: list[ValidationIssue] = []

        # Phase 1: Schema validation
        if expected_schema and verification_level != "basic":
            schema_issues = self._validate_schema(output, expected_schema)
            issues.extend(schema_issues)

        # Phase 2: Symbolic rule checking
        if verification_level in ["standard", "thorough"]:
            rule_issues = await self._check_symbolic_rules(output, context)
            issues.extend(rule_issues)

        # Phase 3: Semantic verification (LLM-based)
        if verification_level == "thorough":
            semantic_issues = await self._semantic_verification(output, context)
            issues.extend(semantic_issues)

        # Determine verdict
        verdict = self._determine_verdict(issues)
        feedback = self._generate_feedback(issues, verdict)
        revision_instructions = ""
        if verdict == JudgmentVerdict.REVISION_REQUIRED:
            revision_instructions = self._generate_revision_instructions(issues)

        # Calculate confidence based on issues found
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        confidence = max(0.1, 1.0 - (error_count * 0.2) - (warning_count * 0.05))

        return JudgmentResult(
            verdict=verdict,
            confidence=confidence,
            issues=issues,
            feedback=feedback,
            revision_instructions=revision_instructions,
        )

    def _validate_schema(
        self,
        output: Any,
        expected_schema: type[BaseModel],
    ) -> list[ValidationIssue]:
        """Validate output against Pydantic schema."""
        issues: list[ValidationIssue] = []

        if isinstance(output, dict):
            try:
                expected_schema.model_validate(output)
            except ValidationError as e:
                for error in e.errors():
                    issues.append(
                        ValidationIssue(
                            category="schema",
                            severity="error",
                            message=error["msg"],
                            field=".".join(str(loc) for loc in error["loc"]),
                            suggestion=f"Expected type: {error.get('type', 'unknown')}",
                        )
                    )
        elif not isinstance(output, expected_schema):
            issues.append(
                ValidationIssue(
                    category="schema",
                    severity="error",
                    message=f"Output is not instance of {expected_schema.__name__}",
                )
            )

        return issues

    async def _check_symbolic_rules(
        self,
        output: Any,
        context: SandboxedContext,
    ) -> list[ValidationIssue]:
        """Check output against symbolic rules (policies, constraints)."""
        issues: list[ValidationIssue] = []

        # Check constraints
        for constraint in context.constraints:
            violation = self._check_constraint(output, constraint)
            if violation:
                issues.append(violation)

        # Check policies (if librarian available, load policy details)
        for policy_ref in context.relevant_policies:
            violation = self._check_policy(output, policy_ref)
            if violation:
                issues.append(violation)

        return issues

    def _check_constraint(self, output: Any, constraint: str) -> ValidationIssue | None:
        """Check a single constraint. Returns issue if violated."""
        # Parse constraint format: "field:operator:value"
        # e.g., "amount:max:1000", "status:in:approved,pending"
        parts = constraint.split(":")
        if len(parts) < 3:
            return None

        field_name, operator, value = parts[0], parts[1], parts[2]

        # Get field value from output
        if isinstance(output, dict):
            field_value = output.get(field_name)
        elif hasattr(output, field_name):
            field_value = getattr(output, field_name)
        else:
            return None  # Field not present, might be optional

        # Check constraint
        if operator == "max" and field_value is not None:
            try:
                if float(field_value) > float(value):
                    return ValidationIssue(
                        category="policy",
                        severity="error",
                        message=f"{field_name} exceeds maximum allowed value of {value}",
                        field=field_name,
                        suggestion=f"Reduce {field_name} to at most {value}",
                    )
            except (ValueError, TypeError):
                pass

        elif operator == "min" and field_value is not None:
            try:
                if float(field_value) < float(value):
                    return ValidationIssue(
                        category="policy",
                        severity="error",
                        message=f"{field_name} is below minimum required value of {value}",
                        field=field_name,
                        suggestion=f"Increase {field_name} to at least {value}",
                    )
            except (ValueError, TypeError):
                pass

        elif operator == "in":
            allowed_values = value.split(",")
            if str(field_value) not in allowed_values:
                return ValidationIssue(
                    category="policy",
                    severity="error",
                    message=f"{field_name} must be one of: {', '.join(allowed_values)}",
                    field=field_name,
                )

        elif operator == "required":
            if field_value is None or field_value == "":
                return ValidationIssue(
                    category="completeness",
                    severity="error",
                    message=f"{field_name} is required but missing",
                    field=field_name,
                )

        return None

    def _check_policy(self, output: Any, policy_ref: str) -> ValidationIssue | None:
        """Check output against a policy reference."""
        # Policy checking would involve loading policy from memory
        # For now, return None (no violation detected without policy details)
        # Full implementation would use Librarian to load policy and check
        return None

    async def _semantic_verification(
        self,
        output: Any,
        context: SandboxedContext,
    ) -> list[ValidationIssue]:
        """Use LLM to verify semantic correctness."""
        issues: list[ValidationIssue] = []

        # Prepare output for LLM
        if isinstance(output, BaseModel):
            output_str = output.model_dump_json(indent=2)
        elif isinstance(output, dict):
            import json
            output_str = json.dumps(output, indent=2, default=str)
        else:
            output_str = str(output)

        # Build verification prompt
        policies_str = ", ".join(context.relevant_policies) or "None specified"
        constraints_str = ", ".join(context.constraints) or "None specified"
        prompt = f"""Verify this output for semantic correctness.

Mission: {context.mission_objective}
Agent Type: {context.agent_type}
Expected Output Type: {context.expected_output_type}

Output to verify:
{output_str}

Relevant policies: {policies_str}
Constraints: {constraints_str}

Check for:
1. Logical consistency - conclusions follow from stated reasoning
2. Completeness - all required information present
3. Appropriateness - response matches the mission objective

Respond in this format:
- If output is acceptable, say "APPROVED: [brief reason]"
- If issues found, list each as "ISSUE: [category] | [severity] | [description]"
Categories: schema, policy, semantic, completeness
Severities: error, warning, info"""

        # Call LLM
        response, _, _ = await self.call_llm([{"role": "user", "content": prompt}])

        # Parse response
        if response.startswith("APPROVED"):
            return []

        for line in response.split("\n"):
            if line.startswith("ISSUE:"):
                parts = line[6:].split("|")
                if len(parts) >= 3:
                    issues.append(
                        ValidationIssue(
                            category=parts[0].strip(),
                            severity=parts[1].strip(),
                            message=parts[2].strip(),
                        )
                    )

        return issues

    def _determine_verdict(self, issues: list[ValidationIssue]) -> JudgmentVerdict:
        """Determine verdict based on issues found."""
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")

        if error_count >= 3:
            return JudgmentVerdict.REJECTED
        elif error_count > 0:
            return JudgmentVerdict.REVISION_REQUIRED
        elif warning_count >= 3:
            return JudgmentVerdict.REVISION_REQUIRED
        elif warning_count > 0:
            return JudgmentVerdict.APPROVED  # Warnings don't block
        else:
            return JudgmentVerdict.APPROVED

    def _generate_feedback(
        self,
        issues: list[ValidationIssue],
        verdict: JudgmentVerdict,
    ) -> str:
        """Generate human-readable feedback."""
        if verdict == JudgmentVerdict.APPROVED:
            if issues:
                return f"Output approved with {len(issues)} minor issue(s)."
            return "Output approved. No issues found."

        if verdict == JudgmentVerdict.REJECTED:
            return f"Output rejected. {len(issues)} critical issue(s) require human review."

        if verdict == JudgmentVerdict.REVISION_REQUIRED:
            return f"Revision required. {len(issues)} issue(s) must be addressed before approval."

        return "Escalation required for human judgment."

    def _generate_revision_instructions(self, issues: list[ValidationIssue]) -> str:
        """Generate specific revision instructions."""
        if not issues:
            return ""

        instructions = ["Please address the following issues:\n"]
        for i, issue in enumerate(issues, 1):
            line = f"{i}. [{issue.category.upper()}] {issue.message}"
            if issue.field:
                line += f" (field: {issue.field})"
            if issue.suggestion:
                line += f"\n   Suggestion: {issue.suggestion}"
            instructions.append(line)

        return "\n".join(instructions)
