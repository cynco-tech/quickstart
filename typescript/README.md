# Cynco API Quickstart -- TypeScript

Complete TypeScript examples using the official `cynco` SDK.

---

## Prerequisites

- Node.js 18 or later
- A Cynco API key (get one from **Settings > API Keys** in your dashboard)

## Setup

```bash
# Install dependencies
npm install

# Set your API key
export CYNCO_API_KEY="cak_your_api_key_here"
```

## Running Examples

Each example is a standalone script. Run them individually:

```bash
# List invoices with filters
npm run example:list

# Create a customer
npm run example:create

# Paginate through all records
npm run example:pagination

# Error handling patterns
npm run example:errors

# Webhook server (starts on port 3456)
npm run example:webhooks

# Pull a trial balance report
npm run example:reports
```

Or run any file directly with tsx:

```bash
npx tsx src/01-list-invoices.ts
```

## Type Checking

```bash
npm run typecheck
```

---

## Examples

### 01 -- List Invoices

Fetch a filtered, sorted, paginated list of invoices.

Key concepts:
- Initializing the SDK client
- Passing filter parameters
- Reading the paginated response envelope
- Formatting monetary values (cents to display)

### 02 -- Create a Customer

Create a new customer record with full address details.

Key concepts:
- POST operations with the SDK
- Idempotency keys for safe retries
- Handling validation errors with typed error classes

### 03 -- Pagination

Three approaches to iterating through large datasets:

1. **Manual offset pagination** -- you control the page loop
2. **Auto-pagination** -- the SDK's async iterator fetches pages automatically
3. **Cursor-based pagination** -- consistent results during concurrent writes

### 04 -- Error Handling

Comprehensive error handling covering every error type:

- `ValidationError` (422) -- inspect `error.details` for field-level messages
- `AuthenticationError` (401) -- bad or missing API key
- `PermissionError` (403) -- insufficient key permissions
- `NotFoundError` (404) -- resource doesn't exist
- `ConflictError` (409) -- state conflict
- `RateLimitError` (429) -- inspect `error.retryAfter` for backoff duration
- `APIError` (5xx) -- server error, safe to retry

Also includes a production-ready `withRetry()` utility with exponential backoff.

### 05 -- Webhooks

An Express server that receives and verifies webhook events.

Key concepts:
- Using `express.raw()` for raw body access (required for signature verification)
- Verifying HMAC-SHA256 signatures with `Cynco.webhooks.verify()`
- Routing events by type
- Always returning 200 to acknowledge receipt

For local development, use [ngrok](https://ngrok.com/) to expose your server:

```bash
ngrok http 3456
```

Then add the ngrok URL as a webhook endpoint in **Settings > Webhooks**.

### 06 -- Reports

Pull a trial balance and format it for display.

Key concepts:
- Fetching accounting reports with date parameters
- Formatting monetary values from cents
- Verifying that debits equal credits
- Other available reports: P&L, Balance Sheet, Aged Receivables

---

## SDK Reference

The `cynco` package provides typed methods for every API endpoint:

```typescript
import Cynco from "@cynco/sdk";

const cynco = new Cynco({ apiKey: process.env.CYNCO_API_KEY });

// Resources
cynco.invoices.list({ ... })
cynco.invoices.retrieve(id)
cynco.invoices.create({ ... })
cynco.invoices.update(id, { ... })
cynco.invoices.delete(id)

cynco.customers.list({ ... })
cynco.customers.retrieve(id)
cynco.customers.create({ ... })
cynco.customers.update(id, { ... })

cynco.vendors.list({ ... })
cynco.vendors.retrieve(id)
cynco.vendors.create({ ... })
cynco.vendors.update(id, { ... })

cynco.reports.trialBalance({ asOf })
cynco.reports.profitAndLoss({ from, to })
cynco.reports.balanceSheet({ asOf })
cynco.reports.agedReceivables({ asOf })

// Webhooks
Cynco.webhooks.verify(body, signature, secret)
```

Full SDK documentation: [docs.cynco.io/sdk/typescript](https://docs.cynco.io/sdk/typescript)
