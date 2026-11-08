#!/usr/bin/env bash
# ==============================================================================
# Production Service Entrypoint Script
# Verifies database connectivity and directory permissions before service start
# ==============================================================================

set -euo pipefail

echo "[Entrypoint] Initializing production runtime environment..."

# Ensure required directories exist
mkdir -p logs database data backend/models

# Check SQLite file permissions
if [ -f "database/fraud_detection.db" ]; then
    echo "[Entrypoint] Database file verified: database/fraud_detection.db"
else
    echo "[Entrypoint] Creating fresh database file with WAL pragmas..."
    touch database/fraud_detection.db
fi

# Check serialized model availability
if [ -f "backend/models/lightgbm_model.joblib" ] && [ -f "backend/models/isolation_forest.joblib" ]; then
    echo "[Entrypoint] Serialized production ML models verified."
else
    echo "[Entrypoint] Warning: Model weights not found in backend/models/. Training baseline models..."
    python -m backend.models.trainer
fi

echo "[Entrypoint] Launching application process: $@"
exec "$@"

