"""
Pytest integration wrapper for post-deployment smoke test suite.
"""

import pytest
from scripts.smoke_test import run_smoke_tests


def test_post_deployment_smoke_suite():
    """Executes full post-deployment workflow smoke test suite."""
    assert run_smoke_tests(base_url=None) is True

