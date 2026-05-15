# Data Model

MVP raw-layer tables:

- `collection_batches`
- `collection_commands`
- `collection_requests`
- `raw_events`
- `collection_errors`
- `collection_checkpoints`

Processing tables:

- `processing_jobs`
- `normalizer_state`
- `canonical_projects`
- `canonical_single_projects`
- `canonical_bid_sections`
- `canonical_work_points`
- `canonical_towers`
- `canonical_stations`
- `canonical_line_sections`
- `canonical_project_progress`
- `canonical_entity_observations`
- `canonical_relationships`

`collection_checkpoints` tracks collection progress. `normalizer_state` tracks
processing progress.
