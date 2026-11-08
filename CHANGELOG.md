# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Added
- **Sprint 2: Data Engineering, Contextual Features & Synthetic Generation**
  - Implemented timestamp drift and freshness validation (`PBI-002` / `FR-ING-002`) guarding against replay attacks beyond +/-300s.
  - Implemented Haversine great-circle spatial displacement calculation (`PBI-003` / `FR-FEA-001`) with domain clamp and symmetry tests.
  - Implemented Shannon entropy analyzer (`PBI-004` / `FR-FEA-002`) detecting obfuscated and malicious QR payload redirects.
  - Integrated in-memory sliding window rolling velocities ($V_{5\text{m}}, V_{1\text{h}}, V_{24\text{h}}$) and velocity ratios (`PBI-005` / `FR-FEA-003`).
  - Implemented customer historical spending baseline Z-score calculator (`PBI-006` / `FR-FEA-004`) with zero-variance protection.
  - Built `FeatureEngineeringPipeline` constructing standardized 16-dimensional tabular feature vectors.
  - Implemented `SyntheticQRTransactionGenerator` (`PBI-007` / `FR-DAT-001`) reproducing acute class imbalance (0.80% fraud) across 4 distinct archetypes (Legitimate baseline, Static Sticker Quishing, Dynamic MITM Amount Surge, High-Velocity Credential Bot Probe).
  - Built `DataPreprocessor` (`PBI-008` / `FR-DAT-003`) enforcing strict split isolation: RobustScaler fitted strictly on training partition, and Borderline-SMOTE / SMOTE applied strictly to training folds while leaving validation and test sets pristine.
  - Added comprehensive automated test suites (`tests/test_feature_engineering.py`, `tests/test_generator.py`, `tests/test_preprocessor.py`), expanding test coverage to **31/31 tests passing (100%)**.
- **Phase 07: Development Environment & Foundation Initialized (Sprint 1 Foundation)**
  - Initialized Git version control repository with `.gitignore` and committed initial foundation codebase.
  - Installed all required scientific and ML dependencies (`lightgbm`, `imbalanced-learn`, `shap`, `streamlit`, `pyod`, `pydantic-settings`, `pytest-asyncio`).
  - Configured environment variables via Pydantic Settings (`backend/config/settings.py`, `.env`, `.env.example`).
  - Implemented structured rotating file and console logging (`backend/config/logging_config.py`, `logs/application.log`).
  - Configured SQLite WAL database connectivity via SQLAlchemy 2.0 with complete relational ORM models (`backend/database/session.py`, `backend/database/models.py`).
  - Built thread-safe in-memory sliding window TTL cache (`backend/cache/memory.py`).
  - Built FastAPI application factory, CORS, request timing middleware (`X-Response-Time-Ms`), and RFC 7807 centralized error handlers (`backend/api/server.py`, `backend/api/errors.py`).
  - Created operational health-check and metrics endpoints (`/api/v1/health`, `/api/v1/metrics`, `/api/v1/predict` foundation).
  - Authored automated test suite (`tests/test_environment.py`, `tests/test_database.py`, `tests/test_health.py`, `tests/test_api_validation.py`) achieving **100% test pass rate (10/10 tests)**.
- **Phase 06: UI/UX Design & Prototyping**
  - Mapped 4 primary personas and comprehensive user journeys (`docs/06_UI_UX/USER_JOURNEY.md`).
  - Screen catalog detailing 6 specialized views and component breakdowns (`docs/06_UI_UX/SCREEN_INVENTORY.md`).
  - Navigation architecture, session state management, and deep links (`docs/06_UI_UX/NAVIGATION_FLOW.md`).
  - Fintech Precision design system with color tokens, typography, and spacing (`docs/06_UI_UX/DESIGN_SYSTEM.md`).
  - High-fidelity ASCII structural wireframes across desktop and laptop viewports (`docs/06_UI_UX/WIREFRAME_SPECIFICATION.md`).
  - Loading, error, empty, and success state specifications with WCAG 2.1 AA accessibility guidelines (`docs/06_UI_UX/UI_UX_SPECIFICATION.md`).
  - Implemented standalone executable Streamlit UI prototype in (`frontend/prototype/app_prototype.py`).
- **Phase 05: Complete System Architecture & Software Design**
  - High-Level Architecture Design with component topologies and subsystem boundaries (`docs/05_System_Design/HIGH_LEVEL_DESIGN.md`).
  - Low-Level Software Design with complete class diagrams, ABC interfaces, and method signatures (`docs/05_System_Design/LOW_LEVEL_DESIGN.md`).
  - Relational Database Design with SQLite WAL pragma optimization and DDL schemas (`docs/05_System_Design/DATABASE_DESIGN.md`).
  - OpenAPI v3 REST API specification with granular endpoints, request/response models, and status codes (`docs/05_System_Design/API_SPECIFICATION.md`).
  - Security architecture, RBAC, PII salted hashing, and circuit breaker pattern (`docs/05_System_Design/SECURITY_DESIGN.md`).
  - Step-by-step documentation of 7 end-to-end system workflows with embedded diagrams (`docs/05_System_Design/SYSTEM_WORKFLOWS.md`).
  - Authored 7 editable Mermaid diagrams in `docs/05_System_Design/diagrams/` (`architecture_diagram.mmd`, `component_diagram.mmd`, `er_diagram.mmd`, `use_case_diagram.mmd`, `sequence_diagram.mmd`, `activity_diagram.mmd`, `data_flow_diagram.mmd`).
