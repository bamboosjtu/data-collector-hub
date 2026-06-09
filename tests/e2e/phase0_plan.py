from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    plan = ROOT / "plan.md"
    assert plan.exists(), "plan.md is missing"
    text = plan.read_text(encoding="utf-8")
    for phase in range(7):
        assert f"Phase {phase}" in text, f"Phase {phase} missing from plan.md"
    assert (ROOT / "tests").is_dir(), "tests directory is missing"
    assert (ROOT / "tests" / "fixtures" / "table_batch_v1").is_dir(), "TableBatch fixture directory is missing"
    print("phase0 ok")


if __name__ == "__main__":
    main()
