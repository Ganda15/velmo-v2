# Chantier 1 Memory — 10-Minute Fused Oral Demo Script (corrected & complete)

> Corrected version, 2026-07-07. All line numbers verified against the real code.
> French narrative version: `docs2/oral-humanise-complet-chantier1.md` (Partie A).

## Before starting

I open VS Code directly in the real project, with a FRESH terminal (close old ones — an old terminal can show old results):

```bash
code -r C:\Users\kanda\velmo-v2
```

⚠️ **Plan B if Windows blocks `uv.exe`** (AppLocker message "stratégie de contrôle d'application"): activate the venv once, then replace `uv run pytest` with `python -m pytest` and `uv run python` with `python` — identical results, because the project is installed in editable mode:

```bash
.\.venv\Scripts\Activate.ps1
```

⚠️ **Never paste the prompt line** (`(velmo-v2) PS C:\...>`) — only what comes after the `>`.

I say:
“Today I will present Chantier 1: Memory. I will not separate theory and demo. I will explain each step, open the real files, run the real commands, and explain the output directly.”

## 1. Start with the problem

“Velmo is a support assistant for a collector football jersey shop.
The agent must answer customer questions about orders, delivery, returns, refunds, stock, and FAQ.
But for a real support agent, answering is not enough. The agent must also be reliable.
It must remember useful customer facts, it must not mix customers, and it must be able to forget information when the customer asks.
So my Chantier 1 objective was to build a durable memory for the agent.
This memory has four requirements:
R1: recall a useful fact after 30 turns.
R2: persist memory between sessions.
R3: isolate memory between customers.
R5: forget a fact on request.
My method was simple: first prove the existing agent is healthy, then run the memory tests red, then implement the missing memory, and finally prove everything with terminal commands.”

## 2. Prove the original business agent is healthy

I run:

```bash
uv run pytest tests/acceptance/test_business.py -v
```

I say while it runs:
“I start with the business tests, before touching memory.
Why?
Because if the original agent is already broken, I cannot know if a future failure comes from my code or from the initial skeleton.
These tests protect the business behavior of Velmo: orders, refunds, stock, escalation, and customer isolation.”

Expected output:

```text
7 passed
```

I explain the output:
“Here, seven business tests passed.
That means the agent already works for the existing business rules.
For example, a shipped order cannot be modified, a refund above the limit is escalated, Marc cannot access Sophie’s order, and the agent does not invent stock when the product is unavailable.
So my starting point is clean. I can now work on memory without breaking the business agent.”

**[ADDED — the API question, before anyone asks]** I add:
“One precision: these tests run offline in 0.2 seconds, through EchoLLM — a three-line deterministic stub, not a local model. The product itself talks only to Kimi through the Azure API, as the expert note requires: `get_llm()` builds the Azure client as soon as the key is configured, and I validated that chain separately — the real Kimi answered. I keep the API out of the tests on purpose: a test that depends on an LLM answer is non-deterministic, and the CI in GitHub Actions must run without my API key. Same switch philosophy as the database: one environment variable, zero code change.
I also checked `git status` at the start: the trainer’s repo was intact — I never touched the tests or the contracts.”

## 3. Open the memory contract

I open the acceptance tests:

```bash
code -r -g C:\Users\kanda\velmo-v2\tests\acceptance\test_memory.py:8
```

I say:
“Now I open the memory acceptance tests.
This file is my contract. I did not change it.
It tells me exactly what the memory must do.”

I explain the four tests:
“The first test is recall over 30 turns. The user gives an important fact at the beginning, then there are 30 noisy messages, and the memory must still return the useful fact.
The second test is cross-session persistence. That means memory cannot live only in Python RAM. If I create a new MemoryManager, the fact must still exist.
The third test is customer isolation. One customer must never see another customer’s memory.
The fourth test is the right to be forgotten. If the user asks to forget something, future reads must not return that fact anymore.”

I add:
“At the beginning, these tests were red. That was normal because the memory was not implemented yet. This is TDD: red first, then code, then green.”

## 4. Open the storage layer: where memories live

