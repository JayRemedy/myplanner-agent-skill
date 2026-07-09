#!/usr/bin/env python3
"""Small dependency-free MyPlanner REST client for agent runtimes."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description="Call the MyPlanner REST API")
    parser.add_argument("method", help="HTTP method, for example GET or POST")
    parser.add_argument("path", help="REST path, for example /me or /boards")
    parser.add_argument("body", nargs="?", help="Optional JSON request body")
    parser.add_argument("--base-url", default=os.environ.get("MYPLANNER_BASE_URL", "https://myplanner.dev"))
    parser.add_argument("--token-stdin", action="store_true", help="Read the API token from stdin")
    args = parser.parse_args()

    token = sys.stdin.readline().strip() if args.token_stdin else os.environ.get("MYPLANNER_API_TOKEN", "")
    if not token:
        print("MYPLANNER_API_TOKEN is required (or use --token-stdin)", file=sys.stderr)
        return 2

    path = "/" + args.path.lstrip("/")
    url = args.base_url.rstrip("/") + "/app/rest.php" + path
    data = args.body.encode("utf-8") if args.body is not None else None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=args.method.upper())
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
            print(payload)
            return 0
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        print(payload or json.dumps({"error": str(exc), "status": exc.code}), file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps({"error": str(exc.reason)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
