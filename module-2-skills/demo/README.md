# Module 2 Demo: On-Demand Incident-Response Skills

This demo continues the `INC-2048` incident-response use case from Module 1.
The authoritative incident is unchanged: production `checkout-api` is
`DEGRADED` with an 18% error rate while `checkout-v42` is deployed, and no
restart, rollback, recovery, or resolution is confirmed.

Module 1's independent evaluation boundary is supplied here. The new question
is how detailed domain guidance reaches the generator:

| Mode | Flow | What the model receives |
| --- | --- | --- |
| `basic` | Write in one model cycle | All four complete `SKILL.md` files, whether relevant or not |
| `skills` | Select/load in cycle 1 → write in cycle 2 | Names and descriptions first, then only the complete files requested through `load_skill` |

The goal is not to guarantee that one mode writes better. The demo makes
context relevance, skill composition, model calls, tokens, and latency visible.

## Skills

| Skill | When it should be selected |
| --- | --- |
| `incident_triage` | Evidence gathering, hypotheses, and next diagnostic checks |
| `checkout_service_runbook` | `checkout-api` failures, health, deployment, and log diagnosis |
| `safe_remediation` | Restarts, rollbacks, production mutations, and verification |
| `incident_communications` | Accurate internal or stakeholder updates |

`catalog.py` reads only each file's `name` and `description` during routing.
The complete body is read only after an exact allowlisted `load_skill` request.

## Requests

All three requests use the same immutable incident:

| Request | Expected relevant skills |
| --- | --- |
| `checkout_diagnosis` | `incident_triage`, `checkout_service_runbook` |
| `stakeholder_update` | `incident_communications` |
| `incident_response` | All four skills composed together |

Each final note must contain exactly 60 whitespace-separated words, include
`INC-2048`, stay grounded in confirmed facts, and give a useful next step.

## Run the reliable classroom demo

The default scripted provider requires no API key or package installation:

```bash
cd module-2-skills/demo
python3 main.py compare --request checkout_diagnosis
```

Then show the smallest and largest context differences:

```bash
python3 main.py compare --request stakeholder_update
python3 main.py compare --request incident_response
python3 main.py compare --request all
```

Add `--pause` to wait for Return after every serving-model cycle. Every run
writes a timestamped terminal log under `output/`.

The scripted provider produces stable, grounded 60-word notes and deterministic
skill choices. Its token counts are illustrative estimates derived from the
request payloads, and its near-zero local timings are not model latency. Use a
live run for real API usage and timing evidence.

## Run with a live model

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Put your course API key in `.env`, then run:

```bash
python3 main.py compare --request checkout_diagnosis --provider live
```

Override the configured model if needed:

```bash
python3 main.py skills --request incident_response \
  --provider live --model gpt-4.1-mini
```

The default endpoint is `https://openai.vocareum.com/v1`; override it with
`OPENAI_BASE_URL`. `.env` and generated logs are ignored by Git.

Live skill selection and prose can vary. A model may omit a relevant skill,
load an unnecessary one, or produce a worse response with less context. Treat
those outcomes as evidence rather than forcing a preferred result.

## What happens in `basic`

`run_basic()` reads every complete skill and adds all of them to one prompt:

```text
base instructions
      +
all four complete SKILL.md bodies
      +
incident request
      ↓
one model call
      ↓
final incident note
```

This is simple and gives the model every rule, but every task pays for every
skill and unrelated guidance competes for attention.

## What happens in `skills`

The on-demand path follows the same two-cycle pattern used by the exercise:

```text
Cycle 1
base instructions + names/descriptions + incident request
                         ↓
             load_skill function calls
                         ↓
harness validates exact names and returns complete skill text

Cycle 2
previous_response_id=selection.id + function_call_output items
                         ↓
tools are no longer offered
                         ↓
final incident note
```

Unknown names, malformed JSON, extra arguments, and unsupported tools become
controlled `ERROR` results. They never become filesystem paths. If the model
selects no skill, cycle 2 still asks for a final response.

## Supplied evaluation boundary

After either serving path finishes, `evaluator.py` applies the Module 1 pattern:

- Python checks the exact 60-word count and `INC-2048` identifier.
- A fresh model conversation judges factual grounding and the next step.

The comparison table excludes this blind evaluator's tokens and time because it
is experiment overhead, not part of the eager or on-demand serving path. Its
cost is printed separately.

## What to show during the demo

1. Open one `SKILL.md` and distinguish its short frontmatter description from
   its detailed body.
2. Run `basic` and show all four complete files in the prompt.
3. Run `skills` and show that cycle 1 contains only the routing catalog.
4. Follow each `load_skill` call to its validated `function_call_output`.
5. Point out that cycle 2 continues from `selection.id` without offering tools.
6. Compare full skill characters, API tokens, model time, and evaluated output.
7. Run `stakeholder_update` to show one selected skill, then
   `incident_response` to show composition.

## From this demo to the exercise

The domain changes from incident response to InspectAI marketing, but the
implementation tasks map directly:

| Demo implementation | Exercise work |
| --- | --- |
| `catalog_prompt()` | Build one name/description line per skill without loading bodies |
| `SKILL_TOOL` | Define the strict `load_skill` function schema |
| `build_selection_instructions()` | Combine base instructions with only the short catalog |
| `resolve_skill_call()` | Parse, allowlist, load, and return one `function_call_output` |
| `write_with_skills()` | Continue from `selection.id` without tools |
| `run_with_skills()` | Connect selection, loading, writing, printing, pauses, and metrics |
| Editing one `SKILL.md` body | Change domain guidance without changing routing code |

The exercise has six marketing skills and six campaign briefs. This demo has
four incident skills and three requests. Both compare an all-skills one-call
baseline with a two-cycle progressive-disclosure path, and both require the
no-skill case to finish successfully.

To observe maintainability directly, make a small safe wording change inside a
demo skill and rerun that request with `--provider live`, then restore the file.
The routing code and catalog do not need to change. Scripted output is fixed and
therefore validates loading behavior rather than semantic response changes.

## Deterministic tests

```bash
python3 -m unittest discover -s . -p 'test_*.py'
```

The tests require no API key. They cover the shared incident, catalog-only
routing, strict tool schema, exact allowlisting, malformed requests, eager
context, selective loading, tool removal in cycle 2, no-skill completion, exact
60-word outputs, and separation of evaluator overhead.

## Repository map

```text
demo/
├── main.py                     # CLI, paired runs, evaluation, comparison
├── agent.py                    # eager and on-demand skill paths
├── catalog.py                  # frontmatter discovery and exact loading
├── clients.py                  # deterministic Responses API double
├── evaluator.py                # supplied Module 1 evaluation boundary
├── scenario.py                 # incident/request loading and shared prompt
├── run_log.py                  # timestamped terminal logs
├── data/
│   └── incident.json           # stable INC-2048 facts
├── requests/                   # three tasks over the same incident
├── skills/                     # four complete incident-response skills
├── test_demo.py
├── .env.example
└── requirements.txt
```

Module 3 will retain these skills and evaluation checks while adding business
tools and deterministic before-tool hooks.
