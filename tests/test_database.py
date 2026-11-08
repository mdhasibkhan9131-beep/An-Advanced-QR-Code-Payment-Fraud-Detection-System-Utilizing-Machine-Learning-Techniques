"""
Tests database schema instantiation and basic CRUD operations.
"""

from sqlalchemy import text
from backend.database.models import TransactionRecord, LedgerBlock, ModelMetric


def test_database_tables_exist(db_session):
    """Verify core tables are created in the database schema."""
    result = db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
    table_names = [row[0] for row in result]

    assert "transactions" in table_names
    assert "ledger_blocks" in table_names
    assert "mfa_challenges" in table_names
    assert "model_metrics" in table_names
    assert "audit_events" in table_names


def test_transaction_record_insert(db_session):
    """Verify inserting and querying a transaction record."""
    tx = TransactionRecord(
        transaction_id="test-uuid-123456",
        timestamp=1731102000000,
        payer_hash="hashed_payer_abc123",
        merchant_id="MERCH_01",
        qr_type=1,
        qr_payload_entropy=3.85,
        amount=150.00,
        merchant_category_code=5411,
        payer_latitude=23.8103,
        payer_longitude=90.4125,
        merchant_latitude=23.8110,
        merchant_longitude=90.4130,
        haversine_distance_km=0.12,
        device_trust_score=0.98,
        scan_to_pay_latency_ms=2500,
        failed_pin_attempts=0,
        velocity_1h=1.0,
        velocity_ratio=0.5,
        amount_zscore=0.2,
        supervised_score=0.04,
        anomaly_score=0.06,
        composite_score=0.046,
        verdict="APPROVE",
        is_fallback=0
    )
    db_session.add(tx)
    db_session.commit()

    retrieved = db_session.query(TransactionRecord).filter_by(transaction_id="test-uuid-123456").first()
    assert retrieved is not None
    assert retrieved.amount == 150.00
    assert retrieved.verdict == "APPROVE"
