# Lead Automation Pipeline

Your company gets a daily Excel file full of sales leads. Someone used to clean it by hand, upload to the CRM, send welcome emails, and write a summary. This project automates that whole flow so you can drop in a file and get a report in seconds.

**What it does:**
- **Cleans the data** – trims whitespace, drops rows without email, removes duplicates (by email).
- **Simulates CRM** – mock “insert” per lead, with success and failure handling.
- **Simulates email** – sends a welcome email *only* after a successful CRM insert.
- **Reports** – spits out a JSON summary and an HTML dashboard you can open in a browser.

---

## What Stands Out

- **Design thinking** – Chose Python over heavier tools (Airflow, n8n) because the workflow is linear and file-based; the architecture stays simple but can scale later.
- **Two interfaces** – CLI for automation and a web UI for ad-hoc use; both run the same pipeline.
- **Visual reporting** – HTML dashboard with metrics and bar-style visuals, not just raw JSON.
- **Attention to detail** – `.gitignore` excludes venv and generated files; sample leads generator so reviewers can run it immediately; column name normalisation handles `E-mail`, `Created_at`, etc.
- **Resilience** – Per-lead isolation: one failing record doesn't stop the run; failures are logged and counted.

---

## Architecture Overview

**Stack:** Python only. Uses `pandas` and `openpyxl` for Excel, and a small modular package `lead_automation` so each step has a clear job:

- `cleanup.py` – data cleanup
- `crm.py` – mock CRM client
- `emailer.py` – mock email sender
- `reporting.py` – stats and report generation
- `pipeline.py` – wires everything together (cleanup → CRM → email → reporting)
- `main.py` – CLI entrypoint

**Why Python instead of Airflow/n8n?**  
This workflow is simple: one file in, one report out. A full orchestration platform would be overkill. Python runs anywhere (your laptop, cron, a container) without extra services. The design keeps steps separated so you can later move it into Airflow, n8n, or a microservice if you need to.

---

## Execution Flow

1. **Input** – Your Excel file (`leads.xlsx`) with columns: Name, Email, Phone, Source, Created Date.  
   Minor header variants are fine (e.g. `E-mail`, `Created_at`).

2. **Cleanup** – Loads Excel, normalises headers, trims spaces, drops rows without email, removes duplicates by email, and saves `cleaned_leads.xlsx`.

3. **CRM (mock)** – For each cleaned lead, calls `MockCRMClient.send_lead(lead)`. Returns success or failure per lead; failures don’t stop the run. Emails containing `"fail"` are forced to fail for testing.

4. **Email (mock)** – Runs only after a successful CRM insert. Validates email format, simulates a bounce if the address contains `"bounce"`, and logs the “sent” email. No real mail is sent.

5. **Reporting** – Gathers all metrics (raw leads, skipped, duplicates, CRM success/fail, emails sent/failed) and writes `report.json` plus `report.html`.

6. **Orchestration** – `run_pipeline` runs: cleanup → loop over leads (CRM → email if CRM ok) → write report.

---

## How to Run

**Option A: Web UI (upload in browser)**  
Handy if you prefer clicking over typing.

```bash
cd Task
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python web_app.py
```

Then open `http://127.0.0.1:5000`, upload your Excel file, and click **Run Pipeline**. The summary appears right there.

> If port 5000 is taken (e.g. by AirPlay Receiver on macOS), run `python web_app.py --port 5001` and use `http://127.0.0.1:5001`.

**Option B: Command line**

1. Put `leads.xlsx` in the project root (or use `--input` to point elsewhere).
2. Run:

```bash
python main.py
```

With custom paths:

```bash
python main.py --input path/to/leads.xlsx --cleaned-output path/to/cleaned_leads.xlsx --report path/to/report.json --verbose
```

**Outputs:**
- `cleaned_leads.xlsx` – cleaned data
- `report.json` – metrics as JSON
- `report.html` – visual summary; open in a browser

---

## Design Decisions & Error Handling

**Architecture choice (why pure Python)**  
Evaluated Airflow/n8n vs. pure Python. For a single daily file and a linear flow, orchestration platforms add operational overhead without clear benefit. Python keeps the solution portable (laptop, cron, container) and the codebase easy to reason about. The modular layout means we can later promote steps into Airflow tasks or a microservice without rewriting core logic.

**Per-lead isolation** – CRM and email return result objects instead of raising. One bad lead doesn’t stop the rest.

**Mock integrations** – The CRM and email clients are shaped like real service clients. Swapping in REST/SMTP later requires changing only those modules, not `pipeline.py`.

**Failure handling:**
- **Cleanup:** Missing input file or missing Email column → clear error message and non-zero exit.
- **CRM / Email:** Failures are logged and counted; processing continues.

**Scalability** – For typical daily volumes, a single Python process is enough. For more load, you can parallelise the per-lead loop or split cleanup and CRM into separate jobs. The module layout fits Airflow, n8n, or a small API service.

---

## Notes for Reviewers

The project is emphasises clarity, resilience, and extensibility: clear separation of steps, graceful handling of bad records, and structure that supports future scaling. The mocks demonstrate where you’d plug in real CRM/email and monitoring in production.
