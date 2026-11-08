# Production Configuration Reference & Hardening Guide

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved Quality Baseline  
**Configuration Interface:** Pydantic Settings (`backend/config/settings.py`)

---

## 1. Environment Variable Reference Matrix

| Variable Name | Type | Default Value | Production Recommendation | Description |
| :--- | :---: | :---: | :---: | :--- |
| `PROJECT_NAME` | `str` | `"Advanced QR Code..."` | `"Advanced QR Code..."` | Canonical system identifier. |
| `VERSION` | `str` | `"1.0.0"` | `"1.0.0"` | Semantic release version. |
| `ENVIRONMENT` | `str` | `"development"` | `"production"` | Operational environment profile (`production` disables debug traces). |
| `DEBUG` | `bool` | `False` | `False` | Debug mode; MUST be `False` in production to prevent stack trace leaks. |
| `APP_HOST` | `str` | `"0.0.0.0"` | `"0.0.0.0"` / `"127.0.0.1"` | Host network binding interface. |
| `APP_PORT` | `int` | `8000` | `8000` | Gateway listening port. |
| `SECRET_KEY` | `str` | *Required* | 64-char Hex String | HMAC-SHA256 secret for cryptographic state signing. |
| `PII_SECRET_SALT` | `str` | *Required* | 64-char Hex String | Salt value for customer/merchant one-way SHA-256 anonymization. |
| `DATABASE_URL` | `str` | `sqlite:///database/...`| `sqlite:///database/...` | SQLAlchemy database connection string. |
| `SQL_ECHO` | `bool` | `False` | `False` | Log raw SQL statements; MUST be `False` in production. |
| `CACHE_BACKEND` | `str` | `"memory"` | `"memory"` | Sliding window cache (`memory` for standalone offline autonomy). |
| `WEIGHT_SUPERVISED`| `float`| `0.70` | `0.70` | Relative weighting $\alpha$ for supervised LightGBM score. |
| `WEIGHT_ANOMALY` | `float`| `0.30` | `0.30` | Relative weighting $(1 - \alpha)$ for unsupervised Isolation Forest. |
| `THRESHOLD_APPROVE`| `float`| `0.30` | `0.30` | Boundary threshold $\tau_1$; $S_{\text{comp}} < \tau_1 \implies \text{APPROVE}$. |
| `THRESHOLD_BLOCK` | `float`| `0.70` | `0.70` | Boundary threshold $\tau_2$; $S_{\text{comp}} \ge \tau_2 \implies \text{BLOCK}$. |
| `ZERO_DAY_ANOMALY_ESCALATION` | `float` | `0.80` | `0.80` | Outlier escalation threshold $\tau_{\text{esc}}$ forcing step-up MFA. |
| `TIMEOUT_CIRCUIT_BREAKER_MS` | `int` | `120` | `120` | Watchdog timeout triggering deterministic heuristic fallback. |
| `SELECTIVE_SHAP_OPTIMIZATION` | `bool` | `True` | `True` | Bypasses SHAP calculation on routine approved payments. |
| `LOG_LEVEL` | `str` | `"INFO"` | `"INFO"` | Logging verbosity (`INFO` or `WARNING` in production). |
| `LOG_FILE_PATH` | `str` | `"logs/application.log"`| `"logs/application.log"`| Rotating file log destination. |

---

## 2. Production Security Hardening

### 2.1 Cryptographic Key Generation
Never use default placeholder strings in production. Generate distinct high-entropy keys:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32)); print('PII_SECRET_SALT=' + secrets.token_hex(32))"
```

### 2.2 File System Permissions
Enforce strict least-privilege permissions:
```bash
# Configuration file must be readable only by application user
chmod 600 .env

# SQLite database directory and files
chmod 700 database/
chmod 600 database/fraud_detection.db*

# Log files
chmod 700 logs/
chmod 640 logs/application.log*
```

### 2.3 CPU Threading & OpenMP Concurrency Tuning
To prevent CPU over-subscription in high-throughput containerized environments, pin OpenMP threads matching container CPU limits:
```bash
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
```

### 2.4 High-Performance SQLite WAL Configuration
The SQLite engine is automatically configured with Write-Ahead Logging (`WAL`) pragmas in `backend/database/session.py`:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64 MB in-memory cache
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456; -- 256 MB memory-mapped I/O
```

