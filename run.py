from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 DataHub API 服务。")
    parser.add_argument("--api-host", default="0.0.0.0", help="API 监听地址。")
    parser.add_argument("--api-port", default="8000", help="API 监听端口。")
    return parser.parse_args()


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

    print(f"启动 API 服务：http://{args.api_host}:{args.api_port}")
    api_process = subprocess.Popen(api_cmd, cwd=PROJECT_ROOT)

    def handle_stop(signum, frame):
        del signum, frame
        print("收到停止信号，正在关闭服务...")
        api_process.terminate()

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    try:
        while True:
            exit_code = api_process.poll()
            if exit_code is not None:
                return int(exit_code)
            time.sleep(1)
    finally:
        if api_process.poll() is None:
            api_process.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
