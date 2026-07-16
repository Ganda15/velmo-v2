# ⛔ SUPERSEDED (2026-07-08) — DO NOT USE FOR THE PRESENTATION

> **Replaced by [`schema-chantier2-EXPLICATION.md`](schema-chantier2-EXPLICATION.md).**
> ⚠️ This file claims "line numbers verified against the real code": **they no longer are.**
> `guardrails/__init__.py` was rewritten on 10/07 (adding `_normalize`, incoming PII and
> `_journalise`), so every line moved. It also says "TDD cycle" although the acceptance tests were
> **provided** by the trainer.
> Kept as a record of the work.

---

# Oral (English) — explaining the Chantier 2 DEMO schema, box by box + file/line

> Schema: `schema-chantier2-demo-complete.png`. Created 2026-07-08.
> For each box / arrow: what you SAY + [in brackets: the file and line to open, and why].
> Line numbers verified against the real code. Right = the TDD cycle; left = the architecture.

**Opening line**:
"Here is my whole Chantier 2 in one image. On the left, what the code does: two security gates around the agent. On the right, how I build and prove it: the TDD cycle. The middle arrow links the two: the code I write on the right becomes the gates on the left."

---

# LEFT PANEL — THE ARCHITECTURE

## Box: CUSTOMER MESSAGE (grey)
"Everything starts with a customer message. We don't trust it by default — it can be normal or hostile."
[Nothing to open — it's the system entry point.]

**→ arrow down**: "The message first enters the first gate."
[This is `agent.py:71` — `gate_in = self.guardrails.check_input(message)`: the agent calls the input guardrail BEFORE everything else.]

## Box ①: check_input — INPUT guardrail (orange)
"First gate. It inspects the message and looks for six things: hate, violence, sexual, prompt injection, out-of-scope, secret request."
[File to open: `src/velmo/guardrails/__init__.py:40` — the `check_input` method. This is where I code the detection. Why this line: it's the empty shell that returns "allow" today, I must fill it.]

**→ side arrow "hostile" → BLOCKED (red)**: "If the message is hostile, it's blocked here: the agent returns a polite refusal and logs the event. The message never reaches the LLM."
[The block decision = `Decision(allowed=False, action="block", category=..., refusal=...)`, defined at `guardrails/__init__.py:24`. The logging = the `events` list, line 38. On the agent side, the refusal is returned at `agent.py:72-73` (`if not gate_in.allowed: return refusal`).]

**→ arrow "allowed" down**: "If the message is clean, it's allowed and passes to the agent."
[`agent.py:72` — when `gate_in.allowed` is true, the code continues to the agent.]

## Box: AGENT (blue)
"The agent does its job: it uses my Chantier 1 memory and the Kimi LLM to produce a reply."
[`agent.py:77` (memory.read) and `agent.py:78` (_handle that produces the reply). That's Chantier 1, already done.]

**→ arrow down**: "But before the reply leaves for the customer, it goes through a second check."
[`agent.py:80` — `gate_out = self.guardrails.check_output(answer)`: the output guardrail on the reply.]

## Box ②: check_output — OUTPUT guardrail (orange)
"Second gate. As the brief states, it checks the same categories as the input + PII leaks (card number), secrets, and out-of-scope. It lets a normal business reply through, but blocks what shouldn't leave."
[File to open: `src/velmo/guardrails/__init__.py:44` — the `check_output` method. Why: it's the other empty shell to fill, with a regex for the card number.]

**→ side arrow "leak" → BLOCKED (red)**: "If the reply contains a leak, it's blocked and replaced by a refusal. The customer never sees the sensitive data."
[On the agent side: `agent.py:81-82` (`if not gate_out.allowed: answer = refusal`).]

**→ arrow "allowed" down**: "Otherwise, the reply is clean and goes to the customer."

## Box: REPLY TO CUSTOMER (green)
"The customer gets a safe reply — checked at the entrance AND at the exit."

---

# RIGHT PANEL — THE TDD CYCLE

## Box A: RUN THE TEST (red) — terminal `5 failed`
"I start by running the 5 acceptance tests BEFORE coding. They're red: that's my contract, it tells me what to block."
[Command: `python -m pytest tests/acceptance/test_guardrails.py -v`. Test file: `tests/acceptance/test_guardrails.py` — I never modify it, it's what judges me.]

**→ arrow "je code" (I code)**: "So I know what to produce, I write the code."

## Box B: WRITE / MODIFY THE CODE (purple)
"I write in `guardrails/__init__.py`: `check_input` detects keywords and returns a block + logs it; `check_output` uses a regex for the card number and secrets."
[File: `src/velmo/guardrails/__init__.py`. The two methods at lines 40 and 44. I use `Decision` (line 24) and `CATEGORIES` (line 12), already provided.]

**→ arrow "je relance" (I re-run)**: "Once the code is written, I re-run the test."

## Box C: RE-RUN THE TEST (green) — terminal `5 passed`
"I re-run the same command. The 5 tests turn green: the contract is fulfilled."
[Same command as A: `python -m pytest tests/acceptance/test_guardrails.py -v`. The test measures the code on disk — so I save first.]

**→ red loop arrow "still RED? I go back to code (B)"**: "If a test is still red, I don't panic: I go back to the code, fix it, re-run. That's the TDD loop — red, fix, green."

**→ arrow down**: "When everything is green, I check I didn't break anything."

## Box D: NON-REGRESSION (grey)
"I run the whole suite. 16 green in total: 5 guardrails + 4 memory + 7 business. Security added without breaking anything."
[Command: `python -m pytest -q`. Expected: 16 passed.]

---

# THE JOURNAL NOTE (bottom left)

"Below the flow, the note: every BLOCK is logged into `self.events`. That's the logging required by the brief — every time a gate blocks, I add an entry. It's an in-memory list (enough for the test); in production I'd persist it."
[File: `guardrails/__init__.py:38` — the `events` list. That's where `check_input` and `check_output` will write `self.events.append({...})` on every block.]

---

# THE MIDDLE ARROW (purple) — the link

"This arrow links the two panels: the code I write in box B **becomes** exactly the two gates ① and ② on the left. It's not two separate things — it's the same thing from two angles: on the left the behavior, on the right how I built it."
[Concretely: `guardrails/__init__.py:40` (check_input) = gate ① ; `guardrails/__init__.py:44` (check_output) = gate ②. The agent calls them at `agent.py:71` and `agent.py:80`.]

---

# 🎓 Likely trainer questions (with file/line)

1. "Where is your guardrail called in the agent?" → "At the input, `agent.py:71`; at the output, `agent.py:80`. I didn't modify the agent, it already called these two points."
2. "How do you log a block?" → "I add an entry to the `events` list of `GuardrailEngine` (`guardrails/__init__.py:38`). The test checks `len(engine.events) >= 3`."
3. "Why doesn't the output block everything?" → "`check_output` must let 'order O-2024-0101 prepared' through but block a card number. It's targeted detection, not blind blocking."
4. "What is `Decision`?" → "It's a guardrail's verdict (`guardrails/__init__.py:24`): `allowed`, `action`, `category`, `refusal`. That's what my two methods return."
