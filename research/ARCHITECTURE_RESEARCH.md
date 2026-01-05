# Platform Architecture Research

## Summary

Multi-tenant AI agent platform architecture requires multiple isolation layers, robust state management, and comprehensive audit capabilities.

## Key Decisions

### Tenant Isolation: Layered Approach

1. **Database Layer**: PostgreSQL Row-Level Security (RLS)
   - Tenant context set on each connection
   - Database enforces isolation (application bugs can't leak data)

2. **Compute Layer**: Kubernetes namespaces + Network Policies
   - Namespace per tenant for resource isolation
   - Network policies for default-deny traffic

3. **Sandbox Layer**: gVisor or Firecracker
   - For code execution, use VM-level isolation
   - gVisor: Lower overhead, integrates with K8s
   - Firecracker: Stronger isolation, used by AWS Lambda

### Sandbox Comparison

| Solution | Isolation | Startup | Use Case |
|----------|-----------|---------|----------|
| Firecracker | Hardware (KVM) | ~125ms | Highest security needs |
| gVisor | Userspace kernel | ~50ms | Container hardening |
| E2B | Cloud sandbox | ~2-5s | Managed code execution |
| Docker | Namespace/cgroups | ~1s | Trusted workloads only |

**Recommendation**: gVisor for most agent execution, E2B for convenience during development

### State Management: LangGraph + PostgreSQL

```python
# LangGraph checkpointing pattern
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)

    # Thread-based persistence
    config = {"configurable": {"thread_id": f"{tenant_id}:{session_id}"}}
    result = await graph.ainvoke(state, config=config)
```

**Key Features:**
- Automatic checkpoints at each step
- History traversal for debugging
- Resume from last checkpoint on failure
- Parent-child propagation for subgraphs

### Credential Management

**Per-Tenant Encryption:**
- Derive tenant-specific keys from master key using HKDF
- Store encrypted credentials in dedicated vault
- Audit all credential access
- Implement automatic rotation

```python
# Key derivation pattern
tenant_key = HKDF(master_key, salt=None, info=tenant_id.encode())
cipher = Fernet(tenant_key)
encrypted = cipher.encrypt(credential.encode())
```

### Rate Limiting & Cost Tracking

**Token Bucket with Redis:**
- Per-tenant, per-resource limits
- Sliding window counter
- Track token usage for billing

**Cost Tracking:**
- Log all LLM calls with token counts
- Calculate costs per model
- Aggregate by tenant for billing

### Audit Logging

**Two-Level Approach:**
1. **Full Replay** (Development): Every thought, tool call, state change
2. **Decision Log** (Customers): Key decisions with reasoning

**Critical Events to Log:**
- Authentication events
- Agent actions (code executed, tools called)
- Data access
- Credential usage
- Cost events

## Reference Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│              TLS, Rate Limiting, Auth                           │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Auth Service │     │Agent Control │     │ Execution    │
│  (Keycloak)  │     │   Plane      │     │   Plane      │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PostgreSQL  │     │    Redis     │     │  Vector DB   │
│  (RLS)       │     │  (Cache)     │     │  (Pinecone)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Technology Choices

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Database | PostgreSQL | RLS, JSONB, mature |
| Cache | Redis | Rate limiting, pub/sub |
| Orchestration | LangGraph | Checkpointing, state management |
| Containers | Kubernetes | Industry standard |
| Sandbox | gVisor/E2B | Security + convenience |
| Secrets | HashiCorp Vault or custom | Per-tenant encryption |
| Observability | OpenTelemetry + Datadog | Distributed tracing |

---
*Research completed: 2025-01-05*
