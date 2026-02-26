from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


@dataclass
class CleanupStats:
    total_raw_leads: int = 0
    leads_skipped_missing_email: int = 0
    duplicates_removed: int = 0

    @property
    def leads_skipped(self) -> int:
        return self.leads_skipped_missing_email


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map: Dict[str, str] = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in {"name"}:
            rename_map[col] = "Name"
        elif key in {"email", "e-mail"}:
            rename_map[col] = "Email"
        elif key in {"phone", "phone number", "mobile"}:
            rename_map[col] = "Phone"
        elif key in {"source"}:
            rename_map[col] = "Source"
        elif key in {"created date", "created_at", "created"}:
            rename_map[col] = "Created Date"
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def clean_leads(input_path: Path, output_path: Path) -> Tuple[pd.DataFrame, CleanupStats]:
    df = pd.read_excel(input_path)
    df = _normalise_columns(df)

    # Trim whitespace from all string-like cells in a way that works across
    # pandas versions (some deprecate/remove DataFrame.applymap).
    df = df.apply(lambda col: col.map(lambda v: v.strip() if isinstance(v, str) else v))

    stats = CleanupStats()
    stats.total_raw_leads = len(df)

    if "Email" not in df.columns:
        raise ValueError("Expected 'Email' column in input leads file.")

    email_series = df["Email"].astype("string")
    has_email_mask = email_series.notna() & email_series.str.strip().ne("")

    df_with_email = df[has_email_mask].copy()
    stats.leads_skipped_missing_email = stats.total_raw_leads - len(df_with_email)

    before_dedup = len(df_with_email)
    df_dedup = df_with_email.drop_duplicates(subset=["Email"], keep="first")
    stats.duplicates_removed = before_dedup - len(df_dedup)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_dedup.to_excel(output_path, index=False)

    return df_dedup, stats
