from __future__ import annotations

from pathlib import Path
import tempfile

from flask import Flask, request, render_template_string

from lead_automation.pipeline import run_pipeline


app = Flask(__name__)


INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Lead Pipeline – Upload</title>
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #1d4ed8 0%, #020617 55%, #000000 100%);
      color: #e5e7eb;
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .shell {
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr);
      gap: 2rem;
      max-width: 960px;
      width: 100%;
      padding: 2.5rem 2.5rem;
      box-sizing: border-box;
    }
    .hero {
      padding-right: 1rem;
    }
    .logo {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.3rem 0.75rem;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.5);
      margin-bottom: 1rem;
      font-size: 0.8rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #9ca3af;
    }
    .logo-dot {
      width: 0.55rem;
      height: 0.55rem;
      border-radius: 999px;
      background: radial-gradient(circle, #22c55e, #15803d);
      box-shadow: 0 0 12px rgba(34, 197, 94, 0.9);
    }
    h1 {
      margin: 0 0 0.6rem 0;
      font-size: 2.1rem;
      letter-spacing: 0.04em;
    }
    .tagline {
      margin: 0 0 1.5rem 0;
      color: #9ca3af;
      font-size: 0.98rem;
      max-width: 28rem;
    }
    .steps {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.75rem;
      margin-top: 0.5rem;
    }
    .step {
      background: rgba(15, 23, 42, 0.75);
      border-radius: 0.85rem;
      padding: 0.7rem 0.8rem;
      border: 1px solid rgba(55, 65, 81, 0.8);
      font-size: 0.78rem;
    }
    .step-number {
      font-size: 0.7rem;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: #6b7280;
      margin-bottom: 0.25rem;
    }
    .step-title {
      font-weight: 600;
      margin-bottom: 0.15rem;
    }
    .step-body {
      color: #9ca3af;
      font-size: 0.78rem;
    }
    .card {
      background: rgba(15, 23, 42, 0.9);
      padding: 1.75rem 1.9rem;
      border-radius: 1.25rem;
      box-shadow: 0 24px 60px rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(148, 163, 184, 0.35);
      width: 100%;
      max-width: 420px;
    }
    .field-label {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #9ca3af;
      margin-bottom: 0.4rem;
    }
    .file-input {
      width: 100%;
      padding: 0.7rem 0.8rem;
      border-radius: 0.75rem;
      border: 1px dashed rgba(148, 163, 184, 0.6);
      background: rgba(15, 23, 42, 0.85);
      color: #e5e7eb;
      font-size: 0.9rem;
      box-sizing: border-box;
    }
    .file-input::file-selector-button {
      margin-right: 0.75rem;
      border: none;
      background: #1d4ed8;
      color: white;
      padding: 0.35rem 0.85rem;
      border-radius: 999px;
      cursor: pointer;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .file-input::file-selector-button:hover {
      background: #2563eb;
    }
    .button {
      margin-top: 1.25rem;
      width: 100%;
      padding: 0.75rem 1rem;
      border-radius: 999px;
      border: none;
      background: linear-gradient(90deg, #22c55e, #a3e635);
      color: #022c22;
      font-weight: 600;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      cursor: pointer;
    }
    .button:hover {
      filter: brightness(1.05);
    }
    .error {
      margin-top: 0.75rem;
      color: #fecaca;
      font-size: 0.85rem;
    }
    .hint {
      margin-top: 0.5rem;
      font-size: 0.8rem;
      color: #9ca3af;
    }
    .microcopy {
      margin-top: 0.75rem;
      font-size: 0.78rem;
      color: #6b7280;
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <div class="logo">
        <span class="logo-dot"></span>
        Lead Automation
      </div>
      <h1>Turn raw Excel leads into ready contacts.</h1>
      <p class="tagline">
        Upload the daily sales spreadsheet and we&apos;ll clean it, push to the mock CRM, trigger mock welcome emails, and give you a one‑view summary.
      </p>
      <div class="steps">
        <div class="step">
          <div class="step-number">Step 1</div>
          <div class="step-title">Clean data</div>
          <div class="step-body">Trim spaces, drop bad rows, remove duplicates.</div>
        </div>
        <div class="step">
          <div class="step-number">Step 2</div>
          <div class="step-title">Mock CRM</div>
          <div class="step-body">Send each lead individually &amp; track failures.</div>
        </div>
        <div class="step">
          <div class="step-number">Step 3</div>
          <div class="step-title">Mock email</div>
          <div class="step-body">Only after a successful CRM insert.</div>
        </div>
      </div>
    </div>
    <div class="card">
      <form method="post" enctype="multipart/form-data">
        <div class="field-label">Leads Excel file</div>
        <input class="file-input" type="file" name="file" accept=".xlsx" required />
        {% if error %}
          <div class="error">{{ error }}</div>
        {% endif %}
        <div class="hint">Expected columns: Name, Email, Phone, Source, Created Date.</div>
        <button type="submit" class="button">Run Pipeline</button>
        <div class="microcopy">This is a demo UI – no real CRM or email is called.</div>
      </form>
    </div>
  </div>
</body>
</html>
"""


RESULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Lead Pipeline – Summary</title>
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #1d4ed8 0%, #020617 55%, #000000 100%);
      color: #e5e7eb;
      min-height: 100vh;
      margin: 0;
      padding: 2rem 1.5rem;
      display: flex;
      justify-content: center;
    }
    .card {
      max-width: 720px;
      width: 100%;
      background: rgba(15, 23, 42, 0.95);
      border-radius: 1.25rem;
      padding: 1.75rem 2rem;
      box-shadow: 0 24px 60px rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(148, 163, 184, 0.35);
    }
    h1 {
      margin-top: 0;
      font-size: 1.7rem;
      letter-spacing: 0.04em;
    }
    .subtitle {
      color: #9ca3af;
      margin-bottom: 1.5rem;
      font-size: 0.95rem;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.75rem;
      margin-bottom: 1.25rem;
    }
    .pill {
      background: rgba(15, 23, 42, 0.85);
      border-radius: 0.9rem;
      padding: 0.55rem 0.7rem;
      border: 1px solid rgba(55, 65, 81, 0.85);
      font-size: 0.8rem;
    }
    .pill-label {
      color: #9ca3af;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      margin-bottom: 0.1rem;
    }
    .pill-value {
      font-variant-numeric: tabular-nums;
      font-weight: 600;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 0.75rem;
    }
    th, td {
      padding: 0.4rem 0.35rem;
      font-size: 0.9rem;
    }
    th {
      text-align: left;
      color: #9ca3af;
      border-bottom: 1px solid rgba(148, 163, 184, 0.35);
      font-weight: 500;
    }
    .metric-name {
      text-transform: capitalize;
    }
    .metric-value {
      text-align: right;
      font-variant-numeric: tabular-nums;
      color: #e5e7eb;
    }
    .bar-bg {
      width: 100%;
      height: 0.5rem;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.9);
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #22c55e, #a3e635);
    }
    .actions {
      margin-top: 1.4rem;
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
    }
    .button-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.55rem 1rem;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.6);
      color: #e5e7eb;
      font-size: 0.85rem;
      text-decoration: none;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .button-link.primary {
      background: rgba(15, 23, 42, 0.8);
    }
    .button-link:hover {
      border-color: #e5e7eb;
    }
    .footer {
      margin-top: 1rem;
      font-size: 0.78rem;
      color: #6b7280;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Lead Pipeline Summary</h1>
    <div class="subtitle">Here&apos;s how this upload performed.</div>
    <div class="summary-grid">
      {% for name, value, _ in metrics[:4] %}
      <div class="pill">
        <div class="pill-label">{{ name }}</div>
        <div class="pill-value">{{ value }}</div>
      </div>
      {% endfor %}
    </div>
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>Value</th>
          <th>Relative</th>
        </tr>
      </thead>
      <tbody>
        {% for name, value, width in metrics %}
        <tr>
          <td class="metric-name">{{ name }}</td>
          <td class="metric-value">{{ value }}</td>
          <td>
            <div class="bar-bg">
              <div class="bar-fill" style="width: {{ width }}%;"></div>
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <div class="actions">
      <a href="/" class="button-link primary">Upload another file</a>
    </div>
    <div class="footer">
      All operations are mocked for the assignment: CRM and email calls are simulated, not sent to real services.
    </div>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(INDEX_TEMPLATE, error=None)

    uploaded = request.files.get("file")
    if not uploaded or uploaded.filename == "":
        return render_template_string(INDEX_TEMPLATE, error="Please choose an Excel (.xlsx) file.")

    if not uploaded.filename.lower().endswith(".xlsx"):
        return render_template_string(INDEX_TEMPLATE, error="File must be an .xlsx Excel workbook.")

    # Save the uploaded Excel to a temporary directory
    tmp_dir = Path(tempfile.mkdtemp(prefix="leads_upload_"))
    input_path = tmp_dir / "leads.xlsx"
    uploaded.save(input_path)

    cleaned_path = tmp_dir / "cleaned_leads.xlsx"
    report_path = tmp_dir / "report.json"

    stats = run_pipeline(
        input_excel=input_path,
        cleaned_excel=cleaned_path,
        report_path=report_path,
    )

    data = stats.to_dict()
    max_value = max(data.values()) if data else 1
    metrics = []
    for key, value in data.items():
        width_pct = 0 if max_value == 0 else int((value / max_value) * 100)
        metrics.append((key.replace("_", " "), value, width_pct))

    return render_template_string(RESULT_TEMPLATE, metrics=metrics)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()
    app.run(debug=True, host=args.host, port=args.port)

