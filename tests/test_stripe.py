import hashlib
import hmac
import json

from pipefish_mesh.commerce import Ledger, load_catalog
from pipefish_mesh.stripe_checkout import (
    build_checkout_session,
    build_customer_portal_session,
    integration_identifier,
    start_checkout,
)
from pipefish_mesh.stripe_webhooks import handle_webhook, route_event, verify_signature


def test_one_time_checkout_omits_payment_method_types() -> None:
    sku = load_catalog().get("mesh.audit.security")
    params = build_checkout_session(
        sku,
        customer_email="buyer@example.com",
        success_url="https://pipefishlabs.io/paid/{CHECKOUT_SESSION_ID}",
        cancel_url="https://pipefishlabs.io/cancel",
        client_reference_id="1",
    )
    assert params["mode"] == "payment"
    assert "payment_method_types" not in params
    assert "automatic_tax" not in params
    assert params["integration_identifier"].startswith("pipefish-")
    assert len(params["integration_identifier"].split("-")[1]) == 8
    assert params["line_items"][0]["price_data"]["unit_amount"] == 450000
    assert params["line_items"][0]["price_data"]["product_data"]["name"] == sku.name
    assert "recurring" not in params["line_items"][0]["price_data"]


def test_retainer_uses_subscription_mode_and_own_product() -> None:
    sku = load_catalog().get("mesh.retain.ops")
    params = build_checkout_session(
        sku,
        customer_email="ops@example.com",
        success_url="https://pipefishlabs.io/paid",
        cancel_url="https://pipefishlabs.io/cancel",
        client_reference_id="2",
    )
    assert params["mode"] == "subscription"
    assert "payment_method_types" not in params
    assert params["line_items"][0]["price_data"]["recurring"] == {"interval": "month"}
    assert params["subscription_data"]["metadata"]["sku_id"] == sku.id
    assert "{CHECKOUT_SESSION_ID}" in params["success_url"]


def test_automatic_tax_requires_active_registration() -> None:
    sku = load_catalog().get("mesh.lane.ping")
    try:
        build_checkout_session(
            sku,
            customer_email="buyer@example.com",
            success_url="https://example.com/ok/{CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            client_reference_id="3",
            enable_automatic_tax=True,
            tax_registration_active=False,
        )
        raise AssertionError("expected tax registration guard")
    except ValueError as exc:
        assert "registration" in str(exc).lower()


def test_start_checkout_is_pending_until_webhook() -> None:
    sku = load_catalog().get("mesh.lane.ping")
    ledger = Ledger()
    params, entry_id = start_checkout(
        sku,
        customer_email="buyer@example.com",
        success_url="https://example.com/ok/{CHECKOUT_SESSION_ID}",
        cancel_url="https://example.com/cancel",
        ledger=ledger,
    )
    assert params["client_reference_id"] == str(entry_id)
    assert ledger.recognized_cents() == 0
    assert ledger.entries()[0]["status"] == "pending"


def test_webhook_signature_and_unpaid_checkout_does_not_fulfill() -> None:
    secret = "whsec_test_fixture"
    payload = json.dumps(
        {
            "id": "evt_1",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_1",
                    "payment_status": "unpaid",
                    "client_reference_id": "9",
                    "metadata": {"sku_id": "mesh.lane.ping"},
                }
            },
        }
    ).encode()
    timestamp = "1700000000"
    signed = timestamp.encode() + b"." + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    header = f"t={timestamp},v1={digest}"
    verify_signature(payload, header, secret, now=1_700_000_000)
    result = handle_webhook(payload, header, secret, now=1_700_000_000)
    assert result.action == "ignore"
    assert "unpaid" in (result.reason or "")


def test_async_payment_succeeded_recognizes_pending_row() -> None:
    sku = load_catalog().get("mesh.consult.discovery")
    ledger = Ledger()
    _, entry_id = start_checkout(
        sku,
        customer_email="buyer@example.com",
        success_url="https://example.com/ok/{CHECKOUT_SESSION_ID}",
        cancel_url="https://example.com/cancel",
        ledger=ledger,
    )
    event = {
        "id": "evt_2",
        "type": "checkout.session.async_payment_succeeded",
        "data": {
            "object": {
                "id": "cs_2",
                "payment_status": "paid",
                "client_reference_id": str(entry_id),
                "metadata": {"sku_id": sku.id},
            }
        },
    }
    result = route_event(event, ledger)
    assert result.action == "recognize"
    assert ledger.recognized_cents() == sku.amount_cents


def test_subscription_and_risk_events_are_required_routes() -> None:
    failed = {"type": "invoice.payment_failed", "data": {"object": {"id": "in_1"}}}
    dispute = {"type": "charge.dispute.created", "data": {"object": {"id": "dp_1"}}}
    deleted = {"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_1"}}}
    assert route_event(failed).action == "payment-failed"
    assert route_event(dispute).action == "risk-review"
    assert route_event(deleted).action == "cancel"


def test_portal_and_integration_identifier_shape() -> None:
    portal = build_customer_portal_session("cus_123", "https://pipefishlabs.io/account")
    assert portal["customer"] == "cus_123"
    token = integration_identifier()
    assert token.startswith("pipefish-")
    assert token.split("-")[1].isalpha()
    assert token.split("-")[1].islower()
