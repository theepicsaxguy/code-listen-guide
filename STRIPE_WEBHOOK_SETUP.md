# Stripe Webhook Setup Guide

## Issue
Stripe webhooks were not being received because the webhook endpoint configuration was incorrect.

## Changes Made

### 1. Fixed Webhook Header Handling (`backend/api/routes/payments.py`)
- Added explicit `alias="Stripe-Signature"` to the header parameter to ensure proper header mapping
- Added validation to check if the Stripe-Signature header is present
- Added detailed logging to help debug webhook issues

### 2. Added Helper Scripts
- **`stripe-webhook-listen.sh`**: Script to start the Stripe CLI webhook listener
- **`test_webhook.sh`**: Script to test the webhook endpoint manually

### 3. Updated Makefile
Added `make stripe-webhook` command for easy webhook listener startup.

## How to Test Webhooks Locally

### Method 1: Using the Makefile (Recommended)

1. **Start your backend server:**
   ```bash
   make dev-backend
   # or if already running, just ensure it's on port 8000
   ```

2. **In a separate terminal, start the Stripe webhook listener:**
   ```bash
   make stripe-webhook
   ```

3. **In another terminal, trigger test events:**
   ```bash
   stripe trigger payment_intent.succeeded
   stripe trigger checkout.session.completed
   stripe trigger charge.refunded
   ```

### Method 2: Manual Stripe CLI

1. **Start the webhook listener:**
   ```bash
   stripe listen --forward-to http://localhost:8000/api/v1/payments/webhook
   ```

2. **Trigger events:**
   ```bash
   stripe trigger payment_intent.succeeded
   ```

### Method 3: Using the Helper Script

```bash
./stripe-webhook-listen.sh
```

## Webhook Endpoint Details

- **URL**: `http://localhost:8000/api/v1/payments/webhook`
- **Method**: POST
- **Required Header**: `Stripe-Signature`
- **Events Handled**:
  - `payment_intent.succeeded` - Marks payment as succeeded and triggers workflow
  - `payment_intent.payment_failed` - Marks payment as failed
  - `checkout.session.completed` - Handles subscription checkouts
  - `charge.refunded` - Handles refunds

## Expected Log Output

When a webhook is received, you should see logs like:

```
INFO: Webhook received - signature_present: True, payload_length: 1234
INFO: Received Stripe webhook - event_type: payment_intent.succeeded, event_id: evt_xxx
INFO: Payment marked as succeeded - payment_id: xxx, intent_id: pi_xxx
INFO: Job marked as paid, triggering workflow - job_id: xxx
```

## Troubleshooting

### No webhook received
1. **Check backend is running on port 8000**:
   ```bash
   lsof -i :8000
   ```

2. **Check Stripe CLI is forwarding to correct URL**:
   - Should be: `http://localhost:8000/api/v1/payments/webhook`
   - NOT: `http://localhost:8080/api/v1/payments/webhook`

3. **Verify Stripe webhook secret in `.env`**:
   ```bash
   grep STRIPE_WEBHOOK_SECRET backend/.env
   ```

### Signature verification fails
- The Stripe CLI automatically generates and updates the webhook secret
- Make sure your `backend/.env` has the correct `STRIPE_WEBHOOK_SECRET`
- The secret should start with `whsec_`

### Backend logs show "Missing Stripe-Signature header"
- This means the webhook request didn't include the signature
- Verify you're using the Stripe CLI to forward events
- Direct curl requests won't work without proper signature generation

## Production Setup

For production, you'll need to:

1. **Create a webhook endpoint in Stripe Dashboard**:
   - Go to https://dashboard.stripe.com/webhooks
   - Add endpoint: `https://your-domain.com/api/v1/payments/webhook`
   - Select events to listen to

2. **Update environment variables**:
   - Set `STRIPE_WEBHOOK_SECRET` to the signing secret from Stripe Dashboard
   - Ensure `API_BASE_URL` points to your production domain

3. **Verify SSL certificate**:
   - Stripe requires HTTPS for webhook endpoints
   - Ensure your domain has a valid SSL certificate

## Testing Payment Flow

To test the complete payment flow:

1. Start backend and webhook listener
2. Create a payment through the frontend
3. Complete the payment in the Stripe checkout
4. Watch for the webhook in your logs
5. Verify the job status updates to "paid" and workflow starts

## Files Modified

- `backend/api/routes/payments.py` - Fixed webhook handler
- `Makefile` - Added `stripe-webhook` command
- `stripe-webhook-listen.sh` - New helper script
- `test_webhook.sh` - New test script

## Related Documentation

- [Stripe Webhooks Documentation](https://stripe.com/docs/webhooks)
- [Stripe CLI Testing Guide](https://stripe.com/docs/stripe-cli/webhooks)
