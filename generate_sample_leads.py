from __future__ import annotations

from datetime import datetime

import pandas as pd


def create_sample_leads(path: str = "leads.xlsx") -> None:
    today = datetime.today().strftime("%Y-%m-%d")
    data = [
        {
            "Name": "Alice Smith",
            "Email": "alice@example.com",
            "Phone": "555-0100",
            "Source": "Website",
            "Created Date": today,
        },
        {
            "Name": "Bob Johnson",
            "Email": "bob@example.com",
            "Phone": "555-0101",
            "Source": "Referral",
            "Created Date": today,
        },
        {
            "Name": "Charlie Fail",
            "Email": "charlie_fail@example.com",
            "Phone": "555-0102",
            "Source": "Event",
            "Created Date": today,
        },
        {
            "Name": "Diana Bounce",
            "Email": "diana_bounce@example.com",
            "Phone": "555-0103",
            "Source": "Ad Campaign",
            "Created Date": today,
        },
    ]
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    print(f"Sample leads written to {path}")


if __name__ == "__main__":
    create_sample_leads()

