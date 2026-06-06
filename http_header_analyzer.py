#!/usr/bin/env python3
"""HTTP Header Analyzer

Usage:
    python3 http_header_analyzer.py https://example.com

If no URL is provided, the script will prompt for one.
"""

import argparse
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
        parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are supported.")
    return url


def fetch_headers(url: str) -> dict:
    request = Request(url, method="HEAD")
    with urlopen(request, timeout=15) as response:
        headers = dict(response.getheaders())
        headers["Status-Code"] = response.getcode()
        return headers


def fetch_headers_get(url: str) -> dict:
    request = Request(url, method="GET")
    with urlopen(request, timeout=15) as response:
        headers = dict(response.getheaders())
        headers["Status-Code"] = response.getcode()
        return headers


def print_header_report(url: str) -> None:
    print(f"Analyzing: {url}\n")
    try:
        headers = fetch_headers(url)
    except HTTPError as exc:
        print(f"HTTP Error: {exc.code} {exc.reason}")
        try:
            headers = dict(exc.headers.items())
            headers["Status-Code"] = exc.code
        except Exception:
            headers = {}
    except URLError as exc:
        print(f"URL Error: {exc.reason}")
        return
    except ValueError as exc:
        print(f"Invalid URL: {exc}")
        return
    except Exception as exc:
        print(f"Error fetching headers: {exc}")
        return

    status_code = headers.get("Status-Code")
    server = headers.get("Server", "N/A")
    content_type = headers.get("Content-Type", "N/A")

    print(f"Status Code: {status_code}")
    print(f"Server: {server}")
    print(f"Content-Type: {content_type}\n")

    print("Response Headers:")
    for name, value in sorted(headers.items()):
        if name == "Status-Code":
            continue
        print(f"{name}: {value}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze HTTP headers for a URL.")
    parser.add_argument("url", nargs="?", help="Target URL to analyze")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    url = args.url
    if not url:
        try:
            url = input("Enter URL: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nNo URL provided. Exiting.")
            return 1

    if not url:
        print("No URL provided. Exiting.")
        return 1

    try:
        url = normalize_url(url)
    except ValueError as exc:
        print(f"Invalid URL: {exc}")
        return 1

    print_header_report(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
