"""Simple script to poll the FastAPI health endpoint.

This script demonstrates how to repeatedly query the `/health` endpoint of
the FastAPI application running locally (default port 8765).  It prints the
JSON response and the HTTP status code for each poll.

Usage:
    python poll_health.py [--host HOST] [--port PORT] [--interval SECONDS]

Example:
    python poll_health.py --interval 5

The script will run indefinitely until interrupted (Ctrl+C).
"""

import argparse
import time
from typing import Any

import httpx

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_INTERVAL = 5


def poll_health(host: str, port: int, interval: int) -> None:
    url = f"http://{host}:{port}/health"
    print(f"Polling {url} every {interval} seconds. Press Ctrl+C to stop.")
    while True:
        try:
            response = httpx.get(url, timeout=10.0)
            status = response.status_code
            try:
                data: Any = response.json()
            except Exception:
                data = response.text
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status: {status}, Response: {data}")
        except Exception as exc:
            print(f"Error polling {url}: {exc}")
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poll FastAPI health endpoint")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host where FastAPI is running")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port where FastAPI is listening")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="Seconds between polls")
    args = parser.parse_args()
    poll_health(args.host, args.port, args.interval)
