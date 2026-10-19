# Storyboard — Video 2: Package, Activate, and Validate the Plugin

**Target runtime:** 7 minutes  
**Visual motif:** Four gates, each proving a different property.

## Slide 1 — Four distinct contracts

**Time:** 0:00–0:40  
**Visual:** Manifest → profile → CLI selection → scenario.  
**On-screen text:** Each stage answers a different question.

## Slide 2 — Package declaration

**Time:** 0:40–1:30  
**Visual:** Annotated `plugin.yaml` with name, version, six tools, four hooks.  
**Callout:** Declaration is not implementation or activation.

## Slide 3 — Runtime registration

**Time:** 1:30–2:15  
**Visual:** `register()` fans out to tool, skill, and hook registrations. A
separate dashed capability-probe path uses unavailable handlers.

## Slide 4 — Activation and bounds

**Time:** 2:15–3:05  
**Visual:** Annotated profile: enabled plugin, CLI toolset, skill discovery off,
coding context off, turn and verify limits.

## Slide 5 — Validator evidence

**Time:** 3:05–4:05  
**Visual:** Validator result cards: parse, load, probe, declarations, collision,
security scan.  
**Warning bar:** No model call. No business workflow proof.

## Slide 6 — Dry-run command preview

**Time:** 4:05–5:05  
**Visual:** Render the resolved command with flags highlighted.  
**On-screen text:** Preview only: no session, tools, state reset, or new evidence.

## Slide 7 — Isolated profile

**Time:** 5:05–6:10  
**Visual:** Temporary Hermes home contains plugin, config, and supported
credential inputs; unrelated profile content remains outside.

## Slide 8 — Proof ladder

**Time:** 6:10–7:00  
**Visual:** Ladder labeled validate → deterministic tests → live scenarios →
post-run audit.  
**Transition:** Next: exact lifecycle ordering.

## Production notes

- Use “structurally loadable,” never “production-safe,” for validator success.
- Show `--dry-run` as an eye icon, not a play icon.
- Do not display real credential values or the user profile path.
- Repository captures: manifest, profile, validation output, dry-run output.
