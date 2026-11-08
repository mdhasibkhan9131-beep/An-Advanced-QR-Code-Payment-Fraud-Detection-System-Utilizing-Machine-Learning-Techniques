"""
Hybrid risk scoring aggregator and three-tier decision gating engine.
Conforms to docs/05_System_Design/LOW_LEVEL_DESIGN.md and FR-DEC-001, FR-DEC-002.
"""

from typing import Tuple, Dict, Any, Optional
import numpy as np

from backend.config.settings import settings


class HybridScorer:
    """
    Computes composite fraud risk score:
    S_comp = alpha * S_supervised + (1 - alpha) * S_anomaly
    """

    def __init__(self, alpha: float = settings.WEIGHT_SUPERVISED):
        self.alpha = float(alpha)

    def calculate_composite_score(
        self,
        supervised_score: float,
        anomaly_score: float,
        alpha_override: Optional[float] = None,
    ) -> float:
        """
        Calculates normalized composite risk score in [0.0, 1.0].
        """
        a = float(alpha_override if alpha_override is not None else self.alpha)
        s_sup = float(np.clip(supervised_score, 0.0, 1.0))
        s_ano = float(np.clip(anomaly_score, 0.0, 1.0))
        comp = (a * s_sup) + ((1.0 - a) * s_ano)
        return float(np.clip(round(comp, 4), 0.0, 1.0))


class DecisionGatingEngine:
    """
    Applies three-tier decision gating and zero-day anomaly escalation policy:
    1. S_comp < threshold_approve -> APPROVE
    2. threshold_approve <= S_comp < threshold_challenge -> CHALLENGE_MFA
    3. S_comp >= threshold_challenge -> BLOCK
    4. Override: If S_anomaly >= threshold_escalation, force CHALLENGE_MFA or BLOCK.
    """

    def __init__(
        self,
        threshold_approve: float = settings.THRESHOLD_APPROVE,
        threshold_challenge: float = settings.THRESHOLD_BLOCK,
        threshold_escalation: float = settings.ZERO_DAY_ANOMALY_ESCALATION,
    ):
        self.th_approve = float(threshold_approve)
        self.th_challenge = float(threshold_challenge)
        self.th_escalation = float(threshold_escalation)

    def evaluate_verdict(
        self,
        supervised_score: float,
        anomaly_score: float,
        composite_score: float,
    ) -> Tuple[str, bool, str]:
        """
        Evaluates final authorization verdict.
        
        Returns:
            Tuple[verdict (str), is_zero_day_escalation (bool), primary_policy (str)]
        """
        is_zero_day = False
        policy_note = "Standard Gating"

        # Baseline three-tier evaluation
        if composite_score >= self.th_challenge:
            verdict = "BLOCK"
        elif composite_score >= self.th_approve:
            verdict = "CHALLENGE_MFA"
        else:
            verdict = "APPROVE"

        # Zero-Day Anomaly Escalation Policy (FR-DEC-002)
        # If unseen novel attack causes low supervised score but extreme anomaly score:
        if anomaly_score >= self.th_escalation and verdict == "APPROVE":
            verdict = "CHALLENGE_MFA"
            is_zero_day = True
            policy_note = "Escalated from APPROVE to CHALLENGE_MFA by Zero-Day Anomaly Engine"
        elif anomaly_score >= (self.th_escalation + 0.10) and verdict == "CHALLENGE_MFA":
            verdict = "BLOCK"
            is_zero_day = True
            policy_note = "Escalated from CHALLENGE_MFA to BLOCK by Critical Outlier Engine"

        return verdict, is_zero_day, policy_note
