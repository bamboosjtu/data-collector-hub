from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phase_scripts_pass() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    for script in sorted((Path(__file__).parent).glob("phase*.py")):
        subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env, check=True)
