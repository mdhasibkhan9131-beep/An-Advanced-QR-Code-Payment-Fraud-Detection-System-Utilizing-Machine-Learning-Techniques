# Software Requirements Specification (SRS)
## Advanced QR Code Payment Fraud Detection System

**Standard:** Conforming to IEEE 830 / ISO/IEC/IEEE 29148  
**Document Version:** 1.0.0  
**Date:** 2026-11-08  
**Status:** Approved for Requirements Baseline (Phase 02)  

---

## Table of Contents
1. [Introduction](#1-introduction)
   1.1 [Purpose](#11-purpose)  
   1.2 [Document Conventions](#12-document-conventions)  
   1.3 [Intended Audience](#13-intended-audience)  
   1.4 [Project Scope](#14-project-scope)  
   1.5 [References](#15-references)  
2. [Overall Description](#2-overall-description)  
   2.1 [Product Perspective](#21-product-perspective)  
   2.2 [Product Functions](#22-product-functions)  
   2.3 [User Classes and Characteristics](#23-user-classes-and-characteristics)  
   2.4 [Operating Environment](#24-operating-environment)  
   2.5 [Design and Implementation Constraints](#25-design-and-implementation-constraints)  
   2.6 [Assumptions and Dependencies](#26-assumptions-and-dependencies)  
3. [External Interface Requirements](#3-external-interface-requirements)  
   3.1 [User Interfaces](#31-user-interfaces)  
   3.2 [Hardware Interfaces](#32-hardware-interfaces)  
   3.3 [Software Interfaces](#33-software-interfaces)  
   3.4 [Communications Interfaces](#34-communications-interfaces)  
4. [System Features & Detailed Capabilities](#4-system-features--detailed-capabilities)  
   4.1 [Payload Ingestion & Structural Sanitization](#41-payload-ingestion--structural-sanitization)  
   4.2 [Real-Time Feature Engineering & Velocity Engine](#42-real-time-feature-engineering--velocity-engine)  
   4.3 [Dual-Model Hybrid Inference Engine](#43-dual-model-hybrid-inference-engine)  
   4.4 [Three-Tier Decision & Policy Gating](#44-three-tier-decision--policy-gating)  
   4.5 [Explainable AI (XAI) Attribution](#45-explainable-ai-xai-attribution)  
   4.6 [Cryptographic Hash-Chained Audit Ledger](#46-cryptographic-hash-chained-audit-ledger)  
   4.7 [Operational Telemetry & Simulation UI](#47-operational-telemetry--simulation-ui)  
   4.8 [Federated Learning Simulation](#48-federated-learning-simulation)  
5. [Non-Functional Requirements Summary](#5-non-functional-requirements-summary)  
6. [Other Requirements](#6-other-requirements)  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) formally defines the functional, behavioral, performance, and interface requirements for the **Advanced QR Code Payment Fraud Detection System**. It serves as the binding contract for all subsequent architecture, implementation, verification, and benchmarking phases.

### 1.2 Document Conventions
- Requirement statements adopt RFC 2119 keywords: **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **RECOMMENDED**, and **MAY**.
- Requirement identifiers follow standard taxonomies:
  - `FR-[MOD]-[NUM]`: Functional Requirement.
  - `NFR-[CAT]-[NUM]`: Non-Functional Requirement.
  - `UC-[NUM]`: Use Case.
  - `US-[NUM]`: Agile User Story.

### 1.3 Intended Audience
- Autonomous Software Engineering Agents executing implementation phases.
- Software Architects, ML Engineers, and Backend Developers.
- Academic Supervisors and Thesis Evaluation Committees.
- QA Engineers and Compliance Auditors.

### 1.4 Project Scope
The system is an autonomous microservice platform that evaluates payment requests initiated via Quick Response (QR) codes. It intercepts transaction payloads in real time, extracts spatial, temporal, behavioral, and payload features, handles extreme class imbalance, and executes hybrid ML scoring to output risk verdicts (`APPROVE`, `CHALLENGE_MFA`, `BLOCK`) accompanied by SHAP explanations and immutable SHA-256 audit blocks.

### 1.5 References
1. Thesis Proposal Specification: `source/PROJECT_SPEC.md`
2. ISO 18245: Merchant Category Codes for Financial Services
3. ISO/IEC 18004: Quick Response Code Bar Code Symbology Specification
4. IEEE 830-1998: Recommended Practice for Software Requirements Specifications

---

## 2. Overall Description

### 2.1 Product Perspective
The system operates as an inline fraud prevention gateway positioned between consumer payment applications (or merchant POS scanners) and core banking authorization switches. It acts as an asynchronous/synchronous filter providing low-latency risk telemetry.

### 2.2 Product Functions
- Ingest and validate transaction JSON payloads against strict Pydantic schemas.
- Calculate rolling velocities ($5\text{m}, 1\text{h}, 24\text{h}$) via stateful in-memory caching.
- Compute Haversine geographic divergence between device GPS and merchant location.
- Calculate Shannon entropy for QR payload strings to flag obfuscation.
- Balance skewed training datasets utilizing SMOTE oversampling.
- Run concurrent inference across supervised classifiers (LightGBM/RF) and unsupervised anomaly detectors (Isolation Forest).
- Arbitrate hybrid risk scores against configurable operational thresholds.
- Compute local SHAP feature attributions for flagged transactions.
- Append tamper-evident audit blocks to an internal cryptographic ledger.
- Expose an interactive simulation dashboard for real-time visualization and manual auditing.

### 2.3 User Classes and Characteristics
- **Client Application / Gateway (Automated):** High-frequency consumer demanding low-latency HTTP REST responses ($\le 100\text{ ms}$).
- **Fraud Operations Analyst (Human):** Domain expert inspecting flagged cases, reviewing SHAP feature waterfalls, and adjusting risk tolerance.
- **System Administrator / ML Engineer (Human):** Executes model retraining, monitors concept drift, and manages API lifecycle.
- **Auditor / Regulatory Officer (Human):** Inspects cryptographic ledger integrity and reviews model bias/fairness metrics.

### 2.4 Operating Environment
- **Operating Systems:** Windows 10/11, Ubuntu 20.04/22.04 LTS, macOS Monterey+.
- **Runtime Environment:** Python 3.10 or 3.11 x86-64.
- **Hardware Profile:** Minimum 2 CPU cores, 4 GB RAM. No specialized GPU acceleration is mandated for inference.

### 2.5 Design and Implementation Constraints
- **Strict Latency Ceiling:** Total round-trip execution for `/api/v1/predict` MUST NOT exceed $100\text{ ms}$ under p99 conditions.
- **Language Constraint:** Primary implementation MUST be in Python 3.10+.
- **Zero External Paid API Dependency:** All classification, explainability, and database engines MUST execute completely offline without proprietary external cloud APIs.
- **Data Privacy Constraint:** Customer identifiers MUST be salted and hashed (SHA-256) prior to feature generation or persistence.

### 2.6 Assumptions and Dependencies
- Network transport utilizes standard HTTP/1.1 or HTTP/2 over TLS.
- Client applications supply valid GPS coordinates when requesting authorization.
- Initial model weights are pre-compiled and serialized via Joblib / ONNX.

---

## 3. External Interface Requirements

### 3.1 User Interfaces (Streamlit Dashboard)
- **Live Transaction Stream:** Interactive UI table displaying incoming simulated transactions with color-coded verdicts (Green: Approve, Yellow: Challenge, Red: Block).
- **Risk Score Gauges:** Visual display of $P_{\text{supervised}}$, $S_{\text{anomaly}}$, and $S_{\text{composite}}$.
- **SHAP Explanation Inspector:** Waterfall and force plots depicting feature impact for highlighted transactions.
- **Simulation Control Panel:** Sliders to inject synthetic anomalies (e.g., massive geo-displacement, rapid scan velocities, payload entropy tampering).

### 3.2 Hardware Interfaces
- No direct custom hardware interface. System interacts with host via standard POSIX/Win32 networking and file system abstractions.

### 3.3 Software Interfaces
- **FastAPI Core Framework:** Exposes OpenAPI v3 compliant endpoints.
- **Redis Cache Interface:** Used for in-memory rolling transaction counter queries.
- **SQLite Database Interface:** SQLAlchemy ORM used for persistent transaction logs and ledger storage.

### 3.4 Communications Interfaces
- **RESTful API:** JSON-over-HTTP/REST on port `8000`.
- **Payload Protocol:** `application/json` with UTF-8 encoding.

---

## 4. System Features & Detailed Capabilities

*(Detailed granular feature specifications are maintained in [`FUNCTIONAL_REQUIREMENTS.md`](FUNCTIONAL_REQUIREMENTS.md).)*

---

## 5. Non-Functional Requirements Summary

*(Full metric definitions and SLA budgets are maintained in [`NON_FUNCTIONAL_REQUIREMENTS.md`](NON_FUNCTIONAL_REQUIREMENTS.md).)*
- **Performance:** End-to-end inference latency $\le 100\text{ ms}$; sustained throughput $\ge 200\text{ req/s}$.
- **Accuracy:** Recall $\ge 95.0\%$, Precision $\ge 90.0\%$, False Positive Rate $\le 1.5\%$.
- **Availability:** API uptime $\ge 99.9\%$ with deterministic heuristic fallback under failure.
- **Security:** Tamper-evident SHA-256 block linking; salted hashing of customer PII.

---

## 6. Other Requirements
- **Federated Simulation:** Modular abstraction demonstrating Federated Averaging (FedAvg) across decentralized merchant client nodes.
- **Packaging:** Reproducible containerization via Docker and pinned dependency manifests (`pyproject.toml`).

