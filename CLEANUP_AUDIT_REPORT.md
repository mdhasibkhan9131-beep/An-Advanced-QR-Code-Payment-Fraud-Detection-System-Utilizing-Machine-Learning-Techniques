# Safe Project Cleanup, File Audit & Structure Optimization Report

**Audit Date:** November 9, 2026  
**Auditor:** Senior Software Architect & Project Maintenance Engineer  
**Project:** Offline Autonomous QR Code Payment Fraud Detection System  
**Status:** Audit Completed — Awaiting User Approval (Phase 4 Approval Gate)

---

## 1. Executive Summary & Audit Baseline

A comprehensive, non-destructive, read-only audit of the entire project repository was performed. Every file and directory was inspected, cross-referenced across the entire codebase, and evaluated against runtime dependencies, test suites, build scripts, deployment configs, documentation, and Git history.

### Key Metrics:
- **Total Files Enumerated:** 225 files across 34 directories
- **Git Tracked Files:** 162 files
- **Git Ignored / Cache Files:** 55 files (`__pycache__`, `.pytest_cache`)
- **Untracked Redundant Files Identified:** 8 files (~2.18 MB)
- **Empty Directories Identified:** 0 (none)
- **Current Operational Status:** Fully Functional (FastAPI on `:8000`, Streamlit UI on `:8501`, 52/52 pytest tests passing)

---

## 2. Project Directory Structure Overview

```
advanced-qr-code-payment-fraud-detection-system/
├── .env / .env.example / .gitignore
├── AGENT_RULES.md / CHANGELOG.md / DECISIONS.md / PROJECT_STATUS.md / README.md
├── pyproject.toml / requirements.txt / requirements-dev.txt
├── .streamlit/
│   └── config.toml                        [Streamlit UI & server configuration]
├── backend/                               [Core Python Package - 23 modules]
│   ├── api/                               [FastAPI routes, schemas, error handlers]
│   ├── cache/                             [LRU in-memory transaction deduplication]
│   ├── config/                            [Settings & logging configuration]
│   ├── data/                              [Feature engineering, preprocessor, generator, kaggle adapter]
│   ├── database/                          [SQLAlchemy models, SQLite session management]
│   ├── ledger/                            [SHA-256 cryptographic audit chain]
│   ├── models/                            [Dual-tier ML engine: LightGBM, Isolation Forest, Scaler]
│   ├── utils/                             [Security, hashing, input sanitization]
│   └── xai/                               [SHAP explainability engine]
├── data/                                  [Datasets: Kaggle PaySim adapted, raw, synthetic]
├── database/                              [Active SQLite DB: fraud_detection.db + backups/]
├── deployment/                            [Production Dockerfile, docker-compose.yml, entrypoint.sh, prod configs]
├── docs/                                  [Phases 02-11 comprehensive specifications, tests, reports]
├── frontend/                              [Streamlit single-page application & prototype]
│   ├── app.py                             [Active production UI dashboard]
│   ├── app.py.bak                         [!] Unused backup file
│   ├── prototype/app_prototype.py         [Phase 7 prototype reference]
│   └── screenshot_*.png (7 files)         [!] Temporary verification screenshots
├── logs/                                  [Active runtime log: application.log]
├── research/benchmarks/                   [benchmark_results.json - loaded dynamically by frontend]
├── scripts/                               [DB backup/restore, smoke test, kaggle import]
├── source/                                [PROJECT_SPEC.md]
└── tests/                                 [15 test suites covering models, api, ledger, security, perf]
```

---

## 3. Categorized File Audit & Recommendations

### Category A: Potentially Safe to Remove (Candidates for Removal)

These files are demonstrably unnecessary for runtime, build, testing, or documentation.

