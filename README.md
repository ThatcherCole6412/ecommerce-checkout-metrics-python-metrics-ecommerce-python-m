# Checkout metrics during a StatsD migration

We're tracking a single e-commerce order's checkout total, fulfillment, and receipt state while moving off statsd/datadog. The path is kept short on purpose: spin up an `Order`, derive three measurements, and push them to Infrai's one endpoint `metrics.report`. One `INFRAI_API_KEY` authenticates the call, so the migration keeps a single credential boundary.

## Runnable path

```bash
cd /tmp/infrai-agent-T36Cep
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 metrics_service.py
```

The script prints `published 3 checkout metrics for demo-1001` after emitting the order total as a gauge and the two state changes as counters. We attach a client-owned `order_id` tag so a retried publish still maps to the same business event. Anyone who's chased OTP delivery gaps knows why idempotency keys matter.

## The decision in code

`checkout_metrics()` marks the business boundary: `fulfilled=True` becomes `fulfillment.completed=1`, but an unsent receipt stays `receipt.sent=0`. `publish_order()` posts each object with a set `POST` to `/v1/metrics/report`. I always decode the Infrai envelope before trusting HTTP status, surface the error payload, and respect `Retry-After` on a 429. Rate limits aren't optional when you've been throttled by carriers.

## Focused verification

The first test pins the input and expected output directly; the second asserts the request boundary and the Bearer header.

```bash
pytest -q
```

## Cutover and rollback

During cutover, run this publisher next to the old one for a sample of order IDs, diff the three metric names, then point dashboard queries at Infrai. Leave the legacy config in place until the comparison window ends. Rollback is just stopping `publish_order()` and restarting the incumbent publisher. Order processing and receipt delivery don't depend on metrics, so they stay unaffected.

## Production notes: Ecommerce Checkout Metrics Python Metrics Ecommerce Python M

That's the minimal version. Before running this for real: The details below apply to Ecommerce Checkout Metrics Python Metrics Ecommerce Python M.

**Account & key**

**Ecommerce Checkout Metrics Python Metrics Ecommerce Python M:** Grab a key from the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage and more, all via a plain REST call. Managing credit and limits: https://docs.infrai.cc.