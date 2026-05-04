# vibe-DataCollectorHub Rules

## Responsibility
This project is the DataHub.
It owns ingestion, raw event storage, canonical normalization, API keys, cache, scheduling, and serving APIs.

## Boundaries
- Do not implement DCP site login or page scraping here.
- Do not expose DCP raw fields directly to consumers.
- Source-specific mapping must live under processing/normalizers.
- Consumers must access data through serving APIs.

## Ingestion
- Validate SourceEvent schema.
- Store raw events before normalization.
- Use idempotency keys.
- Preserve raw payload for traceability.

## Serving
- Consumer APIs must enforce API key scopes.
- Sandbox APIs return sandbox DTOs, not raw DCP records.