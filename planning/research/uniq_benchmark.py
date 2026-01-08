"""Benchmark: Does denser context improve LLM reasoning?

Tests comparing prose vs UNI-Q format on:
1. Information retrieval from large context
2. Relationship traversal (why questions)
3. Multi-entity comparison
"""

import anthropic
import time
import json
import os
from pathlib import Path

# Load .env from backend
env_path = Path(__file__).parent.parent.parent / "backend" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

client = anthropic.Anthropic()

# =============================================================================
# TEST 1: Information Retrieval (20 teams, find specific ones)
# =============================================================================

PROSE_CONTEXT_1 = """
Current status of all teams:

The accounting team is currently idle with no active tasks. They completed their quarterly close yesterday.

The marketing team is actively working on the Q1 campaign with high priority. They are about 60% complete and the trend is improving.

The legal team is blocked waiting on the compliance team to finish their regulatory review. This has been flagged as needing attention.

The sales team is actively working on several deals with normal priority. They are at about 40% completion with a stable trend.

The HR team is idle after completing the annual review cycle.

The engineering team is critically active on a production incident. They are working with high priority and the situation is volatile.

The customer service team is active handling normal ticket volume. Trend is stable at about 70% of capacity.

The compliance team is actively working on the regulatory review that legal is waiting for. High priority, about 30% complete.

The finance team is active on budget planning with normal priority, about 50% complete with improving trend.

The operations team is blocked waiting on a vendor delivery. This is flagged as time-sensitive.

The product team is active on roadmap planning, about 80% complete with stable trend.

The design team is idle between projects.

The QA team is active on release testing, high priority, 90% complete.

The security team is critically blocked on a vulnerability assessment waiting for engineering resources.

The data team is active on pipeline maintenance, normal priority, stable.

The support team is active with degraded health due to high ticket volume.

The infrastructure team is active on cloud migration, 45% complete, improving.

The research team is idle, pending new project assignment.

The partnerships team is active on contract negotiations, flagged as needing attention.

The analytics team is blocked waiting on data team pipeline fixes.
"""

UNIQ_CONTEXT_1 = """
Ⓐacct○;Ⓐmkt◉⁺⑥↗;Ⓐlegal⊘→Ⓐcompliance⚑;Ⓐsales◉④→;Ⓐhr○;Ⓐeng⦿↯;Ⓐcs◉⑦→;Ⓐcompliance◉⁺③;Ⓐfin◉⑤↗;Ⓐops⊘⧖;Ⓐprod◉⑧→;Ⓐdesign○;Ⓐqa◉⁺⑨;Ⓐsec⊗→Ⓐeng;Ⓐdata◉→;Ⓐsupport◉♡;Ⓐinfra◉④↗;Ⓐresearch○◐;Ⓐpartners◉⚑;Ⓐanalytics⊘→Ⓐdata
"""

QUESTION_1 = "Which teams are currently blocked, and what is each one waiting for?"

EXPECTED_1 = {
    "legal": "compliance",
    "operations": "vendor",
    "security": "engineering",
    "analytics": "data"
}

# =============================================================================
# TEST 2: Relationship Traversal (follow the chain)
# =============================================================================

PROSE_CONTEXT_2 = """
Decision record for customer refund case #4721:

The customer service agent approved a $450 refund for customer Maria Chen (ID: C-8842).

This decision was made because:
- Maria is a VIP tier customer with 6 years of tenure
- Her lifetime value is $34,000
- The refund policy for VIP customers allows discretionary refunds up to $500
- The specific policy applied was Refund Policy version 3.2, section 4.1

The refund policy 3.2 section 4.1 states:
- VIP customers may receive discretionary refunds up to $500 without manager approval
- This policy exists to support the strategic goal of customer retention
- The customer retention goal has a target of maintaining 95% retention for customers with 5+ years tenure

Maria's recent interaction history:
- 3 months ago: product complaint, resolved with replacement
- 6 months ago: shipping delay, $50 credit issued
- 1 year ago: positive feedback survey

The decision factors considered were:
1. Customer tier (VIP)
2. Tenure (6 years, exceeds 5-year threshold)
3. Lifetime value ($34K, high value customer)
4. Recent complaint pattern (2 issues in 6 months, concerning but not excessive)
5. Amount requested ($450, within $500 VIP limit)
"""

UNIQ_CONTEXT_2 = """
Ⓥdecision·ref4721✓⟨amt:450·cust:C-8842⟩⊂Ⓔcust·maria-chen⊃Ⓞpolicy·refund-3.2.4.1∧Ⓢgoal·retention

Ⓔcust·maria-chen⟨tier:vip·tenure:6y·ltv:34000⟩
Ⓞpolicy·refund-3.2.4.1⟨vip-limit:500·no-approval-required⟩∧Ⓢgoal·retention
Ⓢgoal·retention⟨target:95%·segment:5y+tenure⟩

Ⓥcomplaint·3mo-ago⊂Ⓔcust·maria-chen⟨resolved:replacement⟩
Ⓥcomplaint·6mo-ago⊂Ⓔcust·maria-chen⟨resolved:credit-50⟩
Ⓥfeedback·1y-ago⊂Ⓔcust·maria-chen⟨sentiment:positive⟩

factors:tier-vip·tenure-6y·ltv-34k·complaints-2in6mo·amt-in-limit
"""

