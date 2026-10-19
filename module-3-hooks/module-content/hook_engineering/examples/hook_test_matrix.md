# Hook Test and Reliability Matrix

## Pure antidote tests

| Rule | Pass cases | Fail/error cases |
| --- | --- | --- |
| Positive amounts | `0.01`, normal cent values | `0`, negative, Boolean, NaN, infinity, invalid string, `0.001` |
| Meal limit | non-meal; meal `100.00` | meal `100.01`; invalid money |
| Approval | `500.00` without approval; any amount with `True` | `500.01` without explicit `True` |
| Unique receipts | all nonempty and distinct | missing, blank, later duplicate |
| Reported total | exact cent sum | ±`0.01`, invalid line amount, invalid total |
| Rollback target | known last-known-good target | unknown or known non-LKG target |
| Resolution | `HEALTHY` and recovery `True` | either condition absent |
| Replay | new canonical signature | exact equivalent signature already executed |

## Hook contract tests

| Boundary | Test | Required evidence |
| --- | --- | --- |
| Target | Unknown hook target | Block; no dispatch |
| Parsing | Malformed JSON | Controlled error; no hook/tool execution |
| Shape | Missing or extra arguments | Block; no dispatch |
| Identity | Incident/report ID mismatch | Block using trusted state |
| Completeness | Several applicable rules fail | Every failure is returned |
| Allow path | All required checks pass | Same business tool executes once |
| Block path | One check fails | Business tool call count remains zero |
| Hook exception | Check raises or times out | Fail closed; diagnostic event |
| Feedback | Block result sent to model | Matching `call_id`; `tool_executed=false` |
| Evidence invalidation | Mutation succeeds | Old freshness flag becomes false |
| Replay | Model repeats an executed mutation | Second execution blocked |
| No proposal | Model answers without protected call | Hook reports not run, not pass |
| Cycle limit | Model never completes | Explicit terminal failure; no manufactured answer |

## Wiring and bypass tests

Pure checks are insufficient unless every sensitive path uses them. Add
integration tests that:

1. wrap the mutation tool with a spy and assert zero calls after `BLOCK`;
2. assert exactly one call after `ALLOW`;
3. invoke every public dispatcher or endpoint that can reach the mutation;
4. reject any direct route that bypasses the hook;
5. verify permission runs before validity checks when authorization exists;
6. verify post-mutation state and evidence invalidation;
7. simulate a stale expected state version and require conditional execution to
   fail; and
8. prove logs distinguish requested, allowed, executed, and completed.

## Property and state-machine tests

- For all cent-precise meal amounts `x <= 100.00`, the meal rule passes.
- For all cent-precise meal amounts `x > 100.00`, it fails.
- Reordering JSON object keys does not change a canonical mutation signature.
- Replaying the same allowed signature cannot execute twice.
- A successful mutation changes the state version and invalidates evidence.
- No transition reaches `RESOLVED` from a non-healthy or unconfirmed state.

Property testing supplements named examples; it does not replace integration
tests at the dispatch boundary.

## Reliability metrics

- protected calls proposed;
- hook invocations;
- allow, block, error, and not-applicable counts by named rule;
- protected tools executed;
- blocked-call execution escapes, which must be zero;
- repeated-call executions, which must be zero when deduplication applies;
- stale-state/conditional-write conflicts;
- model recovery after block;
- cycle-limit failures;
- policy version coverage; and
- latency added by validation and trusted-state retrieval.

## Evidence interpretation

Passing pure tests proves predicate behavior over those cases. Passing wiring
tests supports the claim that dispatch honors the decision. Live-model runs
show whether proposals and explanations exercise the boundary. None of those
alone proves the invariant across untested routes or changing external state.
