#!/bin/bash

# Test script to verify the Stripe webhook endpoint

echo "Testing webhook endpoint..."
echo ""

# Get the backend URL from environment or use default
BACKEND_URL="${VITE_API_BASE_URL:-http://localhost:8000}"

# Test the webhook endpoint
echo "Testing POST to ${BACKEND_URL}/api/v1/payments/webhook"
echo ""

curl -X POST "${BACKEND_URL}/api/v1/payments/webhook" \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test_signature" \
  -d '{"type": "payment_intent.succeeded"}' \
  -v

echo ""
echo ""
echo "Expected: Should receive a 400 error about invalid signature (this is correct!)"
echo ""
echo "To use Stripe CLI for webhook testing:"
echo "  stripe listen --forward-to ${BACKEND_URL}/api/v1/payments/webhook"
echo ""
echo "To trigger test events:"
echo "  stripe trigger payment_intent.succeeded"
echo "  stripe trigger checkout.session.completed"