| Item # | Exact Path | Size | Git Tracked | Application References | Purpose & Removal Justification | Risk Level | Recommended Action |
|:---:|:---|:---:|:---:|:---:|:---|:---:|:---:|
| **A-1** | `frontend/app.py.bak` | 24,581 B | No (Untracked) | 0 references | Old backup of Streamlit UI made during manual refactoring. Superseded by `frontend/app.py`. | **LOW** | **REMOVE** |
| **A-2** | `frontend/screenshot_laptop_perfect.png` | 322,827 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |
| **A-3** | `frontend/screenshot_laptop_view.png` | 312,069 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |
| **A-4** | `frontend/screenshot_ledger_view.png` | 335,387 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |
| **A-5** | `frontend/screenshot_light_mode.png` | 227,526 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |
| **A-6** | `frontend/screenshot_new_ui.png` | 315,995 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |
| **A-7** | `frontend/screenshot_new_ui2.png` | 410,099 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |
| **A-8** | `frontend/screenshot_theme_toggle.png` | 335,701 B | No (Untracked) | 0 references | Temporary visual inspection screenshot from automated browser test. | **LOW** | **REMOVE** |

*Note on Cache Directories:*  
- `__pycache__/` (49 `.pyc` files) and `.pytest_cache/` (5 files): Already safely excluded by `.gitignore`. Can be purged or left for automatic regeneration. Recommended: **LEAVE TO GITIGNORE** while processes are running.

---

### Category B: Requires Investigation / Review

These files require context verification before taking any action.

| Item # | Exact Path | Size | Git Tracked | Application References | Analysis & Recommendation | Risk Level | Recommended Action |
|:---:|:---|:---:|:---:|:---:|:---|:---:|:---:|
| **B-1** | `frontend/prototype/app_prototype.py` | 14,008 B | Yes | Referenced in `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/11_Final_Delivery/FINAL_DELIVERY_CHECKLIST.md` | Milestone 7 delivery prototype. Preserves development history and verification baseline. | **MEDIUM** | **KEEP** |
| **B-2** | `deployment/BACKUP_RECOVERY_PLAN.md` | 185 B | Yes | Self-contained pointer stub | Quickstart pointer for operations referencing `docs/10_Deployment/`. Zero runtime impact. | **LOW** | **KEEP** |
| **B-3** | `deployment/DATABASE_MIGRATION_GUIDE.md` | 202 B | Yes | Self-contained pointer stub | Quickstart pointer for operations referencing `docs/10_Deployment/`. Zero runtime impact. | **LOW** | **KEEP** |
| **B-4** | `deployment/DEPLOYMENT_GUIDE.md` | 517 B | Yes | Self-contained pointer stub | Quickstart pointer with Docker Compose commands. Zero runtime impact. | **LOW** | **KEEP** |
| **B-5** | `deployment/INSTALLATION_GUIDE.md` | 501 B | Yes | Self-contained pointer stub | Quickstart pointer with setup commands. Zero runtime impact. | **LOW** | **KEEP** |
| **B-6** | `deployment/PRODUCTION_CONFIGURATION.md` | 194 B | Yes | Self-contained pointer stub | Quickstart pointer for operations referencing `docs/10_Deployment/`. Zero runtime impact. | **LOW** | **KEEP** |
| **B-7** | `deployment/RELEASE_NOTES.md` | 168 B | Yes | Self-contained pointer stub | Quickstart pointer for operations referencing `docs/10_Deployment/`. Zero runtime impact. | **LOW** | **KEEP** |
| **B-8** | `logs/application.log` | ~122 KB | No (Ignored) | Active logger (`backend.utils.logger`) | Currently actively held by running FastAPI server. Deleting while running risks file handle desync. | **MEDIUM** | **KEEP** |

---

### Category C: Must Preserve (Core Assets — Do Not Touch)

The following 155 files are strictly preserved:

