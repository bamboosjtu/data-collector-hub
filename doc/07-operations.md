# Operations

Useful checks:

```sql
SELECT COUNT(*) FROM collection_batches;
SELECT COUNT(*) FROM collection_commands;
SELECT COUNT(*) FROM collection_requests;
SELECT COUNT(*) FROM raw_events;
SELECT COUNT(*) FROM collection_errors;
SELECT COUNT(*) FROM collection_checkpoints;
SELECT COUNT(*) FROM canonical_projects;
SELECT COUNT(*) FROM canonical_single_projects;
SELECT COUNT(*) FROM canonical_bid_sections;
SELECT COUNT(*) FROM canonical_work_points;
SELECT COUNT(*) FROM canonical_towers;
SELECT COUNT(*) FROM canonical_stations;
SELECT COUNT(*) FROM canonical_line_sections;
SELECT COUNT(*) FROM canonical_project_progress;
SELECT COUNT(*) FROM canonical_entity_observations;
SELECT COUNT(*) FROM canonical_relationships;
```

Use Streamlit only as an internal operations console for batch, request, raw,
error, checkpoint, processing, canonical, and health inspection.
