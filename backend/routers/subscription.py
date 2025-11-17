"""
Subscription and payment router (Stripe integration)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import stripe
import os
from dotenv import load_dotenv

from database import get_db
from models import User
from auth import get_current_user

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter(prefix="/subscription", tags=["subscription"])


class CheckoutSession(BaseModel):
    price_id: str  # monthly or yearly price ID
    success_url: str
    cancel_url: str


@router.post("/create-checkout")
def create_checkout_session(
    checkout: CheckoutSession,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session"""

    try:
        session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': checkout.price_id,
                    'quantity': 1,
                }
            ],
            mode='subscription',
            success_url=checkout.success_url,
            cancel_url=checkout.cancel_url,
            metadata={
                'user_id': user.id
            },
            subscription_data={
                'trial_period_days': 7
            }
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')

        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.subscription_status = 'trial'
                user.subscription_id = session['subscription']
                user.subscription_expires = datetime.utcnow() + timedelta(days=7)
                db.commit()

    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        user = db.query(User).filter(User.subscription_id == subscription['id']).first()

        if user:
            user.subscription_status = 'premium'
            user.subscription_expires = datetime.fromtimestamp(subscription['current_period_end'])
            db.commit()

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        user = db.query(User).filter(User.subscription_id == subscription['id']).first()

        if user:
            if subscription['status'] == 'active':
                user.subscription_status = 'premium'
            elif subscription['status'] in ['past_due', 'canceled', 'unpaid']:
                user.subscription_status = 'free'

            user.subscription_expires = datetime.fromtimestamp(subscription['current_period_end'])
            db.commit()

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        user = db.query(User).filter(User.subscription_id == subscription['id']).first()

        if user:
            user.subscription_status = 'free'
            user.subscription_expires = None
            db.commit()

    return {"status": "success"}


@router.get("/status")
def get_subscription_status(user: User = Depends(get_current_user)):
    """Get current subscription status"""

    is_premium = user.subscription_status in ['premium', 'trial']

    # Check if expired
    if user.subscription_expires and user.subscription_expires < datetime.utcnow():
        is_premium = False

    return {
        "status": user.subscription_status,
        "is_premium": is_premium,
        "expires": user.subscription_expires,
        "subscription_id": user.subscription_id
    }


@router.post("/cancel")
def cancel_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""

    if not user.subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    try:
        # Cancel at period end (don't cancel immediately)
        stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=True
        )

        return {
            "message": "Subscription will be canceled at the end of the billing period",
            "expires": user.subscription_expires
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans")
def get_subscription_plans():
    """Get available subscription plans"""

    return {
        "plans": [
            {
                "id": "monthly",
                "name": "MindPilot+ Monthly",
                "price": 4.99,
                "currency": "USD",
                "interval": "month",
                "price_id": os.getenv("STRIPE_MONTHLY_PRICE_ID"),
                "features": [
                    "Unlimited habits",
                    "Unlimited AI journal reflections",
                    "All audio content",
                    "Sleep analysis",
                    "Weekly personalized reports",
                    "Advanced CBT suggestions",
                    "No limitations"
                ]
            },
            {
                "id": "yearly",
                "name": "MindPilot+ Yearly",
                "price": 39.00,
                "currency": "USD",
                "interval": "year",
                "price_id": os.getenv("STRIPE_YEARLY_PRICE_ID"),
                "savings": "Save 34%",
                "features": [
                    "All monthly features",
                    "Best value - 2 months free!",
                    "Priority support"
                ]
            }
        ],
        "trial_days": 7
    }
