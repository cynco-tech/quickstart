"""
Cynco API Quickstart -- 02: Create a Customer

Demonstrates creating a new customer record with full address details,
including idempotency keys for safe retries and validation error handling.

Run: python 02_create_customer.py
"""

import os
import sys
import time

import requests

API_KEY: str = os.environ.get("CYNCO_API_KEY", "")
BASE_URL: str = "https://app.cynco.io/api/v1"

if not API_KEY:
    print("Missing CYNCO_API_KEY environment variable.")
    print("Set it with: export CYNCO_API_KEY='cak_your_api_key_here'")
    sys.exit(1)

headers: dict[str, str] = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def main() -> None:
    """Create a new customer with address details."""

    # Build the customer payload.
    customer_data: dict = {
        "name": "Acme Corp Sdn Bhd",
        "email": "billing@acme-corp.com.my",
        "phone": "+60123456789",
        "taxId": "C-1234567-X",
        "address": {
            "line1": "Level 15, Menara Acme",
            "line2": "123 Jalan Ampang",
            "city": "Kuala Lumpur",
            "state": "WP Kuala Lumpur",
            "postalCode": "50450",
            "country": "MY",
        },
    }

    # Include an idempotency key to make this request safe to retry.
    # If you send the same key again within 24 hours, the API returns
    # the original response without creating a duplicate.
    request_headers = {
        **headers,
        "Idempotency-Key": f"create-acme-corp-{int(time.time())}",
    }

    response = requests.post(
        f"{BASE_URL}/customers",
        headers=request_headers,
        json=customer_data,
        timeout=30,
    )

    # Handle validation errors specifically.
    if response.status_code == 422:
        body = response.json()
        error = body["error"]
        print(f"Validation failed: {error['message']}")
        for detail in error.get("details", []):
            print(f"  {detail['field']}: {detail['message']}")
        sys.exit(1)

    if response.status_code == 401:
        print("Invalid API key. Check your CYNCO_API_KEY environment variable.")
        sys.exit(1)

    # Raise for any other HTTP errors.
    response.raise_for_status()

    body = response.json()
    customer: dict = body["data"]

    print("Customer created successfully:\n")
    print(f"  ID:      {customer['id']}")
    print(f"  Name:    {customer['name']}")
    print(f"  Email:   {customer['email']}")
    print(f"  Phone:   {customer['phone']}")
    print(f"  Tax ID:  {customer['taxId']}")
    print(f"  City:    {customer['address']['city']}")
    print(f"  Created: {customer['createdAt']}")


if __name__ == "__main__":
    main()
