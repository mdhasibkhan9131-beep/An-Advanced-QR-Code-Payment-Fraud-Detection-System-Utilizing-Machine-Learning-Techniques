# Software Installation & Setup Guide

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved Quality Baseline  
**Target Environments:** Linux (Ubuntu/Debian/RHEL), Microsoft Windows 10/11/Server, macOS

---

## 1. System Requirements & Dependencies

### Hardware Requirements
- **CPU:** 64-bit x86_64 or ARM64 processor (2+ cores recommended)
- **RAM:** 2.0 GB minimum (4.0 GB recommended for high-volume streaming)
- **Disk:** 5.0 GB free disk space (models, databases, and logs)

### Software Prerequisites
- **Python:** Version `3.11.x` (Recommended: 3.11.9)
- **C/C++ OpenMP Runtime:** `libgomp1` (required by LightGBM multi-threading)
- **Git:** Version 2.30+

---

## 2. Step-by-Step Installation

### Step 1: Clone Workspace
```bash
git clone https://github.com/organization/advanced-qr-code-payment-fraud-detection-system.git
cd advanced-qr-code-payment-fraud-detection-system
```

### Step 2: Create Python Virtual Environment
```bash
# On Linux / macOS:
python3.11 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Upgrade Package Manager & Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 4: Configure Local Environment
```bash
# Copy example environment configuration
cp deployment/prod.env.example .env
```
Generate secure 64-character secrets:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32)); print('PII_SECRET_SALT=' + secrets.token_hex(32))"
```
Update `SECRET_KEY` and `PII_SECRET_SALT` inside `.env`.

### Step 5: Initialize Database & Train Production Models
```bash
# 1. Initialize SQLite WAL schemas
python -c "from backend.database.session import init_db; init_db()"

# 2. Train baseline models and serialize weights
python -m backend.models.trainer
```
Expected output:
```
[Trainer] Saved LightGBM to backend/models/lightgbm_model.joblib
[Trainer] Saved Isolation Forest to backend/models/isolation_forest.joblib
[Trainer] Benchmark report exported to research/benchmarks/benchmark_results.json
```

### Step 6: Verify Installation via Test Suite
```bash
pytest -v
```
Ensure all 50+ automated tests pass with 0 failures.

---

## 3. Running the Application

### Launching the API Gateway (FastAPI)
```bash
uvicorn backend.api.server:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation will be accessible at:
- Swagger UI: `http://localhost:8000/docs`
- Redoc UI: `http://localhost:8000/redoc`

### Launching the Interactive Monitoring Dashboard (Streamlit)
In a separate terminal session:
```bash
streamlit run frontend/app.py --server.port 8501
```
The Fintech Dark Theme Dashboard will be accessible at: `http://localhost:8501`.
