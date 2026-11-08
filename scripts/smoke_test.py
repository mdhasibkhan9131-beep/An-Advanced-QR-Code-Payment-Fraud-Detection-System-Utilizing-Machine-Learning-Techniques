"""
Post-Deployment Smoke Test Script.
Validates all critical workflows on the deployed application:
- Health check probe (/api/v1/health)
- Operational metrics telemetry (/api/v1/metrics)
- Routine legitimate payment evaluation (APPROVE verdict & sub-100ms latency)
- Quishing attack detection (BLOCK/CHALLENGE verdict & reason codes)
- Batch transaction evaluation (/api/v1/predict/batch)
- SHA-256 cryptographic audit ledger verification (/api/v1/ledger/verify)
"""

import os
import sys
import time
import argparse
import requests

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.api.server import create_app


def run_smoke_tests(base_url: str = None) -> bool:
    print("================================================================================")
    print("POST-DEPLOYMENT PRODUCTION SMOKE TEST SUITE")
    print(f"Target Environment: {'Live URL (' + base_url + ')' if base_url else 'In-Process TestClient'}")
    print("================================================================================")

    # Pre-warm ML container for immediate sub-100ms inference
    from backend.api.routes import get_model_container
    get_model_container()

    if base_url:
        client = requests.Session()
        is_live = True
        return _execute_smoke_suite(client, base_url, is_live)
    else:
        app = create_app()
        with TestClient(app) as client:
            return _execute_smoke_suite(client, None, False)


