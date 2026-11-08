"""
Pydantic v2 schemas conforming to API_SPECIFICATION.md and SRS.md.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class HealthCheckResponse(BaseModel):
    """Liveness and readiness probe response schema."""
    status: str = Field(..., json_schema_extra={"example": "HEALTHY"})
    version: str = Field(..., json_schema_extra={"example": "0.1.0"})
    environment: str = Field(..., json_schema_extra={"example": "development"})
    database_status: str = Field(..., json_schema_extra={"example": "CONNECTED"})
    cache_backend: str = Field(..., json_schema_extra={"example": "memory"})
    timestamp_utc: str


class OperationalMetricsResponse(BaseModel):
    """System telemetry and model scoreboard response schema."""
    system_status: str
    active_model: str
    total_processed_transactions: int
    verdict_distribution: dict
    latency_metrics: dict
    accuracy_scoreboard: dict


class TransactionRequest(BaseModel):
    """Raw transaction ingestion payload with strict boundary validation."""
    transaction_id: str = Field(..., min_length=10, max_length=64, description="UUIDv4 identifier")
    timestamp: int = Field(..., gt=0, description="Epoch milliseconds")
    payer_id: str = Field(..., min_length=4, max_length=64, description="Payer customer account ID")
    merchant_id: str = Field(..., min_length=4, max_length=64, description="Registered merchant ID")
    qr_type: int = Field(..., ge=0, le=1, description="0: Static, 1: Dynamic")
    qr_payload: str = Field(..., min_length=1, max_length=1024, description="Decoded QR payload string")
    amount: float = Field(..., gt=0.0, le=1_000_000.0, description="Transaction monetary amount")
    merchant_category_code: int = Field(..., ge=1000, le=9999, description="ISO 18245 MCC")
    payer_latitude: float = Field(..., ge=-90.0, le=90.0, description="Payer device latitude")
    payer_longitude: float = Field(..., ge=-180.0, le=180.0, description="Payer device longitude")
    merchant_latitude: float = Field(..., ge=-90.0, le=90.0, description="Merchant POS latitude")
    merchant_longitude: float = Field(..., ge=-180.0, le=180.0, description="Merchant POS longitude")
    device_trust_score: float = Field(..., ge=0.0, le=1.0, description="Integrity score (0.0 to 1.0)")
    scan_to_pay_latency_ms: int = Field(..., ge=0, le=600_000, description="Elapsed optical scan ms")
    failed_pin_attempts: int = Field(default=0, ge=0, le=5, description="Failed PIN authorizations")

    @field_validator("amount")
    @classmethod
    def validate_positive_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be strictly positive.")
        return round(v, 2)


class TransactionResponse(BaseModel):
    """Structured fraud evaluation authorization verdict."""
    transaction_id: str
    timestamp: int
    verdict: str = Field(..., description="APPROVE | CHALLENGE_MFA | BLOCK")
    supervised_score: float
    anomaly_score: float
    composite_score: float
    is_zero_day_escalation: bool = False
    reason_codes: List[str] = Field(default_factory=list)
    ledger_block_hash: str
    response_time_ms: float
    is_fallback: bool = False


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class ProblemDetails(BaseModel):
    """RFC 7807 compliant standardized problem details error response."""
    error_code: str
    message: str
    status_code: int
    timestamp: int
    details: List[ErrorDetail] = Field(default_factory=list)
