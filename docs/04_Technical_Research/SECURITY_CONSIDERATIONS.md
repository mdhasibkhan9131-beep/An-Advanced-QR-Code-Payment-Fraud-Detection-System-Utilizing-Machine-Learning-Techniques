# Security Architecture, Threat Modeling & Privacy Engineering

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 04)  
**Parent Document:** `docs/04_Technical_Research/TECHNOLOGY_COMPARISON.md`  
**Reference Standards:** STRIDE Threat Model, ISO/IEC 27001, GDPR Article 22

---

## 1. STRIDE Threat Model for QR Payment Systems

The system has been evaluated against Microsoft's STRIDE threat classification taxonomy, specifically tailored to the unique physical and digital attack surfaces of QR transactions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STRIDE THREAT MITIGATION                          │
├─────────────────────┬───────────────────────────┬───────────────────────────┤
│ STRIDE Category     │ QR Attack Vector          │ Implemented Countermeasure│
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ Spoofing            │ Static QR sticker replace │ Haversine geo-distance,   │
│                     │ Merchant account spoof    │ Payer/Merchant ID matching│
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ Tampering           │ Dynamic payload MITM      │ Payload Shannon entropy,  │
│                     │ Amount parameter alter    │ Historical Z-score bounds │
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ Repudiation         │ Denied fraud verdict      │ SHA-256 append-only block │
│                     │ Disputed chargebacks      │ chained audit ledger      │
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ Information Discl.  │ Plaintext account leakage │ Salted SHA-256 masking,   │
│                     │ Customer identity theft   │ Zero plaintext PII storage│
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ Denial of Service   │ Micro-probing burst scans │ Rolling 5m/1h velocity,   │
│                     │ Thread starvation flood   │ Heuristic fallback circuit│
├─────────────────────┼───────────────────────────┼───────────────────────────┤
│ Elevation of Priv.  │ Model tampering / exploit │ Pydantic strict schemas,  │
│                     │ Unauthorized admin access │ Read-only model endpoints │
└─────────────────────┴───────────────────────────┴───────────────────────────┘
```

### Granular Threat Assessments:

1. **Spoofing (Physical Sticker Replacement / Quishing):**
   - *Threat:* Fraudster overlays a malicious printed QR code over a legitimate merchant POS sticker.
   - *Mitigation:* The feature pipeline computes Haversine spatial displacement between the payer's GPS and the registered merchant coordinates. If distance $> 5\text{ km}$ for an in-person retail category, the risk score spikes, triggering `BLOCK` or `CHALLENGE_MFA`.

2. **Tampering (Dynamic QR Payload Modification):**
   - *Threat:* Interception or manipulation of dynamic QR strings modifying transaction amount or recipient token.
   - *Mitigation:* The Shannon entropy analyzer flags obfuscated or encoded payload strings ($H(X) \ge 4.5\text{ bits/char}$), while amount Z-scores detect deviations from customer spending baselines.

3. **Repudiation (Disputed Verification & Audit Tampering):**
   - *Threat:* Fraud operations staff or compromised databases retroactively altering decision logs or risk scores.
   - *Mitigation:* Cryptographic SHA-256 parent block chaining:
     $$H_k = \text{SHA256}(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k)$$
     Any alteration of historical rows invalidates the chain verification endpoint (`/api/v1/ledger/verify`).

4. **Information Disclosure (PII Leaks):**
   - *Threat:* Exposure of customer identities, account numbers, or bank tokens via API logs or database breaches.
   - *Mitigation:* Raw `payer_id` and sensitive credentials are salted and hashed immediately upon deserialization:
     $$\text{SaltedHash} = \text{SHA256}(\text{payer\_id} \,\|\, \text{SECRET\_SALT})$$
     Plaintext PII is never stored or passed to downstream feature tensors.

5. **Denial of Service (DoS & Micro-Probing Floods):**
   - *Threat:* Automated bots generating rapid, successive micro-scans to exhaust server threads or drain stolen accounts.
   - *Mitigation:* Stateful sliding window cache immediately captures velocity spikes ($V_{5\text{m}} > 5$), escalating decisions to `BLOCK`. Additionally, a $120\text{ ms}$ timeout circuit breaker prevents thread hanging under heavy concurrency.

---

## 2. Adversarial Machine Learning Robustness

Machine learning models deployed in financial contexts are vulnerable to adversarial evasion, where attackers systematically perturb features (e.g., tweaking transaction values or spoofing scan latencies) to fall just below classification thresholds.

```
[ Incoming Payload ] ──> [ Feature Bounding & Clamping ] ──> [ Dual Model (LightGBM + iForest) ]
```

### Defensive Strategies Implemented:
1. **Input Clamping & Physiological Boundary Enforcement:**
   Every numerical feature is strictly clamped to valid physical boundaries prior to model ingestion:
   - Latitude: $[-90.0, +90.0]$
   - Longitude: $[-180.0, +180.0]$
   - Amount: $[0.01, 1{,}000{,}000.00]$
   - Scan-to-pay latency: $[0, 600{,}000\text{ ms}]$
2. **Dual-Tier Anomaly Defense:**
   Supervised decision trees can be fooled by adversarial perturbations that mimic historical decision boundaries. However, our unsupervised **Isolation Forest** simultaneously evaluates structural density. If an adversarial sample lands in an unpopulated region of the feature space, its anomaly score $S_{\text{anomaly}} > 0.80$ triggers an automatic escalation to `CHALLENGE_MFA`.

---

## 3. Data Privacy & Regulatory Compliance (GDPR / ISO 27001)

### 3.1 GDPR Article 22 (Algorithmic Transparency & Right to Explanation)
Under European and international privacy frameworks, automated decision-making that significantly affects users must provide meaningful explanatory rationale.
- **System Compliance:** Our SHAP TreeExplainer generates local feature attribution reason codes (`AmountDeviation > 3.8 sigma`, `GeoDistance > 450 km`) for all blocked or challenged transactions, satisfying the legal requirement for algorithmic explainability.

### 3.2 Decentralized Privacy Simulation (Federated Learning)
To address banking privacy laws that prohibit pooling sensitive raw financial records across institutions:
- The system includes a **Federated Averaging (FedAvg)** module demonstrating that collaborative fraud intelligence can be achieved by sharing model parameter updates ($W_t^k$) rather than centralizing raw user transactions.

