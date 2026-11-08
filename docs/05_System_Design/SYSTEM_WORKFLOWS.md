# System Workflows & Behavioral Process Engineering

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 05)  
**Parent Document:** `docs/05_System_Design/HIGH_LEVEL_DESIGN.md`  
**Reference Document:** `docs/02_Requirements/USE_CASES.md`

---

## Workflow 1: Real-Time Payment Ingestion & Low-Risk Approval

```mermaid
sequenceDiagram
    autonumber
    actor Client as Payment Client / POS
    participant Gateway as FastAPI Gateway
    participant Validator as Pydantic v2 Validator
    participant FeatureEngine as Feature & Cache Pipeline
    participant Cache as In-Memory State Cache
    participant MLModels as Dual ML Models (LGBM & iForest)
    participant Ensemble as Decision & Policy Gating
    participant Ledger as Cryptographic Ledger

    Client->>Gateway: POST /api/v1/predict (JSON Payload)
    Gateway->>Validator: Validate Schema & Coordinate Bounds
    Validator-->>Gateway: Sanitized & Salted Model Vector

    Gateway->>FeatureEngine: Compute Haversine, Entropy, & Velocities
    FeatureEngine->>Cache: Query & Increment Rolling Counters (5m, 1h, 24h)
    Cache-->>FeatureEngine: Return Velocity Counts
    FeatureEngine-->>Gateway: Normalized Feature Vector X

    par Supervised Scoring
        Gateway->>MLModels: LightGBM predict_proba(X)
        MLModels-->>Gateway: P(Fraud) = 0.04
    and Unsupervised Scoring
        Gateway->>MLModels: Isolation Forest decision_function(X)
        MLModels-->>Gateway: S(Anomaly) = 0.08
    end

    Gateway->>Ensemble: Arbitrate S_comp = (0.7*0.04) + (0.3*0.08) = 0.052
    Ensemble-->>Gateway: Verdict: APPROVE (S_comp < 0.30)

    Note over Gateway: Synchronous SHAP Bypassed (0ms overhead)

    Gateway->>Ledger: Append Block (TxID, 0.052, APPROVE, PrevHash)
    Ledger-->>Gateway: Block Committed (Block Hash H_k)

    Gateway-->>Client: HTTP 200 OK {status: "APPROVED", score: 0.052} (<= 35ms)
```

---

## Workflow 2: Suspicious Transaction & Secondary MFA Challenge

```mermaid
sequenceDiagram
    autonumber
    actor Client as Payment Client / POS
    participant Gateway as FastAPI Gateway
    participant FeatureEngine as Feature & Cache Pipeline
    participant MLModels as Dual ML Models (LGBM & iForest)
    participant Ensemble as Decision Gating
    participant XAI as SHAP TreeExplainer
    participant Ledger as Cryptographic Ledger

    Client->>Gateway: POST /api/v1/predict (High Amount Deviation)
    Gateway->>FeatureEngine: Extract Features (Z_amount = 3.2, Dist = 45km)
    FeatureEngine-->>Gateway: Normalized Vector X

    par Dual Inference
        Gateway->>MLModels: LightGBM predict_proba(X) -> P(Fraud) = 0.48
    and
        Gateway->>MLModels: Isolation Forest -> S(Anomaly) = 0.52
    end

    Gateway->>Ensemble: Blended Score S_comp = 0.492
    Ensemble-->>Gateway: Verdict: CHALLENGE_MFA (0.30 <= S_comp <= 0.70)

    Gateway->>XAI: Compute Local Shapley Values
    XAI-->>Gateway: Top Reason: "AmountDeviation > 3.0 sigma"

    Gateway->>Ledger: Append Block (TxID, 0.492, CHALLENGE_MFA)
    Ledger-->>Gateway: Block Committed

    Gateway-->>Client: HTTP 200 OK {verdict: "CHALLENGE_MFA", reasons: [...], token: "CHAL_...}
```

---

## Workflow 3: Critical Fraud Threat Interception & Block

```mermaid
sequenceDiagram
    autonumber
    actor Fraudster as Fraudulent Actor / Stolen Account
    participant Gateway as FastAPI Gateway
    participant FeatureEngine as Feature Pipeline
    participant MLModels as Dual ML Models
    participant Ensemble as Decision Gating
    participant XAI as SHAP TreeExplainer
    participant Ledger as Cryptographic Ledger

    Fraudster->>Gateway: POST /api/v1/predict (Sticker Quishing Attack)
    Gateway->>FeatureEngine: Compute Haversine (Dist = 620km), Entropy = 6.8
    FeatureEngine-->>Gateway: Normalized Vector X

    par Dual Inference
        Gateway->>MLModels: LightGBM predict_proba(X) -> P(Fraud) = 0.94
    and
        Gateway->>MLModels: Isolation Forest -> S(Anomaly) = 0.91
    end

    Gateway->>Ensemble: Blended Score S_comp = 0.931
    Ensemble-->>Gateway: Verdict: BLOCK (S_comp > 0.70)

    Gateway->>XAI: Compute Shapley Values
    XAI-->>Gateway: Reasons: ["GeoDistance > 500km", "Entropy Critical", "Velocity Spike"]

    Gateway->>Ledger: Append Block (TxID, 0.931, BLOCK)
    Ledger-->>Gateway: Block Committed

    Gateway-->>Fraudster: HTTP 200 OK {verdict: "BLOCK", reasons: [...]} (Mid-Flight Terminated)
```

