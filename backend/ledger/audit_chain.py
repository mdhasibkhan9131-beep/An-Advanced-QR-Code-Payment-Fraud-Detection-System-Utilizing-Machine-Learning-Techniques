"""
Cryptographic append-only block-chained audit ledger.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md and FR-AUD-001, FR-AUD-003.
Provides SHA-256 parent hash chaining and mathematical tamper verification.
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.database.models import LedgerBlock, TransactionRecord
from backend.utils.security import generate_transaction_signature


GENESIS_HASH = "0" * 64


class CryptographicAuditLedger:
    """
    Maintains an append-only cryptographic audit trail linking every fraud evaluation
    verdict to its predecessor via SHA-256 block hashing.
    """

    def compute_block_hash(
        self,
        prev_hash: str,
        transaction_id: str,
        composite_score: float,
        verdict: str,
        timestamp: int,
        reason_codes: str,
        state_signature: str,
    ) -> str:
        """
        Computes deterministic SHA-256 digest of block payload:
        H_i = SHA256(H_{i-1} || TxID || S_comp || Verdict || Timestamp || Reasons || Sig)
        """
        raw_str = (
            f"{prev_hash}|{transaction_id}|{composite_score:.4f}|"
            f"{verdict}|{timestamp}|{reason_codes}|{state_signature}"
        )
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def append_block(
        self,
        db: Session,
        transaction_id: str,
        composite_score: float,
        verdict: str,
        timestamp: int,
        reason_codes: List[str],
    ) -> LedgerBlock:
        """
        Appends a new immutable block to the chain in the database.
        """
        # Retrieve latest block hash to establish parent link
        latest_block = (
            db.query(LedgerBlock)
            .order_by(LedgerBlock.block_id.desc())
            .first()
        )
        prev_hash = latest_block.block_hash if latest_block else GENESIS_HASH

        reasons_str = json.dumps(reason_codes)
        state_sig = generate_transaction_signature(
            payload={"transaction_id": transaction_id, "timestamp": timestamp, "score": composite_score}
        )

        block_hash = self.compute_block_hash(
            prev_hash=prev_hash,
            transaction_id=transaction_id,
            composite_score=composite_score,
            verdict=verdict,
            timestamp=timestamp,
            reason_codes=reasons_str,
            state_signature=state_sig,
        )

        new_block = LedgerBlock(
            prev_hash=prev_hash,
            block_hash=block_hash,
            transaction_id=transaction_id,
            composite_score=float(composite_score),
            verdict=verdict,
            timestamp=int(timestamp),
            reason_codes=reasons_str,
            state_signature=state_sig,
        )

        db.add(new_block)
        db.commit()
        db.refresh(new_block)
        return new_block

    def verify_integrity(self, db: Session) -> Dict[str, Any]:
        """
        Audits entire chain sequentially to verify parent hash links and hash integrity.
        Detects any database row tampering or out-of-order mutations.
        """
        blocks = db.query(LedgerBlock).order_by(LedgerBlock.block_id.asc()).all()

        if not blocks:
            return {
                "is_valid": True,
                "total_blocks": 0,
                "status": "EMPTY_CHAIN",
                "message": "Audit chain is empty; 0 transactions recorded.",
            }

        expected_prev_hash = GENESIS_HASH

        for idx, block in enumerate(blocks):
            # Check 1: Parent link integrity
            if block.prev_hash != expected_prev_hash:
                return {
                    "is_valid": False,
                    "tampered_block_id": block.block_id,
                    "transaction_id": block.transaction_id,
                    "status": "PARENT_HASH_BROKEN",
                    "error": (
                        f"Block {block.block_id} prev_hash mismatch: "
                        f"expected {expected_prev_hash}, got {block.prev_hash}"
                    ),
                }

            # Check 2: Content hash recalculation
            recalculated_hash = self.compute_block_hash(
                prev_hash=block.prev_hash,
                transaction_id=block.transaction_id,
                composite_score=block.composite_score,
                verdict=block.verdict,
                timestamp=block.timestamp,
                reason_codes=block.reason_codes,
                state_signature=block.state_signature,
            )

            if recalculated_hash != block.block_hash:
                return {
                    "is_valid": False,
                    "tampered_block_id": block.block_id,
                    "transaction_id": block.transaction_id,
                    "status": "PAYLOAD_TAMPERED",
                    "error": (
                        f"Block {block.block_id} payload altered: "
                        f"stored {block.block_hash}, recomputed {recalculated_hash}"
                    ),
                }

            expected_prev_hash = block.block_hash

        return {
            "is_valid": True,
            "total_blocks": len(blocks),
            "latest_block_hash": blocks[-1].block_hash,
            "status": "CHAIN_INTEGRITY_VERIFIED",
            "message": f"Successfully verified unbroken cryptographic chain across {len(blocks)} blocks.",
        }


# Global ledger instance
ledger_instance = CryptographicAuditLedger()
