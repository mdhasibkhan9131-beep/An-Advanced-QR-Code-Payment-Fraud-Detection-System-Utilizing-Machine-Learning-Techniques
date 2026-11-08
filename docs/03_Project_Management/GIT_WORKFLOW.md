# Git Version Control & Collaboration Workflow

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 03)  
**Parent Document:** `docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`  
**Reference Policy:** Rule 14 in `AGENT_RULES.md`

---

## 1. Branching Strategy

The repository follows a modified **Git Flow / Trunk-Based Hybrid** designed for disciplined agile delivery:

```
main (Production Releases / Stage-Gate Tags)
  ▲
  │ (Pull Request via Stage-Gate Approval)
develop (Integration & Active Sprint Branch)
  ▲
  ├────── feature/PBI-003-haversine-distance
  ├────── feature/PBI-007-synthetic-generator
  ├────── fix/timeout-heuristic-fallback
  └────── release/v0.3.0
```

### Branch Taxonomies:
- **`main`**: Permanent production branch. Contains only thoroughly tested, stage-gate approved release commits tagged with semantic versions (e.g., `v0.1.0`, `v1.0.0`). Direct pushes are prohibited.
- **`develop`**: Primary continuous integration branch. Active sprint deliverables merge into `develop` once story-level DoD is satisfied.
- **`feature/[PBI-ID]-[short-description]`**: Temporary branches created off `develop` for specific backlog items (e.g., `feature/PBI-010-lightgbm-classifier`).
- **`fix/[bug-description]`**: Bugfix branches branched off `develop` to resolve regression failures or test defects.
- **`release/[version-tag]`**: Stabilization branch prepared for stage-gate review and final verification prior to merging into `main`.

---

## 2. Commit Message Conventions (Conventional Commits)

All commit messages MUST adhere to the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/) standard, referencing the corresponding PBI or Story identifier:

```
<type>(<scope>): <concise subject description in imperative mood> [<PBI-ID>]

[optional body explaining motivation and architectural context]

[optional footer referencing breaking changes or closed issues]
```

### Allowed Types:
- **`feat`**: A new user-facing or architectural capability (e.g., `feat(features): implement Haversine distance calculator [PBI-003]`).
- **`fix`**: A bug fix or defect resolution (e.g., `fix(api): prevent division by zero in velocity ratio [PBI-005]`).
- **`docs`**: Documentation updates or additions (e.g., `docs(management): establish sprint roadmap and WBS [PBI-000]`).
- **`test`**: Adding missing tests or correcting existing test suites (e.g., `test(models): add unit tests for Isolation Forest normalization [PBI-012]`).
- **`refactor`**: Code changes that neither fix bugs nor add features (e.g., `refactor(cache): extract abstract base class for cache adapters [PBI-005]`).
- **`perf`**: A code modification that optimizes execution latency or memory footprint (e.g., `perf(xai): memoize tree explainer background distribution [PBI-018]`).
- **`chore`**: Build system adjustments, dependency lockfile updates, or toolchain configuration (e.g., `chore(deps): pin scikit-learn and lightgbm in pyproject.toml [PBI-000]`).

---

## 3. Pull Request & Code Review Procedure

Every pull request (PR) targeting `develop` or `main` must complete the following checklist:
1. **Automated CI Validation:**
   - Test suite passes 100%: `pytest tests/`.
   - Coverage threshold met: $\ge 85\%$.
   - Linting clean: `ruff check .` with zero errors.
   - Type check clean: `mypy backend/`.
2. **Reviewer Inspection Checklist:**
   - [ ] Does the implementation strictly adhere to `docs/02_Requirements/SRS.md`?
   - [ ] Are all Gherkin acceptance criteria verified by automated tests?
   - [ ] Are docstrings and type annotations complete?
   - [ ] Are there zero hardcoded secrets or PII leaks?
   - [ ] Is latency budgeted and verified?
3. **Approval:**
   - PR requires at least 1 peer or lead reviewer sign-off before squash-and-merge.

---

## 4. Semantic Versioning & Tagging Strategy

Releases follow [Semantic Versioning (SemVer 2.0.0)](https://semver.org/):
$$\text{v}\langle\text{Major}\rangle.\langle\text{Minor}\rangle.\langle\text{Patch}\rangle$$
- **Major ($X.0.0$):** Major milestone release (e.g., `v1.0.0` at final thesis project completion).
- **Minor ($0.X.0$):** Completion of a development sprint or major stage-gate (e.g., `v0.2.0` after Sprint 2 Data Pipeline).
- **Patch ($0.X.Y$):** Minor bugfixes or documentation amendments.

Tags are signed and created strictly on `main` following formal stage-gate approval.

