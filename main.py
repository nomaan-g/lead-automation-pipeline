from __future__ import annotations

from pathlib import Path
import argparse
import logging
import sys

from lead_automation.pipeline import run_pipeline


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        stream=sys.stdout,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily sales leads automation pipeline.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("leads.xlsx"),
        help="Path to raw leads Excel file (default: leads.xlsx in current directory).",
    )
    parser.add_argument(
        "--cleaned-output",
        type=Path,
        default=Path("cleaned_leads.xlsx"),
        help="Where to write the cleaned leads Excel file (default: cleaned_leads.xlsx).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("report.json"),
        help="Where to write the JSON summary report (default: report.json).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(verbose=args.verbose)

    try:
        stats = run_pipeline(
            input_excel=args.input,
            cleaned_excel=args.cleaned_output,
            report_path=args.report,
        )
    except FileNotFoundError as exc:
        print(f"Input Excel file not found: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error while running pipeline: {exc}", file=sys.stderr)
        return 1

    print("Pipeline completed successfully.")
    print(f"Summary report written to: {args.report}")
    print(
        f"Total raw leads: {stats.cleanup.total_raw_leads}, "
        f"Leads skipped: {stats.cleanup.leads_skipped}, "
        f"Duplicates removed: {stats.cleanup.duplicates_removed}, "
        f"Final processed leads: {stats.final_processed_leads}",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

