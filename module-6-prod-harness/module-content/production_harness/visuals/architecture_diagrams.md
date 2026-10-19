# Architecture Diagrams

These Mermaid sources are production references. Redraw them in the course
visual system rather than relying on Mermaid defaults in the final video.

## 1. Runtime ownership

```mermaid
flowchart LR
    O[Operator task]
    H[Hermes runtime<br/>model, continuation, session, usage]
    P[Incident plugin<br/>tools, skills, policy, hooks, oracle]
    S[Authoritative<br/>incident state]
    E[Run evidence]

    O --> H
    H <--> P
    P <--> S
    H --> E
    P --> E
```

**Use:** Video 1.  
**Required annotation:** `run_demo.py` prepares and invokes the runtime; it is
not a second model loop.

## 2. Package-to-session gates

```mermaid
flowchart LR
    M[plugin.yaml<br/>declares]
    R[register ctx<br/>implements]
    V{validator<br/>matches?}
    C[config.yaml<br/>activates]
    L[CLI flags<br/>select toolset + skills]
    X[real session]

    M --> V
    R --> V
    V -->|pass| C --> L --> X
```

**Use:** Video 2.  
**Guardrail:** Validator arrow ends before the real session; do not imply
business behavior was tested.

## 3. Production lifecycle and short circuits

```mermaid
flowchart TD
    A[Selected skills]
    B[pre_llm_call evidence]
    C[Model proposes tool]
    D{Permission?}
    E{Repeat limit?}
    F{Mutation safe?}
    G[Registered handler]
    H[post_tool_call evidence]
    I{pre_verify complete?}
    J[Completion]
    K[Structured executed=false result]
    N[Bounded corrective nudge]

    A --> B --> C --> D
    D -->|deny| K
    D -->|allow| E
    E -->|block| K
    E -->|allow| F
    F -->|block| K
    F -->|allow / nonmutation| G --> H --> I
    K --> I
    I -->|yes| J
    I -->|no| N --> C
```

**Use:** Video 3.  
**Required styling:** Deny and block paths never touch the handler. Add a
maximum-turn/verification badge to the loop from nudge to model.

## 4. Scenario proof matrix

```mermaid
flowchart LR
    subgraph SAFE[Safe rollback]
      S1[Morgan + v41] --> S2[Allow] --> S3[Safety pass] --> S4[Execute] --> S5[v41]
    end
    subgraph UNAUTH[Unauthorized rollback]
      U1[Sam + v41] --> U2[Deny] --> U3[No execution] --> U4[v42]
    end
    subgraph UNSAFE[Unsafe rollback]
      F1[Morgan + v40] --> F2[Allow] --> F3[Safety block] --> F4[No execution] --> F5[v42]
    end
```

**Use:** Videos 1 and 4.  
**Annotation:** Every lane starts from freshly prepared `checkout-v42`.

## 5. Completion evidence

```mermaid
flowchart TD
    Q[Model attempts to finish]
    O{Scenario oracle}
    A[Authoritative state]
    T[Ordered trace]
    C[Completion event]
    N[Continue with corrective nudge]
    P[Final prose]

    A --> O
    T --> O
    Q --> O
    O -->|pass| C
    O -->|fail| N
    P -. not authoritative .-> O
```

**Use:** Videos 3 and 4.  
**Guardrail:** The dashed prose line must not visually override state or trace.

## 6. Evidence reconciliation

```mermaid
flowchart TD
    R[One real run]
    S[incident.json<br/>state]
    T[run.jsonl<br/>ordered cause]
    U[usage.json<br/>runtime work]
    D[run-result.json<br/>derived summary]
    A[Post-run audit]

    R --> S
    R --> T
    R --> U
    S --> D
    T --> D
    U --> D
    S --> A
    T --> A
    U --> A
    D --> A
```

**Use:** Video 4.  
**Annotation:** Derived summary is convenient, not a replacement for source
evidence.

## 7. Exercise ownership comparison

```mermaid
flowchart TD
    C[Equivalent components<br/>and incomplete clients]
    PY[Hand-built Python loop<br/>application owns lifecycle]
    HE[Hermes integration<br/>framework owns lifecycle]
    API[Local XYZ API<br/>/health + /api-docs + /v2/data-sync]
    TP[Python-generated client test]
    TH[Hermes-generated client test]
    PAR{Behavioral parity?}
    COMP[Compare ownership and maintenance]

    C --> PY
    C --> HE
    PY --> API
    HE --> API
    PY --> TP --> PAR
    HE --> TH --> PAR
    PAR -->|yes| COMP
```

**Use:** Video 5.  
**Guardrail:** Do not merge the two generated workspaces or imply their source
must be identical.

## 8. Operational evolution loop

```mermaid
flowchart LR
    A[Runs, failures,<br/>denials, blocks, costs]
    B[Curate privacy-safe<br/>cases and metrics]
    C[Deterministic + live<br/>qualification suite]
    D[Versioned plugin change]
    E{Release gates pass?}
    F[Staged rollout<br/>and monitoring]
    G[Revise or roll back release]

    A --> B --> C --> D --> E
    E -->|yes| F --> A
    E -->|no| G --> D
```

**Use:** Video 5.  
**Required note:** Release rollback here is different from the incident
`rollback_deployment` tool.
