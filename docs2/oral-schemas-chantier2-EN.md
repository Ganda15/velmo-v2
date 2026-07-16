# ⛔ SUPERSEDED (2026-07-08) — DO NOT USE FOR THE PRESENTATION

> **Replaced by [`schema-chantier2-EXPLICATION.md`](schema-chantier2-EXPLICATION.md).**
> Only ONE schema is shown now, in two stages: `schema-A-gauche.png` (0:00→4:30) then
> `schema-AB-complet.png`. The `check_input` box now also carries the `PII` category.
> Kept as a record of the work.

---

# Oral (English) — explaining the 2 Chantier 2 schemas, box by box

> Created 2026-07-08. Two schemas: `schema-chantier2-plan.png` (7-step plan) and `schema-chantier2-portiques.png` (the two gates).
> For each box and each arrow: what you SAY. Story style — every arrow reads as "so".

---

# SCHEMA 1 — The work plan (7 steps)

**Opening line**: "Here is my plan for the guardrails, in 7 steps, TDD method like the memory. Every arrow reads as 'so'."

## Box ① — STEP 1: See the tests RED (red)
"I start by running the 5 acceptance tests BEFORE writing a line. They're all red — and that's intended: red is my contract, it tells me exactly what I must block."

**→ arrow**: "SO, once I know what's expected of me…"

## Box ② — STEP 2: Read the 3 pieces (blue)
"…I read the tools already provided in the code: the `Decision` class, which is the verdict — it holds `allowed`, `action`, `category`, `refusal`. The 7 `CATEGORIES` already listed. And the test file, to see the exact cases. I don't reinvent anything, I use what exists."

**→ arrow**: "SO I know what to produce; now I decide how to detect."

## Box ③ — STEP 3: Design on paper (purple)
"Before coding, I design: for each category — hate, violence, sexual, injection, out-of-scope, secret — I list the keywords that give it away. This is the design, and it's the entry gate the trainer requires: validate the schema before the code."

**→ arrow**: "SO, with my detection plan ready, I code the first guardrail."

## Box ④ — STEP 4: Code check_input (orange)
"The input guardrail: it inspects the customer's message, looks for keywords, and if it finds any, it returns a `Decision` to block, with the right category and a polite refusal — and it logs the event. This step moves 4 tests forward at once: hate/violence/sexual, injection, and out-of-scope."

**→ arrow**: "SO the input is protected; I move to the output."

## Box ⑤ — STEP 5: Code check_output (orange)
"The output guardrail: it inspects the reply BEFORE it leaves. It looks for a bank card number — with a regex — and secrets. But careful: it must let through a normal reply like 'your order O-2024-0101 is prepared'. No blind blocking. This step makes the PII test pass."

**→ arrow**: "SO both gates work; the tricky point remains."

## Box ⑥ — STEP 6: Tune the false-positive threshold (grey)
"This is the hardest test. I must block ALL hostile messages — 35 test cases — AND not block legitimate messages by mistake: less than 10% false positives. It's a balance: too strict, I block real customers; too loose, I let attacks through."

**→ arrow**: "SO, once the balance is found, I prove everything."

## Box ⑦ — STEP 7: Run all tests (green)
"I run the whole suite. The 5 guardrail tests turn green, AND non-regression holds: my 4 memory tests and the 7 business tests stay green. That's 16 green in total. The chantier is proven."

**Closing line**: "Seven steps, from red to green, each one moves a specific test forward."

---

# SCHEMA 2 — The two security gates

**Opening line**: "Security is two gates: one BEFORE the agent, one AFTER. Like the airport: you check at the entrance and at the exit."

## Box — CUSTOMER MESSAGE (grey)
"Everything starts with a customer message. It can be normal… or hostile. We don't trust by default."

**→ arrow (down)**: "The message first enters the first gate."

## Box ① — INPUT GUARDRAIL, check_input (orange)
"First gate. It looks for six things: hate, violence, sexual, prompt injection, out-of-scope, and secret requests. This protects the agent: we filter before the LLM even sees the message."

**→ side arrow "hostile" → BLOCKED box (red)**: "If the message is hostile, it's blocked here: the agent returns a polite refusal and logs the event. The message never reaches the LLM."

**→ arrow "allowed" (down)**: "If the message is clean, SO it's allowed and passes to the agent."

## Box — AGENT (blue)
"The agent does its job: it uses my Chantier 1 memory and the Kimi LLM to produce a reply."

**→ arrow (down)**: "But before that reply leaves for the customer, it goes through another check."

## Box ② — OUTPUT GUARDRAIL, check_output (orange)
"Second gate. As the brief states, it checks the **same categories** as the input, PLUS PII leaks (a card number), secrets, and out-of-scope. It lets a normal business reply through, but blocks anything that shouldn't leave. The test mainly checks the card number."

**→ side arrow "leak" → BLOCKED box (red)**: "If the reply contains a leak, it's blocked and replaced by a refusal. The customer never sees the sensitive data."

**→ arrow "allowed" (down)**: "Otherwise, SO the reply is clean and goes to the customer."

## Box — REPLY TO CUSTOMER (green)
"The customer gets a safe reply — checked at the entrance AND at the exit."

## The JOURNAL box (self.events)
"On the right, the JOURNAL box: every time a gate blocks — at the input or the output — it writes a trace into `self.events`. That's the logging required by the brief. Today it's an in-memory list, which is enough for the test; in production I'd persist it to a database for durable audit — that's the limit I own."

## The legend — the 7 categories
"At the bottom, the 7 controlled categories. The first six — hate, violence, sexual, injection, out-of-scope, secret — are mostly filtered at the input. At the output, we mainly watch for personal data, PII like a card number, and secret leaks."

**Key line to remember**: "Two gates: the input protects the agent from attacks, the output protects the customer from leaks — and every block is logged."

---

# 🎓 Likely trainer questions (English)

1. "Why two guardrails, not one?" → "Input and output carry different risks: the input protects against attacks and manipulation, the output protects against data leaks. One alone wouldn't cover both."
2. "How do you detect a prompt injection?" → "I look for phrasings that try to make the agent disobey: 'ignore your instructions', 'forget your rules', 'developer mode'. It's a minimal keyword choice; in production, an LLM classifier would be more robust."
3. "What's a false positive and why does it matter?" → "It's blocking a legitimate customer by mistake. The test requires under 10%: if I'm too strict, I block real customers — bad for support."
4. "Why log the blocks?" → "For traceability: a security incident must leave a trace to be audited — it's also a GDPR/security requirement."
