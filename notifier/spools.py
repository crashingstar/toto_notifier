from __future__ import annotations

import json
import os
import re
from typing import Any, Iterable


SP_DEFAULT_URL = "https://online.singaporepools.com/en/lottery"


def _import_playwright():
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "Playwright is required. Install with: pip install playwright && playwright install chromium"
        ) from e
    return sync_playwright


def fetch_toto_summary_via_playwright(headless: bool = True, timeout_ms: int = 30000) -> Any:
    """Navigate to Singapore Pools lottery page and scrape TOTO data from the DOM.

    Returns a dict with best-effort fields: jackpot, drawDate, drawNumber,
    winningNumbers (list), additionalNumber.
    """
    sync_playwright = _import_playwright()

    url = os.getenv("SP_URL", SP_DEFAULT_URL)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context()
        page = ctx.new_page()

        # Try to accept consent banners if present (best-effort)
        def _try_accept():
            try:
                page.get_by_role("button", name="Accept").click(timeout=1500)
            except Exception:
                try:
                    page.get_by_text("Accept All").first.click(timeout=1500)
                except Exception:
                    pass

        # Navigate and let content load
        page.goto(url, wait_until="domcontentloaded")
        _try_accept()
        page.wait_for_load_state("networkidle")

        # Locate the TOTO panel by relationship: a panel that has the TOTO logo
        container = page.locator(".sppl-panel:has(.logo--toto)").first
        container.wait_for(state="visible", timeout=timeout_ms)

        # Collect full text for regex fallback
        full_text = container.inner_text(timeout=timeout_ms)

        # Extract jackpot (prefer direct locator inside the panel)
        jackpot: str | None = None
        try:
            jp_el = container.locator(".slab--jackpot .slab__text--highlight").first
            jp_el.wait_for(state="visible", timeout=timeout_ms)
            txt = jp_el.inner_text(timeout=timeout_ms).strip()
            if txt:
                jackpot = txt
        except Exception:
            pass

        # Regex fallback on the full text
        if not jackpot:
            m_j = re.search(
                r"Estimated\s*Jackpot[^\n]*?((?:S\$|\$)?\s*[\d,]+(?:\.\d+)?\s*(?:million|m)?)",
                full_text,
                re.IGNORECASE,
            )
            if m_j:
                jackpot = m_j.group(1).strip()
            else:
                m_j2 = re.search(
                    r"Jackpot[^\n]*?((?:S\$|\$)?\s*[\d,]+(?:\.\d+)?\s*(?:million|m)?)",
                    full_text,
                    re.IGNORECASE,
                )
                if m_j2:
                    jackpot = m_j2.group(1).strip()

        # Draw date: prefer the dedicated element
        draw_date: str | None = None
        try:
            dd_el = container.locator(".lottery__draw-date").first
            dd_el.wait_for(state="visible", timeout=timeout_ms)
            draw_date = dd_el.inner_text(timeout=timeout_ms).strip()
        except Exception:
            m_dd = re.search(r"(\bMon|Tue|Wed|Thu|Fri|Sat|Sun\b[^\n]+)", full_text, re.IGNORECASE)
            if m_dd:
                draw_date = m_dd.group(1).strip()

        # Ensure jackpot is a clean single-line string
        if jackpot:
            jackpot = " ".join(jackpot.split())

        return {
            "jackpot": jackpot,
            "drawDate": draw_date,
        }


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _deep_find_first(data: Any, keys_ci: Iterable[str]) -> Any | None:
    """Depth-first search for first matching key (case-insensitive)."""
    target = {k.lower(): k for k in keys_ci}

    def _walk(obj: Any) -> Any | None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in target:
                    return v
                found = _walk(v)
                if found is not None:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = _walk(item)
                if found is not None:
                    return found
        return None

    return _walk(data)


def format_toto_message(data: Any) -> str:
    """Best-effort formatting for TOTO summary JSON.

    Tries common fields; falls back to pretty JSON if structure is unknown.
    """
    jackpot = _deep_find_first(data, ["estimatedJackpot", "jackpot", "jackpotPrize"])  # type: ignore
    draw_date = _deep_find_first(data, ["nextDrawDate", "drawDate", "date"])  # type: ignore
    numbers = _deep_find_first(data, ["winningNumbers", "numbers", "winningNum"])  # type: ignore
    bonus = _deep_find_first(data, ["additionalNumber", "additional", "bonus", "supplementary"])  # type: ignore

    parts: list[str] = []
    parts.append("<b>TOTO Summary</b>")
    if draw_date is not None:
        parts.append(f"Date: { _html_escape(str(draw_date)) }")
    if jackpot is not None:
        parts.append(f"Estimated Jackpot: { _html_escape(str(jackpot)) }")

    # Format numbers if present
    if isinstance(numbers, list) and numbers:
        try:
            main_nums = ", ".join(str(n) for n in numbers if n is not None)
        except Exception:
            main_nums = _html_escape(str(numbers))
        line = f"Numbers: { _html_escape(main_nums) }"
        if bonus is not None:
            line += f" | Additional: { _html_escape(str(bonus)) }"
        parts.append(line)

    # If we didn’t detect any of the above, pretty-print a compact JSON snapshot
    if len(parts) <= 1:
        snippet = json.dumps(data, indent=2, ensure_ascii=False)
        # Telegram messages are limited; keep it short
        snippet = snippet[:3500]
        parts.extend([
            "Could not recognize fields. Raw JSON:",
            f"<pre>{_html_escape(snippet)}</pre>",
        ])

    return "\n".join(parts)
