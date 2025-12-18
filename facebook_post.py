"""Facebook page posting utility and CLI using Graph API."""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict

import requests
from dotenv import dotenv_values, load_dotenv


class FacebookPostError(Exception):
    """Custom exception for Facebook posting errors."""


class FacebookPoster:
    """Wrapper around Facebook Graph API for page posts."""

    def __init__(
        self,
        page_id: str | None = None,
        access_token: str | None = None,
        api_version: str | None = None,
    ) -> None:
        load_dotenv()
        self._timeout_s = self._load_timeout()

        self.page_id = page_id or os.getenv("FB_PAGE_ID")
        self.access_token = access_token or os.getenv("FB_PAGE_ACCESS_TOKEN")
        self.api_version = api_version or os.getenv("FB_GRAPH_API_VERSION")

        missing = [
            name
            for name, value in (
                ("FB_PAGE_ID", self.page_id),
                ("FB_PAGE_ACCESS_TOKEN", self.access_token),
                ("FB_GRAPH_API_VERSION", self.api_version),
            )
            if not value
        ]
        if missing:
            raise FacebookPostError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        self.base_url = f"https://graph.facebook.com/{self.api_version}/"

    def create_post(self, message: str, link: str | None = None) -> Dict[str, Any]:
        """
        Send a post to the Facebook page feed.

        Args:
            message: Text content of the post.
            link: Optional URL to attach.

        Returns:
            Parsed JSON response from Facebook.

        Raises:
            FacebookPostError: When the request fails or Facebook returns an error.
        """

        if not message:
            raise FacebookPostError("Message is required for a Facebook post.")

        url = f"{self.base_url}{self.page_id}/feed"
        payload = {"message": message, "access_token": self.access_token}
        if link:
            payload["link"] = link

        try:
            response = requests.post(url, data=payload, timeout=self._timeout_s)
        except requests.RequestException as exc:  # pragma: no cover - network failure path
            raise FacebookPostError(f"Failed to reach Facebook API: {exc}") from exc

        try:
            data = response.json()
        except ValueError:
            raise FacebookPostError(
                f"Invalid JSON response from Facebook (status {response.status_code})."
            )

        if response.status_code >= 400 or "error" in data:
            raise FacebookPostError(self._build_error_message(response, data))

        return data

    @staticmethod
    def _build_error_message(response: requests.Response, data: Dict[str, Any]) -> str:
        error_details = data.get("error", {}) if isinstance(data, dict) else {}
        message = error_details.get("message")
        error_type = error_details.get("type")
        error_code = error_details.get("code")

        parts = [f"status {response.status_code}"]
        if error_type:
            parts.append(f"type {error_type}")
        if error_code is not None:
            parts.append(f"code {error_code}")
        if message:
            parts.append(message)

        if not message and not error_details:
            parts.append("Unknown error response from Facebook.")

        return "Facebook API error (" + ", ".join(parts) + ")"

    @staticmethod
    def _load_timeout() -> float:
        cfg = dotenv_values()
        raw_timeout = cfg.get("FACEBOOK_TIMEOUT")
        if raw_timeout is None:
            raise RuntimeError("FACEBOOK_TIMEOUT is not set in .env")

        try:
            timeout_s = float(raw_timeout)
        except (TypeError, ValueError) as exc:
            raise RuntimeError("FACEBOOK_TIMEOUT must be a number greater than 0") from exc

        if timeout_s <= 0:
            raise RuntimeError("FACEBOOK_TIMEOUT must be greater than 0")

        return timeout_s


def post_message(message: str, link: str | None = None) -> Dict[str, Any]:
    """Helper for posting a message using environment configuration."""

    poster = FacebookPoster()
    return poster.create_post(message, link)


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}...{token[-4:]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a post to a Facebook page")
    parser.add_argument(
        "-m",
        "--message",
        required=True,
        help="Text of the post to publish.",
    )
    parser.add_argument(
        "-l",
        "--link",
        help="Optional link to attach to the post.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the request details without sending it.",
    )

    args = parser.parse_args()

    try:
        poster = FacebookPoster()
    except FacebookPostError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)

    url = f"{poster.base_url}{poster.page_id}/feed"
    payload = {"message": args.message, "access_token": poster.access_token}
    if args.link:
        payload["link"] = args.link

    if args.dry_run:
        display_payload = payload.copy()
        display_payload["access_token"] = _mask_token(poster.access_token)
        print("Dry run: would send POST request")
        print(f"URL: {url}")
        print("Parameters:")
        for key, value in display_payload.items():
            print(f"  {key}: {value}")
        return

    try:
        result = poster.create_post(args.message, args.link)
    except FacebookPostError as exc:
        print(f"Error posting to Facebook: {exc}")
        sys.exit(1)

    post_id = result.get("id", "<unknown>")
    print("Post created successfully.")
    print(f"Post ID: {post_id}")


if __name__ == "__main__":
    main()
