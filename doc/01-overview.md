# Overview

The current DataHub release follows the workspace `MVP_ARCHITECTURE.md`.

Active chain:

```text
downloader /sync
  -> POST /ingestion/v1/batch
  -> collection_batches
  -> collection_commands
  -> collection_requests
  -> raw_events
  -> processing
  -> canonical_projects / canonical_single_projects / canonical_bid_sections / canonical_work_points / canonical_towers / canonical_stations / canonical_line_sections / canonical_project_progress
  -> canonical_entity_observations / canonical_relationships
  -> Domain API
```

Older ingestion designs are archived and must not be used for release work.
