from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import logging


@dataclass
class EmailResult:
    success: bool
    message: str
    payload: Dict[str, Any] | None = None


class MockEmailClient:
    """
    Mock email sender.

    For the purposes of this assignment we log the email instead of
    really sending it. Failures are simulated for obviously invalid
    addresses or test patterns.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(__name__)

    def send_welcome_email(self, lead: Dict[str, Any]) -> EmailResult:
        name = str(lead.get("Name", "") or "").strip() or "there"
        email = str(lead.get("Email", "") or "").strip()

        if not email or "@" not in email:
            return EmailResult(success=False, message="Invalid email address.", payload={"lead": lead})

        if "bounce" in email.lower():
            return EmailResult(success=False, message="Simulated email bounce.", payload={"lead": lead})

        subject = "Welcome to our service"
        body = f"Hi {name},\n\nThank you for your interest. We will be in touch shortly.\n"

        self._logger.info("Sending welcome email", extra={"email": email, "subject": subject, "body": body})

        return EmailResult(success=True, message="Welcome email logged as sent.", payload={"lead": lead})

