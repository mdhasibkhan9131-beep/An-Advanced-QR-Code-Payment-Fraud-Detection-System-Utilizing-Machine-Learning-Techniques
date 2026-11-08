# Software Quality Assurance Test Execution Report

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Test Date:** 2026-11-08  
**Execution Context:** Microsoft Windows 11 Enterprise | Python 3.11.9 (64-bit)  
**Test Runner:** Pytest 9.1.1 with AnyIO 4.14.2 & AsyncIO 1.4.1  
**Evidence Artifact:** `docs/09_Testing/Evidence/pytest_session_log.txt`

---

## 1. Executive Summary & Test Scorecard

Independent automated quality assurance testing was executed across all tiers of the application. The test suite evaluates unit algorithms, data pipelines, machine learning classifiers, cryptographic integrity, API contracts, security penetration, and inference latency budgets.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FINAL QA EXECUTION SCORECARD                    │
├────────────────────────────────┬───────────────────────────────────────┤
│ Total Automated Tests Executed │ 50 Test Cases                         │
│ Passed Tests                   │ 50 Passed                             │
│ Failed Tests                   │ 0 Failed                              │
│ Skipped / Inconclusive Tests   │ 0 Skipped                             │
│ Test Suite Pass Rate           │ 100.0%                                │
│ Total Suite Execution Time     │ 7.37 Seconds                          │
│ Critical Outstanding Defects   │ 0 Critical Defects                    │
│ Release Quality Recommendation │ APPROVED FOR STAGE-GATE ADVANCEMENT   │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Granular Module Execution Results

| Test Module File | Domain Tested | Tests Run | Passed | Failed | Pass Rate | Execution Duration |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `tests/test_api_e2e.py` | Full FastAPI Gateway Integration & Verdicts | 4 | 4 | 0 | 100% | 0.85s |
| `tests/test_api_validation.py` | Pydantic v2 Schema & Boundary Rules | 3 | 3 | 0 | 100% | 0.12s |
| `tests/test_database.py` | SQLite WAL Connectivity & Transaction CRUD | 2 | 2 | 0 | 100% | 0.18s |
| `tests/test_environment.py` | Runtime Dependencies & Environment Pinning | 3 | 3 | 0 | 100% | 0.45s |
| `tests/test_feature_engineering.py` | Haversine, Shannon Entropy & Baseline Z-Score | 7 | 7 | 0 | 100% | 0.22s |
| `tests/test_generator.py` | Synthetic Imbalance & 4 Fraud Archetypes | 8 | 8 | 0 | 100% | 1.15s |
| `tests/test_health.py` | Liveness, Readiness & Operational Metrics | 2 | 2 | 0 | 100% | 0.14s |
| `tests/test_ledger.py` | SHA-256 Block Chaining & Tamper Detection | 2 | 2 | 0 | 100% | 0.31s |
| `tests/test_models.py` | Supervised Classifiers, Isolation Forest & Gating | 5 | 5 | 0 | 100% | 1.82s |
| `tests/test_performance.py` | Sub-100ms Inference Latency SLA Benchmark | 1 | 1 | 0 | 100% | 0.62s |
| `tests/test_preprocessor.py` | Split Isolation, RobustScaler & Borderline-SMOTE | 6 | 6 | 0 | 100% | 0.74s |
| `tests/test_security.py` | SQLi Injection, GPS Boundaries & Salted PII | 4 | 4 | 0 | 100% | 0.38s |
| `tests/test_xai.py` | SHAP TreeExplainer & Semantic Reason Codes | 3 | 3 | 0 | 100% | 0.39s |
| **TOTALS** | **End-to-End System Evaluation** | **50** | **50** | **0** | **100%** | **7.37s** |

---

## 3. Key Verification Findings

1. **Inference Latency SLA Adherence:**
   - Under continuous load, the FastAPI gateway achieves a P50 latency of **15.2 ms** and a P95 latency of **28.4 ms**, comfortably outperforming the sub-100ms proposal requirement.
2. **Mathematical Precision of Contextual Features:**
   - Great-circle Haversine distance computations matched authentic geographical benchmarks between Dhaka and Chittagong (~218 km) with domain clamping preventing NaN values.
   - Shannon entropy distinctly separated legitimate EMVCo merchant codes (< 4.3 bits) from randomized high-entropy phishing URLs (> 4.5 bits).
3. **Partition Isolation & Zero Data Leakage:**
   - Borderline-SMOTE oversampling was confirmed strictly isolated to the training split ($70\%$). Test partitions remained 100% pristine and un-oversampled.
4. **Cryptographic Tamper Detection:**
   - The SHA-256 block-chained ledger immediately detected deliberate SQLite row tampering and isolated the exact corrupted block ID.

---

## 4. Test Evidence Reference

The complete stdout/stderr test execution stream has been archived for reproducibility:
- **Raw Log Path:** `docs/09_Testing/Evidence/pytest_session_log.txt`
- **Benchmark Metrics Artifact:** `docs/09_Testing/Evidence/benchmark_results.json`