I open the memory store:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\store.py:20
```

I say:
“The first technical question was: where do memories live?
If I store memory only inside a Python object, it disappears when the program stops. So the persistence test can never pass.
That is why I created a database storage layer.”

I explain the table:
“Here I have a table called `memory_facts`.
One memory is one durable row.
The important columns are:
`id`, the technical identifier.
`user_id`, the customer identifier.
`key`, the name of the fact, for example priority order or delivery address.
`value`, the stored value.
`deleted`, a boolean flag for forgetting.”

Then I explain why each column matters:
“The `user_id` is essential for isolation. Every memory belongs to one customer. So Marc and Sophie can have the same key, but they will still have different memory rows.
The `deleted` flag is essential for the right to be forgotten. I do not physically delete the row. I mark it as deleted. Then `read()` ignores deleted facts.
From the customer point of view, the fact is gone. From the system point of view, we still have an audit trace.
**[ADDED — metadata trap]** And to be precise: `deleted` is my only implemented metadata today. Columns like created_at, version or confidence would be possible evolutions — they do not exist yet, and I will not pretend they do.”

I explain SQLite and Postgres:
“For tests and development, I use SQLite. It is fast, local, and does not need Docker or network — it ships with Python, and SQLAlchemy creates the table automatically at load time.
For production, the same code can use Postgres by setting `MEMORY_DB_URL` — and Postgres itself starts with one `docker run postgres`.
The reason this works is SQLAlchemy. SQLAlchemy is the bridge between Python objects and SQL tables. So the memory code does not need to change when I move from SQLite to Postgres.”

I add the important distinction:
“There are two databases in the project.
`db.py` is the business database from the trainer: orders, products, customers.
`store.py` is my memory database: durable facts about users.
I keep them separate because the business database is reseeded during tests, but memory must survive between sessions. If I mixed them, I could create an amnesiac memory.”

## 5. Open the agent pipeline: where memory is called

I open the agent:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:70
```

I say:
“Now I open the agent pipeline.
This file is not the memory itself. It is the conductor. It receives the customer message and decides what to do.”

I explain the flow:
“Each accepted message goes through five steps.
First, the input guardrail checks the user message — **[ADDED]** and notice one detail: even a refused message gets written to memory, so refusals stay traceable.
Second, the agent calls `memory.read()`.
Third, the agent routes the message. It can detect an order number, understand an intention like refund or address change, call business tools, check stock, check FAQ, or use the LLM as a last resort — and for sensitive actions it first requires an explicit confirmation, and the tools escalate when the order has shipped or the amount exceeds the cap.
Fourth, the output guardrail checks the answer.
Fifth, the agent calls `memory.write()` to extract and store useful facts.”

I say:
“Before my chantier, the pipeline already had the calls to memory, but the memory methods were empty shells.
After my work, the same calls now connect to a real memory.”

Then I open the honest limit:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:138
```

I say:
“I also found one important limit myself.
The agent calls `memory.read()`, but at line 138 the LLM still receives an empty context string.
**[ADDED — the socket argument]** What is interesting is that the socket already exists on the other side: in `llm.py`, the `invoke` method has had a `context` parameter from day one, and the Azure client already knows how to add it to the prompt under a ‘Mémoire:’ block. The skeleton was designed to receive my memory — only the plug is missing.
So the memory storage contract is complete, but the next step is to inject `context.render()` into the LLM prompt.
I prefer to say it clearly: the memory is implemented and tested, but the LLM context injection is the next improvement.”

## 6. Open the memory facade: the methods I implemented

I open the memory facade:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:20
```

I say:
“Now I show the main memory facade.
This is where the acceptance tests are satisfied.”

I explain the pattern:
“Here, `FACT_PATTERN` detects simple useful facts in natural language.
For example, if the user says:
‘Ma commande prioritaire est O-2024-0101’
the memory can extract:
key: commande prioritaire
value: O-2024-0101
This is important because I do not store the full conversation. I distill the useful fact.
**[ADDED — regex limit, owned]** I also own the limit: a regex only covers the planned shapes. In production, this extractor would be the LLM — same architecture, different extractor. The regex is the minimal choice that honours the test contract without network access.”

Then I open `read()`:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:51
```

I say:
“`read()` returns the facts for one user only.
It filters by `user_id`.
It also filters deleted facts.
That is why customer isolation and forgetting work structurally.”

Then I open `write()`:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:63
```

I say:
“`write()` receives the user message and the agent answer.
But it does not store every message.
It extracts only useful facts.
This is important for the token budget. If we store 30 noisy turns, the context becomes too heavy. Instead, we keep compact facts.”

