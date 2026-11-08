# Project Management Plan (PMP)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Author:** Senior Technical Project Manager  
**Reference Standards:** Agile Scrum, ISO/IEC/IEEE 12207, IEEE 1058  
**Parent Document:** `source/PROJECT_SPEC.md` | `AGENT_RULES.md`

---

## 1. Methodology & SDLC Framework

This project follows an **Agile Scrum-based Iterative and Incremental Software Development Life Cycle (SDLC)** integrated with strict **Stage-Gate Approvals** at phase transitions.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                STAGE-GATE APPROVAL GATES                               │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│    Gate 0    │    Gate 1    │    Gate 2    │    Gate 3    │    Gate 4    │   Gate 5    │
│  Workspace   │ Architecture │ Environment  │ ML Benchmarks│  Integration │ Final Audit │
│  Scaffolding │  & Design    │ & Data Pipe  │ & Anomaly    │  (API & UI)  │ & Evaluation│
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
       │              │              │              │              │              │
       ▼              ▼              ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌─────────────┐
│   Sprint 0   ││   Sprint 1   ││   Sprint 2   ││   Sprint 3   ││   Sprint 4   ││  Sprint 5   │
│ Inception &  ││ System Design││ Data Pipe &  ││ ML Models &  ││ Full Stack   ││ Verification│
│ Requirements ││ & Contracts  ││ Synthesizer  ││ Hybrid Gating││ (API, UI, XAI││ & Thesis Rpt│
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘└─────────────┘
```

### 1.1 Key Principles of the Methodology:
1. **Iterative Increments:** Every sprint produces a working, testable increment of the software stack.
2. **Strict Phase Gating:** Development cannot cross into subsequent phases or sprints without explicit stakeholder review and approval (enforcing Rule 7 in `AGENT_RULES.md`).
3. **Traceability by Design:** Every backlog story, task, test case, and commit must link back to requirements specified in `docs/02_Requirements/`.
4. **Empirical Quality Control:** "Working software" is defined strictly by executable automated test suites meeting coverage ($\ge 85\%$) and performance SLA criteria (p99 latency $\le 100\text{ ms}$).

---

## 2. Roles & Responsibilities Matrix (RACI)

| Role | Primary Persona / Agent | Responsibilities |
| :--- | :--- | :--- |
| **Product Owner (PO)** | Stakeholder / Academic Lead | Approves requirements, authorizes architectural decisions, gates phase sign-offs, accepts sprint deliverables. |
| **Scrum Master / PM** | Senior Technical Project Manager | Facilitates sprint execution, tracks velocity, enforces `AGENT_RULES.md`, manages risks, maintains project status. |
| **Software Architect** | Senior Software Architect | Defines system topology, API schemas, design patterns, and hardware/performance budgets. |
| **ML Engineer** | AI/ML Development Agent | Develops data generation, SMOTE pipelines, classifier models (LightGBM/RF/MLP), and Isolation Forest. |
| **Backend & Security Engineer**| Backend Development Agent | Implements FastAPI endpoints, stateful in-memory velocity cache, SHA-256 cryptographic audit ledger, and heuristic fallback. |
| **Frontend Engineer** | UI Development Agent | Develops Streamlit interactive simulation dashboard, real-time risk gauges, and SHAP visual waterfalls. |
| **QA & Verification Engineer** | Test Automation Agent | Develops unit, integration, and load test suites; verifies latency SLAs; enforces Definition of Done. |

### RACI Governance Table:
- **Requirements Approval:** PO (Accountable), PM (Responsible), Architect (Consulted).
- **Architecture & Design:** Architect (Accountable/Responsible), PO (Consulted), Team (Informed).
- **Module Implementation:** Dev Team (Responsible), Architect (Accountable), QA (Consulted).
- **Stage-Gate Sign-Off:** PO (Accountable), PM (Responsible), Entire Team (Informed).

---

## 3. Agile Ceremonies & Operational Cadence

Given the autonomous pair-programming paradigm, ceremonies are adapted into structured asynchronous checkpoints:

| Ceremony | Cadence | Input Artifacts | Expected Output |
| :--- | :--- | :--- | :--- |
| **Sprint Planning** | Start of each sprint | Product Backlog, SRS, WBS | Sprint Backlog, Sprint Goal, Story Point estimates. |
| **Turn Check-ins (Daily Standup)** | Per active work cycle | Active tasks, `PROJECT_STATUS.md` | Incremental task progress, blocker identification, immediate next steps. |
| **Sprint Review** | End of each sprint | Working software increment, test reports | Demonstration of functional increment, acceptance by PO. |
| **Sprint Retrospective** | End of each sprint | Quality metrics, test coverage, bottlenecks | Process optimizations logged in `PROJECT_STATUS.md`. |
| **Stage-Gate Review** | Phase transition | Complete Phase Deliverable Package | Formal sign-off and permission to proceed to next sprint. |

---

## 4. Quality & Engineering Governance

All development activities must conform to the following non-negotiable quality controls:
1. **Source Code Parity:** No application code may be written that contradicts or invents requirements beyond `source/PROJECT_SPEC.md` and approved SRS documents.
2. **Testing Mandate:** Unit test suites for all algorithms, feature calculations, and API routes. Integration tests for end-to-end data flow.
3. **Latency Verification:** Benchmark tests must assert that inference executes within the $\le 100\text{ ms}$ budget under simulated load.
4. **Code Quality Standards:** Clean PEP 8 compliance, explicit type hints (`mypy`), docstrings for all classes and functions, zero hardcoded secrets.

---

## 5. Change Management Procedure

If a technical ambiguity, performance blocker, or new requirement arises:
1. **Log Gap:** The engineer/agent logs the item in `docs/02_Requirements/REQUIREMENTS_GAP_ANALYSIS.md`.
2. **Impact Assessment:** Architect and PM evaluate impact on schedule, latency budgets, and scope.
3. **Decision Record:** Document options and recommended resolution in `DECISIONS.md`.
4. **PO Gate:** Submit decision to Product Owner for formal authorization. No silent changes are permitted.

---

## 6. Project Documentation & Tracking Protocol

- **`PROJECT_STATUS.md`**: Updated at every sprint transition and major task completion.
- **`CHANGELOG.md`**: Updated with every user-facing or architectural increment using Keep a Changelog syntax.
- **`DECISIONS.md`**: Every major design trade-off logged as an ADR (Architecture Decision Record).

