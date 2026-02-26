from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json

from .cleanup import CleanupStats


@dataclass
class PipelineStats:
    cleanup: CleanupStats
    successful_crm_updates: int = 0
    failed_crm_updates: int = 0
    emails_sent: int = 0
    email_failures: int = 0

    def to_dict(self) -> Dict[str, Any]:
        base: Dict[str, Any] = {
            "total_raw_leads": self.cleanup.total_raw_leads,
            "leads_skipped": self.cleanup.leads_skipped,
            "duplicates_removed": self.cleanup.duplicates_removed,
            "final_processed_leads": self.final_processed_leads,
            "successful_crm_updates": self.successful_crm_updates,
            "failed_crm_updates": self.failed_crm_updates,
            "emails_sent": self.emails_sent,
            "email_failures": self.email_failures,
        }
        return base

    @property
    def final_processed_leads(self) -> int:
        return self.successful_crm_updates


def write_report(stats: PipelineStats, output_path: Path) -> None:
    """
    Persist the summary report as JSON and a simple HTML dashboard.
    """
    data = stats.to_dict()

    # JSON output (existing behaviour)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # HTML dashboard next to the JSON (e.g. report.html)
    html_path = output_path.with_suffix(".html")
    max_value = max(data.values()) if data else 1

    rows = []
    for key, value in data.items():
        width_pct = 0 if max_value == 0 else int((value / max_value) * 100)
        rows.append(
            f"""
        <tr>
          <td class="metric-name">{key}</td>
          <td class="metric-value">{value}</td>
          <td>
            <div class="bar-bg">
              <div class="bar-fill" style="width: {width_pct}%;"></div>
            </div>
          </td>
        </tr>
        """
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Lead Pipeline Report</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e5e7eb;
      margin: 0;
      padding: 2rem;
    }}
    .card {{
      max-width: 720px;
      margin: 0 auto;
      background: radial-gradient(circle at top left, #1d4ed8, #020617);
      border-radius: 1rem;
      padding: 1.75rem 2rem;
      box-shadow: 0 24px 60px rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.35);
    }}
    h1 {{
      margin-top: 0;
      font-size: 1.8rem;
      letter-spacing: 0.04em;
    }}
    .subtitle {{
      color: #9ca3af;
      margin-bottom: 1.5rem;
      font-size: 0.95rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 0.75rem;
    }}
    th, td {{
      padding: 0.4rem 0.35rem;
      font-size: 0.9rem;
    }}
    th {{
      text-align: left;
      color: #9ca3af;
      border-bottom: 1px solid rgba(148, 163, 184, 0.35);
      font-weight: 500;
    }}
    .metric-name {{
      text-transform: capitalize;
    }}
    .metric-value {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      color: #e5e7eb;
    }}
    .bar-bg {{
      width: 100%;
      height: 0.5rem;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.9);
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #22c55e, #a3e635);
    }}
    .footer {{
      margin-top: 1.25rem;
      font-size: 0.8rem;
      color: #6b7280;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Lead Pipeline Summary</h1>
    <div class="subtitle">Overview of today&apos;s processed leads.</div>
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>Value</th>
          <th>Relative</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
    <div class="footer">
      Opened from <code>{output_path.name}</code>. Refresh after each run to see updated numbers.
    </div>
  </div>
</body>
</html>
"""

    html_path.write_text(html, encoding="utf-8")

