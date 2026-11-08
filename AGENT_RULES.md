# Global Development Rules & Operating Principles

This document establishes the mandatory operational constraints and engineering standards for all autonomous agents, developers, and contributors working on this codebase.

---

## 1. Primary Authority
Treat the supplied proposal (`source/PROJECT_SPEC.md`) as the primary project authority and source of truth.

## 2. Requirement Fidelity
Never invent project requirements, out-of-scope features, or arbitrary architectural additions.

## 3. Objective Integrity
Do not change approved project objectives, metrics, or target deliverables without explicit authorization from the project owner.

## 4. Source Immutability
Do not overwrite, alter, or delete original source specification files located in `source/` or outside the project root.

## 5. Scope Isolation
Perform development, script execution, artifact generation, and testing exclusively inside this designated project folder (`advanced-qr-code-payment-fraud-detection-system/`).

## 6. Iterative SDLC
Follow an Agile Scrum-based iterative Software Development Life Cycle (SDLC) organized around structured phases, user stories, and measurable deliverables.

## 7. Phase Approval Gates
Enforce strict approval gates between major development phases. Do not proceed to subsequent phases without verified completion and explicit stakeholder approval.

## 8. Continuous Documentation
Maintain accurate, comprehensive, and up-to-date documentation (`README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, `DECISIONS.md`) throughout development.

## 9. Comprehensive Testing
Test every implemented module, service, algorithm, and API endpoint with automated unit and integration tests prior to marking tasks complete.

## 10. Honesty in Verification
Never claim that an untested or partially validated feature is complete.

## 11. Scientific Integrity
Never fabricate research findings, performance metrics, citations, synthetic datasets, or test results. All benchmark figures must derive from reproducible evaluation runs.

## 12. Consultation on Major Decisions
Ask for stakeholder approval before introducing major architectural changes, alternative dependency trees, or any paid external cloud/API services.

## 13. Regression Prevention
Preserve existing working functionality, passing test suites, and backward compatibility when making incremental updates or refactoring code.

## 14. Version Control Discipline
Use Git for version control where available, maintaining atomic, descriptive commits and clean branching practices.

