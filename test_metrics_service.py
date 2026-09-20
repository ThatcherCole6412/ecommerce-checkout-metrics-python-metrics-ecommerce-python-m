import os
from types import SimpleNamespace

from metrics_service import InfraiMetrics, Order, checkout_metrics, publish_order


def test_fulfillment_and_receipt_become_one_metrics_each():
    metrics = checkout_metrics(Order("o-7", 42.5, fulfilled=True, receipt_sent=False))
    values = {item["name"]: item["value"] for item in metrics}
    assert values == {"checkout.order_total": 42.5, "fulfillment.completed": 1, "receipt.sent": 0}


def test_publish_uses_explicit_post_and_bearer(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    calls = []

    def transport(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return SimpleNamespace(status_code=200, headers={}, json=lambda: {"ok": True, "data": {}})

    publish_order(Order("o-8", 10, True, True), InfraiMetrics(transport))
    assert len(calls) == 3
    assert all(call[0] == "POST" and "Bearer test-key" == call[2]["headers"]["Authorization"] for call in calls)
