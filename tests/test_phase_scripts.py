from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase_scripts_pass() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    for script in sorted((ROOT / "tests").glob("phase*.py")):
        subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env, check=True)
