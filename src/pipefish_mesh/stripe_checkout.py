"""Stripe Checkout Session payloads for PipeFish SKUs.

Follows Stripe best practices:
- Checkout Sessions API (not Charges / PaymentIntents for on-session work)
- omit payment_method_types (dynamic payment methods)
- one Product name per SKU
- Prices, not Plans
- restricted API keys via SecretBroker
- StripeClient when the optional stripe extra is installed
- automatic_tax stays off until a registration is confirmed Collecting
"""

from __future__ import annotations

import secrets
import string
from typing import Any

from .commerce import Ledger, Sku
from .secrets import SecretBroker

STRIPE_API_VERSION = "2026-09-30.endive"
INTEGRATION_PREFIX = "pipefish"


def checkout_mode_for(sku: Sku) -> str:
    return sku.checkout_mode


def integration_identifier(prefix: str = INTEGRATION_PREFIX) -> str:
    suffix = "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    return f"{prefix}-{suffix}"


def build_checkout_session(
    sku: Sku,
    *,
    customer_email: str,
    success_url: str,
    cancel_url: str,
    client_reference_id: str,
    enable_automatic_tax: bool = False,
    tax_registration_active: bool = False,
) -> dict[str, Any]:
    """Return Checkout Sessions create params. Does not call Stripe."""
    if not customer_email.strip():
        raise ValueError("customer_email is required")
    if "{CHECKOUT_SESSION_ID}" not in success_url:
        success_url = f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}"

    price_data: dict[str, Any] = {
        "currency": "usd",
        "unit_amount": sku.amount_cents,
        "product_data": {"name": sku.name, "metadata": {"sku_id": sku.id}},
    }
    mode = checkout_mode_for(sku)
    if mode == "subscription":
        price_data["recurring"] = {"interval": "month"}

    params: dict[str, Any] = {
        "mode": mode,
        "customer_email": customer_email.strip(),
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": client_reference_id,
        "integration_identifier": integration_identifier(),
        "line_items": [{"quantity": 1, "price_data": price_data}],
        "metadata": {
            "sku_id": sku.id,
            "cadence": sku.cadence,
            "lane": sku.lane,
        },
    }
    if mode == "subscription":
        params["subscription_data"] = {"metadata": {"sku_id": sku.id}}
    if enable_automatic_tax:
        if not tax_registration_active:
            raise ValueError(
                "Refusing automatic_tax: Stripe collects nothing until a Tax "
                "registration is Collecting. Confirm Dashboard → Tax → Registrations "
                "before enabling."
            )
        params["automatic_tax"] = {"enabled": True}
    return params


def build_customer_portal_session(customer_id: str, return_url: str) -> dict[str, Any]:
    if not customer_id.strip():
        raise ValueError("customer_id is required")
    return {"customer": customer_id, "return_url": return_url}


def restricted_api_key(broker: SecretBroker | None = None) -> str:
    """Prefer a restricted key (rk_) over a secret key (sk_)."""
    secrets_broker = broker or SecretBroker()
    for name in ("STRIPE_RESTRICTED_KEY", "STRIPE_SECRET_KEY"):
        try:
            value = secrets_broker.get(name)
        except KeyError:
            continue
        if value.startswith(("rk_", "sk_")):
            return value
    raise KeyError("STRIPE_RESTRICTED_KEY (preferred) or STRIPE_SECRET_KEY is not configured")


def start_checkout(
    sku: Sku,
    *,
    customer_email: str,
    success_url: str,
    cancel_url: str,
    ledger: Ledger,
    enable_automatic_tax: bool = False,
    tax_registration_active: bool = False,
) -> tuple[dict[str, Any], int]:
    """Insert a pending ledger row and build Checkout params. Fulfillment is webhook-only."""
    entry_id = ledger.record(
        sku.id,
        sku.amount_cents,
        source="stripe-checkout",
        status="pending",
    )
    params = build_checkout_session(
        sku,
        customer_email=customer_email,
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(entry_id),
        enable_automatic_tax=enable_automatic_tax,
        tax_registration_active=tax_registration_active,
    )
    return params, entry_id


def create_checkout_session(params: dict[str, Any], *, api_key: str | None = None) -> Any:
    """Live create via StripeClient. Requires the optional stripe extra."""
    try:
        from stripe import StripeClient
    except ImportError as exc:  # pragma: no cover - optional extra
        raise RuntimeError(
            "Install pipefish-mesh[stripe] to create live Checkout Sessions"
        ) from exc
    key = api_key or restricted_api_key()
    client = StripeClient(key, stripe_version=STRIPE_API_VERSION)
    return client.v1.checkout.sessions.create(**params)
