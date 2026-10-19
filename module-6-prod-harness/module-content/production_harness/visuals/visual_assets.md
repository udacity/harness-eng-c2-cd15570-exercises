# Visual Asset Inventory

## Required course-native assets

| ID | Asset | Format | Used in |
| --- | --- | --- | --- |
| A1 | Hermes/runtime versus plugin ownership diagram | Editable vector | Video 1 |
| A2 | Three-scenario execute/deny/block matrix | Editable vector | Videos 1, 4 |
| A3 | Manifest/profile/CLI/scenario proof gates | Editable vector | Video 2 |
| A4 | Annotated plugin manifest | Repository capture | Video 2 |
| A5 | Annotated isolated profile | Repository capture | Video 2 |
| A6 | Validator output with limitation callout | Terminal capture | Video 2 |
| A7 | Redacted dry-run command | Terminal capture | Video 2 |
| A8 | Lifecycle short-circuit diagram | Editable vector | Video 3 |
| A9 | Evidence-freshness token animation | Editable vector | Video 3 |
| A10 | State-plus-trace completion oracle | Editable vector | Videos 3, 4 |
| A11 | Four-artifact evidence panel | Editable template | Video 4 |
| A12 | Verification pyramid | Editable vector | Video 5 |
| A13 | Python-loop versus Hermes responsibility table | Editable table | Video 5 |
| A14 | Operational evolution loop | Editable vector | Video 5 |

## Repository captures

Capture only the lines needed for the teaching point:

- `demo/data.py`: the three scenario definitions;
- `demo/.hermes/plugins/incident-response-demo/plugin.yaml`;
- `demo/.hermes/config.yaml`;
- `demo/plugin_impl.py`: `register`, `before_tool`, `after_tool`, and
  `before_completion`;
- `demo/components/permissions.py`: default deny and role decision;
- `demo/components/hooks.py`: freshness, target, repeat, and completion rules;
- `demo/run_demo.py`: command construction and dry-run branch;
- `demo/test_demo.py`: representative deterministic tests;
- `solution/python/loop/configured_agent_loop.py`: custom lifecycle ownership;
- `solution/hermes/configured_plugin.py`: native registrations; and
- `solution/harness-comparison.md`: scoped conclusion.

Do not capture `.env`, credential files, temporary profile contents, full user
paths, or raw prompts containing sensitive operational information.

## Terminal capture plan

1. `hermes --version`
2. `hermes config get model --json` with sensitive fields redacted
3. `hermes plugins validate .hermes/plugins/incident-response-demo`
4. deterministic unit tests
5. safe dry run
6. each real scenario and its compact result
7. selected JSONL events and final incident state

Capture output on the recording machine immediately before recording. CLI text
and current test counts can change with repository or runtime updates.

## Asset provenance

All proposed visuals can be built from course-authored diagrams, local code,
and local terminal output. No third-party stock image or dataset is required.

If a Hermes logo, screenshot from external documentation, or other third-party
asset is later introduced, record its source, license or usage basis,
attribution requirement, modifications, and approval status before publishing.

## Redaction checklist

- [ ] No API keys, tokens, or credential values.
- [ ] No `.env` content.
- [ ] No personal home-directory path.
- [ ] No unrelated plugin or account names from a user profile.
- [ ] No raw incident details beyond the fictional course case.
- [ ] Usage record checked for provider metadata safe to display.
- [ ] Temporary runtime home removed after the run.
- [ ] Trace excerpts preserve meaning after redaction.

## Accessibility checklist

- [ ] Every decision uses shape and text, not color alone.
- [ ] Code font is legible at 1080p.
- [ ] JSON excerpts show no more than the fields being narrated.
- [ ] Animations pause at every short-circuit outcome.
- [ ] Diagrams have equivalent narration and alt text.
- [ ] Deny, block, execute, and complete use distinct labels.
