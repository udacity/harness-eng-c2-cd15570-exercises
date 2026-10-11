# Module 2 Demo: Six-Minute Instructor Script

## Before the demonstration

Confirm that the dependencies are installed and that `.env` contains a current
Vocareum `OPENAI_API_KEY`. Start in `module-2-skills/demo`.

Keep these files open in the editor:

1. `data/incident.json`
2. `requests/stakeholder_update.json`
3. `skills/incident_communications/SKILL.md`
4. `catalog.py`
5. `agent.py`
6. `main.py`

Use `stakeholder_update` for the recorded demonstration because it shows the
clearest contrast: `basic` supplies all four complete skills, while the
on-demand path should need only incident communications. Live skill choices and
final notes vary. Describe the result that appears instead of promising a
specific selection, token count, or evaluation result.

## 0:00–1:00 — Connect skills to the incident

**Show:** `data/incident.json`, then `requests/stakeholder_update.json`.

**Say:**

> This demo continues incident `INC-2048` from Module 1. Production
> `checkout-api` is degraded with an 18 percent error rate while
> `checkout-v42` is active. The incident is still under investigation. No
> restart, rollback, or recovery is confirmed.
>
> Our request is an exactly 60-word stakeholder update. That task needs
> communication guidance, but it does not need every detailed runbook in the
> repository. Module 2 asks how an agent can discover and load only the
> instructions relevant to the current request.

**Point out:**

- The incident and request are identical in both modes.
- A skill supplies instructions; loading one does not execute a production
  action.
- The Module 1 evaluator still checks the finished note independently.

## 1:00–2:10 — Show progressive disclosure

**Show:** `skills/incident_communications/SKILL.md`.

**Say:**

> Each skill has two layers. The frontmatter contains a short name and routing
> description. The body contains the detailed domain guidance. The catalog can
> expose the small routing layer without placing every complete skill in the
> model context.
>
> This communication skill explains how to report confirmed impact, preserve
> uncertainty, distinguish proposed actions from completed actions, and end
> with a useful next step. Other skills contain similarly detailed guidance for
> triage, the checkout service, and safe remediation.

**Show:** `catalog.py`.

**Say:**

> `discover_skills` reads only frontmatter when it builds the catalog. If the
> model later requests a skill, `load_skill` accepts only an exact name already
> in that catalog. The catalog is therefore both a routing index and an
> allowlist; arbitrary paths are never loaded.

## 2:10–3:20 — Compare the two serving paths

**Show:** `run_basic` in `agent.py`.

**Say:**

> The basic path eagerly reads all four complete `SKILL.md` files and places
> them in one prompt. It needs one model cycle, but this stakeholder request
> pays for triage, checkout, remediation, and communication guidance whether
> those instructions are relevant or not.

**Show:** `build_selection_instructions`, `resolve_skill_call`, and
`run_with_skills` in `agent.py`.

**Say:**

> The skills path uses two cycles. Cycle one receives the request, the short
> catalog, and a strict `load_skill` tool. The harness validates each requested
> name and returns the complete selected file as a tool result.
>
> Cycle two continues from the selection response ID, supplies those tool
> results, and asks for the final note. The loading tool is no longer offered,
> so selection ends before writing begins.

**Summarize the comparison:**

```text
basic:  request + all complete skills → final note

skills: request + short catalog → load selected skill
                                  → final note using selected guidance
```

## 3:20–6:10 — Run and narrate the demo

**Show:** the terminal in `module-2-skills/demo`.

**Run:**

```bash
python3 main.py compare --request stakeholder_update
```

### At the request display

**Say:**

> The terminal prints the authoritative incident, the operator request, and the
> expected skill benchmark. The benchmark is useful for this experiment, but it
> does not force the model's selection.

### At `BASIC LOOP START`

**Say:**

> The basic loop has one serving cycle. Notice that the prompt includes all
> four complete skill files. `Full skill text supplied` is their raw character
> count, not a token count.

Wait for the final note and the `Cycle complete` prompt.

**Say:**

> This is the basic candidate. Pressing Return ends the presenter pause; the
> waiting time is excluded from model latency. The independent evaluator now
> checks the exact word count, incident ID, factual grounding, and next step.

Press Return. Briefly describe the displayed evaluation result. If it fails,
name the failed criterion without treating the failure as a problem with the
demo.

### At `SKILLS LOOP START`

**Say:**

> The on-demand path begins with names and descriptions only. The catalog is
> small even though the complete skill bodies are detailed.

Wait for the first `Cycle complete` prompt.

**Say:**

> The tool-call lines show what the model selected, and each tool result shows
> the exact file the harness loaded. For this request, incident communications
> is the expected selection. If the model selected anything else, we record
> that observed behavior rather than changing it.

Press Return.

### At `SKILLS CYCLE 2 OF 2`

**Say:**

> The writing call continues from the first cycle using
> `previous_response_id`. The selected skill text is now available, and tools
> are not offered again. This separates routing from final writing.

Wait for the final note and press Return. Briefly describe the independent
evaluation result and the `Expected skill selection matched` line.

### At the final comparison table

**Say:**

> `Skill chars` is the amount of complete skill text supplied. In basic mode it
> is all four files; in skills mode it is only the files selected through the
> tool.
>
> `Input` and `Output` are API tokens. The skills row adds both serving cycles,
> so input is not just the selected file. It also includes routing instructions,
> the catalog, the tool definition, conversation context, and the writing
> cycle. `Total` adds input and output tokens, and `Seconds` adds model time but
> excludes our pauses and evaluator overhead.
>
> Read the `change` row from basic to skills. Negative skill characters or
> input tokens mean the on-demand path used less context. Positive output or
> time can reflect the extra selection cycle. The important tradeoff is smaller
> task-specific context versus an additional model call.

## 6:10–6:40 — Close the demonstration

**Say:**

> Skills turn a large instruction library into a small routing catalog plus
> detailed guidance loaded on demand. The harness keeps control of discovery,
> exact-name validation, tool-result delivery, and loop termination. The model
> chooses what appears relevant, while the application decides what can be
> loaded and measures the result.
>
> For a composition example, run `incident_response` after the video. That
> request needs all four skills, so it demonstrates that on-demand loading is
> most useful when a task needs only part of the available instruction library.

