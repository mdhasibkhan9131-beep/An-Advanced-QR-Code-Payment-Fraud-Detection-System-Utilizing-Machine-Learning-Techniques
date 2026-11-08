# Production Deployment & Operations Guide

Refer to `docs/10_Deployment/DEPLOYMENT_GUIDE.md` for full detailed instructions and architecture diagrams.

## Quickstart (Docker Compose)

```bash
# 1. Setup production environment
cp deployment/prod.env.example .env

# 2. Launch container stack
docker compose -f deployment/docker-compose.yml up -d --build

# 3. Verify health
curl -f http://localhost:8000/api/v1/health

# 4. Run post-deployment smoke test
python scripts/smoke_test.py --url http://localhost:8000
```
