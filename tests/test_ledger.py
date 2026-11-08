"""
Unit tests for Cryptographic Audit Ledger:
- SHA-256 block creation and parent hash chaining
- Ledger integrity audit on pristine chain
- Tamper detection when database rows are modified
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.session import Base
from backend.database.models import LedgerBlock, TransactionRecord
from backend.ledger.audit_chain import CryptographicAuditLedger, GENESIS_HASH


@pytest.fixture
def in_memory_db():
    """Provides isolated SQLite in-memory database for ledger tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_ledger_append_and_chaining(in_memory_db):
    """Verifies that blocks are chained sequentially with SHA-256 parent links."""
    ledger = CryptographicAuditLedger()

    # Block 1 (Parent must be GENESIS_HASH)
    b1 = ledger.append_block(
        db=in_memory_db,
        transaction_id="tx-001",
        composite_score=0.15,
        verdict="APPROVE",
        timestamp=1700000000000,
        reason_codes=[],
    )
    assert b1.block_id == 1
    assert b1.prev_hash == GENESIS_HASH
    assert len(b1.block_hash) == 64

    # Block 2 (Parent must be Block 1's block_hash)
    b2 = ledger.append_block(
        db=in_memory_db,
        transaction_id="tx-002",
        composite_score=0.85,
        verdict="BLOCK",
        timestamp=1700000005000,
        reason_codes=["GEOGRAPHIC_DISPLACEMENT_EXCEEDED"],
    )
    assert b2.block_id == 2
    assert b2.prev_hash == b1.block_hash

    # Verify chain integrity
    audit = ledger.verify_integrity(in_memory_db)
    assert audit["is_valid"] is True
    assert audit["total_blocks"] == 2
    assert audit["status"] == "CHAIN_INTEGRITY_VERIFIED"


def test_ledger_tamper_detection(in_memory_db):
    """
    CRITICAL SECURITY TEST (FR-AUD-003):
    Modifying any database field must trigger audit verification failure.
    """
    ledger = CryptographicAuditLedger()

    # Add 3 blocks
    for i in range(1, 4):
        ledger.append_block(
            db=in_memory_db,
            transaction_id=f"tx-00{i}",
            composite_score=0.10 * i,
            verdict="APPROVE",
            timestamp=1700000000000 + i * 1000,
            reason_codes=[],
        )

    # Initial check must pass
    assert ledger.verify_integrity(in_memory_db)["is_valid"] is True

    # Malicious tampering: adversary modifies composite_score of block 2 in database
    block2 = in_memory_db.query(LedgerBlock).filter(LedgerBlock.block_id == 2).first()
    block2.composite_score = 0.999  # Tampered score
    in_memory_db.commit()

    # Audit must detect tampering and report exact failure
    tamper_audit = ledger.verify_integrity(in_memory_db)
    assert tamper_audit["is_valid"] is False
    assert tamper_audit["tampered_block_id"] == 2
    assert tamper_audit["status"] == "PAYLOAD_TAMPERED"

