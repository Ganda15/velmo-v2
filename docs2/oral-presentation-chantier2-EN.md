# ⛔ SUPERSEDED (2026-07-08) — DO NOT USE FOR THE PRESENTATION

> **Replaced by [`oral-final-chantier2-EN.md`](oral-final-chantier2-EN.md).**
> Stale on three counts: (1) it says "TDD" although the acceptance tests were **provided**;
> (2) it opens the demo with `pytest`, whereas the trainer asked for a **conversational** demo
> (Chantier 1, criticism #3); (3) it predates the two flaws closed on 10/07 (accents, incoming PII),
> and the line numbers moved when `guardrails/__init__.py` was rewritten.
> Kept as a record of the work.

---

# Presentation oral — Chantier 2 Guardrails (EN)

> Two versions: ① 10 minutes (full, with code remarks), ② 5 minutes (condensed).
> Structured around the 7 steps. Style: a story — each step soldered to its why.
> Visual aid: `schema-chantier2-demo-complete.png`. Proof: `pytest`.

---

# ① 10-MINUTE VERSION

## [0:00] Opening — the problem

"Chantier 2 is the guardrails. An SAV agent wired to an LLM can be manipulated: if insulted, it might reply with awful content; if told 'ignore your instructions', it might disobey; and it could leak sensitive data, like a card number. So we need a barrier BEFORE the agent — to filter what comes in — and a barrier AFTER — to filter what goes out. Two security gates, like at the airport. I built this in seven steps, using TDD."

## [1:00] Step 1 — see the tests red

"My first action wasn't to write code, but to run the five acceptance tests. All red. That's intended: it's my TDD contract. Red tells me exactly what to block — hate, violence, sexual, injection, out-of-scope, and the leak of a card number. Until I'd seen them fail, I didn't know precisely what was expected of me."

## [2:00] Step 2 — read the provided tools

"Then I read what already existed in the code, before inventing anything. Three things: the seven categories already listed; the Decision class, which is a guardrail's verdict — it holds allowed, action, category and a refusal message; and the events list, which is my journal, where I'll trace every block. I invent nothing, I fill the empty shells with these tools."

## [3:00] Step 3 — design the keywords (before coding)

"Before writing a line, I designed the detection. For each category, I listed the keywords that give it away. And I made an important choice: I took them from the REAL test messages, not at random. For example, for hate: 'hais', 'race'; for violence: 'frapper', 'tuer'; for injection: 'ignore tes instructions'. In French, because the messages are French, and without accents, because the messages have none. That way, every hostile message has at least one triggering keyword."

## [4:00] Step 4 — code the input guardrail

"Then I coded check_input."
[Code remark] "The core is a dictionary: to each category, a list of keywords. The method lowercases the message, loops over each category, and if a keyword is present, it blocks: it returns a Decision 'block' with the right category and a polite refusal, AND it adds an entry to the events journal. If nothing is found, it lets the message through."
"Result: four tests pass at once."

## [5:00] Step 5 — code the output guardrail

"The last red remained: the card number on output."
[Code remark] "Here I use a regular expression. The test wants to block '4111 1111 1111 1111' but let through an order number like 'O-2024-0101'. The difference is the length: a card is sixteen digits in four groups of four; an order, only eight digits. My regex looks for exactly sixteen digits in four groups. So it blocks the card without blocking the order. And I reuse my input keywords, because the brief asks for the same categories plus secrets on the output too."
"Result: the fifth test passes. All five guardrails are green."

## [6:30] Step 6 — the false-positive balance

"The hardest test was the balance: block ALL hostiles without blocking real customers. A false positive is blocking a legit customer by mistake — that's bad for support. The threshold is under ten percent. I have zero false positives. Why? Because my keywords are precise. For example, I block on 'authentifier' — someone wanting a jersey bought elsewhere authenticated — but not on 'authentiques' — a real customer asking whether our jerseys have a certificate. A one-word difference, but my design tells them apart. This balance was already met at Step 4, thanks to the design."

## [8:00] Step 7 — non-regression

"Last step: prove I broke nothing. I re-run the WHOLE suite, not just the guardrails. Sixteen green tests: my Chantier 1 memory and the business agent stayed green. Zero regression. Three reds remain, but those are Chantier 3 tests, the MLOps, which I haven't started — the run_eval function is still empty. It's not a bug, it's the remaining work. And the brief requires it: a regression would block delivery."

## [9:00] Closing — proof and limits

"To conclude: two functional guardrails, tested, logging every block. Five acceptance tests green, sixteen total, zero regression. My choices: keyword and regex detection, simple and deterministic — in production, an LLM classifier would be more robust, I own that. And my journal is in memory, which is enough for the contract; in production I'd persist it for durable audit. Everything is traced in my logbook, step by step, with the why behind each choice."

[End — questions.]

---

# ② 5-MINUTE VERSION

## [0:00] The problem
"Chantier 2: the guardrails. An SAV agent wired to an LLM can be manipulated or leak data. We need a barrier at the input and one at the output. I did it with TDD."

## [0:40] The TDD method (steps 1 to 3)
"First I ran the five tests: all red, that's my contract. Then I read the provided tools — the categories, the Decision class, the events journal. Then I designed my keywords from the real test messages, in French."

## [1:40] The two guardrails (steps 4 and 5)
"check_input, the input: a dictionary category → keywords; if a word is found, I block with the right category, a refusal, and I log it. Four tests pass. check_output, the output: a regex detecting sixteen digits in four groups — a card number — without blocking an order number, which has only eight digits. The fifth test passes."

## [3:00] The balance (step 6)
"The hardest test: block all hostiles without blocking real customers. Zero false positives, because my keywords are precise: I block 'authentifier' but not 'authentiques'."

## [3:50] The proof (step 7)
"I re-run the whole suite: sixteen green, zero regression. The three remaining reds are Chantier 3, MLOps, not started yet."

## [4:30] Closing
"Two tested and logged guardrails. Owned choices: keywords and regex rather than an LLM, in-memory journal rather than persisted — the right level for the brief."

[End — questions.]

---

# 🎓 Likely questions (recap)
1. "Why two guardrails?" → "The input protects the agent from attacks, the output protects the customer from leaks. Different risks."
2. "How do you avoid blocking a real customer?" → "Precise keywords: 'authentifier' blocked, 'authentiques' not. Zero false positives."
3. "How do you tell a card from an order?" → "Length: my regex requires sixteen digits, the order has only eight."
4. "Why are there still reds?" → "Chantier 3 MLOps, run_eval not coded. Not a regression."
5. "What's your logging?" → "Every block adds an entry to the events list. In memory today, persisted in production."
