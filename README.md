# TOTO Notifier (Playwright)

Fetch Singapore Pools TOTO summary via Playwright and send it to your Telegram chat.

## Prerequisites

- Python 3.10+
- Playwright and Chromium browser binaries

Install once:
```
pip install playwright
playwright install chromium
```

## Configure

Create `.env` with your Telegram credentials:

```
TELEGRAM_BOT_TOKEN=123456:ABCDEF_your_bot_token
TELEGRAM_CHAT_ID=000000000
# Optional
# MESSAGE_PARSE_MODE=HTML
# SP_URL=https://online.singaporepools.com/en/lottery
```

Notes:
- To find `TELEGRAM_CHAT_ID`, send a message to your bot and open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`.
- Leave `SP_URL` unset to use the default.

## Run

```
python -m notifier.toto_main
```

Windows runner:
```
run_toto.bat
```

## How It Works

- `notifier/spools.py`: Opens the lottery page, waits for the TOTO summary XHR, parses JSON, formats a message. Attempts to auto-accept cookie banners.
- `notifier/toto_main.py`: Loads env, fetches summary, sends the Telegram message.
- `notifier/telegram.py`: Sends messages via Telegram Bot API.
- `notifier/config.py`: Loads `.env` and exposes Telegram settings.

## Scheduling (Windows)

Use Task Scheduler to run `run_toto.bat` daily. Ensure Python is on PATH or activate your venv in the BAT file.

## Troubleshooting

- If the message fails, verify your bot token/chat ID and that you’ve started the bot (sent it a message).
- For debugging the scraper, switch to headful by editing `fetch_toto_summary_via_playwright(headless=False)`.
