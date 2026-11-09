"""Stripe webhook verification and fulfillment routing.

Webhooks are required. Fulfillment never runs on the success page.
Checkout: handle checkout.session.completed and
checkout.session.async_payment_succeeded, and only when payment_status
is not unpaid. Subscriptions also need invoice and risk events.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

from .commerce import Ledger

CHECKOUT_FULFILL_EVENTS = frozenset(
    {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }
)
CHECKOUT_FAIL_EVENTS = frozenset({"checkout.session.async_payment_failed"})
SUBSCRIPTION_EVENTS = frozenset(
    {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
        "invoice.payment_succeeded",
    }
)
RISK_EVENTS = frozenset(
    {
        "charge.dispute.created",
        "charge.refunded",
        "radar.early_fraud_warning.created",
    }
)


@dataclass(frozen=True, slots=True)
class Fulfillment:
    action: str
    event_type: str
    stripe_object_id: str
    entry_id: int | None = None
    sku_id: str | None = None
    reason: str | None = None


def verify_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
    *,
    tolerance_seconds: int = 300,
    now: float | None = None,
) -> None:
    """Verify Stripe-Signature (t=, v1=) with HMAC-SHA256."""
    if not signature_header:
        raise ValueError("missing Stripe-Signature header")
    items: dict[str, str] = {}
    for part in signature_header.split(","):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        items[key.strip()] = value.strip()
    timestamp = items.get("t")
    digest = items.get("v1")
    if not timestamp or not digest:
        raise ValueError("Stripe-Signature must include t and v1")
    age = abs((now if now is not None else time.time()) - int(timestamp))
    if age > tolerance_seconds:
        raise ValueError("Stripe-Signature timestamp is outside tolerance")
    signed = timestamp.encode("utf-8") + b"." + payload
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, digest):
        raise ValueError("Stripe-Signature mismatch")


def should_fulfill_checkout(session: dict[str, Any]) -> bool:
    return session.get("payment_status") != "unpaid"


def route_event(event: dict[str, Any], ledger: Ledger | None = None) -> Fulfillment:
    event_type = str(event.get("type", ""))
    data = event.get("data", {}).get("object") or {}
    object_id = str(data.get("id") or event.get("id") or "")
    sku_id = (data.get("metadata") or {}).get("sku_id")
    reference = data.get("client_reference_id")
    entry_id = int(reference) if str(reference or "").isdigit() else None

    if event_type in CHECKOUT_FAIL_EVENTS:
        if ledger is not None and entry_id is not None:
            ledger.set_status(entry_id, "failed")
        return Fulfillment("fail", event_type, object_id, entry_id, sku_id, "async payment failed")

    if event_type in CHECKOUT_FULFILL_EVENTS:
        if not should_fulfill_checkout(data):
            return Fulfillment(
                "ignore",
                event_type,
                object_id,
                entry_id,
                sku_id,
                "payment_status is unpaid; wait for async_payment_succeeded",
            )
        if ledger is not None and entry_id is not None:
            ledger.set_status(entry_id, "recognized")
        return Fulfillment("recognize", event_type, object_id, entry_id, sku_id)

    if event_type in SUBSCRIPTION_EVENTS:
        action = "subscription-sync"
        if event_type == "invoice.payment_failed":
            action = "payment-failed"
        elif event_type in {"invoice.paid", "invoice.payment_succeeded"}:
            action = "recognize"
            if ledger is not None and sku_id:
                from .commerce import load_catalog

                sku = load_catalog().get(sku_id)
                ledger.recognize(sku, source=f"stripe:{event.get('id')}")
        elif event_type == "customer.subscription.deleted":
            action = "cancel"
        return Fulfillment(action, event_type, object_id, entry_id, sku_id)

    if event_type in RISK_EVENTS:
        return Fulfillment("risk-review", event_type, object_id, entry_id, sku_id)

    return Fulfillment("ignore", event_type, object_id, entry_id, sku_id, "unhandled event")


def handle_webhook(
    payload: bytes,
    signature_header: str,
    secret: str,
    ledger: Ledger | None = None,
    *,
    now: float | None = None,
) -> Fulfillment:
    verify_signature(payload, signature_header, secret, now=now)
    event = json.loads(payload.decode("utf-8"))
    return route_event(event, ledger)