def _execute_smoke_suite(client, base_url: str, is_live: bool) -> bool:
    def get_url(path: str) -> str:
        return f"{base_url.rstrip('/')}{path}" if is_live else path

    passed_count = 0
    total_count = 6

    # Test 1: Health Check Probe
    print("\n[Smoke Test 1/6] Pinging Liveness & Readiness Probe (/api/v1/health)...")
    t0 = time.perf_counter()
    res = client.get(get_url("/api/v1/health"))
    lat = (time.perf_counter() - t0) * 1000
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    body = res.json()
    assert body["status"] == "HEALTHY", f"Unhealthy status: {body['status']}"
    assert body["database_status"] == "CONNECTED", f"Database disconnected: {body['database_status']}"
    print(f"  -> PASS (HTTP 200, status={body['status']}, db={body['database_status']}, {lat:.2f}ms)")
    passed_count += 1

    # Test 2: Operational Metrics
    print("\n[Smoke Test 2/6] Verifying Operational Telemetry (/api/v1/metrics)...")
    res = client.get(get_url("/api/v1/metrics"))
    assert res.status_code == 200
    body = res.json()
    assert body["system_status"] == "HEALTHY"
    print(f"  -> PASS (HTTP 200, active_model={body['active_model']})")
    passed_count += 1

    # Test 3: Routine Legitimate Payment
    print("\n[Smoke Test 3/6] Evaluating Routine Legitimate Payment (/api/v1/predict)...")
    now_ms = int(time.time() * 1000)
    routine_payload = {
        "transaction_id": f"smoke-routine-{now_ms}",
        "timestamp": now_ms,
        "payer_id": "PAYER_SMOKE_USER",
        "merchant_id": "MCH_5411_GROCERY",
        "qr_type": 0,
        "qr_payload": "00020101021126580014bd.bkash.b2b0110MCH_5411_GROCERY520454115303050",
        "amount": 320.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 23.7812,
        "merchant_longitude": 90.4155,
        "device_trust_score": 0.95,
        "scan_to_pay_latency_ms": 4200,
        "failed_pin_attempts": 0,
    }
    t0 = time.perf_counter()
    res = client.post(get_url("/api/v1/predict"), json=routine_payload)
    lat = (time.perf_counter() - t0) * 1000
    assert res.status_code == 200
    body = res.json()
    assert body["verdict"] == "APPROVE"
    assert body["composite_score"] < 0.30
    assert len(body["ledger_block_hash"]) == 64
    assert lat < 100.0, f"SLA Violation: {lat:.2f}ms"
    print(f"  -> PASS (Verdict: {body['verdict']}, Score: {body['composite_score']:.4f}, Latency: {lat:.2f}ms < 100ms)")
    passed_count += 1

    # Test 4: Quishing Attack Vector
    print("\n[Smoke Test 4/6] Evaluating Sticker Replacement Quishing Attack Vector...")
    quish_payload = {
        "transaction_id": f"smoke-quishing-{now_ms}",
        "timestamp": now_ms,
        "payer_id": "PAYER_SMOKE_VICTIM",
        "merchant_id": "MCH_ROGUE_STIKER",
        "qr_type": 0,
        "qr_payload": "https://secure-qr.bkash-auth.net/pay/v2?redirect=login&session=7f9a8b1c4e2d3f0a9b8c7d6e5f4a3b2c1d0e9f8a",
        "amount": 450.0,
        "merchant_category_code": 5411,
        "payer_latitude": 23.7808,
        "payer_longitude": 90.4152,
        "merchant_latitude": 24.8949,  # Remote displacement (~150km away)
        "merchant_longitude": 91.8687,
        "device_trust_score": 0.88,
        "scan_to_pay_latency_ms": 5500,
        "failed_pin_attempts": 0,
    }
    res = client.post(get_url("/api/v1/predict"), json=quish_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["verdict"] in ["BLOCK", "CHALLENGE_MFA"]
    assert len(body["reason_codes"]) > 0
    print(f"  -> PASS (Verdict: {body['verdict']}, Score: {body['composite_score']:.4f}, Reasons: {body['reason_codes']})")
    passed_count += 1

    # Test 5: Batch Clearing Endpoint
    print("\n[Smoke Test 5/6] Testing Batch Clearance Processing (/api/v1/predict/batch)...")
    batch = [
        {
            "transaction_id": f"smoke-batch-{now_ms}-{i}",
            "timestamp": now_ms,
            "payer_id": f"PAYER_BATCH_{i}",
            "merchant_id": "MCH_5411",
            "qr_type": 0,
            "qr_payload": "00020101021126580014bd.bkash.b2b",
            "amount": 100.0 * (i + 1),
            "merchant_category_code": 5411,
            "payer_latitude": 23.7808,
            "payer_longitude": 90.4152,
            "merchant_latitude": 23.7810,
            "merchant_longitude": 90.4154,
            "device_trust_score": 0.90,
            "scan_to_pay_latency_ms": 3000,
            "failed_pin_attempts": 0,
        }
        for i in range(2)
    ]
    res = client.post(get_url("/api/v1/predict/batch"), json=batch)
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 2
    print(f"  -> PASS (Processed {len(body)} batch transactions successfully)")
    passed_count += 1

    # Test 6: Cryptographic Audit Ledger Integrity
    print("\n[Smoke Test 6/6] Auditing SHA-256 Ledger Blockchain (/api/v1/ledger/verify)...")
    res = client.get(get_url("/api/v1/ledger/verify"))
    assert res.status_code == 200
    body = res.json()
    assert body["is_valid"] is True
    assert body["total_blocks"] >= 1
    print(f"  -> PASS (Status: {body['status']}, Verified {body['total_blocks']} sequential blocks)")
    passed_count += 1

    print("\n================================================================================")
    print(f"SMOKE TEST SUMMARY: {passed_count}/{total_count} WORKFLOWS PASSED (100% SUCCESS)")
    print("APPLICATION IS HEALTHY, OPERATIONAL, AND READY FOR TRAFFIC!")
    print("================================================================================")
    return True


def main():
    parser = argparse.ArgumentParser(description="Post-Deployment Smoke Test Runner")
    parser.add_argument("--url", default=None, help="Base URL of deployed API gateway (e.g. http://localhost:8000)")
    args = parser.parse_args()

    try:
        success = run_smoke_tests(base_url=args.url)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n[Smoke Test FAILURE] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
