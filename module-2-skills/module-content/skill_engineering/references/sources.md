# Sources and Research Notes

Accessed October 18, 2026. Recheck changing specifications and API guidance
before final recording.

## R1 — Agent Skills specification

**Agent Skills project.** “Specification.”  
[Specification source](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx) ·
[Project repository](https://github.com/agentskills/agentskills)

**Relevant use:** Defines a skill directory centered on `SKILL.md`, required
metadata, optional resources, validation constraints, and progressive
disclosure from metadata to instructions to supporting files.

**Guardrail:** The Module 2 repository is a teaching-specific subset. It uses
underscore names, a minimal frontmatter parser, one Markdown file per skill,
and no automatic supporting-resource loader. Do not claim full specification
conformance.

## R2 — OpenAI function calling

**OpenAI.** “Function calling.”  
[Official OpenAI documentation](https://developers.openai.com/api/docs/guides/function-calling)

**Relevant use:** Supports the model-call/tool-call/tool-result flow, JSON
Schema function definitions, handling zero or more calls, correlation through
`call_id`, `function_call_output`, strict-mode guidance, and continuation to a
final model response.

**Guardrail:** The course's `load_skill` design is application code built on
function calling. It is not a claim that the API automatically discovers or
secures local `SKILL.md` files. The current demo closes its argument object with
`additionalProperties: false` but does not set the provider's `strict: true`
flag. The pseudocode example recommends that flag; the harness validates every
call in either case.

## R3 — Prompt injection risk

**OWASP GenAI Security Project.** “LLM01:2025 Prompt Injection.”  
[OWASP guidance](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

**Relevant use:** Supports treating model-consumed instructions and retrieved
content as a possible instruction-injection surface rather than a trusted
security boundary.

**Guardrail:** Do not claim that allowlisting a skill name eliminates prompt
injection. Allowlisting controls which package is loaded; review, provenance,
runtime isolation, permissions, and hooks address different risks.

## R4 — Secure development lifecycle

**NIST.** “SP 800-218A: Secure Software Development Practices for Generative AI
and Dual-Use Foundation Models.” July 2024.  
[NIST publication page](https://csrc.nist.gov/pubs/sp/800/218/a/final) ·
[DOI](https://doi.org/10.6028/NIST.SP.800-218A)

**Relevant use:** Supports treating AI-system artifacts and dependencies within
a secure development lifecycle: provenance, review, testing, controlled
release, and vulnerability response.

**Guardrail:** This module applies those general lifecycle principles to skill
packages. NIST does not prescribe this repository's exact catalog or loader.

## R5 — Repository implementation: Module 2 demo

Primary local sources:

- `module-2-skills/demo/catalog.py`
- `module-2-skills/demo/agent.py`
- `module-2-skills/demo/test_demo.py`
- `module-2-skills/demo/skills/*/SKILL.md`

**Relevant use:** Authoritative source for claims about this demo's supported
frontmatter, symlink handling, exact-name lookup, two-cycle path, no-skill
fallback, tool removal, metrics, and deterministic tests.

**Guardrail:** A behavior demonstrated here is not automatically a universal
Agent Skills or provider behavior.

## R6 — Repository implementation: Module 3 hooks

Primary local sources:

- `module-3-hooks/demo/hooks.py`
- `module-3-hooks/demo/agent.py`
- `module-3-hooks/demo/README.md`

**Relevant use:** Authoritative source for the course distinction between
model-facing skill guidance and deterministic before-tool enforcement.

**Guardrail:** Use Module 3 only to clarify the boundary. Module 2 does not ask
students to implement the complete hook system.

## Claim-to-source map

| Course claim | Source | Approved phrasing |
| --- | --- | --- |
| Skills can use staged metadata, instruction, and resource loading | R1 | “The broader specification defines progressive disclosure; runtime support varies.” |
| Tool calls require application-side handling and correlated outputs | R2 | “The harness parses calls, executes or resolves them, and returns results using the call ID.” |
| Model-consumed content can create instruction-injection risk | R3 | “Trusted distribution and runtime controls are still required.” |
| AI artifacts should be governed through a secure lifecycle | R4 | “Review, test, trace, stage, monitor, and support rollback.” |
| This demo uses exact catalog names and two cycles | R5 | “The Module 2 implementation behaves this way.” |
| Hooks can block a mutation before tool execution | R6 | “The Module 3 before-tool hook enforces this boundary.” |

## Citation and recording policy

1. Cite current official or primary sources in speaker notes.
2. Identify repository-specific behavior as repository-specific.
3. Recheck R1 and R2 immediately before recording.
4. Do not present illustrative routing or token numbers as measured results.
5. Do not quote changing limits or platform features unless verified on the
   recording date.
6. Keep external specification details secondary to the harness engineering
   principles learners implement locally.
