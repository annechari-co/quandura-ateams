# Research & Design Documents

This folder contains research findings and design specs that will inform Quandura development.

## Contents

| Document | Description | Status |
|----------|-------------|--------|
| `UNIQ_SPEC.md` | Token-efficient agent communication grammar | Ready for implementation |
| `GHOST_TOWN.md` | Analysis of Steve Yegge's agent framework | Pending |
| `AGENT_LANGUAGE.md` | Agent-specific language concepts | Pending |

## How These Fit Together

```
UNI-Q (communication)     →  How agents talk to each other efficiently
Ghost Town (framework)    →  How to structure agent teams (TBD)
Agent Language (DSL)      →  How agents reason internally (TBD)
```

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
