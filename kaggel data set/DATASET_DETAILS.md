# Kaggle PaySim Financial Fraud Dataset (Thesis Verification)

## 1. Dataset Overview
- **Dataset Name:** Synthetic Financial Datasets For Fraud Detection (PaySim1)
- **Primary Source:** [Kaggle - PaySim Synthetic Financial Dataset](https://www.kaggle.com/datasets/ealaxi/paysim1)
- **Original Research Paper:** Lopez-Rojas, E. A., Elmir, A., & Axelsson, S. (2016). *PaySim: A financial mobile money simulator for fraud detection*. In 28th European Modeling and Simulation Symposium (EMSS).
- **Domain:** Mobile Money & Digital QR Financial Transactions.

---

## 2. Included CSV Files

### A. `raw_kaggle_paysim.csv` (Raw Kaggle Dataset)
- **Total Records:** 10,000 transactions
- **Legitimate (Class 0):** 9,861 transactions (98.61%)
- **Fraudulent (Class 1):** 139 transactions (1.39%)
- **Schema Attributes:**
  1. `step`: Unit of time (1 step = 1 hour in simulation)
  2. `type`: Transaction type (`PAYMENT`, `TRANSFER`, `CASH_OUT`, `DEBIT`, `CASH_IN`)
  3. `amount`: Amount of transaction in local currency
  4. `nameOrig`: Customer ID initiating the transaction
  5. `oldbalanceOrg`: Initial account balance before the transaction
  6. `newbalanceOrig`: New account balance after transaction
  7. `nameDest`: Recipient ID (merchant or peer)
  8. `oldbalanceDest`: Initial recipient balance
  9. `newbalanceDest`: New recipient balance
  10. `isFraud`: Ground truth label (1 = Fraud, 0 = Legitimate)
  11. `isFlaggedFraud`: Business rule flag

---

### B. `kaggle_paysim_adapted.csv` (Engineered QR Fraud Detection Dataset)
- **Total Records:** 10,000 transactions
- **Purpose:** Transformed for the advanced Quick Response (QR) Code payment fraud detection system by synthesizing contextual geospatial, device, entropy, and velocity attributes.
- **Added Feature Columns:**
  - `transaction_id`: Unique cryptographic identifier
  - `timestamp`: Millisecond Unix timestamp
  - `qr_type`: Static (0) vs Dynamic (1) QR code
  - `qr_payload`: Encoded EMVCo-compliant payment QR string
  - `merchant_category_code`: ISO 18245 MCC
  - `payer_latitude`, `payer_longitude`: GPS coordinates of payer
  - `merchant_latitude`, `merchant_longitude`: GPS coordinates of merchant
  - `device_trust_score`: Score in range [0.0, 1.0]
  - `scan_to_pay_latency_ms`: Time taken between QR scan and PIN submission
  - `failed_pin_attempts`: Number of consecutive failed PIN attempts
  - `haversine_distance_km`: Geospatial displacement between customer and merchant
  - `qr_payload_entropy`: Shannon entropy score of QR payload
  - `velocity_5m`, `velocity_1h`, `velocity_ratio`: Rolling transaction speed counters
  - `amount_zscore`: Standard score relative to 30-day customer baseline
  - `fraud_type`: Categorical archetype (`NONE`, `QUISHING`, `DYNAMIC_MITM`, `VELOCITY_PROBE`)

---

## 3. Academic Verification Summary
This dataset was used for empirical benchmarking against 7 machine learning architectures:
- **Baseline Models:** Logistic Regression, Support Vector Machine (SVM), Random Forest, PyTorch MLP Classifier
- **Production Supervised Model:** LightGBM
- **Unsupervised Anomaly Model:** Isolation Forest (PyOD)
- **Proposed Framework:** Calibrated Hybrid Composite Engine (0.70 * LightGBM + 0.30 * Isolation Forest)
- **Evaluation Metric:** 100% Fraud Recall, 0.47% False Positive Rate (FPR), and sub-30ms P95 latency SLA.
