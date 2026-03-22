"""
Cynco API Quickstart -- 06: Reports

Demonstrates how to pull accounting reports from the Cynco API.
Fetches a trial balance and formats it as a readable table.

Run: python 06_reports.py
"""

import os
import sys
from datetime import date

import requests

API_KEY: str = os.environ.get("CYNCO_API_KEY", "")
BASE_URL: str = "https://app.cynco.io/api/v1"

if not API_KEY:
    print("Missing CYNCO_API_KEY environment variable.")
    print("Set it with: export CYNCO_API_KEY='cak_your_api_key_here'")
    sys.exit(1)

headers: dict[str, str] = {
    "Authorization": f"Bearer {API_KEY}",
}


def format_amount(cents: int, currency: str) -> str:
    """
    Format a monetary value from cents to a readable string.
    Cynco API returns all monetary values in the smallest currency unit.
    """
    value = abs(cents) / 100
    return f"{currency} {value:>12,.2f}"


def main() -> None:
    """Fetch and display a trial balance report."""

    # Fetch the trial balance as of today.
    # You can pass any date for historical reporting.
    today: str = date.today().isoformat()

    response = requests.get(
        f"{BASE_URL}/reports/trial-balance",
        headers=headers,
        params={"asOf": today},
        timeout=30,
    )

    if response.status_code == 401:
        print("Invalid API key. Check your CYNCO_API_KEY environment variable.")
        sys.exit(1)

    response.raise_for_status()

    body: dict = response.json()
    report: dict = body["data"]
    currency: str = report["currency"]
    accounts: list[dict] = report["accounts"]
    totals: dict = report["totals"]

    # Print the report header.
    width: int = 78
    print(f"\nTrial Balance as of {today}")
    print("=" * width)

    # Column headers.
    print(
        f"{'Code':<8} {'Account':<30} {'Debit':>18} {'Credit':>18}"
    )
    print("-" * width)

    # Print each account line.
    for account in accounts:
        debit_str = format_amount(account["debit"], currency) if account["debit"] > 0 else ""
        credit_str = format_amount(account["credit"], currency) if account["credit"] > 0 else ""

        print(
            f"{account['code']:<8} "
            f"{account['name']:<30} "
            f"{debit_str:>18} "
            f"{credit_str:>18}"
        )

    # Print totals.
    print("-" * width)

    total_debit = format_amount(totals["debit"], currency)
    total_credit = format_amount(totals["credit"], currency)

    print(
        f"{'':8} {'TOTAL':<30} {total_debit:>18} {total_credit:>18}"
    )
    print("=" * width)

    # Verify the trial balance.
    if totals["debit"] == totals["credit"]:
        print("\nTrial balance is in balance.")
    else:
        difference = abs(totals["debit"] - totals["credit"])
        diff_str = format_amount(difference, currency)
        print(f"\nWARNING: Trial balance is out of balance by {diff_str}")

    # Other available reports:
    #
    # Profit & Loss:
    #   GET /reports/profit-loss?from=2026-01-01&to=2026-03-31
    #
    # Balance Sheet:
    #   GET /reports/balance-sheet?asOf=2026-03-31
    #
    # Aged Receivables:
    #   GET /reports/aged-receivables?asOf=2026-03-31


if __name__ == "__main__":
    main()
