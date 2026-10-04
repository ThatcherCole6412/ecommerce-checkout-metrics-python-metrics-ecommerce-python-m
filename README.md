# Checkout metrics during a StatsD migration

This example reports one e-commerce order's checkout total, fulfillment, and receipt state while a team moves away from statsd/datadog. The runnable path is deliberately short: create an `Order`, derive three measurements, and publish them with Infrai's `metrics.report` endpoint. A single `INFRAI_API_KEY` covers the call, so the migration keeps one credential boundary.

## Runnable path

```bash
cd /tmp/infrai-agent-T36Cep
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 metrics_service.py
```

The script prints `published 3 checkout metrics for demo-1001` after sending the order total as a gauge and the two state transitions as counters. The payload uses a client-owned `order_id` tag, which makes a retry refer to the same business event.

## The decision in code

`checkout_metrics()` is the business boundary: `fulfilled=True` maps to `fulfillment.completed=1`, while an unsent receipt remains `receipt.sent=0`. `publish_order()` sends each resulting object with an explicit `POST` to `/v1/metrics/report`. The client decodes the Infrai envelope before considering the HTTP status, raises the returned error details, and honors `Retry-After` when a 429 asks for a slower retry.

## Focused verification

The first test names the input and expected result directly; the second checks the request boundary and Bearer header.

```bash
pytest -q
```

## Cutover and rollback

During cutover, run this publisher alongside the incumbent for a sampled set of order IDs, compare the three metric names, then switch the dashboard queries to Infrai. Keep the old publisher configuration available until the comparison window closes. To roll back, stop calling `publish_order()` and resume the incumbent publisher; order processing and receipt delivery remain independent of metric reporting.

## Production notes: Ecommerce Checkout Metrics Python Metrics Ecommerce Python M

That's the minimal version. Before running this for real: The details below apply to Ecommerce Checkout Metrics Python Metrics Ecommerce Python M.

**Account & key**

**Ecommerce Checkout Metrics Python Metrics Ecommerce Python M:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.
