# Definition of Done (DoD)

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Document:** `AGENT_RULES.md`

---

## 1. Overview & Purpose

The Definition of Done (DoD) establishes the mandatory quality criteria that every development artifact, user story, sprint increment, and phase release must satisfy before being declared complete. In accordance with Rule 10 of `AGENT_RULES.md`, **no feature may ever be claimed as complete if it remains untested or unverified**.

---

## 2. Multi-Level Definition of Done

```
┌────────────────────────────────────────────────────────┐
│ 1. Task-Level DoD (Unit Implementation & Styling)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Story-Level DoD (Acceptance Criteria & Integration) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Sprint-Level DoD (Working Increment & Regression)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Stage-Gate Release DoD (Formal Stakeholder Sign-Off)│
└────────────────────────────────────────────────────────┘
```

---

## 3. Granular Quality Criteria

### 3.1 Task-Level Definition of Done
A technical task or subtask is **Done** when:
- [ ] Code is fully implemented in Python 3.10+ following PEP 8 conventions.
- [ ] Explicit type annotations are applied across all function signatures and variables, passing static type analysis (`mypy`).
- [ ] No hardcoded configuration parameters, API secrets, or magic numbers exist (all centralized in `backend/config/settings.py`).
- [ ] Unit tests are written for all newly introduced functions, algorithms, or utility classes.
- [ ] Code passes all local linting checks (`ruff check .` / `flake8`) with zero fatal errors or warnings.
- [ ] Docstrings (NumPy/Google format) are present for all public classes, methods, and functions.

### 3.2 Story-Level Definition of Done
A user story (PBI) is **Done** when:
- [ ] All associated tasks are complete and verified.
- [ ] All Gherkin-syntax acceptance criteria defined in `docs/02_Requirements/ACCEPTANCE_CRITERIA.md` are satisfied.
- [ ] Positive, negative, boundary, and edge-case test scenarios pass without exceptions.
- [ ] Automated test coverage for the story's target module is $\ge 85\%$.
- [ ] Code changes do not regress any pre-existing tests or functionality (Rule 13 in `AGENT_RULES.md`).
- [ ] Code review checklist is satisfied.

### 3.3 Sprint-Level Definition of Done
A development sprint is **Done** when:
- [ ] All committed sprint user stories meet their Story-Level DoD.
- [ ] The full automated test suite passes: `pytest --cov=backend tests/`.
- [ ] System end-to-end integration passes without unhandled exceptions.
- [ ] Execution performance complies with the latency budget ($p99 \le 100\text{ ms}$ for serving components).
- [ ] `PROJECT_STATUS.md` is updated with completed backlog items, updated metrics, and next sprint goals.
- [ ] `CHANGELOG.md` is updated reflecting newly delivered functionality under `[Unreleased]` or version tag.
- [ ] Any architectural trade-offs or decisions are documented in `DECISIONS.md`.

### 3.4 Stage-Gate Release Definition of Done
A development phase reaches **Gate Acceptance** when:
- [ ] The Sprint-Level DoD is satisfied for all sprints within the phase.
- [ ] A formal Stage-Gate Review Report is presented to the Product Owner / Academic Stakeholder.
- [ ] The Requirements Traceability Matrix (`RTM.md`) is updated and verified.
- [ ] All non-functional metrics (Recall $\ge 95\%$, Precision $\ge 90\%$, FPR $\le 1.5\%$) are verified against holdout datasets.
- [ ] Explicit stakeholder approval is granted in writing before advancing to the subsequent project phase.