1. **Backend Source Code (`backend/`):** All 23 Python modules across `api/`, `cache/`, `config/`, `data/`, `database/`, `ledger/`, `models/`, `utils/`, and `xai/`.
2. **Trained Machine Learning Models (`backend/models/`):**
   - `lightgbm_model.joblib` (Trained supervised GBDT classifier)
   - `isolation_forest.joblib` (Trained unsupervised anomaly detector)
   - `scaler.joblib` (StandardScaler fitted feature transformer)
3. **Datasets (`data/`):**
   - `kaggle_paysim_adapted.csv` (Transformed Kaggle PaySim dataset)
   - `raw_kaggle_paysim.csv` (Raw benchmark dataset)
   - `synthetic_transactions.csv` (Synthetic generator validation data)
4. **Database & Backups (`database/`):**
   - `fraud_detection.db` (Primary SQLite database with WAL mode)
   - `database/backups/backup_20261108_172643.db.gz` (Automated database backup archive)
   - `database/backups/backup_20261108_172643.db.gz.sha256` (Cryptographic backup checksum)
5. **Frontend Core (`frontend/`):**
   - `frontend/app.py` (Active single-page modern UI dashboard)
   - `.streamlit/config.toml` (Theme & server configurations)
6. **Research Benchmarks (`research/`):**
   - `research/benchmarks/benchmark_results.json` (**CRITICAL**: dynamically loaded by `frontend/app.py` for Empirical Scoreboard metrics)
   - `research/REFERENCES.md` (Academic citations and research literature)
7. **Complete Documentation Suite (`docs/` - 60 files):**
   - Requirements (`docs/02_Requirements/`)
   - Project Management & Backlog (`docs/03_Project_Management/`)
   - Technical Research (`docs/04_Technical_Research/`)
   - System Design & Architecture Diagrams (`docs/05_System_Design/` + `diagrams/`)
   - UI/UX Specifications (`docs/06_UI_UX/`)
   - Testing & Audit Evidence (`docs/09_Testing/` + `Evidence/`)
   - Deployment Guides (`docs/10_Deployment/`)
   - Final Delivery Documentation (`docs/11_Final_Delivery/`)
8. **Test Suites (`tests/` - 15 files):**
   - All unit, integration, validation, security, and performance test suites.
9. **Administrative Scripts (`scripts/` - 4 files):**
   - `backup_database.py`, `restore_database.py`, `smoke_test.py`, `import_kaggle_dataset.py`.
10. **Deployment Configurations (`deployment/`):**
    - `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `.dockerignore`, `prod.env.example`.
11. **Root Specifications & Metadata:**
    - `source/PROJECT_SPEC.md`, `README.md`, `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, `AGENT_RULES.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, `DECISIONS.md`, `.env`, `.env.example`, `.gitignore`.

---

## 4. Proposed Cleanup Action Items (Upon Explicit Approval)

Only the **8 items from Category A** are proposed for removal:

```
frontend/app.py.bak                     (24.0 KB)
frontend/screenshot_laptop_perfect.png  (315.3 KB)
frontend/screenshot_laptop_view.png     (304.8 KB)
frontend/screenshot_ledger_view.png     (327.5 KB)
frontend/screenshot_light_mode.png      (222.2 KB)
frontend/screenshot_new_ui.png          (308.6 KB)
frontend/screenshot_new_ui2.png         (400.5 KB)
frontend/screenshot_theme_toggle.png    (327.8 KB)
------------------------------------------------
Total space to be reclaimed:            ~2.18 MB
```

### Safety & Reversibility Plan:
1. Prior to removal, a full zip archive of these 8 files will be stored in `database/backups/cleanup_pre_backup_<timestamp>.zip` or a designated backup folder.
2. The Git working tree will remain completely clean and operational.
3. Post-cleanup regression tests (`pytest`) and live health checks (`FastAPI` + `Streamlit`) will be executed immediately.

---

## 5. Phase 4 Approval Gate (STOP HERE)

**No files have been modified, renamed, moved, or deleted.**

Awaiting user approval before proceeding to Phase 5.

