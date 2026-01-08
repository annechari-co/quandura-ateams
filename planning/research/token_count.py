"""Quick token count comparison using tiktoken (GPT tokenizer as proxy)."""

try:
    import tiktoken
except ImportError:
    print("Installing tiktoken...")
    import subprocess
    subprocess.run(["pip", "install", "tiktoken"], capture_output=True)
    import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

PROSE_1 = """
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

UNIQ_1 = """Ⓐacct○;Ⓐmkt◉⁺⑥↗;Ⓐlegal⊘→Ⓐcompliance⚑;Ⓐsales◉④→;Ⓐhr○;Ⓐeng⦿↯;Ⓐcs◉⑦→;Ⓐcompliance◉⁺③;Ⓐfin◉⑤↗;Ⓐops⊘⧖;Ⓐprod◉⑧→;Ⓐdesign○;Ⓐqa◉⁺⑨;Ⓐsec⊗→Ⓐeng;Ⓐdata◉→;Ⓐsupport◉♡;Ⓐinfra◉④↗;Ⓐresearch○◐;Ⓐpartners◉⚑;Ⓐanalytics⊘→Ⓐdata"""

PROSE_2 = """
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

UNIQ_2 = """Ⓥdecision·ref4721✓⟨amt:450·cust:C-8842⟩⊂Ⓔcust·maria-chen⊃Ⓞpolicy·refund-3.2.4.1∧Ⓢgoal·retention

Ⓔcust·maria-chen⟨tier:vip·tenure:6y·ltv:34000⟩
Ⓞpolicy·refund-3.2.4.1⟨vip-limit:500·no-approval-required⟩∧Ⓢgoal·retention
Ⓢgoal·retention⟨target:95%·segment:5y+tenure⟩

Ⓥcomplaint·3mo-ago⊂Ⓔcust·maria-chen⟨resolved:replacement⟩
Ⓥcomplaint·6mo-ago⊂Ⓔcust·maria-chen⟨resolved:credit-50⟩
Ⓥfeedback·1y-ago⊂Ⓔcust·maria-chen⟨sentiment:positive⟩

factors:tier-vip·tenure-6y·ltv-34k·complaints-2in6mo·amt-in-limit"""


def count_tokens(text, name):
    tokens = enc.encode(text)
    return len(tokens)


print("="*60)
print("TOKEN COUNT COMPARISON (GPT-4 tokenizer)")
print("="*60)

print("\nTest 1: 20-Team Status")
prose_tokens = count_tokens(PROSE_1, "prose")
uniq_tokens = count_tokens(UNIQ_1, "uniq")
print(f"  Prose:  {prose_tokens} tokens")
print(f"  UNI-Q:  {uniq_tokens} tokens")
print(f"  Reduction: {(1 - uniq_tokens/prose_tokens)*100:.1f}%")

print("\nTest 2: Decision Trace")
prose_tokens = count_tokens(PROSE_2, "prose")
uniq_tokens = count_tokens(UNIQ_2, "uniq")
print(f"  Prose:  {prose_tokens} tokens")
print(f"  UNI-Q:  {uniq_tokens} tokens")
print(f"  Reduction: {(1 - uniq_tokens/prose_tokens)*100:.1f}%")

print("\n" + "="*60)
print("ATTENTION COMPUTE COMPARISON (O(n²))")
print("="*60)

prose1 = count_tokens(PROSE_1, "")
uniq1 = count_tokens(UNIQ_1, "")
prose2 = count_tokens(PROSE_2, "")
uniq2 = count_tokens(UNIQ_2, "")

print("\nTest 1: 20-Team Status")
print(f"  Prose attention ops:  {prose1**2:,}")
print(f"  UNI-Q attention ops:  {uniq1**2:,}")
print(f"  Reduction: {(1 - (uniq1**2)/(prose1**2))*100:.1f}%")

print("\nTest 2: Decision Trace")
print(f"  Prose attention ops:  {prose2**2:,}")
print(f"  UNI-Q attention ops:  {uniq2**2:,}")
print(f"  Reduction: {(1 - (uniq2**2)/(prose2**2))*100:.1f}%")
