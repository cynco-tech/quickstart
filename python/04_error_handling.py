"""
Cynco API Quickstart -- 04: Error Handling

Demonstrates how to handle every error type the Cynco API can return:
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Validation Error
- 429 Rate Limited
- 5xx Server Error

Also includes a production-ready retry utility with exponential backoff.

Run: python 04_error_handling.py
"""

import os
import sys
import time
from typing import Any, Callable, TypeVar

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

T = TypeVar("T")


class CyncoAPIError(Exception):
    """Base error for Cynco API responses."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        request_id: str | None = None,
        details: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.request_id = request_id
        self.details = details or []


def handle_response(response: requests.Response) -> dict:
    """
    Parse a Cynco API response, raising typed exceptions for errors.
    Use this as a central response handler in your application.
    """
    # 2xx responses are successful.
    if response.ok:
        return response.json()

    # Parse the error body.
    try:
        body: dict = response.json()
        error: dict = body.get("error", {})
        meta: dict = body.get("meta", {})
    except ValueError:
        # Non-JSON error response (rare).
        raise CyncoAPIError(
            status_code=response.status_code,
            code="UNKNOWN",
            message=f"HTTP {response.status_code}: {response.text}",
        )

    raise CyncoAPIError(
        status_code=response.status_code,
        code=error.get("code", "UNKNOWN"),
        message=error.get("message", "Unknown error"),
        request_id=meta.get("requestId"),
        details=error.get("details"),
    )


def demonstrate_error_handling() -> None:
    """Show how to catch and handle different error types."""
    print("=== Error Handling Examples ===\n")

    # 1. Not Found (404) -- fetching a nonexistent resource.
    print("--- 404 Not Found ---")
    try:
        response = requests.get(
            f"{BASE_URL}/customers/cus_nonexistent",
            headers=headers,
            timeout=30,
        )
        result = handle_response(response)
        print(f"Customer: {result['data']['name']}")
    except CyncoAPIError as e:
        if e.status_code == 404:
            print(f"  Resource not found: {e.message}")
            print(f"  Request ID: {e.request_id}")
        else:
            print(f"  Unexpected error ({e.status_code}): {e.message}")
    print()

    # 2. Validation Error (422) -- sending invalid data.
    print("--- 422 Validation Error ---")
    try:
        response = requests.post(
            f"{BASE_URL}/customers",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "name": "",  # Name is required
                "email": "not-an-email",  # Invalid email format
            },
            timeout=30,
        )
        result = handle_response(response)
        print(f"Customer: {result['data']['name']}")
    except CyncoAPIError as e:
        if e.status_code == 422:
            print(f"  Validation failed: {e.message}")
            for detail in e.details:
                print(f"    {detail['field']}: {detail['message']}")
        else:
            print(f"  Unexpected error ({e.status_code}): {e.message}")
    print()

    # 3. Rate Limit (429) -- too many requests.
    print("--- 429 Rate Limit ---")
    print("  (Simulating rate limit handling)")
    print("  On a real 429, the response includes:")
    print("    Retry-After: <seconds until you can retry>")
    print("    X-RateLimit-Limit: <your tier limit>")
    print("    X-RateLimit-Remaining: 0")
    print("  Use the retry utility below to handle this automatically.")
    print()


def with_retry(
    fn: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> T:
    """
    Retry a function with exponential backoff.
    Retries on rate limits (429) and server errors (5xx).
    Does not retry client errors (4xx except 429).
    """
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except CyncoAPIError as e:
            is_last_attempt = attempt == max_retries

            if e.status_code == 429:
                # Rate limited -- use the Retry-After hint if available.
                if is_last_attempt:
                    raise
                delay = base_delay * (2 ** attempt)
                print(f"  Rate limited. Retrying in {delay:.1f}s...")
                time.sleep(delay)

            elif e.status_code >= 500:
                # Server error -- retry with backoff.
                if is_last_attempt:
                    raise
                delay = base_delay * (2 ** attempt)
                print(f"  Server error ({e.status_code}). Retrying in {delay:.1f}s...")
                time.sleep(delay)

            else:
                # Client error (4xx except 429) -- don't retry.
                raise

    # Unreachable, but satisfies the type checker.
    raise RuntimeError("Unreachable")


def demonstrate_retry() -> None:
    """Show the retry utility in action."""
    print("=== Retry with Backoff ===\n")

    def fetch_invoices() -> dict:
        response = requests.get(
            f"{BASE_URL}/invoices",
            headers=headers,
            params={"limit": 5},
            timeout=30,
        )
        return handle_response(response)

    try:
        result = with_retry(fetch_invoices, max_retries=3, base_delay=1.0)
        invoice_count = len(result["data"])
        print(f"Fetched {invoice_count} invoices with retry support.\n")
    except CyncoAPIError as e:
        print(f"All retries exhausted: {e.message}")
    except requests.RequestException as e:
        print(f"Network error: {e}")


def main() -> None:
    demonstrate_error_handling()
    demonstrate_retry()


if __name__ == "__main__":
    main()