- **Phase 04: Technical Research, Technology Selection & Feasibility**
  - Comparative trade-off analysis across all architectural tiers (`docs/04_Technical_Research/TECHNOLOGY_COMPARISON.md`).
  - Granular latency profiling and theoretical feasibility assessment (`docs/04_Technical_Research/TECHNICAL_FEASIBILITY.md`).
  - Academic literature synthesis mapping solutions to the 5 proposal research gaps (`docs/04_Technical_Research/RESEARCH_ANALYSIS.md`).
  - In-depth mathematical equations and algorithmic formulations (`docs/04_Technical_Research/ALGORITHM_SELECTION.md`).
  - Computational capacity, hardware budgets, and concurrency projections (`docs/04_Technical_Research/HARDWARE_REQUIREMENTS.md`).
  - STRIDE threat modeling, adversarial defenses, and privacy compliance analysis (`docs/04_Technical_Research/SECURITY_CONSIDERATIONS.md`).
  - Consolidated technology stack recommendations and rejected alternatives rationale (`docs/04_Technical_Research/TECHNICAL_RECOMMENDATIONS.md`).
  - Verified primary literature citations with original DOIs archived in (`research/REFERENCES.md`).
- **Phase 03: Project Management & Agile Planning**
  - Project Management Plan establishing Agile Scrum SDLC and stage-gates (`docs/03_Project_Management/PROJECT_MANAGEMENT_PLAN.md`).
  - 11-tier Work Breakdown Structure (`docs/03_Project_Management/WBS.md`).
  - 32-item Product Backlog with MoSCoW prioritization and provisional story points (`docs/03_Project_Management/PRODUCT_BACKLOG.md`).
  - 6-iteration Sprint Roadmap with goals, deliverables, and exit criteria (`docs/03_Project_Management/SPRINT_PLAN.md`).
  - Milestone schedule (M0 - M7) and critical path analysis (`docs/03_Project_Management/PROJECT_TIMELINE.md`).
  - 10-point Risk Register with probability, impact, triggers, and contingencies (`docs/03_Project_Management/RISK_REGISTER.md`).
  - Multi-tier Definition of Done from task to stage-gate level (`docs/03_Project_Management/DEFINITION_OF_DONE.md`).
  - Git version control workflow and Conventional Commits specification (`docs/03_Project_Management/GIT_WORKFLOW.md`).
- **Phase 02: Complete Project Analysis & Requirements Engineering**
  - Generated comprehensive project problem analysis and scope boundaries (`docs/02_Requirements/PROJECT_ANALYSIS.md`).
  - Formulated IEEE 830-compliant Software Requirements Specification (`docs/02_Requirements/SRS.md`).
  - Defined granular functional requirements across 10 modules (`docs/02_Requirements/FUNCTIONAL_REQUIREMENTS.md`).
  - Defined quantitative non-functional SLAs, latency budgets, and security constraints (`docs/02_Requirements/NON_FUNCTIONAL_REQUIREMENTS.md`).
  - Authored 8 end-to-end use case specifications (`docs/02_Requirements/USE_CASES.md`).
  - Authored 19 INVEST-compliant Agile User Stories across 7 epics (`docs/02_Requirements/USER_STORIES.md`).
  - Documented Gherkin-syntax acceptance criteria for all requirements and edge cases (`docs/02_Requirements/ACCEPTANCE_CRITERIA.md`).
  - Built full bidirectional Requirements Traceability Matrix (`docs/02_Requirements/RTM.md`).
  - Conducted gap analysis distinguishing confirmed vs recommended requirements and listing decisions requiring approval (`docs/02_Requirements/REQUIREMENTS_GAP_ANALYSIS.md`).

---

## [0.1.0] - 2026-11-08
### Added
- Inspected and verified source specification (`PROJECT_SPEC.md`).
- Initialized isolated workspace root `advanced-qr-code-payment-fraud-detection-system/`.
- Created standardized 9-directory scaffolding (`source/`, `docs/`, `frontend/`, `backend/`, `database/`, `tests/`, `scripts/`, `research/`, `deployment/`).
- Copied immutable source document into `source/PROJECT_SPEC.md`.
- Formulated `AGENT_RULES.md` defining 14 non-negotiable engineering principles.
- Initialized `PROJECT_STATUS.md` at Phase: `Workspace Initialization`.
- Added Architecture Decision Records baseline (`DECISIONS.md`).
- Created project overview and repository navigation documentation (`README.md`).
