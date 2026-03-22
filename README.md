# Cynco API Quickstart

Get started with the Cynco API in under 5 minutes. This repository contains complete, runnable examples in multiple languages that cover authentication, CRUD operations, pagination, error handling, webhooks, and reporting.

---

## Prerequisites

1. A Cynco account -- sign up at [app.cynco.io](https://app.cynco.io)
2. An API key -- generate one from **Settings > API Keys** in your dashboard
3. Your API key will start with `cak_` (Cynco API Key)

Set your API key as an environment variable:

```bash
export CYNCO_API_KEY="cak_your_api_key_here"
```

---

## Choose Your Language

| Language | Directory | Setup Time | Notes |
|----------|-----------|------------|-------|
| [cURL](#curl) | [`curl/`](./curl/) | 0 min | No setup needed -- run from any terminal |
| [TypeScript](#typescript) | [`typescript/`](./typescript/) | 2 min | Uses the `cynco` SDK |
| [Python](#python) | [`python/`](./python/) | 1 min | Uses `requests` -- no SDK required |

---

## cURL

No dependencies, no setup. Copy and paste into your terminal.

```bash
curl -s https://app.cynco.io/api/v1/invoices \
  -H "Authorization: Bearer $CYNCO_API_KEY" | jq .
```

See [`curl/README.md`](./curl/README.md) for the full reference covering every HTTP method, pagination, filtering, and more.

---

## TypeScript

Uses the official `cynco` npm package.

```bash
cd typescript
npm install
npm run example:list
```

**Examples included:**

| File | Description |
|------|-------------|
| `src/01-list-invoices.ts` | List invoices with filters |
| `src/02-create-customer.ts` | Create a customer with validation |
| `src/03-pagination.ts` | Auto-paginate through all records |
| `src/04-error-handling.ts` | Typed error handling patterns |
| `src/05-webhooks.ts` | Webhook signature verification |
| `src/06-reports.ts` | Pull a trial balance report |

See [`typescript/README.md`](./typescript/README.md) for setup and details.

---

## Python

Uses the `requests` library -- no SDK required.

```bash
cd python
pip install -r requirements.txt
python 01_list_invoices.py
```

**Examples included:**

| File | Description |
|------|-------------|
| `01_list_invoices.py` | List invoices with filters |
| `02_create_customer.py` | Create a customer with validation |
| `03_pagination.py` | Paginate through all records |
| `04_error_handling.py` | Error handling patterns |
| `05_webhooks.py` | Webhook signature verification |
| `06_reports.py` | Pull a trial balance report |

See [`python/README.md`](./python/README.md) for setup and details.

---

## Common Patterns

### Authentication

Every request requires a Bearer token in the `Authorization` header:

```
Authorization: Bearer cak_your_api_key_here
```

API keys are scoped to a single organization. You can create multiple keys with different permissions from the dashboard.

### Response Envelope

All responses follow the same structure:

```json
{
  "success": true,
  "data": { ... },
  "pagination": {
    "total": 142,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2026-03-22T10:00:00.000Z"
  }
}
```

For errors:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email address",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  },
  "meta": {
    "requestId": "req_def456",
    "timestamp": "2026-03-22T10:00:00.000Z"
  }
}
```

### Pagination

The API supports offset-based pagination on all list endpoints:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Records per page (max 100) |
| `offset` | integer | 0 | Number of records to skip |

For large datasets, use cursor-based pagination with the `cursor` parameter:

| Parameter | Type | Description |
|-----------|------|-------------|
| `cursor` | string | Opaque cursor from `pagination.nextCursor` |
| `limit` | integer | Records per page (max 100) |

### Rate Limits

| Tier | Limit |
|------|-------|
| Starter | 120 requests/min |
| Professional | 160 requests/min |
| Enterprise | 200 requests/min |

Rate limit headers are included in every response:

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 117
X-RateLimit-Reset: 1711094460
```

### Idempotency

For POST, PUT, and PATCH requests, include an `Idempotency-Key` header to safely retry requests:

```
Idempotency-Key: your-unique-key-here
```

The API guarantees that a request with the same idempotency key will only be processed once within a 24-hour window.

---

## API Reference

- **Full API Documentation:** [docs.cynco.io](https://docs.cynco.io)
- **OpenAPI Specification:** [app.cynco.io/api/v1/openapi.json](https://app.cynco.io/api/v1/openapi.json)
- **TypeScript SDK:** [`cynco` on npm](https://www.npmjs.com/package/cynco)
- **Status Page:** [status.cynco.io](https://status.cynco.io)

---

## License

MIT -- see [LICENSE](./LICENSE).
