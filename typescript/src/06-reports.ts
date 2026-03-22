/**
 * Cynco API Quickstart -- 06: Reports
 *
 * Demonstrates how to pull accounting reports from the Cynco API.
 * This example fetches a trial balance and formats it for display.
 *
 * Run: npm run example:reports
 */

import Cynco from "@cynco/sdk";

const cynco = new Cynco({
  apiKey: process.env.CYNCO_API_KEY,
});

/**
 * Format a monetary value from cents to a readable string.
 * Cynco API returns all monetary values in the smallest currency unit.
 */
function formatAmount(cents: number, currency: string): string {
  const value = Math.abs(cents) / 100;
  const formatted = value.toLocaleString("en-MY", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `${currency} ${formatted}`;
}

/**
 * Pad a string to a fixed width for table formatting.
 */
function padRight(str: string, width: number): string {
  return str.length >= width ? str : str + " ".repeat(width - str.length);
}

function padLeft(str: string, width: number): string {
  return str.length >= width ? str : " ".repeat(width - str.length) + str;
}

async function main(): Promise<void> {
  // Fetch the trial balance as of today.
  // You can pass any date -- the API supports historical reporting.
  const today = new Date().toISOString().split("T")[0];

  console.log(`Trial Balance as of ${today}`);
  console.log("=".repeat(78));

  const report = await cynco.reports.trialBalance({
    asOf: today,
  });

  // Print the header.
  console.log(
    `${padRight("Code", 8)} ${padRight("Account", 30)} ${padLeft("Debit", 18)} ${padLeft("Credit", 18)}`
  );
  console.log("-".repeat(78));

  // Print each account line.
  for (const account of report.accounts) {
    const debit =
      account.debit > 0
        ? formatAmount(account.debit, report.currency)
        : "";
    const credit =
      account.credit > 0
        ? formatAmount(account.credit, report.currency)
        : "";

    console.log(
      `${padRight(account.code, 8)} ${padRight(account.name, 30)} ${padLeft(debit, 18)} ${padLeft(credit, 18)}`
    );
  }

  // Print totals.
  console.log("-".repeat(78));

  const totalDebit = formatAmount(report.totals.debit, report.currency);
  const totalCredit = formatAmount(report.totals.credit, report.currency);

  console.log(
    `${padRight("", 8)} ${padRight("TOTAL", 30)} ${padLeft(totalDebit, 18)} ${padLeft(totalCredit, 18)}`
  );
  console.log("=".repeat(78));

  // Verify the trial balance balances (debits = credits).
  if (report.totals.debit === report.totals.credit) {
    console.log("\nTrial balance is in balance.");
  } else {
    const difference = Math.abs(report.totals.debit - report.totals.credit);
    console.log(
      `\nWARNING: Trial balance is out of balance by ${formatAmount(difference, report.currency)}`
    );
  }

  // You can also fetch other reports with similar patterns:
  //
  // Profit & Loss:
  //   const pnl = await cynco.reports.profitAndLoss({
  //     from: "2026-01-01",
  //     to: "2026-03-31",
  //   });
  //
  // Balance Sheet:
  //   const bs = await cynco.reports.balanceSheet({
  //     asOf: "2026-03-31",
  //   });
  //
  // Aged Receivables:
  //   const ar = await cynco.reports.agedReceivables({
  //     asOf: "2026-03-31",
  //   });
}

main().catch((error: unknown) => {
  if (error instanceof Cynco.AuthenticationError) {
    console.error("Invalid API key. Check your CYNCO_API_KEY environment variable.");
  } else {
    console.error("Failed to generate report:", error);
  }
  process.exit(1);
});
