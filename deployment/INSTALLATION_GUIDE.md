# Software Installation & Setup Guide

Refer to `docs/10_Deployment/INSTALLATION_GUIDE.md` for full detailed instructions.

## Quick Installation

```bash
# 1. Virtual Environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1

# 2. Dependencies
pip install -r requirements.txt

# 3. Initialize Database & Models
python -c "from backend.database.session import init_db; init_db()"
python -m backend.models.trainer

# 4. Run Smoke Test
python scripts/smoke_test.py
```
