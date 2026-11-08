# Screen Inventory & Component Breakdown

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 06)  
**Parent Document:** `docs/06_UI_UX/USER_JOURNEY.md`  
**Framework:** Streamlit Multi-Page Architecture

---

## 1. Global Layout & Shell Structure

The user interface utilizes a standardized enterprise dashboard shell:
- **Left Collapsible Sidebar (Navigation):** Global system status badge, active model version indicator, page navigation links, live system latency counter, and connection health pulse.
- **Top Utility Header:** Real-time system clock (UTC/local), active environment tag (`STANDALONE_OFFLINE`), and dark/light contrast toggle.
- **Main Content Stage:** Dynamic multi-column responsive canvas displaying the selected screen view.

---

## 2. Granular Screen Catalog

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM SCREEN INVENTORY                           │
├────┬─────────────────────────────┬──────────────────────────────────────────┤
│ ID │ Screen Name                 │ Primary Purpose                          │
├────┼─────────────────────────────┼──────────────────────────────────────────┤
│ S1 │ Live Telemetry & Feed       │ Real-time transaction stream & triage    │
│ S2 │ Transaction Detail & XAI    │ Root-cause SHAP inspection & GPS mapping │
│ S3 │ Fraud Vector Simulator      │ Interactive parameter testing of attacks │
│ S4 │ Benchmark Scoreboard        │ Comparative evaluation (LGBM/RF/SVM/MLP) │
│ S5 │ Ledger & Audit Explorer     │ SHA-256 block chain verification         │
│ S6 │ Federated Simulation        │ Decentralized FedAvg training monitor    │
└────┴─────────────────────────────┴──────────────────────────────────────────┘
```

---

### Screen 1: Live Telemetry & Transaction Stream (`/live-stream`)

- **Primary Persona:** Fraud Operations Analyst (Alex).
- **Core Purpose:** High-density live monitoring of incoming transactions, instant triage of flagged payments, and aggregate throughput tracking.
- **Key UI Components:**
  - **KPI Banner (5 Metric Cards):**
    1. *Throughput:* Current transactions/second (e.g., `342 req/s`).
    2. *Approve Rate:* Percentage of transactions cleared (e.g., `96.8%`).
    3. *MFA Challenge Rate:* Percentage flagged for step-up (e.g., `2.1%`).
    4. *Block Rate:* Percentage intercepted as high-risk fraud (e.g., `1.1%`).
    5. *System Latency (p95):* Real-time round-trip latency (e.g., `58.4 ms`).
  - **Filter & Search Drawer:**
    - Filter by Verdict (`ALL`, `APPROVE`, `CHALLENGE_MFA`, `BLOCK`).
    - Minimum Risk Score Slider (`0.0 - 1.0`).
    - Payer Hash Search Box.
    - Merchant Category Filter (Retail, Dining, Transfer, etc.).
  - **Live Auto-Refreshing Transaction Table:**
    - Columns: Time, Tx ID, Payer Hash, Merchant, Amount, Haversine Distance, Entropy, Risk Score, Verdict Badge, Actions (`Inspect`).
    - Visual Cues: Color-coded rows and badges (Green: Approve, Amber: Challenge, Crimson: Block).
- **Interactive Actions:**
  - Pause/Resume Live Stream toggle.
  - "Inspect" button per row: transitions user to Screen 2 with pre-populated transaction ID.
- **API Bindings:** `GET /api/v1/metrics`, WebSocket / polling stream from SQLite transaction store.

---

### Screen 2: Transaction Detail & XAI Inspector (`/transaction-detail`)

- **Primary Persona:** Fraud Operations Analyst (Alex), Compliance Auditor (Sarah).
- **Core Purpose:** Exhaustive investigative drilldown into an individual transaction, visualizing spatial separation, dual-model scores, and dynamic SHAP feature attributions.
- **Key UI Components:**
  - **Transaction Header Banner:** Displays Tx ID, Timestamp, Verdict Pill, and Cryptographic Block Hash.
  - **Column 1: Raw & Engineered Metadata Card:**
    - Key-value list: Amount ($), Merchant Category Code, Payer GPS, Merchant GPS, Device Trust Score ($0.0 - 1.0$), Scan Latency ($ms$), Rolling 1h Velocity, Amount Z-Score.
  - **Column 2: Spatial Haversine Vector & Geo-Map:**
    - Interactive map pinpointing Payer GPS vs. Registered Merchant POS GPS with a connecting spatial displacement line labeled with distance (e.g., `Haversine Distance: 412.5 km`).
  - **Column 3: Dual-Engine Risk Breakdown Gauges:**
    - Gauge 1: Supervised LightGBM Probability: $P_{\text{fraud}} \in [0, 1]$.
    - Gauge 2: Unsupervised Isolation Forest Score: $S_{\text{anomaly}} \in [0, 1]$.
    - Gauge 3: Composite Blended Risk Index: $S_{\text{composite}} \in [0, 1]$.
    - Zero-Day Escalation Banner (if triggered).
  - **Full-Width Section: SHAP Feature Attribution Inspector:**
    - Rendered interactive Plotly SHAP Waterfall / Force Plot depicting the exact baseline shift ($\phi_0 \to f(x)$) caused by each feature.
    - Standardized Reason Codes Table (e.g., `GEO_DISTANCE_ANOMALOUS`, `PAYLOAD_ENTROPY_CRITICAL`).
- **Interactive Actions:**
  - `Copy Block Hash` button.
  - `Mark False Positive` analyst override action.
  - `Issue Secondary MFA Challenge` action.
- **API Bindings:** `POST /api/v1/explain`, `GET /api/v1/transactions/{id}`.

---

### Screen 3: Interactive Fraud Vector Simulator (`/simulator`)

- **Primary Persona:** Academic Evaluator (Dr. Rahman), ML Engineer.
- **Core Purpose:** Live interactive sandbox allowing users to manipulate attack vectors, inject synthetic anomalies, and observe instantaneous model decisions and latency under test conditions.
- **Key UI Components:**
  - **Attack Preset Selector Dropdown:**
    - Presets: `1. Normal Routine Payment`, `2. Physical Sticker Replacement (Quishing)`, `3. Dynamic MITM Amount Tampering`, `4. High-Velocity Micro-Probing Bot`.
  - **Interactive Parameter Sliders & Inputs:**
    - *Transaction Amount (\$):* Float slider (`$1.00 - $10,000.00`).
    - *Payer Latitude / Longitude:* Co-ordinate inputs with quick-buttons (Local vs. Remote City).
    - *QR Payload String:* Text area with auto-calculated Shannon Entropy meter (`0.0 - 8.0 bits/char`).
    - *Scan-to-Pay Latency (ms):* Slider (`100 ms - 60,000 ms`).
    - *Device Trust Score:* Slider (`0.0 - 1.0`).
    - *Failed PIN Attempts:* Integer stepper (`0 - 5`).
  - **Execution Control:** Large primary CTA button: `Simulate Payment Transaction`.
  - **Instantaneous Result Stage:**
    - Decision Card: Pulsing verdict banner (`APPROVE` / `CHALLENGE_MFA` / `BLOCK`).
    - Execution Timer: `Round-Trip Inference Latency: 34.2 ms (Sub-100ms SLA Satisfied)`.
    - Live SHAP Waterfall visualization generated on-the-fly.
- **API Bindings:** `POST /api/v1/predict`, `POST /api/v1/explain`.

---

### Screen 4: Model Performance & Benchmark Scoreboard (`/benchmarks`)

- **Primary Persona:** Academic Evaluator (Dr. Rahman), ML Engineer.
- **Core Purpose:** Rigorous academic validation displaying comparative performance tables, ROC/PR curves, and cost loss optimizations across all proposal algorithms.
- **Key UI Components:**
  - **Algorithm Scoreboard Table:**
    - Rows: LightGBM (Production), Random Forest, Support Vector Machine (SVM), PyTorch Deep MLP, Isolation Forest.
    - Columns: Recall (%), Precision (%), F1-Score, F2-Score, PR-AUC, p50 Latency (ms), p95 Latency (ms), Model Memory (MB).
  - **Comparative Curve Visualizer:**
    - Chart 1: Receiver Operating Characteristic (ROC) curves with AUC scores.
    - Chart 2: Precision-Recall (PR) curves (highlighting performance under $\le 1\%$ class imbalance).
  - **Asymmetric Financial Utility Loss Calculator:**
    - Interactive sliders for $C_{\text{fraud}}$ (\$150), $C_{\text{friction}}$ (\$5), and $C_{\text{review}}$ (\$0.50).
    - Live calculated Total Economic Loss comparing rule-based legacy systems vs. our ML framework.
- **API Bindings:** `GET /api/v1/metrics`.

---

### Screen 5: Cryptographic Ledger & Audit Explorer (`/ledger-audit`)

- **Primary Persona:** Compliance & Audit Officer (Sarah).
- **Core Purpose:** Mathematical verification of transaction non-repudiation and SHA-256 block chain continuity.
- **Key UI Components:**
  - **Audit Status Hero Card:**
    - Large verification badge: `SYSTEM INTEGRITY: VERIFIED (100% UNBROKEN)` or `TAMPER DETECTED`.
    - Total Blocks Committed counter.
    - Genesis Block Digest display.
  - **Audit Action Control:**
    - Primary CTA button: `Run Cryptographic Chain Audit`.
    - Real-time animated verification progress bar.
  - **Ledger Sequence Table:**
    - Columns: Block #, Prev Hash (Truncated with copy icon), Block Hash, Tx Reference, Verdict, Timestamp, Signature.
  - **Tamper Simulation Playground (Testing Utility):**
    - Button: `Simulate Malicious Row Modification` (intentionally modifies an isolated test row to demonstrate that `/api/v1/ledger/verify` immediately catches the corruption).
- **API Bindings:** `GET /api/v1/ledger/verify`.

---

### Screen 6: Federated Privacy Simulation Monitor (`/federated`)

- **Primary Persona:** Academic Evaluator (Dr. Rahman), Data Privacy Auditor.
- **Core Purpose:** Visualizing decentralized multi-institution model training (FedAvg) demonstrating cross-bank intelligence sharing without raw data centralization.
- **Key UI Components:**
  - **Institutional Node Map:** Visual cards representing Bank A (Private Node 1), Bank B (Private Node 2), Bank C (Private Node 3).
  - **Federated Training Progression:**
    - Round Slider (Rounds 1 to 5).
    - Animation showing local weights ($W_t^k$) being averaged into global model $W_{t+1}$.
  - **Convergence & Accuracy Comparison Chart:**
    - Line chart comparing Federated Model Recall vs. Centralized Training Baseline across training epochs.
- **API Bindings:** Offline simulation script runner (`scripts/run_federated_simulation.py`).

