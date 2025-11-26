#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv


def die(msg: str, payload: Any | None = None) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    if payload is not None:
        print(payload, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    load_dotenv()

    app_id = os.getenv("FB_CLIENT_ID")
    app_secret = os.getenv("FB_CLIENT_SECRET")
    page_id = os.getenv("FB_PAGE_ID")
    api_version = os.getenv("FB_GRAPH_API_VERSION", "v21.0")
    short_token = os.getenv("FB_PAGE_SHORT_TOKEN")

    if not app_id or not app_secret or not page_id or not short_token:
        die(
            "Missing one of required env vars: "
            "FB_CLIENT_ID, FB_CLIENT_SECRET, FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN"
        )

    base_url = f"https://graph.facebook.com/{api_version}"

    # 1) short-lived USER token -> long-lived USER token
    print("[INFO] Exchanging short-lived user token for long-lived...")
    r = requests.get(
        f"{base_url}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
        timeout=15,
    )
    if not r.ok:
        die("HTTP error during /oauth/access_token", r.text)

    data = r.json()
    long_user_token = data.get("access_token")
    expires_in = data.get("expires_in")

    if not long_user_token:
        die("No access_token in /oauth/access_token response", data)

    if expires_in is None:
        print("[INFO] Got long-lived user token. 'expires_in' is not present in response.")
        print("[DEBUG] Raw response from /oauth/access_token:", data)
    else:
        days = expires_in / 86400
        print(
            f"[INFO] Got long-lived user token, "
            f"expires_in ≈ {expires_in} seconds (~{days:.1f} days)"
        )

    # 2) long-lived USER token -> PAGE token for given FB_PAGE_ID
    print("[INFO] Fetching pages for this user...")
    r2 = requests.get(
        f"{base_url}/me/accounts",
        params={"access_token": long_user_token},
        timeout=15,
    )
    if not r2.ok:
        die("HTTP error during /me/accounts", r2.text)

    data2 = r2.json()
    pages = data2.get("data", [])
    if not isinstance(pages, list):
        die("Unexpected /me/accounts response", data2)

    page_token = None
    for page in pages:
        if page.get("id") == page_id:
            page_token = page.get("access_token")
            break

    if not page_token:
        die(f"Page with id {page_id} not found in /me/accounts", pages)

    print("\n[OK] New page access token obtained.\n")
    print("Add this line to your .env:\n")
    print(f"FB_PAGE_ACCESS_TOKEN={page_token}\n")


if __name__ == "__main__":
    main()
