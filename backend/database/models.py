"""
SQLAlchemy ORM models conforming to DATABASE_DESIGN.md.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, BigInteger, Text,
    ForeignKey, DateTime, Index
)
from sqlalchemy.orm import relationship
from backend.database.session import Base


class TransactionRecord(Base):
    """Stores full feature and metadata records for incoming QR payment attempts."""
    __tablename__ = "transactions"

    transaction_id = Column(String(36), primary_key=True, index=True)
    timestamp = Column(BigInteger, nullable=False, index=True)
    payer_hash = Column(String(64), nullable=False, index=True)
    merchant_id = Column(String(32), nullable=False)
    qr_type = Column(Integer, nullable=False)  # 0: Static, 1: Dynamic
    qr_payload_entropy = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    merchant_category_code = Column(Integer, nullable=False)
    payer_latitude = Column(Float, nullable=False)
    payer_longitude = Column(Float, nullable=False)
    merchant_latitude = Column(Float, nullable=False)
    merchant_longitude = Column(Float, nullable=False)
    haversine_distance_km = Column(Float, nullable=False)
    device_trust_score = Column(Float, nullable=False)
    scan_to_pay_latency_ms = Column(Integer, nullable=False)
    failed_pin_attempts = Column(Integer, default=0, nullable=False)
    velocity_1h = Column(Float, nullable=False)
    velocity_ratio = Column(Float, nullable=False)
    amount_zscore = Column(Float, nullable=False)
    supervised_score = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    composite_score = Column(Float, nullable=False)
    verdict = Column(String(16), nullable=False, index=True)
    is_fallback = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ledger_block = relationship("LedgerBlock", back_populates="transaction", uselist=False)
    mfa_challenge = relationship("MFAChallenge", back_populates="transaction", uselist=False)


class LedgerBlock(Base):
    """Cryptographic append-only block linking verdict to parent SHA-256 hash."""
    __tablename__ = "ledger_blocks"

    block_id = Column(Integer, primary_key=True, autoincrement=True)
    prev_hash = Column(String(64), nullable=False, index=True)
    block_hash = Column(String(64), nullable=False, unique=True, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.transaction_id"), nullable=False, unique=True)
    composite_score = Column(Float, nullable=False)
    verdict = Column(String(16), nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    reason_codes = Column(Text, nullable=True)
    state_signature = Column(String(64), nullable=False)

    # Relationships
    transaction = relationship("TransactionRecord", back_populates="ledger_block")


class MFAChallenge(Base):
    """Tracks step-up authentication tokens for ambiguous transactions."""
    __tablename__ = "mfa_challenges"

    challenge_id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), ForeignKey("transactions.transaction_id"), nullable=False, unique=True)
    status = Column(String(16), default="PENDING", nullable=False, index=True)
    issued_at = Column(BigInteger, nullable=False)
    expires_at = Column(BigInteger, nullable=False)
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    transaction = relationship("TransactionRecord", back_populates="mfa_challenge")


class ModelMetric(Base):
    """Persists model benchmark scoreboard records."""
    __tablename__ = "model_metrics"

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(32), nullable=False, index=True)
    model_version = Column(String(16), nullable=False)
    recall = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    f2_score = Column(Float, nullable=False)
    pr_auc = Column(Float, nullable=False)
    p50_latency_ms = Column(Float, nullable=False)
    p95_latency_ms = Column(Float, nullable=False)
    p99_latency_ms = Column(Float, nullable=False)
    evaluated_at = Column(BigInteger, nullable=False)


class AuditEvent(Base):
    """Tracks operational events, tamper alerts, and retraining triggers."""
    __tablename__ = "audit_events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False)
    details = Column(Text, nullable=False)
    target_block_id = Column(Integer, nullable=True)
    performed_by = Column(String(32), default="SYSTEM", nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

