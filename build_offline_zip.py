from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path


EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "build_offline",
    "data",
    "venv",
}
EXCLUDE_NAMES = {".env", "offline_package.zip"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3"}

PROJECT_DIR = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_DIR / "build_offline"
PACKAGE_DIR = BUILD_DIR / "vibe-DataCollectorHub"
WHL_DIR = PACKAGE_DIR / "whl"
ZIP_FILE = PROJECT_DIR / "offline_package.zip"


def should_exclude(path: Path) -> bool:
    if set(path.parts) & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_NAMES:
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    if BUILD_DIR in path.parents or path == BUILD_DIR:
        return True
    if path == ZIP_FILE:
        return True
    return False


def clean_build_dir() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    PACKAGE_DIR.mkdir(parents=True)


def copy_project_files() -> None:
    for path in PROJECT_DIR.rglob("*"):
        if should_exclude(path):
            continue

        relative_path = path.relative_to(PROJECT_DIR)
        target_path = PACKAGE_DIR / relative_path

        if path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="打包 DataCollectorHub 源码，可选下载 pip 离线依赖。")
    parser.add_argument(
        "--pip",
        action="store_true",
        help="下载 pyproject.toml 中 dependencies 的离线依赖到 whl 目录。",
    )
    return parser.parse_args()


def download_wheels() -> None:
    pyproject = PROJECT_DIR / "pyproject.toml"
    if not pyproject.exists():
        raise FileNotFoundError(f"未找到 pyproject.toml：{pyproject}")

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    dependencies = data.get("project", {}).get("dependencies", [])
    if not dependencies:
        print("pyproject.toml 中未找到 [project].dependencies")
        return

    WHL_DIR.mkdir(parents=True, exist_ok=True)
    requirements_file = BUILD_DIR / "requirements.txt"
    requirements_file.write_text("\n".join(dependencies) + "\n", encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "-r",
            str(requirements_file),
            "-d",
            str(WHL_DIR),
        ],
        cwd=PROJECT_DIR,
        check=True,
    )


def make_zip() -> None:
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()

    with zipfile.ZipFile(ZIP_FILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in BUILD_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(BUILD_DIR))


def main() -> int:
    args = parse_args()
    try:
        clean_build_dir()
        copy_project_files()
        if args.pip:
            download_wheels()
        make_zip()
        print(f"打包完成：{ZIP_FILE}")
        return 0
    finally:
        shutil.rmtree(BUILD_DIR, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
