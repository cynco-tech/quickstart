# Cynco API -- cURL Examples

Complete cURL reference for the Cynco API. No dependencies, no setup -- just copy, paste, and run.

---

## Prerequisites

Set your API key:

```bash
export CYNCO_API_KEY="cak_your_api_key_here"
```

All examples below use `$CYNCO_API_KEY` and pipe output through `jq` for readability. Install jq with `brew install jq` (macOS) or `apt install jq` (Linux) if you don't have it.

---

## Authentication

Every request requires the `Authorization` header:

```bash
curl -s https://app.cynco.io/api/v1/invoices \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

An invalid or missing key returns a `401`:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing API key"
  }
}
```

---

## List Invoices (GET)

```bash
curl -s https://app.cynco.io/api/v1/invoices \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": "inv_01j5k3m7q9",
      "invoiceNumber": "INV-2026-0042",
      "customerId": "cus_01h8n2p4r6",
      "customerName": "Acme Corp",
      "status": "sent",
      "currency": "MYR",
      "subtotal": 150000,
      "tax": 12000,
      "total": 162000,
      "dueDate": "2026-04-15",
      "issuedDate": "2026-03-15",
      "createdAt": "2026-03-15T08:30:00.000Z"
    }
  ],
  "pagination": {
    "total": 42,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

Note: monetary values are in the smallest currency unit (e.g., cents for MYR, so `150000` = RM 1,500.00).

---

## Get a Single Customer (GET with ID)

```bash
curl -s https://app.cynco.io/api/v1/customers/cus_01h8n2p4r6 \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

Response:

```json
{
  "success": true,
  "data": {
    "id": "cus_01h8n2p4r6",
    "name": "Acme Corp",
    "email": "billing@acme.com",
    "phone": "+60123456789",
    "taxId": "C-1234567-X",
    "address": {
      "line1": "123 Jalan Ampang",
      "city": "Kuala Lumpur",
      "state": "WP Kuala Lumpur",
      "postalCode": "50450",
      "country": "MY"
    },
    "createdAt": "2026-01-10T14:00:00.000Z"
  }
}
```

---

## Create a Customer (POST)

```bash
curl -s -X POST https://app.cynco.io/api/v1/customers \
  -H "Authorization: Bearer $CYNCO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: create-acme-$(date +%s)" \
  -d '{
    "name": "Acme Corp",
    "email": "billing@acme.com",
    "phone": "+60123456789",
    "taxId": "C-1234567-X",
    "address": {
      "line1": "123 Jalan Ampang",
      "city": "Kuala Lumpur",
      "state": "WP Kuala Lumpur",
      "postalCode": "50450",
      "country": "MY"
    }
  }' | jq .
```

Response (201 Created):

```json
{
  "success": true,
  "data": {
    "id": "cus_01j9m4n8p2",
    "name": "Acme Corp",
    "email": "billing@acme.com",
    "phone": "+60123456789",
    "taxId": "C-1234567-X",
    "address": {
      "line1": "123 Jalan Ampang",
      "city": "Kuala Lumpur",
      "state": "WP Kuala Lumpur",
      "postalCode": "50450",
      "country": "MY"
    },
    "createdAt": "2026-03-22T10:00:00.000Z"
  }
}
```

---

## Update a Vendor (PATCH)

PATCH requests perform a partial update -- only the fields you include will be changed.

```bash
curl -s -X PATCH https://app.cynco.io/api/v1/vendors/ven_01k2p5r8t4 \
  -H "Authorization: Bearer $CYNCO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: update-vendor-email-$(date +%s)" \
  -d '{
    "email": "new-billing@supplier.com",
    "phone": "+60198765432"
  }' | jq .
```

Response:

```json
{
  "success": true,
  "data": {
    "id": "ven_01k2p5r8t4",
    "name": "Global Supplies Sdn Bhd",
    "email": "new-billing@supplier.com",
    "phone": "+60198765432",
    "updatedAt": "2026-03-22T10:05:00.000Z"
  }
}
```

---

## Delete an Item (DELETE)

```bash
curl -s -X DELETE https://app.cynco.io/api/v1/items/itm_01m3q6s9u5 \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

Response (200 OK):

```json
{
  "success": true,
  "data": {
    "id": "itm_01m3q6s9u5",
    "deleted": true
  }
}
```

Note: most DELETE operations are soft deletes. The record is archived and can be restored within 30 days.

---

## Pagination

### Offset-based Pagination

Use `limit` and `offset` query parameters:

```bash
# First page (records 1-20)
curl -s "https://app.cynco.io/api/v1/invoices?limit=20&offset=0" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .

# Second page (records 21-40)
curl -s "https://app.cynco.io/api/v1/invoices?limit=20&offset=20" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

### Cursor-based Pagination

For large datasets, use cursor-based pagination for consistent results:

```bash
# First page
curl -s "https://app.cynco.io/api/v1/invoices?limit=50" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .

# Next page -- use the nextCursor value from the previous response
curl -s "https://app.cynco.io/api/v1/invoices?limit=50&cursor=eyJpZCI6Imludl8wMWo1azNtN3E5In0" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

### Loop Through All Pages (Bash)

```bash
OFFSET=0
LIMIT=100
TOTAL=1  # Will be updated on first request

