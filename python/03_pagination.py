"""
Cynco API Quickstart -- 03: Pagination

Demonstrates two approaches to paginating through large result sets:
1. Offset-based pagination (simple, good for known-size datasets)
2. Cursor-based pagination (consistent results during concurrent writes)

Run: python 03_pagination.py
"""

import os
import sys
from typing import Generator

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


def offset_pagination() -> None:
    """
    Approach 1: Offset-based pagination.
    You control the offset and limit yourself.
    """
    print("=== Offset-based Pagination ===\n")

    limit: int = 20
    offset: int = 0
    total: int = 0
    fetched: int = 0
    page: int = 0

    while True:
        response = requests.get(
            f"{BASE_URL}/invoices",
            headers=headers,
            params={
                "limit": limit,
                "offset": offset,
                "sort": "createdAt",
                "order": "desc",
            },
            timeout=30,
        )
        response.raise_for_status()

        body: dict = response.json()
        invoices: list[dict] = body["data"]
        pagination: dict = body["pagination"]

        total = pagination["total"]
        fetched += len(invoices)
        page += 1

        print(f"Page {page}: {len(invoices)} invoices ({fetched}/{total})")

        # Stop if there are no more pages.
        if not pagination["hasMore"]:
            break

        offset += limit

    print(f"\nDone. Fetched {fetched} invoices total.\n")


def iterate_all_invoices(
    status: str | None = None,
) -> Generator[dict, None, None]:
    """
    Approach 2: Generator that yields all invoices using cursor-based pagination.
    Encapsulates the pagination logic so callers just iterate.
    """
    cursor: str | None = None
    limit: int = 100

    while True:
        params: dict = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status

        response = requests.get(
            f"{BASE_URL}/invoices",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        body: dict = response.json()
        invoices: list[dict] = body["data"]
        pagination: dict = body["pagination"]

        for invoice in invoices:
            yield invoice

        # nextCursor is null/absent when there are no more pages.
        cursor = pagination.get("nextCursor")
        if cursor is None:
            break


def cursor_pagination() -> None:
    """Use the generator to process all paid invoices."""
    print("=== Cursor-based Pagination (Generator) ===\n")

    count: int = 0
    total_amount: int = 0

    for invoice in iterate_all_invoices(status="paid"):
        count += 1
        total_amount += invoice["total"]

        # Log progress every 50 invoices.
        if count % 50 == 0:
            print(f"  Processed {count} invoices so far...")

    display_total = total_amount / 100
    print(f"\nProcessed {count} paid invoices.")
    print(f"Total value: MYR {display_total:,.2f}\n")


def main() -> None:
    offset_pagination()
    cursor_pagination()


if __name__ == "__main__":
    main()
