/**
 * Cynco API Quickstart -- 02: Create a Customer
 *
 * Demonstrates creating a new customer record with full address details,
 * including idempotency keys for safe retries and validation error handling.
 *
 * Run: npm run example:create
 */

import Cynco from "@cynco/sdk";

const cynco = new Cynco({
  apiKey: process.env.CYNCO_API_KEY,
});

async function main(): Promise<void> {
  // Create a new customer.
  // The idempotencyKey ensures this request is safe to retry --
  // if the same key is sent again, the API returns the original response.
  const customer = await cynco.customers.create(
    {
      name: "Acme Corp Sdn Bhd",
      email: "billing@acme-corp.com.my",
      phone: "+60123456789",
      taxId: "C-1234567-X",
      address: {
        line1: "Level 15, Menara Acme",
        line2: "123 Jalan Ampang",
        city: "Kuala Lumpur",
        state: "WP Kuala Lumpur",
        postalCode: "50450",
        country: "MY",
      },
    },
    {
      idempotencyKey: `create-acme-corp-${Date.now()}`,
    }
  );

  console.log("Customer created successfully:\n");
  console.log(`  ID:    ${customer.id}`);
  console.log(`  Name:  ${customer.name}`);
  console.log(`  Email: ${customer.email}`);
  console.log(`  Phone: ${customer.phone}`);
  console.log(`  Tax ID: ${customer.taxId}`);
  console.log(`  City:  ${customer.address.city}`);
  console.log(`  Created: ${customer.createdAt}`);
}

main().catch((error: unknown) => {
  // The SDK throws typed errors for different failure modes.
  // See 04-error-handling.ts for comprehensive error handling patterns.
  if (error instanceof Cynco.ValidationError) {
    console.error("Validation failed:");
    for (const detail of error.details) {
      console.error(`  ${detail.field}: ${detail.message}`);
    }
  } else if (error instanceof Cynco.AuthenticationError) {
    console.error("Invalid API key. Check your CYNCO_API_KEY environment variable.");
  } else {
    console.error("Unexpected error:", error);
  }
  process.exit(1);
});
