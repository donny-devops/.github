"""Slack Block Kit payloads for mesh events. Send via an incoming webhook."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .commerce import Sku


def deal_blocks(sku: Sku, *, source: str, status: str) -> dict[str, Any]:
    return {
        "text": f"{status.title()} {sku.name} (${sku.price_usd:,.0f})",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"PipeFish · {status.title()}"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*SKU*\n`{sku.id}`"},
                    {"type": "mrkdwn", "text": f"*Amount*\n${sku.price_usd:,.2f} / {sku.cadence}"},
                    {"type": "mrkdwn", "text": f"*Lane*\n{sku.lane}"},
                    {"type": "mrkdwn", "text": f"*Source*\n{source}"},
                ],
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": sku.description,
                    }
                ],
            },
        ],
    }


def post_webhook(payload: dict[str, Any], url: str | None = None) -> bool:
    """POST a Slack payload. No-ops when the webhook is unset."""
    target = url or os.environ.get("SLACK_WEBHOOK_URL")
    if not target:
        return False
    request = urllib.request.Request(
        target,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            return 200 <= response.status < 300
    except urllib.error.URLError:
        return False
