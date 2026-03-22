# Cynco API Quickstart -- Python

Complete Python examples using raw HTTP requests with the `requests` library. No SDK required.

---

## Prerequisites

- Python 3.10 or later
- A Cynco API key (get one from **Settings > API Keys** in your dashboard)

## Setup

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export CYNCO_API_KEY="cak_your_api_key_here"
```

## Running Examples

Each example is a standalone script. Run them individually:

```bash
# List invoices with filters
python 01_list_invoices.py

# Create a customer
python 02_create_customer.py

# Paginate through all records
python 03_pagination.py

# Error handling patterns
python 04_error_handling.py

# Webhook server (starts on port 3456)
python 05_webhooks.py

# Pull a trial balance report
python 06_reports.py
```

---

## Examples

### 01 -- List Invoices

Fetch a filtered, sorted, paginated list of invoices.

Key concepts:
- Setting the Authorization header
- Passing query parameters for filtering and sorting
- Reading the response envelope (`success`, `data`, `pagination`)
- Formatting monetary values (cents to display)

### 02 -- Create a Customer

Create a new customer record with full address details.

Key concepts:
- Sending JSON POST requests
- Idempotency keys for safe retries
- Handling 422 validation errors with field-level details

### 03 -- Pagination

Two approaches to iterating through large datasets:

1. **Offset-based pagination** -- manual loop with `limit` and `offset`
2. **Cursor-based pagination** -- generator function using `nextCursor` for consistent results

The generator pattern is recommended for production use -- it encapsulates the pagination logic and yields one record at a time, keeping memory usage constant regardless of dataset size.

### 04 -- Error Handling

Comprehensive error handling with a reusable `CyncoAPIError` class and `handle_response()` utility.

Covers every HTTP status the API returns:
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Validation Error (with field-level details)
- 429 Rate Limited
- 5xx Server Error

Also includes a `with_retry()` utility with exponential backoff for handling transient errors.

### 05 -- Webhooks

A Flask server that receives and verifies webhook events.

Key concepts:
- HMAC-SHA256 signature verification
- Timestamp validation to prevent replay attacks
- Constant-time comparison to prevent timing attacks
- Routing events by type
- Always returning 200 to acknowledge receipt

For local development, use [ngrok](https://ngrok.com/) to expose your server:

```bash
ngrok http 3456
```

Then add the ngrok URL as a webhook endpoint in **Settings > Webhooks**.

### 06 -- Reports

Pull a trial balance and format it as a readable table.

Key concepts:
- Fetching accounting reports with date parameters
- Formatting monetary values from cents
- Verifying that debits equal credits
- Other available reports: P&L, Balance Sheet, Aged Receivables

---

## HTTP Request Patterns

Since there is no Python SDK yet, here are the common patterns for making requests:

```python
import requests

API_KEY = os.environ["CYNCO_API_KEY"]
BASE_URL = "https://app.cynco.io/api/v1"

headers = {"Authorization": f"Bearer {API_KEY}"}

# GET with query parameters
response = requests.get(
    f"{BASE_URL}/invoices",
    headers=headers,
    params={"status": "sent", "limit": 20},
    timeout=30,
)

# POST with JSON body
response = requests.post(
    f"{BASE_URL}/customers",
    headers={**headers, "Content-Type": "application/json"},
    json={"name": "Acme Corp", "email": "billing@acme.com"},
    timeout=30,
)

# PATCH (partial update)
response = requests.patch(
    f"{BASE_URL}/vendors/ven_01k2p5r8t4",
    headers={**headers, "Content-Type": "application/json"},
    json={"email": "new@email.com"},
    timeout=30,
)

# DELETE
response = requests.delete(
    f"{BASE_URL}/items/itm_01m3q6s9u5",
    headers=headers,
    timeout=30,
)
```

Always set a `timeout` on every request. The default `requests` behavior is to wait indefinitely, which can hang your application.
