# save_rendered_page.py
# Usage:
#   pip install playwright beautifulsoup4
#   python -m playwright install chromium
#   python save_rendered_page.py "https://plasmodb.org/plasmo/app/static-content/PlasmoDB/mahpic.html" out_base

import sys
import time
import re 
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

STABILITY_WINDOW_S = 2.0      # how long the text length must stay unchanged
MAX_RENDER_WAIT_S  = 60.0     # hard cap for waiting

def wait_until_text_stable(page, min_chars: int = 500) -> None:
    """
    Wait until document.body.innerText length stops changing for STABILITY_WINDOW_S
    or until MAX_RENDER_WAIT_S is reached. Also requires a minimal length to avoid
    capturing skeleton screens.
    """
    start = time.time()
    last_len: Optional[int] = None
    last_change = time.time()

    while True:
        try:
            cur_len = page.evaluate("document.body && document.body.innerText ? document.body.innerText.length : 0")
        except Exception:
            cur_len = 0

        if last_len is None or cur_len != last_len:
            last_len = cur_len
            last_change = time.time()

        # small scroll to trigger lazy loaders
        page.evaluate("window.scrollBy(0, 1200)")
        page.wait_for_timeout(200)
        page.evaluate("window.scrollTo(0, 0)")

        stable_for = time.time() - last_change
        if cur_len >= min_chars and stable_for >= STABILITY_WINDOW_S:
            return
        if time.time() - start > MAX_RENDER_WAIT_S:
            return

def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)        # collapse all whitespace
    #text = re.sub(r"\n{2,}", "\n\n", text) 
    return text.strip()

def save_page(url: str, out_base: str) -> None:
    out_base = Path(out_base)
    out_base.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0.0.0 Safari/537.36")
        )
        page = context.new_page()
        page.set_default_timeout(60_000)

        page.goto(url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=20_000)
        except PWTimeout:
            pass

        # wait for rendered text to stabilize
        wait_until_text_stable(page, min_chars=500)

        # capture rendered HTML
        rendered_html = page.content()
        (out_base.with_suffix(".html")).write_text(rendered_html, encoding="utf-8")

        # capture single-file MHTML (like browser save-as single file)
        cdp = context.new_cdp_session(page)
        cdp.send("Page.enable")
        mhtml = cdp.send("Page.captureSnapshot", {"format": "mhtml"})  # includes inlined resources
        text = mhtml["data"]
        text = re.sub(r'\r\n', '\n', text)      # normalize CRLF to LF
        text = re.sub(r'\n\s*\n+', '\n', text)  # collapse multiple blank lines
        text = re.sub(r'[ \t]+', ' ', text)     # collapse runs of spaces or tabs
        text = text.strip()
        (out_base.with_suffix(".mhtml")).write_text(mhtml["data"], encoding="utf-8")

        # optional: extract plain text for downstream processing
        text = clean_text(rendered_html)
        (out_base.with_suffix(".txt")).write_text(text, encoding="utf-8")

        browser.close()

    print(f"Saved:\n  {out_base.with_suffix('.html')}\n  {out_base.with_suffix('.mhtml')}\n  {out_base.with_suffix('.txt')}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python save_rendered_page.py <url> <output_base_path_without_extension>")
        sys.exit(1)
    save_page(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
