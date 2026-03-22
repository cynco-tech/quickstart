"""
Cynco API Quickstart -- 01: List Invoices

Demonstrates how to authenticate with the Cynco API and fetch
a filtered list of invoices using raw HTTP requests.

Run: python 01_list_invoices.py
"""

import os
import sys

import requests

# Read the API key from the environment.
API_KEY: str = os.environ.get("CYNCO_API_KEY", "")
BASE_URL: str = "https://app.cynco.io/api/v1"

if not API_KEY:
    print("Missing CYNCO_API_KEY environment variable.")
    print("Set it with: export CYNCO_API_KEY='cak_your_api_key_here'")
    sys.exit(1)

# All requests use the same Authorization header.
headers: dict[str, str] = {
    "Authorization": f"Bearer {API_KEY}",
}


def main() -> None:
    """List invoices with filters and display the results."""

    # Fetch sent invoices, sorted by due date (ascending), 10 per page.
    response = requests.get(
        f"{BASE_URL}/invoices",
        headers=headers,
        params={
            "status": "sent",
            "limit": 10,
            "sort": "dueDate",
            "order": "asc",
        },
        timeout=30,
    )

    # Raise an exception for HTTP errors (4xx, 5xx).
    response.raise_for_status()

    body: dict = response.json()

    # The response envelope always has: success, data, pagination, meta.
    pagination = body["pagination"]
    invoices: list[dict] = body["data"]

    print(f"Found {pagination['total']} sent invoices\n")

    for invoice in invoices:
        # Monetary values are in the smallest currency unit (e.g., cents).
        # Divide by 100 to get the display value.
        total = invoice["total"] / 100

        print(
            f"{invoice['invoiceNumber']} | "
            f"{invoice['customerName']} | "
            f"{invoice['currency']} {total:,.2f} | "
            f"Due: {invoice['dueDate']}"
        )

    if pagination["hasMore"]:
        remaining = pagination["total"] - len(invoices)
        print(f"\n... and {remaining} more")


if __name__ == "__main__":
    main()
