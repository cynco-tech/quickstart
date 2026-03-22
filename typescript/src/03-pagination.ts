/**
 * Cynco API Quickstart -- 03: Pagination
 *
 * Demonstrates three approaches to paginating through large result sets:
 * 1. Manual offset-based pagination
 * 2. Auto-pagination with the SDK's async iterator
 * 3. Cursor-based pagination for consistent results
 *
 * Run: npm run example:pagination
 */

import Cynco from "@cynco/sdk";

const cynco = new Cynco({
  apiKey: process.env.CYNCO_API_KEY,
});

/**
 * Approach 1: Manual offset-based pagination.
 * You control the offset and limit yourself.
 * Best when you need a specific page or know the total size.
 */
async function manualPagination(): Promise<void> {
  console.log("=== Manual Offset Pagination ===\n");

  const limit = 20;
  let offset = 0;
  let total = 0;
  let fetched = 0;

  do {
    const response = await cynco.invoices.list({
      limit,
      offset,
      sort: "createdAt",
      order: "desc",
    });

    total = response.pagination.total;
    fetched += response.data.length;

    console.log(
      `Page ${Math.floor(offset / limit) + 1}: ` +
        `${response.data.length} invoices (${fetched}/${total})`
    );

    offset += limit;
  } while (offset < total);

  console.log(`\nDone. Fetched ${fetched} invoices total.\n`);
}

/**
 * Approach 2: Auto-pagination with the SDK's async iterator.
 * The SDK handles fetching pages automatically -- you just iterate.
 * Best for processing all records without worrying about pagination logic.
 */
async function autoPagination(): Promise<void> {
  console.log("=== Auto Pagination (Async Iterator) ===\n");

  let count = 0;
  let totalAmount = 0;

  // The .list() method returns an object with an async iterator.
  // Use for-await-of to iterate through ALL invoices across all pages.
  for await (const invoice of cynco.invoices.list({ status: "paid" })) {
    count++;
    totalAmount += invoice.total;

    // Log every 50th invoice to show progress.
    if (count % 50 === 0) {
      console.log(`  Processed ${count} invoices so far...`);
    }
  }

  const displayTotal = (totalAmount / 100).toFixed(2);
  console.log(`\nProcessed ${count} paid invoices.`);
  console.log(`Total value: MYR ${displayTotal}\n`);
}

/**
 * Approach 3: Cursor-based pagination.
 * Uses an opaque cursor instead of offset for consistent results,
 * even if records are added or removed during pagination.
 * Best for large datasets or real-time data.
 */
async function cursorPagination(): Promise<void> {
  console.log("=== Cursor-based Pagination ===\n");

  let cursor: string | undefined = undefined;
  let pageNumber = 0;
  let totalFetched = 0;

  do {
    const response = await cynco.invoices.list({
      limit: 50,
      cursor,
    });

    pageNumber++;
    totalFetched += response.data.length;

    console.log(
      `Page ${pageNumber}: ${response.data.length} invoices ` +
        `(${totalFetched} total)`
    );

    // The nextCursor is undefined when there are no more pages.
    cursor = response.pagination.nextCursor;
  } while (cursor !== undefined);

  console.log(`\nDone. Fetched ${totalFetched} invoices total.\n`);
}

async function main(): Promise<void> {
  await manualPagination();
  await autoPagination();
  await cursorPagination();
}

main().catch((error: unknown) => {
  console.error("Pagination example failed:", error);
  process.exit(1);
});
