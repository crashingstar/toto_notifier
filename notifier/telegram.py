from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request


def send_message(token: str, chat_id: str | int, text: str, parse_mode: str | None = "HTML") -> None:
    """Send a Telegram message using the Bot API via stdlib only.

    See: https://core.telegram.org/bots/api#sendmessage
    """
    base = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": str(chat_id),
        "text": text,
        # Disable link previews by default to avoid noisy cards; customize as needed
        "disable_web_page_preview": "true",
    }
    if parse_mode:
        data["parse_mode"] = parse_mode

    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(base, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "toto-notifier/1.0"
    })

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Telegram HTTP error: {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Telegram network error: {e.reason}") from e

    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        raise RuntimeError("Telegram returned non-JSON response")

    if not payload.get("ok", False):
        # Telegram usually returns {ok:false, description:..., error_code:...}
        desc = payload.get("description", "Unknown error from Telegram")
        raise RuntimeError(f"Telegram API error: {desc}")

