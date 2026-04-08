"""
Debug helper: fetch a rendered WIX page and dump the HTML to a file for inspection.

Usage:
    uv run python -m migration.debug_fetch https://www.elseyworld.com/post/portland-la
    uv run python -m migration.debug_fetch https://www.elseyworld.com/blog/categories/south-pacific-1997
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def fetch_and_dump(url: str, output_path: Path, scroll: bool = True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        print(f"Fetching {url} ...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)

        if scroll:
            print("Scrolling to trigger lazy loading ...")
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)

        html = page.content()
        browser.close()

    output_path.write_text(html, encoding="utf-8")
    print(f"Saved {len(html):,} bytes to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    slug = url.rstrip("/").split("/")[-1]
    out = Path(f"/tmp/wix_debug_{slug}.html")
    fetch_and_dump(url, out)
