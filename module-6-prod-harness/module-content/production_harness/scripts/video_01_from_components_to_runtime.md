# Video 1 — From Components to a Production Runtime

**Target runtime:** 6 minutes  
**Teaching purpose:** Establish the production-runtime ownership boundary and
introduce the three use cases before discussing commands or implementation.

## Opening

The first five modules answered five different questions. How do we evaluate a
candidate response? How do we give the model scoped operating knowledge? How do
we enforce deterministic state rules? How do we restrict actions to trusted
authority? And how do we measure whether each component earns its place?

Module 6 asks the integration question: who owns the complete lifecycle when
these qualified components run together?

A folder containing tools, skills, hooks, and permissions is not yet a
production harness. Each component must be attached to a runtime event. The
runtime must continue after tool results, enforce bounded stopping behavior,
record usage, and verify business completion. Those responsibilities need one
explicit owner.

## Start with the use cases

Before opening the plugin, introduce the three scenarios in `demo/data.py`.
They all start from the same degraded incident. `checkout-api` is running
`checkout-v42` with an 18 percent error rate. Recovery is not confirmed.

The first scenario is `safe-rollback`. Morgan Chen is the incident commander,
and the target is `checkout-v41`, the last-known-good deployment. Permission
and safety must allow the request, and the rollback handler must execute.

The second is `unauthorized-rollback`. The target remains safe, but the trusted
user is Sam Rivera, the assigned support engineer. Sam can read assigned
incident evidence, but does not have `deployment.rollback`. Authorization must
deny the mutation.

The third is `unsafe-rollback`. Morgan is again authorized, but the requested
target is `checkout-v40`, which is not last-known-good. Permission must allow
the request and deterministic safety must block it.

```text
authorized + safe   -> execute
unauthorized + safe -> deny
authorized + unsafe -> block
```

The first row is the positive control. A harness that denies every mutation can
look safe in a negative test, but it cannot recover the service. Production
control means letting valid work pass while stopping invalid work for the right
reason.

## The ownership boundary

Open `demo/README.md` and draw two columns.

Hermes owns the generic mechanics: model calls, tool-call continuation, session
state, delivery of preloaded skills, lifecycle dispatch, completion nudges,
turn limits, and usage accounting.

The plugin owns the domain contract: six incident tools, two response skills,
trusted permissions, repeated-call and mutation rules, scenario completion
criteria, and structured incident evidence.

```text
Hermes runtime                 incident plugin
--------------                 ---------------
model lifecycle                business tools
tool continuation              domain skills
hook dispatch                  authorization policy
session bounds                 deterministic safety
completion mechanism           completion criteria
usage accounting               incident trace semantics
```

This is not a statement that frameworks remove application work. It is a
statement about separation of responsibilities. The application still has to
define what is authorized, what is safe, and what counts as complete. It does
not have to reimplement generic model and tool continuation.

## One execution path

The incident demo uses one execution path: the real Hermes CLI. It does not
present a handwritten loop beside Hermes.

`run_demo.py` can look loop-like because it constructs a command, prepares an
isolated profile, creates fresh scenario state, invokes a subprocess, and
derives a summary. But it never parses a model tool request and decides what to
call next. That iteration stays inside Hermes.

This distinction matters during review. If launch support also begins handling
tool continuation or completion retries, the repository has created a second
runtime with a second set of lifecycle semantics.

## Components become boundary contracts

A production integration does more than import files.

The two skills must be registered and then selected for the session. The
permission policy must run before a proposed tool. Repeated-call and mutation
hooks must run only after authorization admits the call. Successful tool
results must update evidence state. Completion must be checked before the
runtime accepts a final response.

Each connection needs an observable fact. Availability of a skill is not the
same as delivery. A model proposal is not execution. A process exit is not
business completion.

## What production means here

In this module, “production harness” means a framework-owned agent lifecycle
with explicit extensions, scoped capabilities, trusted enforcement, bounded
continuation, and structured run evidence.

The local demo does not claim to implement a full deployment platform. It does
not establish enterprise secret management, distributed locking, durable
queues, high availability, or organization-wide incident policy. Those are
important production concerns, but they are outside this repository's proof.

Precision about scope is itself a production habit.

## Closing

Module 6 begins with three business outcomes and one ownership boundary. Hermes
owns the generic lifecycle. The plugin owns the incident contract. The safe
case must execute, the unauthorized case must be denied, and the unsafe case
must be blocked.

Next, we will turn that ownership model into a package, activate it in an
isolated profile, validate its declared capabilities, and inspect the real
command without executing a scenario.

## On-screen repository anchors

- `demo/README.md`: architecture and scenario table
- `demo/data.py`: trusted users, target versions, expected boundaries
- `demo/run_demo.py`: launch and profile-isolation support
- `demo/plugin_impl.py`: domain-to-runtime adapter
