from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="同时启动 DataHub API 服务和 Streamlit 管理界面。")
    parser.add_argument("--api-host", default="0.0.0.0", help="API 监听地址。")
    parser.add_argument("--api-port", default="8000", help="API 监听端口。")
    parser.add_argument("--dashboard-host", default="0.0.0.0", help="管理界面监听地址。")
    parser.add_argument("--dashboard-port", default="8501", help="管理界面监听端口。")
    return parser.parse_args()


def _popen(command: list[str]) -> subprocess.Popen:
    return subprocess.Popen(command, cwd=PROJECT_ROOT)


def _terminate(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    deadline = time.time() + 10
    for process in processes:
        remaining = max(0.1, deadline - time.time())
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    args = parse_args()

    api_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.datahub.app:app",
        "--host",
        str(args.api_host),
        "--port",
        str(args.api_port),
    ]
    dashboard_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard/app.py",
        "--server.address",
        str(args.dashboard_host),
        "--server.port",
        str(args.dashboard_port),
    ]

    print(f"启动 API 服务：http://{args.api_host}:{args.api_port}")
    api_process = _popen(api_cmd)
    print(f"启动管理界面：http://{args.dashboard_host}:{args.dashboard_port}")
    dashboard_process = _popen(dashboard_cmd)
    processes = [api_process, dashboard_process]

    stopping = False

    def handle_stop(signum, frame):
        nonlocal stopping
        del signum, frame
        if not stopping:
            stopping = True
            print("收到停止信号，正在关闭服务...")
            _terminate(processes)

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    try:
        while True:
            for process in processes:
                exit_code = process.poll()
                if exit_code is not None:
                    _terminate(processes)
                    return int(exit_code)
            time.sleep(1)
    finally:
        _terminate(processes)


if __name__ == "__main__":
    raise SystemExit(main())
