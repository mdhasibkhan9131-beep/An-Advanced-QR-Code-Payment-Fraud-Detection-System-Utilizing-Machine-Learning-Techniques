"""
Verifies development environment, Python version, dependencies, and settings.
"""

import sys
import pytest
from backend.config.settings import settings


def test_python_version():
    """Verify runtime Python version conforms to >= 3.10 and < 3.12."""
    major, minor = sys.version_info.major, sys.version_info.minor
    assert major == 3, "Must be Python 3"
    assert minor >= 10, "Python version must be >= 3.10"
    assert minor <= 12, "Python version must be < 3.12 for optimum ML compatibility"


def test_required_packages_importable():
    """Verify all core scientific, ML, and web libraries are importable."""
    import fastapi
    import uvicorn
    import pydantic
    import sqlalchemy
    import sklearn
    import lightgbm
    import imblearn
    import shap
    import pyod
    import torch
    import numpy
    import pandas
    import streamlit

    assert fastapi.__version__ is not None
    assert lightgbm.__version__ is not None
    assert imblearn.__version__ is not None
    assert shap.__version__ is not None
    assert streamlit.__version__ is not None


def test_settings_loaded():
    """Verify Pydantic settings are correctly initialized with defaults."""
    assert settings.PROJECT_NAME == "Advanced QR Code Payment Fraud Detection System"
    assert settings.VERSION == "0.1.0"
    assert settings.WEIGHT_SUPERVISED == 0.70
    assert settings.WEIGHT_ANOMALY == 0.30
    assert settings.THRESHOLD_APPROVE == 0.30
    assert settings.THRESHOLD_BLOCK == 0.70
    assert settings.TIMEOUT_CIRCUIT_BREAKER_MS == 120
