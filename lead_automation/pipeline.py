from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import logging

from .cleanup import clean_leads, CleanupStats
from .crm import MockCRMClient, CRMResult
from .emailer import MockEmailClient, EmailResult
from .reporting import PipelineStats, write_report


logger = logging.getLogger(__name__)


def run_pipeline(
    input_excel: Path,
    cleaned_excel: Path,
    report_path: Path,
    crm_client: MockCRMClient | None = None,
    email_client: MockEmailClient | None = None,
) -> PipelineStats:
    """
    Run the full lead processing pipeline:
    - cleanup (Excel -> cleaned Excel)
    - CRM insertion per lead
    - welcome email after each successful CRM insert
    - summary reporting
    """
    crm_client = crm_client or MockCRMClient()
    email_client = email_client or MockEmailClient(logger=logger)

    cleaned_df, cleanup_stats = clean_leads(input_excel, cleaned_excel)

    stats = PipelineStats(cleanup=cleanup_stats)

    records = cleaned_df.to_dict(orient="records")

    for idx, lead in enumerate(records, start=1):
        logger.info("Processing lead", extra={"index": idx, "email": lead.get("Email")})

        crm_result: CRMResult = crm_client.send_lead(lead)
        if crm_result.success:
            stats.successful_crm_updates += 1
        else:
            stats.failed_crm_updates += 1
            logger.warning("CRM failed for lead", extra={"index": idx, "reason": crm_result.message})
            continue

        email_result: EmailResult = email_client.send_welcome_email(lead)
        if email_result.success:
            stats.emails_sent += 1
        else:
            stats.email_failures += 1
            logger.warning("Email failed for lead", extra={"index": idx, "reason": email_result.message})

    write_report(stats, report_path)

    return stats

