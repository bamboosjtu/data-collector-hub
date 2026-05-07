"""Runtime config validation for plugins."""

from typing import Any


VALID_DCP_COLLECTIONS = {"safePages", "projectPages", "planPages"}
VALID_DCP_SCOPES = {
    "standalone",
    "snapshot",
    "date_partitioned",
    "project",
    "project_snapshot",
    "project_single",
}
VALID_CHECKPOINT_MODES = {
    "cursor",
    "timestamp",
    "page",
    "date_partition",
    "mixed",
}
REQUIRED_DCP_ENABLED_DATASETS = {
    "daily_meeting",
    "tower",
    "station",
    "line_section",
    "project_preconstruction",
    "year_progress",
}
SENSITIVE_CONFIG_KEYS = {
    "account",
    "username",
    "password",
    "passwd",
    "token",
    "cookie",
    "authorization",
}
ALLOWED_SECRET_REFERENCE_KEYS = {"credentials_profile", "secret_ref"}


def _find_sensitive_config_paths(value: Any, path: str = "") -> list[str]:
    if isinstance(value, dict):
        sensitive_paths: list[str] = []
        for key, nested_value in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            normalized_key = str(key).lower()
            if (
                normalized_key in SENSITIVE_CONFIG_KEYS
                and normalized_key not in ALLOWED_SECRET_REFERENCE_KEYS
            ):
                sensitive_paths.append(key_path)
            sensitive_paths.extend(_find_sensitive_config_paths(nested_value, key_path))
        return sensitive_paths
    if isinstance(value, list):
        sensitive_paths = []
        for index, item in enumerate(value):
            key_path = f"{path}[{index}]" if path else f"[{index}]"
            sensitive_paths.extend(_find_sensitive_config_paths(item, key_path))
        return sensitive_paths
    return []


def validate_plugin_runtime_config(plugin_id: str, config: dict[str, Any]) -> list[str]:
    """Validate plugin runtime config."""
    errors: list[str] = []

    if plugin_id != "dcp":
        return errors

    datasets = config.get("datasets")
    if not isinstance(datasets, dict):
        return ["datasets must be an object"]

    dataset_keys = set(datasets.keys())

    plaintext_keys = sorted(_find_sensitive_config_paths(config))
    if plaintext_keys:
        errors.append(
            f"plaintext credential fields are not allowed: {', '.join(plaintext_keys)}"
        )

    enabled_datasets = config.get("enabled_datasets", [])
    if not isinstance(enabled_datasets, list):
        errors.append("enabled_datasets must be an array")
    else:
        unknown = set(enabled_datasets) - dataset_keys
        if unknown:
            errors.append(
                f"enabled_datasets contains unknown datasets: {sorted(unknown)}"
            )
        missing_required = REQUIRED_DCP_ENABLED_DATASETS - set(enabled_datasets)
        if missing_required:
            errors.append(
                f"enabled_datasets missing required DCP datasets: {sorted(missing_required)}"
            )
        for dataset_key in enabled_datasets:
            dataset = datasets.get(dataset_key)
            if isinstance(dataset, dict) and dataset.get("enabled") is not True:
                errors.append(
                    f"enabled_datasets contains disabled dataset: {dataset_key}"
                )

    monitor_datasets = config.get("monitor_datasets", [])
    if not isinstance(monitor_datasets, list):
        errors.append("monitor_datasets must be an array")
    else:
        unknown = set(monitor_datasets) - dataset_keys
        if unknown:
            errors.append(
                f"monitor_datasets contains unknown datasets: {sorted(unknown)}"
            )
        if isinstance(enabled_datasets, list):
            not_enabled = set(monitor_datasets) - set(enabled_datasets)
            if not_enabled:
                errors.append(
                    f"monitor_datasets must be a subset of enabled_datasets: {sorted(not_enabled)}"
                )
        for dataset_key in monitor_datasets:
            dataset = datasets.get(dataset_key)
            if isinstance(dataset, dict) and dataset.get("expose_to_monitor") is not True:
                errors.append(
                    f"monitor_datasets contains dataset not exposed to monitor: {dataset_key}"
                )

    checkpoint_mode = config.get("checkpoint_mode")
    if checkpoint_mode not in VALID_CHECKPOINT_MODES:
        errors.append(
            f"checkpoint_mode must be one of: {sorted(VALID_CHECKPOINT_MODES)}"
        )

    scheduler = config.get("scheduler")
    if scheduler is not None:
        if not isinstance(scheduler, dict):
            errors.append("scheduler must be an object")
        else:
            if "enabled" in scheduler and not isinstance(scheduler["enabled"], bool):
                errors.append("scheduler.enabled must be boolean")
            if "tick_interval_seconds" in scheduler:
                tick_interval = scheduler["tick_interval_seconds"]
                if not isinstance(tick_interval, int) or tick_interval <= 0:
                    errors.append(
                        "scheduler.tick_interval_seconds must be a positive integer"
                    )

    collection_profiles = config.get("collection_profiles")
    if collection_profiles is not None:
        if not isinstance(collection_profiles, dict):
            errors.append("collection_profiles must be an object")
        else:
            for profile_name, profile in collection_profiles.items():
                if not isinstance(profile, dict):
                    errors.append(
                        f"collection_profiles.{profile_name} must be an object"
                    )
                    continue
                if "datasets" in profile and not isinstance(profile["datasets"], list):
                    errors.append(
                        f"collection_profiles.{profile_name}.datasets must be an array"
                    )
                if "schedule_cron" in profile and not isinstance(
                    profile["schedule_cron"], str
                ):
                    errors.append(
                        f"collection_profiles.{profile_name}.schedule_cron must be a string"
                    )

    for dataset_key, dataset in datasets.items():
        if not isinstance(dataset, dict):
            errors.append(f"datasets.{dataset_key} must be an object")
            continue

        collection = dataset.get("collection")
        if collection not in VALID_DCP_COLLECTIONS:
            errors.append(
                f"datasets.{dataset_key}.collection must be one of: {sorted(VALID_DCP_COLLECTIONS)}"
            )

        scope = dataset.get("scope")
        if scope not in VALID_DCP_SCOPES:
            errors.append(
                f"datasets.{dataset_key}.scope must be one of: {sorted(VALID_DCP_SCOPES)}"
            )

        if "enabled" in dataset and not isinstance(dataset["enabled"], bool):
            errors.append(f"datasets.{dataset_key}.enabled must be boolean")

        if "expose_to_monitor" in dataset and not isinstance(
            dataset["expose_to_monitor"], bool
        ):
            errors.append(f"datasets.{dataset_key}.expose_to_monitor must be boolean")

        if "processing_supported" in dataset and not isinstance(
            dataset["processing_supported"], bool
        ):
            errors.append(f"datasets.{dataset_key}.processing_supported must be boolean")

    return errors
