#!/bin/bash

# Stripe CLI webhook listener for local development
# This script forwards Stripe webhook events to your local backend

# Default backend URL (can be overridden with environment variable)
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "================================================"
echo "Starting Stripe webhook listener..."
echo "================================================"
echo ""
echo "Backend URL: ${BACKEND_URL}"
echo "Webhook endpoint: ${BACKEND_URL}/api/v1/payments/webhook"
echo ""
echo "This will forward Stripe events to your local backend."
echo "Keep this terminal running while testing payments."
echo ""
echo "To trigger test events in another terminal:"
echo "  stripe trigger payment_intent.succeeded"
echo "  stripe trigger checkout.session.completed"
echo "  stripe trigger charge.refunded"
echo ""
echo "================================================"
echo ""

# Start the Stripe CLI listener
stripe listen --forward-to "${BACKEND_URL}/api/v1/payments/webhook"
