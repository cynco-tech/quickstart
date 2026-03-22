"""
Cynco API Quickstart -- 05: Webhook Signature Verification

Demonstrates how to receive and verify webhook events from Cynco
using Flask. The verification logic can be adapted to any Python
web framework.

Setup:
  1. Create a webhook endpoint in Settings > Webhooks
  2. Copy the signing secret (starts with whsec_)
  3. Set it as CYNCO_WEBHOOK_SECRET in your environment
  4. Point the webhook URL to your server (use ngrok for local dev)

Run: python 05_webhooks.py
"""

import hashlib
import hmac
import json
import os
import sys
import time

from flask import Flask, Response, request

app = Flask(__name__)

# The webhook signing secret from your Cynco dashboard.
WEBHOOK_SECRET: str = os.environ.get("CYNCO_WEBHOOK_SECRET", "")

if not WEBHOOK_SECRET:
    print("Missing CYNCO_WEBHOOK_SECRET environment variable.")
    print("Get it from Settings > Webhooks in your Cynco dashboard.")
    sys.exit(1)

# Maximum age of a webhook event (5 minutes).
# Events older than this are rejected to prevent replay attacks.
MAX_AGE_SECONDS: int = 300


def verify_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
) -> dict:
    """
    Verify the HMAC-SHA256 signature of a webhook event.

    The signature header format is: t=<timestamp>,v1=<signature>

    Steps:
      1. Parse the timestamp and signature from the header
      2. Check the timestamp is within the tolerance window
      3. Compute the expected signature: HMAC-SHA256(secret, timestamp.payload)
      4. Compare signatures using constant-time comparison

    Returns the parsed event payload if verification succeeds.
    Raises ValueError if verification fails.
    """
    # Parse the signature header.
    # Format: t=1711094460,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
    parts: dict[str, str] = {}
    for element in signature_header.split(","):
        key, _, value = element.partition("=")
        parts[key.strip()] = value.strip()

    timestamp_str = parts.get("t")
    signature = parts.get("v1")

    if not timestamp_str or not signature:
        raise ValueError("Invalid signature header format")

    # Check the timestamp to prevent replay attacks.
    try:
        timestamp = int(timestamp_str)
    except ValueError:
        raise ValueError("Invalid timestamp in signature header")

    age = abs(time.time() - timestamp)
    if age > MAX_AGE_SECONDS:
        raise ValueError(
            f"Webhook timestamp is too old ({int(age)}s). "
            f"Maximum age is {MAX_AGE_SECONDS}s."
        )

    # Compute the expected signature.
    # The signed payload is: "{timestamp}.{raw_body}"
    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks.
    if not hmac.compare_digest(expected, signature):
        raise ValueError("Signature verification failed")

    # Signature is valid -- parse and return the event.
    return json.loads(payload)


@app.route("/webhooks/cynco", methods=["POST"])
def handle_webhook() -> tuple[Response, int] | tuple[dict, int]:
    """Handle incoming webhook events from Cynco."""

    # Get the signature header.
    signature = request.headers.get("Cynco-Signature")
    if not signature:
        return {"error": "Missing Cynco-Signature header"}, 400

    # Get the raw request body (required for signature verification).
    payload: bytes = request.get_data()

    # Verify the signature.
    try:
        event: dict = verify_signature(payload, signature, WEBHOOK_SECRET)
    except ValueError as e:
        print(f"Webhook verification failed: {e}")
        return {"error": "Invalid signature"}, 400

    # The event is verified -- process it.
    event_type: str = event.get("type", "unknown")
    event_id: str = event.get("id", "unknown")
    data: dict = event.get("data", {})

    print(f"Received event: {event_type} ({event_id})")

    if event_type == "invoice.created":
        print(
            f"  Invoice {data.get('invoiceNumber')} created "
            f"for {data.get('customerName')}"
        )
        total = data.get("total", 0) / 100
        print(f"  Total: {data.get('currency')} {total:,.2f}")

    elif event_type == "invoice.paid":
        print(f"  Invoice {data.get('invoiceNumber')} paid!")
        total = data.get("total", 0) / 100
        print(f"  Amount: {data.get('currency')} {total:,.2f}")

    elif event_type == "invoice.overdue":
        print(f"  Invoice {data.get('invoiceNumber')} is overdue.")
        print(f"  Due date was: {data.get('dueDate')}")

    elif event_type == "customer.created":
        print(f"  New customer: {data.get('name')} ({data.get('email')})")

    elif event_type == "payment.received":
        amount = data.get("amount", 0) / 100
        print(
            f"  Payment received: {data.get('currency')} {amount:,.2f}"
        )
        print(f"  Method: {data.get('method')}")

    else:
        print(f"  Unhandled event type: {event_type}")

    # Always respond with 200 to acknowledge receipt.
    # Cynco retries with exponential backoff on non-2xx responses
    # (up to 3 retries over 24 hours).
    return {"received": True}, 200


def main() -> None:
    port = int(os.environ.get("PORT", "3456"))

    print(f"Webhook server listening on port {port}")
    print(f"\nEndpoint: POST http://localhost:{port}/webhooks/cynco")
    print("\nFor local development, expose this with ngrok:")
    print(f"  ngrok http {port}")
    print(
        "\nThen add the ngrok URL as a webhook endpoint in your Cynco dashboard."
    )

    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
