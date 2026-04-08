"""
Playwright-based WIX page fetcher.

Manages a single browser session for efficiency. Usage:

    with WixFetcher() as fetcher:
        html = fetcher.fetch_post_page("https://www.elseyworld.com/post/portland-la")
        listing_html = fetcher.fetch_category_listing("south-pacific-1997")
"""
from playwright.sync_api import sync_playwright, Browser, Page

from migration.config import BASE_URL

# Selectors that indicate WIX blog content has rendered
_CONTENT_SELECTORS = [
    '[data-hook="post-description"]',
    '[data-hook="post-title"]',
    '[data-hook="post-list-pro-gallery-container"]',
    '[data-hook="post-list-item"]',
]

_LOAD_MORE_SELECTORS = [
    '[data-hook="load-more-button"]',
    'button[data-hook*="more"]',
    '[aria-label*="Show more"]',
    '[aria-label*="show more"]',
]


def _wait_for_content(page: Page, timeout_ms: int = 20000) -> None:
    """Wait for any WIX blog content selector to appear."""
    per_sel = timeout_ms // len(_CONTENT_SELECTORS)
    for sel in _CONTENT_SELECTORS:
        try:
            page.wait_for_selector(sel, timeout=per_sel)
            return
        except Exception:
            pass


def _scroll_to_load(page: Page, max_iters: int = 10, pause_ms: int = 1500) -> None:
    """Scroll the page repeatedly to trigger lazy loading / infinite scroll."""
    for _ in range(max_iters):
        prev_h = page.evaluate("document.body.scrollHeight")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(pause_ms)

        # Click any visible "load more" button
        for sel in _LOAD_MORE_SELECTORS:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    page.wait_for_timeout(1200)
                    break
            except Exception:
                pass

        new_h = page.evaluate("document.body.scrollHeight")
        if new_h == prev_h:
            break


class WixFetcher:
    """Reusable playwright fetcher for WIX blog pages."""

    def __init__(self, headless: bool = True):
        self._headless = headless
        self._pw = None
        self._browser: Browser | None = None

    def __enter__(self) -> "WixFetcher":
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self._headless)
        return self

    def __exit__(self, *_) -> None:
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _new_page(self) -> Page:
        return self._browser.new_page(viewport={"width": 1280, "height": 900})

    def fetch_post_page(self, url: str) -> str:
        """Fetch a WIX blog post page and return rendered HTML."""
        page = self._new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            _wait_for_content(page)
            page.wait_for_timeout(1500)
            # Scroll to trigger lazy image loading then return to top
            _scroll_to_load(page, max_iters=5, pause_ms=700)
            page.evaluate("window.scrollTo(0, 0)")
            return page.content()
        finally:
            page.close()

    def fetch_category_listing(self, category_slug: str) -> str:
        """Fetch a WIX category listing page, scrolling to load all posts."""
        url = f"{BASE_URL}/blog/categories/{category_slug}"
        page = self._new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            _scroll_to_load(page, max_iters=40, pause_ms=1200)
            return page.content()
        finally:
            page.close()

    def fetch_all_posts_listing(self) -> str:
        """Fetch the main /blog listing page, scrolling to load all ~86 posts."""
        url = f"{BASE_URL}/blog"
        page = self._new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            _scroll_to_load(page, max_iters=80, pause_ms=1500)
            return page.content()
        finally:
            page.close()
