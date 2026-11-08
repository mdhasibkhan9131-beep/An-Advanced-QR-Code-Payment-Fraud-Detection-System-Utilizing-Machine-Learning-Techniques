# Production Deployment & Operations Guide

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Production Deployment (Milestone M7)  
**Author:** Lead DevOps Engineer & Release Manager  
**Release Target:** On-Premise Enterprise / Containerized Microservices

---

## 1. System Architecture & Topology

The production deployment architecture is designed for **100% offline autonomy**, sub-100ms inference processing, and zero external cloud API dependencies.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION RUNTIME TOPOLOGY                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [ Client POS / Mobile App ]            [ Compliance Auditor ]        │
│                │                                    │                  │
│                ▼ (:8000)                            ▼ (:8501)          │
│   ┌───────────────────────────┐         ┌──────────────────────────┐   │
│   │   FastAPI API Gateway     │         │   Streamlit Dashboard    │   │
│   │   (Uvicorn 4 Workers)     │         │   (Interactive Web UI)   │   │
│   └─────────────┬─────────────┘         └────────────┬─────────────┘   │
│                 │                                    │                 │
│                 ▼                                    ▼                 │
│       ┌────────────────────────────────────────────────────┐           │
│       │             Core Production ML Engine              │           │
│       │  - LightGBM GBDT Production Classifier             │           │
│       │  - Unsupervised Isolation Forest Anomaly Engine    │           │
│       │  - SHAP TreeExplainer & Reason Code Mapper         │           │
│       │  - In-Memory Sliding Window TTL Velocity Cache     │           │
│       └─────────────────────────┬──────────────────────────┘           │
│                                 │                                      │
│                                 ▼                                      │
│       ┌────────────────────────────────────────────────────┐           │
│       │        Persistent Storage & Cryptographic Layer    │           │
│       │  - SQLite 3.45 WAL Database (Normalized Tables)    │           │
│       │  - SHA-256 Block-Chained Cryptographic Ledger      │           │
│       └────────────────────────────────────────────────────┘           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites & System Requirements

- **Operating System:** Linux (Ubuntu 22.04 LTS / RHEL 9) or Windows Server 2022
- **Container Engine:** Docker 24.0+ and Docker Compose v2.20+
- **Host Hardware:**
  - CPU: Minimum 2 Cores (Recommended: 4 Cores)
  - RAM: Minimum 2.0 GB (Recommended: 4.0 GB)
  - Storage: 10 GB SSD for logs, database, and snapshot backups
- **Network Ports:**
  - Port `8000`: FastAPI REST Inference Gateway
  - Port `8501`: Streamlit Telemetry & Simulation UI

---

## 3. Containerized Deployment (Docker Compose)

### Step 1: Clone Repository and Inspect Environment
```bash
git clone https://github.com/organization/advanced-qr-code-payment-fraud-detection-system.git
cd advanced-qr-code-payment-fraud-detection-system
```

### Step 2: Configure Production Environment Variables
Copy the production environment template and generate secure cryptographic keys:
```bash
cp deployment/prod.env.example .env
```
Generate cryptographic secret keys and paste into `.env`:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32)); print('PII_SECRET_SALT=' + secrets.token_hex(32))"
```

### Step 3: Launch Services via Docker Compose
```bash
docker compose -f deployment/docker-compose.yml up -d --build
```

### Step 4: Verify Container Health & Status
```bash
docker compose -f deployment/docker-compose.yml ps
```
Expected output:
```
NAME                    IMAGE                         STATUS                    PORTS
qr-fraud-api-gateway    deployment-api-gateway        Up (healthy) (8000/tcp)   0.0.0.0:8000->8000/tcp
qr-fraud-dashboard      deployment-monitoring-dashboard Up (8501/tcp)           0.0.0.0:8501->8501/tcp
```

### Step 5: Execute Post-Deployment Smoke Tests
```bash
python scripts/smoke_test.py --url http://localhost:8000
```
Expected output:
```
SMOKE TEST SUMMARY: 6/6 WORKFLOWS PASSED (100% SUCCESS)
APPLICATION IS HEALTHY, OPERATIONAL, AND READY FOR TRAFFIC!
```

---

## 4. Bare-Metal Production Deployment (Systemd)

For bare-metal or virtual machine deployments without Docker:

### Step 1: Install Python Virtual Environment
```bash
sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv libgomp1
python3.11 -m venv /opt/qr-fraud/venv
source /opt/qr-fraud/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Pre-warm Models & Database Schemas
```bash
python -m backend.database.session
python -m backend.models.trainer
```

### Step 3: Configure Systemd Service Units

Create `/etc/systemd/system/qr-fraud-api.service`:
```ini
[Unit]
Description=QR Payment Fraud Detection FastAPI Gateway
After=network.target

[Service]
Type=simple
User=qruser
Group=qruser
WorkingDirectory=/opt/qr-fraud
EnvironmentFile=/opt/qr-fraud/.env
ExecStart=/opt/qr-fraud/venv/bin/uvicorn backend.api.server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now qr-fraud-api
```

---

## 5. Reverse Proxy Configuration (Nginx)

To terminate TLS/SSL and provide rate limiting:

```nginx
upstream api_gateway {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream streamlit_ui {
    server 127.0.0.1:8501;
}

server {
    listen 443 ssl http2;
    server_name fraud-shield.bank.internal;

    ssl_certificate /etc/ssl/certs/fraud_shield.crt;
    ssl_certificate_key /etc/ssl/private/fraud_shield.key;

    # Inference API Gateway
    location /api/ {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_read_timeout 15s;
    }

    # Monitoring Dashboard
    location / {
        proxy_pass http://streamlit_ui;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 6. Rollback Procedures

If an anomalous regression occurs in production:
1. **Containerized Rollback:**
   ```bash
   docker compose -f deployment/docker-compose.yml down
   git checkout <PREVIOUS_STABLE_COMMIT_OR_TAG>
   docker compose -f deployment/docker-compose.yml up -d --build
   ```
2. **Database State Rollback:**
   Restore database snapshot via automated recovery utility:
   ```bash
   python scripts/restore_database.py --backup-file database/backups/backup_PREVIOUS_STABLE.db.gz
   ```
3. Run post-rollback verification:
   ```bash
   python scripts/smoke_test.py --url http://localhost:8000
   ```
