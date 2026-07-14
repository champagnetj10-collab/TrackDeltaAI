"""Subscriptions router — Stripe checkout, billing portal, and webhook handling.

Requires real Stripe test/live keys (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET,
STRIPE_PRICE_ID_PRO_MONTHLY) to actually create sessions or verify webhooks —
without them, /checkout and /portal return 503 and the webhook rejects with 400.
This has not been exercised against a real Stripe account.
"""
from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import rate_limit
from app.models.subscription_event import SubscriptionEvent
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
# Mounted without the /v1 prefix and without auth — Stripe calls this directly.
webhook_router = APIRouter(tags=["webhooks"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


class CheckoutRequest(BaseModel):
    price_id: str | None = None


class CheckoutResponse(BaseModel):
    url: str


class PortalResponse(BaseModel):
    url: str


class SubscriptionStatusResponse(BaseModel):
    subscription_tier: str
    subscription_status: str | None
    subscription_period_end: str | None
    monthly_uploads_used: int
    monthly_upload_limit: int | None


def _require_stripe_configured() -> None:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Billing is not configured yet.")
    stripe.api_key = settings.stripe_secret_key


@router.get("/current", response_model=SubscriptionStatusResponse)
def get_current_subscription(current_user: CurrentUser) -> SubscriptionStatusResponse:
    return SubscriptionStatusResponse(
        subscription_tier=current_user.subscription_tier,
        subscription_status=current_user.subscription_status,
        subscription_period_end=(
            current_user.subscription_period_end.isoformat()
            if current_user.subscription_period_end else None
        ),
        monthly_uploads_used=current_user.monthly_uploads_used,
        monthly_upload_limit=(
            None if current_user.subscription_tier == "pro" else settings.free_tier_monthly_uploads
        ),
    )


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    dependencies=[rate_limit(5, 60, "subscriptions-checkout")],
)
def create_checkout_session(
    body: CheckoutRequest, current_user: CurrentUser, db: DB
) -> CheckoutResponse:
    _require_stripe_configured()

    price_id = body.price_id or settings.stripe_price_id_pro_monthly
    if not price_id:
        raise HTTPException(status_code=400, detail="No Stripe price configured.")

    if not current_user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(email=current_user.email)
        except stripe.StripeError as exc:
            logger.exception("Stripe customer creation failed")
            raise HTTPException(
                status_code=502, detail="Billing is temporarily unavailable. Please try again shortly."
            ) from exc
        current_user.stripe_customer_id = customer.id
        db.commit()

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{settings.frontend_url}/billing?checkout=success",
            cancel_url=f"{settings.frontend_url}/billing?checkout=cancelled",
        )
    except stripe.StripeError as exc:
        logger.exception("Stripe checkout session creation failed")
        raise HTTPException(
            status_code=502, detail="Billing is temporarily unavailable. Please try again shortly."
        ) from exc

    return CheckoutResponse(url=checkout_session.url)


@router.post(
    "/portal",
    response_model=PortalResponse,
    dependencies=[rate_limit(5, 60, "subscriptions-portal")],
)
def create_portal_session(current_user: CurrentUser) -> PortalResponse:
    _require_stripe_configured()

    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account yet — upgrade to Pro first.")

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{settings.frontend_url}/billing",
        )
    except stripe.StripeError as exc:
        logger.exception("Stripe portal session creation failed")
        raise HTTPException(
            status_code=502, detail="Billing is temporarily unavailable. Please try again shortly."
        ) from exc

    return PortalResponse(url=portal_session.url)


@webhook_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: DB) -> dict[str, str]:
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Billing is not configured yet.")
    stripe.api_key = settings.stripe_secret_key

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {exc}") from exc

    # Idempotency: Stripe may deliver the same event more than once.
    if db.query(SubscriptionEvent).filter_by(stripe_event_id=event["id"]).first():
        return {"status": "already_processed"}

    obj = event["data"]["object"]
    event_type = event["type"]

    user: User | None = None
    customer_id = obj.get("customer")
    if customer_id:
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user is not None:
        if event_type == "checkout.session.completed":
            user.subscription_tier = "pro"
            user.subscription_status = "active"
        elif event_type == "customer.subscription.updated":
            user.subscription_status = obj.get("status")
            period_end = obj.get("current_period_end")
            if period_end:
                user.subscription_period_end = datetime.fromtimestamp(period_end, tz=UTC)
        elif event_type == "customer.subscription.deleted":
            user.subscription_tier = "free"
            user.subscription_status = "canceled"
        elif event_type == "invoice.payment_failed":
            user.subscription_status = "past_due"

    db.add(SubscriptionEvent(
        id=uuid.uuid4(),
        user_id=user.id if user else None,
        event_type=event_type,
        stripe_event_id=event["id"],
        event_data=obj,
    ))
    db.commit()

    return {"status": "processed"}
