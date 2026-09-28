| Evidence | Hand-built Python loop | Hermes |
| --- | --- | --- |
| Baseline smoke test | Pass — `python/runs/smoke.json` records `HARNESS_OK` after 4 cycles | Pass — `hermes/runs/smoke.json` records `HARNESS_OK` after 5 cycles |
| Integration tests | Pass — 5 deterministic integration tests passed | Pass — 10 deterministic integration tests passed |
| Skill loaded | `skill_loaded` for `xyz-api-client` from `python/components/skill/SKILL.md` | `skill_registered` and `skill_loaded` for `xyz-api-harness:xyz-api-client` |
| Hook tests | Pass — repeated-call, syntax, and completion hooks were verified | Pass — repeated-call, syntax, and completion hooks were verified |
| Permission tests | Pass — default-deny and assigned-file restrictions were verified | Pass — default-deny and assigned-file restrictions were verified |
| Generated client | `python/runs/src/xyz_api_client.py` | `hermes/runs/src/xyz_api_client.py` |
| Client behavioral tests | Pass — 1 test passed in 0.085 seconds | Pass — 1 test passed in 0.090 seconds |
| Task completed | Yes — trace contains the final `status: completed` event | Yes — trace contains the final `status: completed` event |

# Harness comparison

## Results

Both harnesses completed the assignment and produced working clients. The clients are not identical, but both called `POST /v2/data-sync` with the required headers and body, used a timeout, parsed JSON, and returned errors as dictionaries. The Python-generated client used `requests`, a five-second timeout, and fixed valid client credentials. The Hermes-generated client used the standard library, generated its token and client ID with UUIDs, used a thirty-second timeout, and handled `HTTPError` separately so it could return a rejected API response as parsed JSON.

The final `test-results.json` file for each harness shows a return code of zero. The Python client passed its behavioral test in 0.085 seconds, and the Hermes client passed the same test in 0.090 seconds. This difference is too small to support a performance conclusion, especially because the harnesses used different models and providers.

The baseline evidence also passed for both harnesses. The Python smoke run completed the required read, health check, and documentation request in four cycles. Hermes completed the same operations in five cycles. In both cases, the agent retrieved `/api-docs` instead of guessing the fictional 2026 API contract.

## Skill loading

For the hand-built loop, I connected the skill with `SkillConnection`. Its `add_to_context()` method appends the contents of `python/components/skill/SKILL.md` to the loop's base instructions before the first model call. It also writes a `skill_loaded` event to the trace. The Python run contains that event before any tool use.

For Hermes, I registered `hermes/components/skill/SKILL.md` through `ctx.register_skill()`. The runner passed `--skills xyz-api-harness:xyz-api-client`, and a `pre_llm_call` hook recorded when the skill was loaded into the model context. The Hermes trace therefore contains separate `skill_registered` and `skill_loaded` events. I found the Hermes evidence a little more explicit because it distinguishes making a skill available from actually loading it for a model call.

## Hook connections

The hand-built loop required explicit calls at every lifecycle boundary:

- The repeated-call hook runs after permission approval and before tool execution.
- The syntax hook runs after a successful `write_file` operation and changes the tool result to `hook_blocked` if the generated Python is invalid.
- The completion hook runs for the `run_tests` tool and again before the loop accepts the agent's final response.

Hermes used native lifecycle registrations for the same behavior:

- `pre_tool_call` applies the permission check and then the repeated-call hook.
- `transform_tool_result` applies the syntax hook after a write.
- `pre_verify` applies the completion hook before Hermes finishes.
- `post_tool_call` records trusted results and updates permission state.
- `pre_llm_call` records skill loading.

The configured traces show successful repeated-call checks, a passing syntax check after each generated client was written, and passing completion checks before the final `completed` events. The deterministic integration tests also checked the failure paths: a sixth equivalent call is blocked, invalid Python is rejected, and completion cannot succeed until the fixed behavioral test passes.

## Permission enforcement

Both harnesses used a default-deny `PermissionPolicy`. It limited file access to the assigned generated client, allowed only the local health and documentation URLs, denied public web access, allowed the fixed behavioral test, and required a successful `/api-docs` result before a client write. Both integrations ran the policy before the repeated-call hook or the requested tool, then allowed the policy to observe the trusted result afterward.

In the Python loop, this ordering is application code inside `_handle_tool_call()`. A denial is converted into a structured tool result with `executed: false`, so the model can continue without the denied operation running.

In Hermes, the same policy is attached to `pre_tool_call` and `post_tool_call`. The captured Hermes run gives useful real examples: `tool_search` and `tool_describe` were denied by the default rule, and an attempt to read the supplied test file was denied because it was outside the assigned client path. The agent continued after all three denials. This confirmed that Hermes returned permission failures to the agent instead of crashing or silently executing them.

## Integration effort

The hand-built Python loop required me to own the entire control path. Besides the three connection classes, the loop parses model tool arguments, normalizes paths, applies permissions and hooks in the correct order, dispatches five tools, converts results into model inputs, carries the previous response ID, limits cycles, retries after failed completion, records trace events, and aggregates token usage. This is flexible and the order is easy to see in one file, but every new lifecycle rule has to be placed correctly in custom loop code.

The Hermes integration still required a real adapter rather than only a YAML setting. I registered the five scoped tools, the skill, and five hook boundaries in `configured_plugin.py`. I also enabled the plugin and toolset in `.hermes/config.yaml`, allowed the required tool overrides in the plugin manifest, and used the runner to create an isolated temporary profile. However, Hermes owned the model loop, turn continuation, session handling, and final verification lifecycle. My application code mainly translated the exercise policy and evidence format into Hermes's existing extension points.

Line count by itself would be misleading here because the Hermes runner includes profile isolation, CLI process handling, progress output, and usage capture. The more important difference is ownership: the Python version owns both agent orchestration and component integration, while the Hermes version mainly owns an adapter around a production harness.

## Errors and traces

The Python trace was the simpler one to follow because its successful run took a direct path: documentation discovery, client read, client write, tests, and completion. Each event recorded the selected permission rule, hook result, tool result, and completion status.

Hermes produced clearer evidence for failures in this run. It recorded the denied capability, matching rule, reason, and `executed: false` result. It also captured an early behavioral-test failure while the client still contained `NotImplementedError`. The completion hook rejected that state, the agent wrote the client, the syntax hook passed, and the next behavioral test passed. That recovery sequence demonstrated more of the enforcement behavior than the straight-through Python run.

## Maintainability conclusion

I would choose Hermes for a production harness that is expected to gain more tools, policies, or hooks. Its named lifecycle events make the intended boundary clear, and the framework owns the difficult model-loop state. Adding or replacing a hook is less likely to accidentally break response continuation or tool-result delivery.

The hand-built loop is still a reasonable choice for a small, controlled workflow. It has fewer external framework concepts, and its successful trace was straightforward to debug. Its disadvantage is that the application is responsible for more security-sensitive ordering and state. As the harness grows, maintaining custom dispatch, continuation, completion retries, tracing, and permission boundaries together would create more opportunities for regressions.

Based on the captured results, both approaches were correct, but Hermes provided the better long-term separation of responsibilities. The hand-built loop gave maximum control; Hermes achieved the same observable behavior while keeping the core agent lifecycle inside the harness.

## Verification scope

While preparing this comparison, I reran the deterministic integration tests without making additional live-provider calls. The Python suite reported 5 passed and 1 live-model test deselected; the Hermes suite reported 10 passed and 1 live-model test deselected. The saved smoke files and configured run traces provide the live-model evidence used above, and both saved behavioral-test result files report passing clients.