Then I open `remember_fact()`:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:71
```

I say:
“`remember_fact()` stores a fact.
It works like an upsert: if the fact already exists, it updates it. If it does not exist, it inserts it.
So the same customer can update a fact without creating useless duplicates.
**[ADDED — reuse argument]** And `write()` calls `remember_fact()` instead of writing its own SQL: one single write path to the database, one single place to debug.”

Then I open `forget()`:

```bash
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:87
```

I say:
“`forget()` implements the right to be forgotten.
The test may ask to forget ‘address’, but the stored key can be ‘delivery address’.
So exact equality is too strict. I use containment logic.
Then I mark the fact as `deleted=True`.
I do not delete the row physically. This is soft-delete.
After that, `read()` no longer returns it — **[ADDED]** and the elegant part is that I never had to modify `read()` for this: it has filtered deleted facts from day one. A decision made two steps earlier paid off here.”

## 7. Live demo: extraction, noise ignored, forgetting

I run the live command:

```bash
uv run python -c "
from velmo.memory import MemoryManager
mm = MemoryManager()
mm.write('demo', 'Ma commande prioritaire est O-2024-0101.', 'ok')
mm.write('demo', 'Question de suivi sur un maillot.', 'ok')
print('Retained:', mm.read('demo', '?').render())
print('Forget:', mm.forget('demo', 'commande'), 'fact deleted')
print('After:', repr(mm.read('demo', '?').render()))
"
```

I say before pressing Enter:
“Now I demonstrate the whole memory chantier in one small live example.
First, I create a MemoryManager.
Then I write a useful sentence: ‘My priority order is O-2024-0101.’
Then I write a noisy follow-up question.
After that, I read the memory.
Then I forget the command fact.
Finally, I read again.”

Expected output:

```text
Retained: fact:commande prioritaire=O-2024-0101
Forget: 1 fact deleted
After: ''
```

I explain the output:
“The first line shows that memory retained only the useful fact:
`fact:commande prioritaire=O-2024-0101`
The noisy message was ignored.
So `write()` distilled the conversation instead of storing everything.
The second line says:
`Forget: 1 fact deleted`
That means one matching fact was found and marked as deleted.
The third line says:
`After: ''`
That means after forgetting, memory read returns empty.
So this live demo proves extraction, noise filtering, soft-delete, and right to be forgotten.”

## 8. Run the memory acceptance tests

I run:

```bash
uv run pytest tests/acceptance/test_memory.py -v
```

I say:
“Now I run the official memory acceptance tests.
This is the real proof, because these are not my demo commands. These are the required tests.”

Expected output:

```text
4 passed
```

I explain:
“Four tests passed.
That means the memory satisfies the four requirements:
R1: recall after 30 turns.
R2: persistence between sessions.
R3: isolation between customers.
R5: forget on request.
So the memory contract is complete.
**[ADDED — the progression and the disk lesson]** The progression is in my logbook: 4 red at the baseline, 2 green after the store, 3 green after extraction, then one more failure that taught me a lesson — I re-ran the tests believing `forget` was coded, but the file on disk still said `return 0`. A test does not measure my intention: it measures the code on disk. Once the code was really saved: 4 green.”

## 9. Run the business tests again for non-regression

I run again:

```bash
uv run pytest tests/acceptance/test_business.py -v
```

I say:
“I run the business tests again because memory must not break the existing agent.
A feature is not finished only when its own tests pass. It must also preserve the previous behavior.”

Expected output:

```text
7 passed
```

I explain:
“The seven business tests are still green.
So I have 4 memory tests passed and 7 business tests passed.
Together, that gives 11 green tests for the completed part.”

## 10. Optional global command

I can run:

```bash
uv run pytest -q
```

I say:
“This command runs the broader test suite.
If there are remaining red tests, they correspond to future chantiers, especially guardrails and MLOps.
For my current scope, the important result is:
4 memory tests green.
7 business tests green.
No regression on the existing agent.”

## Final closing

“To conclude, my Chantier 1 is not just code.
It is a tested memory contract.
I started by proving the existing agent with 7 business tests.
Then I used the 4 memory tests as my TDD contract.
I created a durable `memory_facts` table with `user_id` for isolation and `deleted` for forgetting.
I implemented `read`, `write`, `remember_fact`, and `forget`.
I demonstrated that the memory extracts useful facts, ignores noise, persists between sessions, isolates customers, and forgets facts on request.
**[ADDED — complete honest limits]** The honest remaining limits are three: the LLM context injection at line 138 — the memory is read, but `context.render()` still needs to be passed into the prompt, and the socket for it already exists in `llm.py`; the `inspect()` method — observability comfort, with no acceptance test, that I will code right after this debrief; and the token budget of 2000 — respected by design because I only store compact facts, but with no truncation code yet, which will become necessary when short-term history and episodic memory arrive.
So today I can defend exactly what is finished:
The agent still works.
The business tests are green.
The memory tests are green.
The memory covers R1, R2, R3, and R5.
And every claim I made is proven by a command, a file, and an output.”
