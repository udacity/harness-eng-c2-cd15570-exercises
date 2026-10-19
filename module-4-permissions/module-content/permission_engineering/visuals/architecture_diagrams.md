# Architecture Diagrams

These Mermaid sources are production references. Redraw them in the course
visual system rather than relying on Mermaid defaults in final video.

## 1. Capability is not authority

```mermaid
flowchart LR
    T[Tool schema<br/>what the harness can do]
    M[Model proposal<br/>name + arguments]
    P[Production authorization<br/>what this principal may do]
    X[Business execution]

    T --> M
    M --> P
    P -->|explicit ALLOW| X
    P -->|DENY / ERROR| N[No execution]
```

**Use:** Video 1.  
**Required label:** A proposal is not a side effect.

## 2. Permission-derived catalog plus runtime enforcement

```mermaid
flowchart TD
    I[Verified principal]
    E[Production roles, scopes,<br/>relationships, elevation]
    A[Complete governed tool catalog]
    F[Catalog filter]
    C[Least-privilege model catalog]
    M[Model proposes exact call]
    R[Resolve current resource/context]
    D{Runtime authorization}
    X[Next safety gate / dispatch]
    N[No execution]

    I --> E
    E --> F
    A --> F
    F --> C
    C --> M
    M --> R
    I --> D
    E --> D
    R --> D
    D -->|ALLOW| X
    D -->|DENY / ERROR| N
```

**Use:** Videos 2 and 3.  
**Required annotation:** Filtering narrows opportunity; runtime authorization
enforces authority.

## 3. Subject-action-resource-context decision

```mermaid
flowchart LR
    S[Subject<br/>trusted user/workload]
    A[Action<br/>mapped permission]
    R[Resource<br/>trusted attributes]
    C[Context<br/>tenant, environment,<br/>time, policy version]
    D{ALLOW or DENY}

    S --> D
    A --> D
    R --> D
    C --> D
```

**Use:** Video 3.  
**Do not show:** Prompt text feeding role, owner, tenant, or approval fields.

## 4. Decision and enforcement separation

```mermaid
sequenceDiagram
    participant M as Model
    participant PEP as Harness enforcement point
    participant PDP as Permission policy
    participant H as Safety hook
    participant T as Business tool/service

    M->>PEP: Proposed call(name, arguments, call_id)
    PEP->>PEP: Parse and allowlist
    PEP->>PDP: Trusted subject + action + resource + context
    PDP-->>PEP: ALLOW or DENY + policy version
    alt DENY, error, or unusable result
        PEP-->>M: permission_denied, executed=false
    else ALLOW
        PEP->>H: Check operational invariants
        alt Hook blocks
            PEP-->>M: blocked, executed=false
        else Hook allows
            PEP->>T: Execute with bounded credential
            T-->>PEP: Actual result
            PEP-->>M: Correlated execution result
        end
    end
```

**Use:** Video 4.  
**Vocabulary:** The harness is the policy enforcement point in this course.
The policy code or service is the decision point.

## 5. Independent multi-action authorization

```mermaid
flowchart LR
    Q[Request: approve and issue P-1042]
    C1[Call 1<br/>approve_application]
    D1{permit.approve?}
    E1[Execute approval]
    C2[Call 2<br/>issue_permit]
    D2{permit.issue?}
    N2[Do not issue]

    Q --> C1 --> D1
    D1 -->|ALLOW| E1
    E1 --> C2 --> D2
    D2 -->|DENY| N2
```

**Use:** Videos 3 and 5.  
**Required final-state label:** `P-1042 = APPROVED`, not `PERMIT_ISSUED`.

## 6. Trust boundaries

```mermaid
flowchart TB
    subgraph Untrusted
        U[User request text]
        MO[Model output]
        AR[Proposed arguments]
    end

    subgraph Trusted application boundary
        AU[Authenticated principal]
        PS[Production policy]
        RS[Current resource state]
        PEP[Enforcement point]
        EV[Protected audit evidence]
    end

    U --> MO
    MO --> AR
    AR --> PEP
    AU --> PEP
    PS --> PEP
    RS --> PEP
    PEP --> EV
```

**Use:** Throughout.  
**Accessibility:** Do not encode trust only by color; use boundary labels and
solid versus dashed line styles.
