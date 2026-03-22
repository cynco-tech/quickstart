/**
 * Cynco API Quickstart -- 05: Webhook Signature Verification
 *
 * Demonstrates how to receive and verify webhook events from Cynco.
 * This example uses Express, but the verification logic works with any
 * Node.js HTTP framework.
 *
 * Setup:
 *   1. Create a webhook endpoint in Settings > Webhooks
 *   2. Copy the signing secret (starts with whsec_)
 *   3. Set it as CYNCO_WEBHOOK_SECRET in your environment
 *   4. Point the webhook URL to your server (use ngrok for local dev)
 *
 * Run: npm run example:webhooks
 */

import express, { type Request, type Response } from "express";
import Cynco from "@cynco/sdk";

const app = express();
const port = process.env.PORT ?? 3456;

// The webhook signing secret from your Cynco dashboard.
const webhookSecret = process.env.CYNCO_WEBHOOK_SECRET;

if (!webhookSecret) {
  console.error("Missing CYNCO_WEBHOOK_SECRET environment variable.");
  console.error("Get it from Settings > Webhooks in your Cynco dashboard.");
  process.exit(1);
}

// IMPORTANT: Webhooks require the raw request body for signature verification.
// Use express.raw() instead of express.json() for the webhook route.
app.post(
  "/webhooks/cynco",
  express.raw({ type: "application/json" }),
  (req: Request, res: Response): void => {
    // Extract the signature header.
    const signature = req.headers["cynco-signature"] as string | undefined;

    if (!signature) {
      res.status(400).json({ error: "Missing cynco-signature header" });
      return;
    }

    // Verify the webhook signature using the SDK.
    // This checks:
    //   1. The HMAC-SHA256 signature matches the payload
    //   2. The timestamp is within the tolerance window (5 minutes by default)
    let event: Cynco.WebhookEvent;

    try {
      event = Cynco.webhooks.verify(req.body, signature, webhookSecret);
    } catch (error: unknown) {
      if (error instanceof Cynco.WebhookVerificationError) {
        console.error("Webhook verification failed:", error.message);
        res.status(400).json({ error: "Invalid signature" });
        return;
      }
      throw error;
    }

    // The event is verified -- process it.
    console.log(`Received event: ${event.type} (${event.id})`);

    switch (event.type) {
      case "invoice.created": {
        const invoice = event.data;
        console.log(
          `  Invoice ${invoice.invoiceNumber} created for ${invoice.customerName}`
        );
        console.log(
          `  Total: ${invoice.currency} ${(invoice.total / 100).toFixed(2)}`
        );
        break;
      }

      case "invoice.paid": {
        const invoice = event.data;
        console.log(
          `  Invoice ${invoice.invoiceNumber} paid!`
        );
        console.log(
          `  Amount: ${invoice.currency} ${(invoice.total / 100).toFixed(2)}`
        );
        break;
      }

      case "invoice.overdue": {
        const invoice = event.data;
        console.log(
          `  Invoice ${invoice.invoiceNumber} is overdue.`
        );
        console.log(`  Due date was: ${invoice.dueDate}`);
        break;
      }

      case "customer.created": {
        const customer = event.data;
        console.log(`  New customer: ${customer.name} (${customer.email})`);
        break;
      }

      case "payment.received": {
        const payment = event.data;
        console.log(
          `  Payment received: ${payment.currency} ${(payment.amount / 100).toFixed(2)}`
        );
        console.log(`  Method: ${payment.method}`);
        break;
      }

      default: {
        // Log unhandled event types for debugging.
        // It's safe to acknowledge events you don't handle yet.
        console.log(`  Unhandled event type: ${event.type}`);
      }
    }

    // Always respond with 200 to acknowledge receipt.
    // If you return a non-2xx status, Cynco will retry the webhook
    // with exponential backoff (up to 3 retries over 24 hours).
    res.status(200).json({ received: true });
  }
);

app.listen(port, () => {
  console.log(`Webhook server listening on port ${port}`);
  console.log(`\nEndpoint: POST http://localhost:${port}/webhooks/cynco`);
  console.log(
    "\nFor local development, expose this with ngrok:"
  );
  console.log(`  ngrok http ${port}`);
  console.log(
    "\nThen add the ngrok URL as a webhook endpoint in your Cynco dashboard."
  );
});