---

## Workflow 4: Zero-Day Anomaly Escalation Override

```mermaid
flowchart TD
    Inference[Execute Supervised & Unsupervised Models] --> EvalScores[P_supervised = 0.35, S_anomaly = 0.86]
    EvalScores --> CheckEscalation{Is P_sup in [0.25, 0.45]\nand S_anomaly > 0.80?}

    CheckEscalation -->|Yes: Novel Threat Detected| OverrideAction[Override Standard Linear Gating]
    OverrideAction --> EscalateVerdict[Assign Verdict: CHALLENGE_MFA]
    EscalateVerdict --> FlagZeroDay[Add Diagnostic: ZERO_DAY_ANOMALY_ESCALATION]
    FlagZeroDay --> LogAudit[Commit to SHA-256 Ledger]
    LogAudit --> ReturnClient[Return HTTP 200 with Step-Up Requirement]

    CheckEscalation -->|No| StandardGating[Apply Standard Gating Thresholds]
```

---

## Workflow 5: Latency Watchdog & Heuristic Fallback Circuit Breaker

```mermaid
flowchart TD
    Ingest[Receive Transaction Request] --> StartWatchdog[Start 120ms Async Timeout Watchdog]
    StartWatchdog --> ExecutePipeline[Trigger Feature Extraction & Dual ML Models]

    ExecutePipeline --> WatchdogCheck{Completed Within\n120ms?}

    WatchdogCheck -->|Yes: Healthy Execution| NormalFlow[Return ML Authorization Decision]
    WatchdogCheck -->|No: Timeout Exceeded| CircuitBreaker[Trigger Heuristic Fallback Circuit Breaker]

    CircuitBreaker --> Rule1{Amount > $1000\nor Velocity_5m > 5?}
    Rule1 -->|Yes| FallbackChallenge[Assign Verdict: CHALLENGE_MFA]
    Rule1 -->|No| FallbackApprove[Assign Verdict: APPROVE]

    FallbackChallenge --> ReturnFallback[Return Response with Header: X-Fallback-Engaged: true]
    FallbackApprove --> ReturnFallback
```

---

## Workflow 6: Cryptographic Chain Auditing & Tamper Identification

```mermaid
flowchart TD
    TriggerAudit[Auditor Calls GET /api/v1/ledger/verify] --> InitChain[Fetch Genesis Block H_0]
    InitChain --> LoopBlocks[Iterate Blocks k = 1 to N]

    LoopBlocks --> RecalculateHash["Compute Expected Digest: H_k* = SHA256(H_k-1 || TxID || Score || Verdict || Timestamp)"]
    RecalculateHash --> CompareHash{Does Stored H_k\nMatch H_k*?}

    CompareHash -->|Yes: Intact| CheckNext{More Blocks?}
    CheckNext -->|Yes| NextBlock[Advance to Block k+1]
    NextBlock --> LoopBlocks
    CheckNext -->|No| ReportSuccess[Return Status: VERIFIED - 100% Chain Intact]

    CompareHash -->|No: Mismatch| TamperDetected[Flag TAMPER_DETECTED at Block ID #k]
    TamperDetected --> HaltAudit[Return HTTP 200 with Corrupted Block ID and Diagnostics]
```

---

## Workflow 7: Decentralized Federated Model Aggregation (FedAvg)

```mermaid
sequenceDiagram
    autonumber
    actor Coordinator as Central Federated Coordinator
    participant BankA as Bank Node A (Private Data)
    participant BankB as Bank Node B (Private Data)
    participant BankC as Bank Node C (Private Data)

    Coordinator->>BankA: Distribute Initial Global Model Weights W_0
    Coordinator->>BankB: Distribute Initial Global Model Weights W_0
    Coordinator->>BankC: Distribute Initial Global Model Weights W_0

    par Local SGD on Decentralized Silos
        BankA->>BankA: Train Local Epochs on Private Data -> W_1^A
    and
        BankB->>BankB: Train Local Epochs on Private Data -> W_1^B
    and
        BankC->>BankC: Train Local Epochs on Private Data -> W_1^C
    end

    BankA-->>Coordinator: Send Parameter Weights W_1^A (No Raw Transactions)
    BankB-->>Coordinator: Send Parameter Weights W_1^B (No Raw Transactions)
    BankC-->>Coordinator: Send Parameter Weights W_1^C (No Raw Transactions)

    Coordinator->>Coordinator: Compute Weighted Average W_1 = Sum( (n_k / n) * W_1^k )
    Coordinator->>Coordinator: Benchmark Global Model Accuracy vs Centralized Baselines

    Coordinator-->>BankA: Distribute Updated Global Weights W_1
    Coordinator-->>BankB: Distribute Updated Global Weights W_1
    Coordinator-->>BankC: Distribute Updated Global Weights W_1
```

