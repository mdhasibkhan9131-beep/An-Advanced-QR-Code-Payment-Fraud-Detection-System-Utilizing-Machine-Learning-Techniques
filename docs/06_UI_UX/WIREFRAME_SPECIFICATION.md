# Wireframe Specification & Responsive Layout Architecture

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 06)  
**Parent Document:** `docs/06_UI_UX/SCREEN_INVENTORY.md` | `docs/06_UI_UX/DESIGN_SYSTEM.md`

---

## 1. Responsive Breakpoint Rules

The Streamlit UI adapts fluidly across standard enterprise displays:
- **Ultra-Wide / Desktop ($\ge 1440\text{ px}$):** Full multi-column dashboard layouts (3-column risk inspector, side-by-side simulator).
- **Standard Laptop ($1024\text{ px} - 1439\text{ px}$):** 2-column stacked layout; KPI metrics wrap into a $3 \times 2$ grid.
- **Tablet / Mobile Viewport ($< 1024\text{ px}$):** Single-column stacked vertical stream; navigation collapses into a slide-over hamburger drawer.

---

## 2. High-Fidelity Structural Wireframes

### Wireframe 1: Live Telemetry & Transaction Stream (`/live-stream`)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [● ONLINE] QR PAYMENT FRAUD SURVEILLANCE CENTER              [Active Model: LightGBM_v1.0.0]  [p95: 58.4ms] [22:30 UTC]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KPI SUMMARY METRICS                                                                                                    │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│ │ THROUGHPUT           │ │ APPROVE RATE         │ │ MFA CHALLENGE        │ │ BLOCKED FRAUD    │ │ MEDIAN LATENCY   │ │
│ │ 342.5 req/s          │ │ 96.8% (24,892)       │ │ 2.1% (540)           │ │ 1.1% (284)       │ │ 28.2 ms          │ │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └──────────────────┘ └──────────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ LIVE TRANSACTION STREAM                                                                 [⏸ Pause Stream] [⬇ Export CSV]│
│ Filter: [ Verdict: ALL ▼ ]  [ Min Risk: ────○───── 0.30 ]  [ Payer Hash: [ Search... ] ] [ Category: Retail ▼ ]       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIME (UTC)   │ TX ID (UUIDv4)     │ PAYER HASH  │ AMOUNT    │ GEO-DIST │ ENTROPY │ RISK SCORE │ VERDICT   │ ACTIONS    │
├──────────────┼────────────────────┼─────────────┼───────────┼──────────┼─────────┼────────────┼───────────┼────────────┤
│ 22:30:14.210 │ 9b1deb4d-3b7d...   │ 8f92a10b... │ $ 145.50  │   0.4 km │    3.82 │ 0.052      │ [APPROVE] │ [ Inspect ]│
│ 22:30:13.880 │ e82491b2-104a...   │ 4c91029e... │ $ 890.00  │  48.2 km │    4.12 │ 0.492      │ [CHALLENGE]│ [ Inspect ]│
│ 22:30:12.450 │ 1048ba92-f810...   │ 110948ab... │ $ 1,420.0 │ 620.5 km │    6.84 │ 0.941      │ [BLOCK]   │ [ Inspect ]│
│ 22:30:11.900 │ a9401928-8921...   │ 77481920... │ $  24.00  │   1.2 km │    3.40 │ 0.018      │ [APPROVE] │ [ Inspect ]│
│ 22:30:10.120 │ f8102948-4819...   │ 38104812... │ $  65.00  │   0.8 km │    3.65 │ 0.041      │ [APPROVE] │ [ Inspect ]│
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Wireframe 2: Transaction Detail & XAI Inspector (`/transaction-detail`)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ← Back to Live Stream   |   TRANSACTION AUDIT: 1048ba92-f810-4820-9182-4810294810ab                 [🔴 VERDICT: BLOCK]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────┐ ┌───────────────────────────────────┐ ┌───────────────────────────────────────┐ │
│ │ TRANSACTION METADATA              │ │ SPATIAL HAVERSINE DISPLACEMENT    │ │ DUAL-MODEL RISK BREAKDOWN             │ │
│ ├───────────────────────────────────┤ ├───────────────────────────────────┤ ├───────────────────────────────────────┤ │
│ │ Timestamp:    1731102000000       │ │   [ MAP VISUALIZATION ]           │ │ Supervised (LGBM):   [█████████░] 0.94│ │
│ │ Payer Hash:   110948ab... (Salted)│ │                                   │ │ Anomaly (iForest):   [█████████░] 0.91│ │
│ │ Merchant ID:  MERCH_POS_104829    │ │   ● Payer GPS: (23.810, 90.412)   │ │ Composite S_comp:    [█████████░] 0.93│ │
│ │ Category:     5411 (Retail)       │ │   │                               │ │                                       │ │
│ │ Amount:       $ 1,420.00 (+4.8 σ) │ │   └─── 620.5 km Separation ───┐   │ │ Policy Gating:       CRITICAL BLOCK │ │
│ │ QR Type:      0 (Static QR)       │ │                                │   │ │ Zero-Day Escalation: False (Known)   │ │
│ │ Scan Latency: 420 ms (Rapid Bot)  │ │   ● Merchant POS: (22.35, 91.78)  │ │ Latency to Score:    34.2 ms         │ │
│ │ Failed PINs:  2 Attempts          │ │                                   │ │ Ledger Hash:         9f83acb1... [📋] │ │
│ └───────────────────────────────────┘ └───────────────────────────────────┘ └───────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ EXPLAINABLE AI (XAI): LOCAL SHAP FEATURE ATTRIBUTIONS                                                                  │
│ Base Value: E[f(x)] = 0.0082 ────────────────────────────────────────────────────────────► Predicted Output: f(x) = 0.94│
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ [ SHAP WATERFALL / FORCE PLOT ]                                                                                    │ │
│ │  haversine_distance_km (+0.42)   ████████████████████████████████████████                                          │ │
│ │  qr_payload_entropy (+0.28)      ██──────────────────────────                                                      │ │
│ │  amount_zscore (+0.14)           ██─────────────                                                                   │ │
│ │  scan_to_pay_latency_ms (+0.08)  █───────                                                                          │ │
│ │  device_trust_score (-0.02)      ░                                                                                 │ │
│ └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│ STANDARDIZED REGULATORY REASON CODES:                                                                                  │
│ 1. [GEO_DISTANCE_CRITICAL] Payer device is 620.5 km from physical merchant terminal.                                  │
│ 2. [PAYLOAD_ENTROPY_ELEVATED] Scanned QR text contains high Shannon entropy (6.84 bits), indicating obfuscation.        │
│ 3. [AMOUNT_DEVIATION_EXTREME] Monetary value ($1,420.00) exceeds historical payer baseline by +4.8 standard deviations.│
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Wireframe 3: Interactive Fraud Vector Simulator (`/simulator`)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ INTERACTIVE FRAUD VECTOR SIMULATOR & DEFENSE TESTBED                                       [Mode: Real-Time Inference] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ SELECT ATTACK SCENARIO PRESET: [ Preset: 2. Physical Sticker Replacement (Quishing) ▼ ]        [↺ Reset to Baseline]   │
├──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────┤
│ SIMULATION PARAMETERS & INPUT CONTROLS                           │ INFERENCE OUTPUT & REAL-TIME TELEMETRY              │
├──────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
│ Transaction Amount ($):                                          │ VERDICT BADGE:                                      │
│ [ 420.00                        ] ────○────────────────── $10,000│ ┌─────────────────────────────────────────────────┐ │
│                                                                  │ │ 🔴 BLOCK (High Risk Intercepted Mid-Flight)     │ │
│ Payer GPS Coordinates:                                           │ └─────────────────────────────────────────────────┘ │
│ Latitude:  [ 23.8103  ]   Longitude: [ 90.4125  ] [📍 Set Remote]│ Composite Risk Score:     0.942 / 1.000             │
│                                                                  │ Supervised Probability:   0.928                     │
│ Scanned QR Payload String:                                       │ Unsupervised Anomaly:     0.974                     │
│ [ https://evil-phish.net/q?token=8f9a2b10492810ab4819284019 ]   │ Execution Latency:        38.2 ms (SLA <= 100ms)    │
│ Computed Shannon Entropy: [ 6.54 bits/char ] [⚠️ High Risk]      │                                                     │
│                                                                  │ TOP IDENTIFIED THREAT DRIVERS:                      │
│ Optical Scan-to-Pay Latency:                                     │ • Haversine Distance: 450.0 km from Merchant POS    │
│ [ 800 ms (Rapid Scan)           ] ──○─────────────────── 60,000ms│ • Shannon Entropy: 6.54 bits (High Obfuscation)     │
│                                                                  │ • Amount Deviation: +3.2 σ above user mean          │
│ Device Trust Score:                                              │                                                     │
│ [ 0.20 (Suspicious/Rooted)      ] ──○──────────────────── 1.00   │ CRYPTOGRAPHIC AUDIT COMMITMENT:                     │
│                                                                  │ Committed Block Hash: 4f82a10b98204918...           │
│ ┌──────────────────────────────────────────────────────────────┐ │                                                     │
│ │ [⚡ SIMULATE PAYMENT TRANSACTION (SUB-100MS)]                │ │ [ 🔍 Inspect Full SHAP Explanation Waterfall ]    │ │
│ └──────────────────────────────────────────────────────────────┘ │                                                     │
└──────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────┘
```

---

### Wireframe 4: Cryptographic Ledger Explorer (`/ledger-audit`)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CRYPTOGRAPHIC AUDIT LEDGER & NON-REPUDIATION EXPLORER                                        [Engine: SHA-256 Chained] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ AUDIT INTEGRITY OVERVIEW                                                                                               │
│ ┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │ LEDGER STATUS                        │ │ TOTAL COMMITTED BLOCKS               │ │ GENESIS SEED HASH                 │ │
│ │ 🟢 VERIFIED (100% UNBROKEN)          │ │ 14,820 Blocks                        │ │ 000000000000000000000000...       │ │
│ └──────────────────────────────────────┘ └──────────────────────────────────────┘ └─────────────────────────────────┘ │
│                                                                                                                        │
│ [ 🛡️ Run Cryptographic Chain Audit ]   [ ⚠️ Simulate Block Tamper (Testing) ]   [ ⬇ Export Audit Package (JSONL) ]    │
│ Progress: [██████████████████████████████████████████████████████████████████████] 14,820 / 14,820 Blocks Verified (0.12s)  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BLOCK # │ PREVIOUS HASH (H_k-1)  │ CURRENT BLOCK HASH (H_k) │ TX REFERENCE       │ VERDICT   │ TIMESTAMP    │ STATUS   │
├─────────┼────────────────────────┼──────────────────────────┼────────────────────┼───────────┼──────────────┼──────────┤
│ 14820   │ 8f92a104b820... [📋]   │ 9f83acb18204... [📋]     │ 1048ba92-f810...   │ [BLOCK]   │ 22:30:12.450 │ [VALID]  │
│ 14819   │ 3c8102948102... [📋]   │ 8f92a104b820... [📋]     │ e82491b2-104a...   │ [CHALLENGE]│ 22:30:13.880│ [VALID]  │
│ 14818   │ 110492810482... [📋]   │ 3c8102948102... [📋]     │ 9b1deb4d-3b7d...   │ [APPROVE] │ 22:30:14.210 │ [VALID]  │
│ 14817   │ 774819204812... [📋]   │ 110492810482... [📋]     │ a9401928-8921...   │ [APPROVE] │ 22:30:10.120 │ [VALID]  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