while [ "$OFFSET" -lt "$TOTAL" ]; do
  RESPONSE=$(curl -s "https://app.cynco.io/api/v1/invoices?limit=$LIMIT&offset=$OFFSET" \
    -H "Authorization: Bearer $CYNCO_API_KEY")

  TOTAL=$(echo "$RESPONSE" | jq '.pagination.total')
  COUNT=$(echo "$RESPONSE" | jq '.data | length')

  echo "Fetched $COUNT invoices (offset $OFFSET of $TOTAL)"

  # Process each invoice
  echo "$RESPONSE" | jq -r '.data[] | "\(.invoiceNumber)\t\(.total)\t\(.status)"'

  OFFSET=$((OFFSET + LIMIT))
done
```

---

## Filter and Sort

### Filtering

Use query parameters to filter results:

```bash
# Invoices with status "overdue"
curl -s "https://app.cynco.io/api/v1/invoices?status=overdue" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .

# Invoices for a specific customer
curl -s "https://app.cynco.io/api/v1/invoices?customerId=cus_01h8n2p4r6" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .

# Invoices created after a date
curl -s "https://app.cynco.io/api/v1/invoices?createdAfter=2026-03-01" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .

# Combine multiple filters
curl -s "https://app.cynco.io/api/v1/invoices?status=sent&createdAfter=2026-03-01&createdBefore=2026-03-31" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

### Sorting

Use `sort` and `order` parameters:

```bash
# Sort by due date, ascending (oldest first)
curl -s "https://app.cynco.io/api/v1/invoices?sort=dueDate&order=asc" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .

# Sort by total amount, descending (largest first)
curl -s "https://app.cynco.io/api/v1/invoices?sort=total&order=desc" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

---

## Field Selection

Request only the fields you need to reduce payload size:

```bash
curl -s "https://app.cynco.io/api/v1/invoices?fields=id,invoiceNumber,total,status" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": "inv_01j5k3m7q9",
      "invoiceNumber": "INV-2026-0042",
      "total": 162000,
      "status": "sent"
    }
  ]
}
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request -- check your parameters |
| 401 | Unauthorized -- invalid or missing API key |
| 403 | Forbidden -- key lacks permission for this action |
| 404 | Not found -- resource does not exist |
| 409 | Conflict -- resource already exists or state conflict |
| 422 | Validation error -- check `error.details` |
| 429 | Rate limited -- slow down, check `Retry-After` header |
| 500 | Server error -- retry with exponential backoff |

### Handling Rate Limits

```bash
RESPONSE=$(curl -s -w "\n%{http_code}" https://app.cynco.io/api/v1/invoices \
  -H "Authorization: Bearer $CYNCO_API_KEY")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "429" ]; then
  RETRY_AFTER=$(curl -sI https://app.cynco.io/api/v1/invoices \
    -H "Authorization: Bearer $CYNCO_API_KEY" | grep -i "retry-after" | awk '{print $2}' | tr -d '\r')
  echo "Rate limited. Retry after $RETRY_AFTER seconds."
  sleep "$RETRY_AFTER"
fi
```

### Validation Errors

```bash
# This will fail -- email is invalid
curl -s -X POST https://app.cynco.io/api/v1/customers \
  -H "Authorization: Bearer $CYNCO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Corp",
    "email": "not-an-email"
  }' | jq .
```

Response (422):

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

---

## Idempotency Keys

For safe retries on POST, PUT, and PATCH requests, include an `Idempotency-Key` header. If the same key is sent again within 24 hours, the API returns the original response without reprocessing.

```bash
# Safe to retry -- same key returns same result
curl -s -X POST https://app.cynco.io/api/v1/customers \
  -H "Authorization: Bearer $CYNCO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: create-customer-abc-20260322" \
  -d '{
    "name": "ABC Trading",
    "email": "accounts@abc-trading.com"
  }' | jq .

# Retry with the same key -- returns the same response, no duplicate created
curl -s -X POST https://app.cynco.io/api/v1/customers \
  -H "Authorization: Bearer $CYNCO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: create-customer-abc-20260322" \
  -d '{
    "name": "ABC Trading",
    "email": "accounts@abc-trading.com"
  }' | jq .
```

Use a unique, deterministic key for each logical operation (e.g., `create-customer-{name}-{date}` or a UUID).

---

## Reports

### Trial Balance

```bash
curl -s "https://app.cynco.io/api/v1/reports/trial-balance?asOf=2026-03-31" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

Response:

```json
{
  "success": true,
  "data": {
    "asOf": "2026-03-31",
    "currency": "MYR",
    "accounts": [
      {
        "code": "1000",
        "name": "Cash and Bank",
        "debit": 5000000,
        "credit": 0
      },
      {
        "code": "2000",
        "name": "Accounts Payable",
        "debit": 0,
        "credit": 1200000
      }
    ],
    "totals": {
      "debit": 12500000,
      "credit": 12500000
    }
  }
}
```

### Profit and Loss

```bash
curl -s "https://app.cynco.io/api/v1/reports/profit-loss?from=2026-01-01&to=2026-03-31" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

### Balance Sheet

```bash
curl -s "https://app.cynco.io/api/v1/reports/balance-sheet?asOf=2026-03-31" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

### Aged Receivables

```bash
curl -s "https://app.cynco.io/api/v1/reports/aged-receivables?asOf=2026-03-31" \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```