QUESTION_2 = "Why was this refund approved? Trace the reasoning from the decision back to the strategic goal."

# =============================================================================
# TEST 3: Multi-Entity Comparison
# =============================================================================

PROSE_CONTEXT_3 = """
You need to assign an urgent contract review task. Here are the available legal team members:

Attorney Alice Chen:
- Current status: Active, working on 2 other tasks
- Current workload: 75% capacity
- Specialty: Corporate contracts, M&A
- Average completion time: 4 hours for standard reviews
- Quality score: 94%
- Currently blocked: No

Attorney Bob Martinez:
- Current status: Active, working on 1 task
- Current workload: 40% capacity
- Specialty: Employment law, HR contracts
- Average completion time: 3 hours for standard reviews
- Quality score: 91%
- Currently blocked: No

Attorney Carol Williams:
- Current status: Blocked, waiting on client documents
- Current workload: 60% capacity (when unblocked)
- Specialty: Corporate contracts, vendor agreements
- Average completion time: 3.5 hours for standard reviews
- Quality score: 97%
- Currently blocked: Yes, waiting on client

Attorney David Park:
- Current status: Idle
- Current workload: 0% capacity
- Specialty: Litigation, disputes
- Average completion time: 5 hours for standard reviews
- Quality score: 88%
- Currently blocked: No

The task is: Urgent vendor contract review for a software licensing agreement. Needs corporate contracts expertise. Must complete within 4 hours.
"""

UNIQ_CONTEXT_3 = """
Task: Ⓣreview·vendor-sw⁺⟨type:corporate·deadline:4h⟩

Ⓐatty·alice◉¾⟨spec:corporate,m&a·η4h·qual:94⟩
Ⓐatty·bob◉②⟨spec:employment,hr·η3h·qual:91⟩
Ⓐatty·carol⊘→client-docs⟨spec:corporate,vendor·η3.5h·qual:97⟩
Ⓐatty·david○⟨spec:litigation·η5h·qual:88⟩
"""

QUESTION_3 = "Which attorney should be assigned to this task? Explain your reasoning considering expertise match, availability, and ability to meet the deadline."

# =============================================================================
# RUN TESTS
# =============================================================================

def run_test(context: str, question: str, format_name: str) -> dict:
    """Run a single test and return results."""

    prompt = f"""Given this context:

{context}

Question: {question}

Provide a clear, concise answer."""

    start = time.time()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    elapsed = time.time() - start

    return {
        "format": format_name,
        "context_chars": len(context),
        "response": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_ms": int(elapsed * 1000)
    }


def compare_test(name: str, prose: str, uniq: str, question: str):
    """Run both formats and compare."""

    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"\nQuestion: {question}\n")

    prose_result = run_test(prose, question, "prose")
    uniq_result = run_test(uniq, question, "uniq")

    # Print results
    print(f"\n--- PROSE FORMAT ---")
    print(f"Context: {prose_result['context_chars']} chars, {prose_result['input_tokens']} input tokens")
    print(f"Latency: {prose_result['latency_ms']}ms")
    print(f"\nResponse:\n{prose_result['response']}")

    print(f"\n--- UNI-Q FORMAT ---")
    print(f"Context: {uniq_result['context_chars']} chars, {uniq_result['input_tokens']} input tokens")
    print(f"Latency: {uniq_result['latency_ms']}ms")
    print(f"\nResponse:\n{uniq_result['response']}")

    # Calculate savings
    token_savings = (1 - uniq_result['input_tokens'] / prose_result['input_tokens']) * 100
    latency_savings = (1 - uniq_result['latency_ms'] / prose_result['latency_ms']) * 100

    print(f"\n--- COMPARISON ---")
    print(f"Token reduction: {token_savings:.1f}%")
    print(f"Latency change: {latency_savings:.1f}%")

    return {
        "test": name,
        "prose_tokens": prose_result['input_tokens'],
        "uniq_tokens": uniq_result['input_tokens'],
        "token_reduction_pct": round(token_savings, 1),
        "prose_latency_ms": prose_result['latency_ms'],
        "uniq_latency_ms": uniq_result['latency_ms'],
    }


if __name__ == "__main__":
    results = []

    results.append(compare_test(
        "Information Retrieval (20 teams)",
        PROSE_CONTEXT_1, UNIQ_CONTEXT_1, QUESTION_1
    ))

    results.append(compare_test(
        "Relationship Traversal",
        PROSE_CONTEXT_2, UNIQ_CONTEXT_2, QUESTION_2
    ))

    results.append(compare_test(
        "Multi-Entity Comparison",
        PROSE_CONTEXT_3, UNIQ_CONTEXT_3, QUESTION_3
    ))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for r in results:
        print(f"\n{r['test']}:")
        print(f"  Prose: {r['prose_tokens']} tokens, {r['prose_latency_ms']}ms")
        print(f"  UNI-Q: {r['uniq_tokens']} tokens, {r['uniq_latency_ms']}ms")
        print(f"  Token reduction: {r['token_reduction_pct']}%")

    avg_reduction = sum(r['token_reduction_pct'] for r in results) / len(results)
    print(f"\nAverage token reduction: {avg_reduction:.1f}%")
