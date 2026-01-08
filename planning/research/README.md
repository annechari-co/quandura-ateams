# Research & Design Documents

This folder contains research findings and design specs that will inform Quandura development.

## Contents

| Document | Description | Status |
|----------|-------------|--------|
| `UNIQ_SPEC.md` | Token-efficient agent communication grammar | Ready for implementation |
| `UNIQ_EXAMPLES.md` | Practical scenarios: decision traces, cross-team coordination | Ready for implementation |
| `SCENARIO_OHS_INSPECTION.md` | Full lifecycle scenario: inspection → invoice → closure | Reference |
| `DECISION_LOG.md` | Systematic analysis of architectural decisions | In Progress |
| `token_count.py` | Token efficiency benchmarks (tiktoken) | Complete |
| `uniq_benchmark.py` | LLM reasoning quality benchmarks (needs API key) | Draft |
| `GHOST_TOWN.md` | Analysis of Steve Yegge's Gas Town framework | Complete |
| `AGENT_LANGUAGE.md` | Agent-specific language concepts | Pending |

## How These Fit Together

```
UNI-Q (communication)     →  How agents talk to each other efficiently
Gas Town (framework)      →  Agent lifecycle, health monitoring, escalation patterns
Agent Language (DSL)      →  How agents reason internally (TBD)
```

### Key Patterns from Gas Town Analysis

1. **Propulsion Principle** - Immediate execution on assignment (aligns with UNI-Q subscriptions)
2. **Three-Layer Lifecycle** - Session (ephemeral) / Sandbox (persistent) / Identity (persistent)
3. **Watchdog Chain** - Mechanical heartbeat + intelligent triage for health monitoring
4. **Structured Escalation** - Severity levels + categories + tiered routing
5. **Molecule Tracking** - Step-by-step workflow progress

## Integration with Quandura

These research items affect:

1. **Memory System** - UNI-Q micro format, resolution contracts
2. **Orchestrator** - Subscription registry, message routing
3. **Agent Base Class** - Query intent, zoom-in logic
4. **Team Architecture** - Cross-team coordination patterns

## Implementation Priority

1. UNI-Q core grammar (symbols, parsing)
2. Smart resolution system (intent, prefetch, confidence)
3. Evaluate Ghost Town patterns for team structure
4. Consider agent language for complex reasoning

---

*Created: 2025-01-08*
