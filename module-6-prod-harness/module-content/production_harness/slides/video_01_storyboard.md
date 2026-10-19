# Storyboard — Video 1: From Components to a Production Runtime

**Target runtime:** 6 minutes  
**Visual motif:** Loose component cards lock into named runtime boundaries.

## Slide 1 — The integration question

**Time:** 0:00–0:35  
**On-screen text:** Who owns the complete lifecycle?  
**Visual:** Evaluator, skills, hooks, permissions, and tools float around an
unfinished loop.

## Slide 2 — Three use cases

**Time:** 0:35–1:25  
**Visual:** Three-row matrix.

| Subject | Target | Outcome |
| --- | --- | --- |
| Authorized | Safe v41 | Execute |
| Unauthorized | Safe v41 | Deny |
| Authorized | Unsafe v40 | Block |

**Callout:** Start from fresh `checkout-v42` every time.

## Slide 3 — Why the positive control matters

**Time:** 1:25–2:05  
**Visual:** A locked door versus a selective access gate.  
**On-screen text:** Blocking everything is not operational success.

## Slide 4 — Runtime versus plugin

**Time:** 2:05–3:05  
**Visual:** Two ownership columns with no overlapping boxes.

| Hermes | Plugin |
| --- | --- |
| Calls and continuation | Tools and skills |
| Lifecycle dispatch | Permissions and hooks |
| Session bounds | Completion criteria |
| Usage accounting | Domain evidence |

## Slide 5 — One execution path

**Time:** 3:05–3:45  
**Visual:** `run_demo.py` launches one Hermes box; no parallel custom-loop box.  
**Callout:** Launcher ≠ agent runtime.

## Slide 6 — Components become contracts

**Time:** 3:45–4:40  
**Visual:** Skill snaps into pre-model, permission and safety into pre-tool,
trace into post-tool, oracle into pre-verify.

## Slide 7 — Scope of “production”

**Time:** 4:40–5:25  
**Visual:** Inner ring labeled “demonstrated”: lifecycle, scoping, enforcement,
bounds, evidence. Outer ring labeled “additional system work”: durable state,
secrets, HA, release process.

## Slide 8 — Takeaway

**Time:** 5:25–6:00  
**Full-screen statement:** “One runtime owns mechanics. The plugin owns domain
truth.”  
**Transition:** Next: declare, activate, validate, and select.

## Production notes

- Introduce the scenarios before any command.
- Use different visual shapes for denial and safety block.
- Never draw `run_demo.py` as a second model loop.
- Repository capture: `demo/data.py`, then `demo/plugin_impl.py`.
