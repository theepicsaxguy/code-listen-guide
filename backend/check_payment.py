#!/usr/bin/env python3
"""
Check a specific payment record in the database.
"""

import sys
import os
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import get_settings
from backend.models.payment import Payment
from backend.models.user import User


def check_payment(payment_id: str):
    """Check payment details."""
    print("\n" + "="*70)
    print(f"Checking Payment: {payment_id}")
    print("="*70)
    
    try:
        # Get database connection
        settings = get_settings()
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Query payment
        try:
            payment_uuid = UUID(payment_id)
        except ValueError:
            print(f"❌ Invalid UUID format: {payment_id}")
            return
        
        payment = db.query(Payment).filter(Payment.id == payment_uuid).first()
        
        if not payment:
            print(f"❌ Payment not found in database")
            return
        
        print(f"✅ Payment found")
        print(f"\nPayment Details:")
        print(f"  ID: {payment.id}")
        print(f"  User ID: {payment.user_id}")
        print(f"  Job ID: {payment.job_id}")
        print(f"  Amount: ${payment.amount_cents / 100:.2f} ({payment.amount_cents} cents)")
        print(f"  Currency: {payment.currency}")
        print(f"  Status: {payment.status}")
        print(f"  Payment Method: {payment.payment_method_type}")
        print(f"  Created: {payment.created_at}")
        print(f"  Completed: {payment.completed_at}")
        
        print(f"\nStripe Details:")
        print(f"  Payment Intent ID: {payment.stripe_payment_intent_id or '❌ MISSING'}")
        print(f"  Charge ID: {payment.stripe_charge_id or '❌ MISSING'}")
        
        # Check if can refund
        print(f"\nRefund Status:")
        if payment.status != 'succeeded':
            print(f"  ❌ Cannot refund - payment status is '{payment.status}' (must be 'succeeded')")
        elif not payment.stripe_payment_intent_id and not payment.stripe_charge_id:
            print(f"  ❌ Cannot refund - no Stripe payment intent or charge ID")
            print(f"  → This payment was not processed through Stripe")
        else:
            print(f"  ✅ Can refund")
        
        # Get user info
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            print(f"\nUser Details:")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_payment.py <payment_id>")
        print("\nExample:")
        print("  python check_payment.py 2a857fc7-2299-4db2-ac16-1e0bde1a4307")
        sys.exit(1)
    
    payment_id = sys.argv[1]
    check_payment(payment_id)
    print()
