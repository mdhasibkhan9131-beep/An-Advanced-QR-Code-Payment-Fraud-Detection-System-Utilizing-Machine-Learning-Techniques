# ==============================================================================
# Multi-Stage Production Dockerfile for Advanced QR Fraud Detection System
# Standard: Non-root execution, CPU-optimized PyTorch/LightGBM, Offline Capable
# ==============================================================================

FROM python:3.11-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies in virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------------------------
# Production Runtime Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Install essential runtime shared libraries (libgomp for LightGBM OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Create non-root system user and group
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Copy application source code and models
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY database/ ./database/
COPY deployment/ ./deployment/
COPY research/ ./research/
COPY pyproject.toml .

# Create persistent directories and set ownership
RUN mkdir -p logs database data backend/models && \
    chown -R appuser:appgroup /app

USER appuser

# Expose API gateway (8000) and Streamlit dashboard (8501)
EXPOSE 8000 8501

# Liveness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command launches FastAPI gateway with 4 workers
CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

