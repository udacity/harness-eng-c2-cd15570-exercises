# Architecture Diagrams

These Mermaid diagrams are editable references for slide production. Rebuild
them in the course visual language instead of using raw screenshots.

## Basic versus hook-protected execution

```mermaid
flowchart LR
    M[Model proposal] --> P[Parsed tool call]
    P --> B[Basic dispatcher]
    B --> T1[Mutation tool]
    P --> H{before_tool_call}
    S[Trusted state] --> H
    H -->|ALLOW| T2[Same mutation tool]
    H -->|BLOCK/ERROR| R[Structured violations]
    T1 --> E1[State changed without invariant decision]
    T2 --> E2[State changed after checks]
    R --> M
```

## Deterministic hook decision

```mermaid
flowchart TB
    TN[Canonical tool name]
    A[Validated arguments]
    S[Trusted state snapshot]
    X[Prior execution signatures]
    P[Policy + code version]
    F[Pure antidotes]
    D{All required checks pass?}
    TN --> F
    A --> F
    S --> F
    X --> F
    P --> F
    F --> D
    D -->|yes| AL[ALLOW]
    D -->|no/error| BL[BLOCK]
```

## Cumulative control order

```mermaid
flowchart LR
    C[function_call] --> V[Parse/schema validation]
    V --> I[Resolve identity and trusted state]
    I --> P{Permission}
    P -->|deny| PR[Permission result]
    P -->|allow| H{Deterministic safety hook}
    H -->|block| HR[Hook result]
    H -->|allow| T[Atomic/conditional tool]
    T --> PC[Postcondition + evidence invalidation]
    PC --> O[function_call_output]
    PR --> O
    HR --> O
    O --> M[Next model cycle]
```

## Incident antidote composition

```mermaid
flowchart TB
    Q[Proposed mutation]
    C1[Fresh health]
    C2[Target exists]
    C3[Target last-known-good]
    C4[Not repeated]
    C5[Resolution state valid]
    R[HookResult]
    Q --> C1
    Q --> C2
    Q --> C3
    Q --> C4
    Q --> C5
    C1 --> R
    C2 --> R
    C3 --> R
    C4 --> R
    C5 --> R
    R -->|no violations| A[ALLOW]
    R -->|violation/error| B[BLOCK]
```

## Evidence invalidation and replay

```mermaid
sequenceDiagram
    participant M as Model
    participant H as Harness/hook
    participant T as Mutation tool
    participant S as State store

    M->>H: request mutation(signature K)
    H->>S: read state v17 + fresh evidence
    H->>H: antidotes PASS; K unseen
    H->>T: execute with expected state v17 + idempotency K
    T->>S: conditional write v17 -> v18; record K
    S-->>T: success
    T-->>H: executed
    H->>H: invalidate health evidence
    M->>H: retry mutation(signature K)
    H->>H: replay antidote BLOCKS
    H-->>M: already executed / blocked result
```

## Check/use race and conditional fix

```mermaid
sequenceDiagram
    participant H as Hook
    participant A as Other actor
    participant S as Shared state
    participant T as Tool

    H->>S: read/check version 17
    S-->>H: invariant passes
    A->>S: update to version 18
    H->>T: execute expecting version 17
    T->>S: conditional write if version == 17
    S-->>T: conflict; no write
    T-->>H: stale-state failure
```

## Hook result feedback loop

```mermaid
sequenceDiagram
    participant M as Model
    participant H as Harness
    participant K as Hook
    participant T as Tool

    M->>H: function_call + call_id
    H->>K: canonical call + trusted state
    alt allowed
        K-->>H: ALLOW + checks
        H->>T: execute
        T-->>H: execution result
        H-->>M: function_call_output(call_id, executed)
    else blocked/error
        K-->>H: BLOCK + findings
        Note over H,T: Tool is not called
        H-->>M: function_call_output(call_id, blocked)
    end
```
