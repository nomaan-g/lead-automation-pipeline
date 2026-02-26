from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import random
import time


@dataclass
class CRMResult:
    success: bool
    message: str
    payload: Dict[str, Any] | None = None


class MockCRMClient:
    """
    Mock CRM integration.

    This simulates a per-lead API call and injects controlled failures
    (e.g. for emails containing 'fail') without raising, so the pipeline
    can continue processing remaining leads.
    """

    def __init__(self, failure_rate: float = 0.0, min_latency: float = 0.0, max_latency: float = 0.0) -> None:
        self.failure_rate = max(0.0, min(1.0, failure_rate))
        self.min_latency = max(0.0, min_latency)
        self.max_latency = max(self.min_latency, max_latency)

    def send_lead(self, lead: Dict[str, Any]) -> CRMResult:
        """
        "Send" a single lead to the CRM.

        Rules:
        - If email contains the word 'fail', this lead fails.
        - Otherwise, the optional failure_rate introduces random failures.
        - Simulated latency is added if configured.
        """
        email = str(lead.get("Email", "") or "")

        if self.max_latency > 0.0:
            delay = random.uniform(self.min_latency, self.max_latency)
            time.sleep(delay)

        if "fail" in email.lower():
            return CRMResult(success=False, message="Email flagged as failing test case.", payload={"lead": lead})

        if self.failure_rate > 0.0 and random.random() < self.failure_rate:
            return CRMResult(success=False, message="Random simulated CRM failure.", payload={"lead": lead})

        return CRMResult(success=True, message="Lead successfully stored in CRM.", payload={"lead": lead})

