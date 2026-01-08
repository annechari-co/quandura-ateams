# Scenario: OHS Facility Inspection

*Reference document for system design - captures the workflow, not solutions*

## Context

- OHS Team interfaces with human consultant doing real-world facility inspections
- Consultant performs inspection for local county government (contract approved)
- Data/photos collected via Inspection App, stored where OHS Team has access
- This scenario tests the full lifecycle from data intake to job closure

## Workflow Stages

### Stage 1: Data Ingestion

**What happens:** Inspector completes field work, uploads data/photos via Inspection App.

**System interaction:**
```
External World (Inspection App) → [?] → OHS Team Orchestrator
```

**Questions raised:**
- How does external data enter our system?
- Where are artifacts (photos, raw data) stored?
- What triggers mission creation?

---

### Stage 2: Data Parsing & Distribution

**What happens:** OHS Team receives intake, parses raw data, routes to specialists.

**Actors:**
- OHS Orchestrator
- Data Parser Agent
- Other specialist agents

**Questions raised:**
- How is work distributed within a team?
- How is progress tracked?

---

### Stage 3: Findings Analysis

**What happens:** Analyst agent reviews parsed data, identifies violations/issues.

**Example findings:**
- Finding-001: Fire extinguisher missing (warehouse-B, severity: high)
- Finding-002: Egress blocked (loading-dock, severity: critical)
- Finding-003: Signage missing (multiple locations, severity: low)
- Finding-004: Eyewash expired (lab-2, severity: medium)
- Finding-005: Training records incomplete (severity: medium)

**Questions raised:**
- Where do detailed findings (with photos, measurements) live?
- How are findings referenced in messages vs. stored in full?

---

### Stage 4: Cross-Team to Legal

**What happens:** OHS needs legal citations for each finding from Legal Team.

**Nature of interaction:**
- Discrete request/response
- OHS sends: 5 findings needing OSHA code citations
- Legal returns: Formatted citations for each finding

**Questions raised:**
- What communication pattern for cross-team request/response?
- How much shared context is needed?
- How is this different from ongoing collaboration?

---

### Stage 5: Citation Formatting

**What happens:** Legal returns citations in required format.

**Example output:**
```
Finding: fire-extinguisher-missing
Citation: OSHA 29 CFR 1910.157(d)(1)
Text: "Portable fire extinguishers shall be provided..."
Formatted: "Violation of OSHA 29 CFR 1910.157(d)(1): ..."
```

**Questions raised:**
- Who defines the required format?
- Where is format specification stored?

---

### Stage 6: Report Assembly

**What happens:** Report drafter agent combines:
- Parsed inspection data
- Analyzed findings
- Legal citations
- Photos/evidence
- Into report template

**Questions raised:**
- Where do templates live?
- How are templates versioned?
- Are templates client-specific?

---

### Stage 7: Report Review

**What happens:** QA agent validates:
- All findings have citations
- Template properly filled
- No contradictions
- Evidence attached

**Possible outcomes:**
- Pass: Ready for signoff
- Fail: Issues identified, needs revision

**Questions raised:**
- What validation rules apply?
- How are failures routed back for correction?

---

### Stage 8: Human Signoff

**What happens:** Report needs human approval before transmission.

**Questions raised:**
- How do agents escalate to humans?
- How does human response return to the system?
- Who is authorized to sign off?
- What happens if human rejects?

---

### Stage 9: Report Transmission

**What happens:** Approved report sent to client (county).

**Questions raised:**
- How do agents send external communications?
- Email? Portal? API?
- How is delivery confirmed?

---

### Stage 10: Invoice Creation

**What happens:** Generate invoice based on contract/scope of work.

**Questions raised:**
- Who generates invoices? (OHS? Finance team?)
- Where does pricing/contract info live?
- What triggers invoice generation?

---

### Stage 11: Invoice Transmission

**What happens:** Invoice sent to client.

**Questions raised:**
- Same external transmission questions as report
- Different recipient? Same recipient?

---

### Stage 12: Payment Tracking

**What happens:** Monitor for payment, send reminders if overdue.

**Questions raised:**
- How are time-based events handled?
- Who monitors payment status?
- When are reminders sent?
- When does it escalate?

---

### Stage 13: Payment Receipt

**What happens:** Payment received and recorded.

**Questions raised:**
- How does payment info enter the system?
- Bank integration? Manual entry?
- How is payment matched to invoice?

---

### Stage 14: Tax Allocation

**What happens:** Taxes calculated and allocated from payment.

**Questions raised:**
- Who handles tax calculations?
- Where are tax rules stored?
- Federal/state/local breakdown

---

### Stage 15: Account Reconciliation

**What happens:** Business accounts updated to reflect payment.

**Questions raised:**
- What accounting system?
- How are accounts structured?
- Who has authority to update accounts?

---

### Stage 16: Projections & Goals

**What happens:** Compare actuals against projections/goals.

**Questions raised:**
- Where are goals/projections defined?
- How are metrics aggregated?
- Who sees these reports?

---

### Stage 17: Job Closure

**What happens:** Mission archived and cataloged.

**Questions raised:**
- What gets archived?
- How long is retention?
- How is it searchable later?

---

## Teams Involved

| Team | Role in Scenario |
|------|------------------|
| OHS Team | Primary - owns the inspection mission |
| Legal Team | Supporting - provides citations |
| Finance Team? | Invoicing, payment, accounting |
| C-Suite Team? | Projections, goals, oversight |

---

## Identified Gaps (Questions, Not Solutions)

1. **External Interface** - How does data enter/exit our system?
2. **Artifact Storage** - Where do documents, photos, reports live?
3. **Cross-Team Patterns** - What pattern for team-to-team communication?
4. **Template Management** - How are document templates handled?
5. **Human Escalation** - How do agents interact with humans?
6. **Time-Based Events** - How are scheduled triggers handled?
7. **Financial Operations** - Who handles invoicing, payments, accounting?
8. **Metrics/Analytics** - How are business metrics tracked?

---

## Job Lifecycle States

```
INTAKE → PARSING → ANALYSIS → LEGAL_REVIEW → DRAFTING → REVIEW
    → SIGNOFF → TRANSMITTED → INVOICED → PAYMENT_PENDING
    → PAYMENT_RECEIVED → RECONCILED → CLOSED
```

**Exception paths:**
- Any → BLOCKED (waiting on dependency)
- Any → ESCALATED (needs human intervention)
- REVIEW → REVISION (issues found)
- SIGNOFF → REJECTED (human rejected)
- PAYMENT_PENDING → COLLECTIONS (overdue)

---

*This document captures the scenario for reference. Solutions are developed in DECISION_LOG.md*

*Created: 2025-01-08*
