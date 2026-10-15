# Architecture Diagrams

These Mermaid sources are editable references. Recreate them in the course's
native diagram system for final slides if Mermaid rendering is not supported.

## 1. Weak same-conversation acceptance

```mermaid
flowchart LR
    U[User request] --> G[Generator]
    G --> C[Candidate]
    C --> S[Same-conversation self-review]
    S -->|PASS| X[Stop]
    S -->|FAIL| G
```

**Teaching note:** The diagram does not claim that self-review always passes.
It shows that generation and the only acceptance signal share one conversation.

## 2. Generator–evaluator–controller separation

```mermaid
flowchart LR
    U[Request + evidence] --> G[Generator]
    G --> C[Candidate]
    C --> D[Deterministic checks]
    C --> E[Independent evaluator]
    D --> H[Harness controller]
    E --> H
    H -->|all required criteria pass| A[Accept]
    H -->|actionable failures + budget| G
    H -->|limit or high-risk uncertainty| F[Fail or escalate]
```

**Teaching note:** Feedback returns through controller policy. The evaluator
does not directly command acceptance or invoke the generator.

## 3. Conversation branches

```mermaid
sequenceDiagram
    participant H as Harness controller
    participant G as Generator conversation
    participant E as Fresh evaluator conversation

    H->>G: request + authoritative context
    G-->>H: candidate + response_id
    H->>E: requirements + evidence + candidate
    E-->>H: structured findings
    alt every criterion passes
        H-->>H: accept and record evidence
    else failures and budget remains
        H->>G: previous candidate branch + findings
        G-->>H: revised candidate
    else limit reached
        H-->>H: fail or escalate
    end
```

## 4. Layered checks

```mermaid
flowchart TD
    C[Candidate] --> S{Schema and parse valid?}
    S -->|no| FD[Return deterministic findings]
    S -->|yes| X{Counts, IDs, tests pass?}
    X -->|no| FD
    X -->|yes| I[Inferential review]
    I --> R{Grounding and usefulness pass?}
    R -->|no| FI[Return semantic findings]
    R -->|yes| A[Eligible for acceptance]
```

**Accuracy note:** Some systems may batch checks differently for latency. This
is the recommended default when early exact failures can avoid model cost.

## 5. Runtime state machine

```mermaid
stateDiagram-v2
    [*] --> Generating
    Generating --> Evaluating: candidate produced
    Evaluating --> Accepted: all required criteria pass
    Evaluating --> Revising: failures + budget remains
    Revising --> Evaluating: revised candidate
    Evaluating --> Failed: attempt/budget limit
    Evaluating --> Escalated: high-risk uncertainty
    Accepted --> [*]
    Failed --> [*]
    Escalated --> [*]
```

## 6. Evidence model

```mermaid
flowchart TB
    R[Original requirements] --> V[Evaluation record]
    A[Authoritative evidence] --> V
    C[Candidate version] --> V
    D[Deterministic outputs] --> V
    J[Raw + parsed evaluator findings] --> V
    M[Model/prompt versions, tokens, latency] --> V
    V --> O[Accept / retry / fail / escalate]
```

**Privacy note:** Store decision-relevant inputs and outputs under the product's
data policy. Do not request or retain private chain-of-thought.
