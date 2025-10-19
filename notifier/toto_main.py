from __future__ import annotations

import sys
import traceback
from datetime import datetime

from .config import get_config, load_env
from .spools import fetch_toto_summary_via_playwright, format_toto_message
from .telegram import send_message


def main() -> int:
    ts = datetime.now().isoformat(timespec="seconds")
    try:
        # Load env early to allow SP_* overrides too
        load_env()
        cfg = get_config()

        data = fetch_toto_summary_via_playwright(headless=True)
        text = format_toto_message(data)

        send_message(
            token=cfg["TELEGRAM_BOT_TOKEN"],
            chat_id=cfg["TELEGRAM_CHAT_ID"],
            text=text,
            parse_mode=cfg["MESSAGE_PARSE_MODE"],
        )
        print(f"[{ts}] Sent TOTO update successfully.")
        return 0
    except Exception as e:
        print(f"[{ts}] ERROR: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

