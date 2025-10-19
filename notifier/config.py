import os
from pathlib import Path


def load_env(dotenv_path: str | os.PathLike | None = None) -> None:
    """Load a simple .env file into os.environ if present.

    Supports lines like KEY=VALUE, ignores comments (# ...) and blank lines.
    Does not override keys that already exist in the environment.
    """
    path = Path(dotenv_path) if dotenv_path else Path.cwd() / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        # Strip simple surrounding quotes
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def get_config() -> dict:
    """Return config dict from env vars for the Playwright flow.

    Calls load_env() implicitly and only returns Telegram-related settings.
    """
    # Attempt to load a .env from the project root by default
    load_env()
    return {
        "TELEGRAM_BOT_TOKEN": require_env("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": require_env("TELEGRAM_CHAT_ID"),
        # Optional
        "MESSAGE_PARSE_MODE": os.getenv("MESSAGE_PARSE_MODE", "HTML"),
    }
