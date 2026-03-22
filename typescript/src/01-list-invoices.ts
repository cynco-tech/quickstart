/**
 * Cynco API Quickstart -- 01: List Invoices
 *
 * Demonstrates how to authenticate with the Cynco API and fetch
 * a filtered list of invoices using the TypeScript SDK.
 *
 * Run: npm run example:list
 */

import Cynco from "@cynco/sdk";

// Initialize the client with your API key.
// The SDK reads from CYNCO_API_KEY by default, but you can pass it explicitly.
const cynco = new Cynco({
  apiKey: process.env.CYNCO_API_KEY,
});

async function main(): Promise<void> {
  // List invoices with filters.
  // All list methods return a paginated response with { data, pagination }.
  const response = await cynco.invoices.list({
    status: "sent",
    limit: 10,
    sort: "dueDate",
    order: "asc",
  });

  console.log(`Found ${response.pagination.total} sent invoices\n`);

  // Iterate over the returned page of invoices.
  for (const invoice of response.data) {
    // Monetary values are in the smallest currency unit (e.g., cents).
    // Divide by 100 to get the display value.
    const total = (invoice.total / 100).toFixed(2);

    console.log(
      `${invoice.invoiceNumber} | ${invoice.customerName} | ${invoice.currency} ${total} | Due: ${invoice.dueDate}`
    );
  }

  // Check if there are more pages.
  if (response.pagination.hasMore) {
    console.log(
      `\n... and ${response.pagination.total - response.data.length} more`
    );
  }
}

main().catch((error: unknown) => {
  console.error("Failed to list invoices:", error);
  process.exit(1);
});
