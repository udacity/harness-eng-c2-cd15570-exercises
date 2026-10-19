# Architecture Diagrams

These Mermaid diagrams are editable references for slide production. Rebuild
them in the course visual system rather than relying on Mermaid screenshots.

## Eager and on-demand serving paths

```mermaid
flowchart LR
    R[Task request]
    A[All complete skills]
    C[Compact catalog]
    S[Selection call]
    V[Exact-name validator]
    L[Selected skill text]
    B[One writing call]
    W[Final writing call]

    R --> B
    A --> B
    B --> O1[Candidate]

    R --> S
    C --> S
    S --> V
    V --> L
    L --> W
    S -. previous response context .-> W
    W --> O2[Candidate]
```

## Skill versus hook

```mermaid
flowchart TB
    T[Task] --> M[Model]
    K[Selected skill instructions] -. influence .-> M
    M --> P[Proposed tool call]
    P --> H{Before-tool hook}
    E[Trusted state] --> H
    H -->|allow| X[Execute tool]
    H -->|block| F[Return violations]
    X --> R[Tool result]
    F --> M
    R --> M
```

## Discovery and resolution boundary

```mermaid
flowchart LR
    ROOT[Trusted skill root] --> DISC[Discover candidates]
    DISC --> META[Validate metadata]
    META --> ID[Check folder/name and duplicates]
    ID --> CAT[Catalog snapshot]
    CAT --> PROMPT[Metadata-only routing prompt]
    MODEL[Model-selected string] --> LOOKUP{Exact catalog lookup}
    CAT --> LOOKUP
    LOOKUP -->|known| BODY[Load catalog-owned path]
    LOOKUP -->|unknown| ERR[Controlled error result]
    BODY --> PROV[Text plus provenance]
```

## Bounded two-cycle loop

```mermaid
sequenceDiagram
    participant H as Harness
    participant M as Model
    participant C as Trusted catalog

    H->>M: Cycle 1: task + metadata + load_skill
    M-->>H: zero or more function_call items
    loop Each proposed call, up to configured limit
        H->>H: Parse and validate name/arguments
        H->>C: Exact-name lookup
        C-->>H: Skill text + provenance, or error
    end
    H->>M: Cycle 2: correlated outputs; no loader
    M-->>H: Final artifact
    H->>H: Evaluate and record serving metrics
```

## Responsibility boundaries

```mermaid
flowchart LR
    Q[User task] --> G[Generator]
    S[Skills: methods and guidance] -. context .-> G
    D[Retrieval: current facts] --> G
    G --> P[Proposed action]
    A[Permissions: identity/resource] --> B{Execution boundary}
    H[Hooks: deterministic event checks] --> B
    P --> B
    B -->|allowed| T[Business tool]
    B -->|blocked| G
    T --> G
    G --> O[Final output]
    O --> E[Evaluator/checks]
```

## Versioned skill lifecycle

```mermaid
flowchart LR
    A[Author v1.2] --> R[Review]
    R --> V[Validate format/security]
    V --> E[Behavior evaluation]
    E --> C[Canary]
    C --> P[Promote]
    P --> M[Monitor]
    M -->|regression| RB[Rollback to pinned v1.1]
    M -->|new evidence| A
```
