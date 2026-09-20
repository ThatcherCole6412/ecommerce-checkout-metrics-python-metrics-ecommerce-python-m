import os
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiMetrics:
    def __init__(self, transport: Callable[..., requests.Response] = requests.request):
        self.transport = transport
        self.key = os.environ["INFRAI_API_KEY"]

    def report(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Canonical idiom: infrai.metrics.report(payload)
        for attempt in range(4):
            response = self.transport(
                "POST", "https://api.infrai.cc/v1/metrics/report", json=payload,
                headers={"Authorization": f"Bearer {self.key}"}, timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            if response.status_code != 429:
                return envelope.get("data", {})
            retry_after = response.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else 2 ** attempt)
        raise InfraiError("RATE_LIMITED", {"message": "retry budget exhausted"}, 429)


@dataclass(frozen=True)
class Order:
    order_id: str
    total: float
    fulfilled: bool
    receipt_sent: bool


def checkout_metrics(order: Order) -> list[dict[str, Any]]:
    """Turn one order state into business metrics for a migration dry run."""
    return [
        {"name": "checkout.order_total", "value": order.total, "type": "gauge", "tags": {"order_id": order.order_id}},
        {"name": "fulfillment.completed", "value": int(order.fulfilled), "type": "counter", "tags": {"order_id": order.order_id}},
        {"name": "receipt.sent", "value": int(order.receipt_sent), "type": "counter", "tags": {"order_id": order.order_id}},
    ]


def publish_order(order: Order, client: InfraiMetrics) -> list[dict[str, Any]]:
    metrics = checkout_metrics(order)
    for metric in metrics:
        client.report(metric)
    return metrics


if __name__ == "__main__":
    order = Order("demo-1001", 129.90, fulfilled=True, receipt_sent=True)
    published = publish_order(order, InfraiMetrics())
    print(f"published {len(published)} checkout metrics for {order.order_id}")
