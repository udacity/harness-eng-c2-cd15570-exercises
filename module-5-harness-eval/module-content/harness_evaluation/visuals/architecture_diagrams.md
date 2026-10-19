# Architecture Diagrams

These Mermaid sources are production references. Redraw them in the course
visual system rather than relying on Mermaid defaults in final video.

## 1. System under evaluation

```mermaid
flowchart TD
    R[Operator request]
    G[Generator / agent]
    S[Optional on-demand skills]
    P[Optional permission check]
    H[Optional deterministic hook]
    T[Business tool]
    C[Candidate response]
    O[Optional online critic<br/>and one text-only revision]
    F[Final response]
    J[Blind offline judge]

    R --> G
    S --> G
    G --> P --> H --> T --> C
    C --> O --> F
    F --> J
```

**Use:** Video 1.  
**Required labels:** Online critic is serving; blind judge is experiment
overhead.

## 2. Evidence layers

```mermaid
flowchart LR
    A[Model proposal]
    B[Permission decision]
    C[Hook decision]
    D[Dispatcher event]
    E[Final trusted state]
    F[Deterministic oracle]
    G[Blind quality judge]
    H[Trial row]

    A --> B --> C --> D --> E
    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    F --> H
    G --> H
```

**Use:** Videos 1 and 3.  
**Annotation:** No prose-to-execution shortcut.

## 3. Controlled ablation pairs

```mermaid
flowchart TD
    FULL[full<br/>S E H P]
    NS[no-skills<br/>- E H P]
    NE[no-evaluator<br/>S - H P]
    NH[no-hooks<br/>S E - P]
    NP[no-permissions<br/>S E H -]
    BARE[bare<br/>- - - -]

    FULL -->|skills effect| NS
    FULL -->|evaluator effect| NE
    FULL -->|hooks effect| NH
    FULL -->|permissions effect| NP
    FULL -. four variables .-> BARE
```

**Use:** Video 2.  
**Required note:** Bare is a baseline, not a one-component estimate.

## 4. Target task design

```mermaid
flowchart LR
    S[Skills] --> ST[Specialized diagnosis<br/>private owner + playbook]
    E[Online evaluator] --> ET[Stakeholder update<br/>response policy]
    H[Hooks] --> HT[Unsafe rollback<br/>v40 invalid]
    P[Permissions] --> PT[Permission boundary<br/>v41 safe but unauthorized]
```

**Use:** Video 2.  
**Annotation:** A baseline routine-triage task sits outside the four targets.

## 5. Shadow observation

```mermaid
sequenceDiagram
    participant M as Model
    participant L as Ablated serving loop
    participant O as Read-only observer
    participant T as Tool
    participant X as Experiment metrics

    M->>L: Proposed mutation
    L->>O: Copy proposal for policy observation
    O-->>X: Would DENY/BLOCK
    Note over O: No control over serving
    L->>T: Execute because boundary is disabled
    T-->>L: Side effect result
    L-->>X: Executed=true
    X->>X: Record invalid or unauthorized execution
```

**Use:** Video 3.  
**Required styling:** Observer arrows are dashed and never intercept dispatch.

## 6. Recommendation pipeline

```mermaid
flowchart LR
    R[Raw trial rows]
    P{Plan complete?}
    C{Measurements and<br/>probes complete?}
    Q{Meets every<br/>hard threshold?}
    K[Qualifying configurations]
    O[Rank by components,<br/>serving tokens, seconds]
    N[Scoped recommendation]
    I[Inconclusive / rerun]

    R --> P
    P -->|no| I
    P -->|yes| C
    C -->|no| I
    C -->|yes| Q
    Q -->|no| R2[Nonqualifier]
    Q -->|yes| K --> O --> N
```

**Use:** Video 4.  
**Required order:** Cost never appears before qualification.

## 7. Continuous evaluation lifecycle

```mermaid
flowchart LR
    A[Production logs,<br/>failures, near misses]
    B[Curate and label<br/>with privacy controls]
    C[Versioned eval suite]
    D[Evaluate proposed change]
    E{Release gates pass?}
    F[Deploy and monitor]
    G[Revise or reject]

    A --> B --> C --> D --> E
    E -->|yes| F --> A
    E -->|no| G --> D
```

**Use:** Video 5.  
**Guardrail:** Passing the suite is necessary evidence, not universal proof.
