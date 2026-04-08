"""
Parse rendered WIX blog HTML into structured PostData and PostCard objects.

Key WIX HTML patterns (confirmed from live page inspection):
  - Post title:      <h1 data-hook="post-title">
  - Post date:       <span data-hook="time-ago" title="Feb 1, 1997">
  - Post body:       <section data-hook="post-description">
  - Images:          <figure data-hook="figure-IMAGE"> containing
                       <wow-image id="{wix-uri}" data-image-info='{"alignType":"...","imageData":{"uri":"..."}}'>
                       <figcaption> (optional)
  - Category links:  <a href="https://www.elseyworld.com/blog/categories/{slug}">
  - Metadata:        JSON-LD <script type="application/ld+json"> with headline, datePublished, description, image
  - Listing cards:   <div class="...post-list-item..."> with [data-hook="post-title"] and [data-hook="post-description"]
"""

import json
import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from bs4 import BeautifulSoup, NavigableString, Tag

from migration.config import BASE_URL, WIXSTATIC_CDN, WIXDOC_CDN, IGNORED_CATEGORIES

# UTC+10 (AEST, used for all post dates)
AEST = timezone(timedelta(hours=10))


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ImageInfo:
    """Metadata for one image found in a post body."""
    wix_uri: str        # WIX media filename, e.g. "ebf3d7_da38...~mv2.jpg"
    align: str          # "center", "left", or "right"
    alt: str
    caption: str
    placeholder: str    # unique token inserted into markdown body, e.g. "___IMG_0___"


@dataclass
class DocInfo:
    """Metadata for a linked document (PDF/DOC)."""
    doc_url: str        # full https://docs.wixstatic.com/... URL
    link_text: str
    placeholder: str    # e.g. "___DOC_0___"


@dataclass
class PostCard:
    """Summary data scraped from a category listing page."""
    url: str
    slug: str
    title: str
    description: str    # truncated excerpt from listing page


@dataclass
class PostData:
    """Full data for one post, ready for markdown rendering."""
    url: str
    slug: str
    title: str
    description: str        # from JSON-LD or listing page
    date_iso: str           # e.g. "2002-04-10T00:00:00.000+10:00"
    category_slugs: list[str] = field(default_factory=list)
    images: list[ImageInfo] = field(default_factory=list)
    docs: list[DocInfo] = field(default_factory=list)
    cover_image_uri: str = ""   # WIX URI of the JSON-LD cover image
    markdown_body: str = ""     # body with ___IMG_N___ / ___DOC_N___ placeholders


# ---------------------------------------------------------------------------
# Listing page parser
# ---------------------------------------------------------------------------

def parse_listing(html: str) -> list[PostCard]:
    """
    Parse a WIX category (or main blog) listing page.
    Returns PostCard list in page order.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards: list[PostCard] = []
    seen: set[str] = set()

    # Post cards are divs containing the "post-list-item" class
    for card in soup.find_all(class_=re.compile(r"\bpost-list-item\b")):
        # Find the primary post link
        link = card.find("a", href=re.compile(r"/post/"))
        if not link:
            continue
        href = link.get("href", "")
        if not href:
            continue

        # Build absolute URL and extract slug
        if href.startswith("/"):
            href = BASE_URL + href
        slug_match = re.search(r"/post/([^/?#]+)", href)
        if not slug_match:
            continue
        slug = slug_match.group(1)
        if slug in seen:
            continue
        seen.add(slug)

        # Title: look for data-hook="post-title" h2 inside card
        title_el = card.find(attrs={"data-hook": "post-title"})
        title = title_el.get_text(strip=True) if title_el else slug

        # Description: data-hook="post-description" inside card
        desc_el = card.find(attrs={"data-hook": "post-description"})
        description = desc_el.get_text(strip=True) if desc_el else ""

        cards.append(PostCard(
            url=f"{BASE_URL}/post/{slug}",
            slug=slug,
            title=title,
            description=description,
        ))

    return cards


# ---------------------------------------------------------------------------
# Post detail page parser
# ---------------------------------------------------------------------------

def parse_post(html: str, url: str) -> PostData:
    """
    Parse a WIX blog post detail page into PostData.
    Images and docs in the body are replaced with placeholders.
    """
    soup = BeautifulSoup(html, "html.parser")
    slug = _slug_from_url(url)

    # --- Metadata from JSON-LD ---
    ld = _extract_jsonld(soup)

    title = _extract_title(soup, ld)
    date_iso = _extract_date(soup, ld)
    description = _clean_description(ld.get("description", "").strip())
    cover_image_uri = _extract_cover_image_uri(ld)
    category_slugs = _extract_post_category_slugs(soup)

    # --- Body content ---
    body_section = soup.find(attrs={"data-hook": "post-description"})
    images: list[ImageInfo] = []
    docs: list[DocInfo] = []
    markdown_body = ""

    if body_section:
        _replace_figures_with_placeholders(body_section, images)
        _replace_doc_links_with_placeholders(body_section, docs)
        markdown_body = _convert_body_to_markdown(body_section).strip()

    return PostData(
        url=url,
        slug=slug,
        title=title,
        description=description,
        date_iso=date_iso,
        category_slugs=category_slugs,
        images=images,
        docs=docs,
        cover_image_uri=cover_image_uri,
        markdown_body=markdown_body,
    )


# ---------------------------------------------------------------------------
# Internal helpers — metadata extraction
# ---------------------------------------------------------------------------

def _slug_from_url(url: str) -> str:
    m = re.search(r"/post/([^/?#]+)", url)
    return m.group(1) if m else url.rstrip("/").split("/")[-1]


def _extract_jsonld(soup: BeautifulSoup) -> dict:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict) and data.get("@type") in ("BlogPosting", "Article", "NewsArticle"):
                return data
            # Sometimes it's a list
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") in ("BlogPosting", "Article"):
                        return item
        except (json.JSONDecodeError, AttributeError):
            pass
    return {}


def _extract_title(soup: BeautifulSoup, ld: dict) -> str:
    # Prefer rendered h1
    el = soup.find("h1", attrs={"data-hook": "post-title"})
    if el:
        return el.get_text(strip=True)
    el = soup.find(attrs={"data-hook": "post-title"})
    if el:
        h1 = el.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return el.get_text(strip=True)
    # Fallback: JSON-LD
    return ld.get("headline", "").strip()


def _extract_date(soup: BeautifulSoup, ld: dict) -> str:
    """
    Return an ISO-8601 date string in AEST (+10:00).
    Source: JSON-LD datePublished (preferred) or time-ago span title.
    Time is normalised to 00:00:00 on the AEST calendar date.
    """
    raw = ld.get("datePublished", "")
    if raw:
        try:
            # Parse UTC timestamp and convert to AEST date
            dt_utc = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            dt_aest = dt_utc.astimezone(AEST)
            # Use midnight AEST on that calendar date
            dt_out = dt_aest.replace(hour=0, minute=0, second=0, microsecond=0)
            return dt_out.isoformat(timespec="milliseconds")
        except ValueError:
            pass

    # Fallback: span data-hook="time-ago" title attribute (e.g. "Feb 1, 1997")
    span = soup.find("span", attrs={"data-hook": "time-ago"})
    if span:
        title_attr = span.get("title", "")
        try:
            dt = datetime.strptime(title_attr, "%b %d, %Y")
            dt = dt.replace(tzinfo=AEST)
            return dt.isoformat(timespec="milliseconds")
        except ValueError:
            pass

    return ""


def _extract_cover_image_uri(ld: dict) -> str:
    """Extract the WIX URI from the JSON-LD image field."""
    img = ld.get("image", {})
    if isinstance(img, dict):
        url = img.get("url", "")
    elif isinstance(img, str):
        url = img
    else:
        return ""

    # Strip CDN base and transform params to get just the WIX URI
    if WIXSTATIC_CDN in url:
        uri = url.replace(WIXSTATIC_CDN, "")
        # Strip /v1/... transform suffix
        uri = re.sub(r"/v1/.*", "", uri)
        return uri
    return ""


def _clean_description(text: str) -> str:
    """Strip WIX-added 'Learn more ....' suffix and other noise from descriptions."""
    text = re.sub(r"\s*Learn more\s*\.{1,4}\s*$", "", text, flags=re.IGNORECASE).strip()
    return text


def _extract_post_category_slugs(soup: BeautifulSoup) -> list[str]:
    """
    Find the category slugs that belong to this specific post.
    WIX renders category navigation links (all categories) on every page, so we look
    specifically in the post metadata / tag area rather than the whole page.

    The post's own categories are shown in a metadata section near the title or at
    the bottom of the post, typically inside a container with data-hook="post-metadata"
    or similar. We look for category links that are NOT inside the site navigation.
    """
    slugs = []
    seen: set[str] = set()

    # Try to find category links specifically in the post metadata sections
    # WIX post metadata is in elements with data-hook containing "tag", "category", or "metadata"
    metadata_hooks = ["post-metadata", "post-tags", "categories", "tag-list", "hashtag-list"]
    metadata_containers = []
    for hook in metadata_hooks:
        metadata_containers.extend(soup.find_all(attrs={"data-hook": re.compile(hook, re.IGNORECASE)}))

    search_scope = metadata_containers if metadata_containers else [soup]

    for container in search_scope:
        for a in container.find_all("a", href=re.compile(r"/blog/categories/")):
            href = a.get("href", "")
            m = re.search(r"/blog/categories/([^/?#]+)", href)
            if m:
                slug = m.group(1).rstrip("/")
                if slug not in seen:
                    seen.add(slug)
                    slugs.append(slug)

    # If still nothing found, fall back to all category links on the page
    # (navigation noise — caller should filter with IGNORED_CATEGORIES + CATEGORY_MAP)
    if not slugs:
        for a in soup.find_all("a", href=re.compile(r"/blog/categories/")):
            href = a.get("href", "")
            m = re.search(r"/blog/categories/([^/?#]+)", href)
            if m:
                slug = m.group(1).rstrip("/")
                if slug not in seen:
                    seen.add(slug)
                    slugs.append(slug)

    return slugs


# ---------------------------------------------------------------------------
# Internal helpers — image / doc placeholder substitution
# ---------------------------------------------------------------------------

# Alt text patterns that indicate WIX navigation UI images (not content)
_NAV_IMAGE_ALT_PATTERNS = re.compile(
    r"go to (next|previous)|next blog post|previous blog post", re.IGNORECASE
)


def _replace_figures_with_placeholders(body: Tag, images: list[ImageInfo]) -> None:
    """
    Find all <figure data-hook="figure-IMAGE"> in the body tree,
    extract their metadata, and replace the figure with a placeholder.
    Navigation/UI images (e.g. next-post buttons) are removed entirely.
    """
    for figure in body.find_all("figure", attrs={"data-hook": "figure-IMAGE"}):
        wix_uri, align, alt, caption = _extract_image_info(figure)

        # Skip WIX navigation/UI images
        if _NAV_IMAGE_ALT_PATTERNS.search(alt):
            _remove_figure_wrapper(body, figure)
            continue

        # Skip very small images (likely UI elements, e.g. 123×37 nav buttons)
        wow = figure.find("wow-image")
        if wow:
            try:
                info = json.loads(wow.get("data-image-info", "{}"))
                w = info.get("imageData", {}).get("width", 9999)
                h = info.get("imageData", {}).get("height", 9999)
                if w < 150 and h < 150:
                    _remove_figure_wrapper(body, figure)
                    continue
            except (json.JSONDecodeError, AttributeError):
                pass

        idx = len(images)
        placeholder = f"___IMG_{idx}___"
        images.append(ImageInfo(
            wix_uri=wix_uri,
            align=align,
            alt=alt,
            caption=caption,
            placeholder=placeholder,
        ))

        _remove_figure_wrapper(body, figure, placeholder)


def _remove_figure_wrapper(body: Tag, figure: Tag, placeholder: str = "") -> None:
    """
    Walk up from a figure to its outermost single-child wrapper div,
    then replace it with a placeholder NavigableString (or remove it if no placeholder).
    """
    target = figure
    for _ in range(4):
        parent = target.parent
        if parent and parent.name in ("div",) and parent is not body:
            # Only walk up if the parent's only meaningful content is this image
            real_children = [c for c in parent.children
                             if not (isinstance(c, NavigableString) and not c.strip())]
            if len(real_children) <= 1:
                target = parent
            else:
                break
        else:
            break

    if placeholder:
        target.replace_with(NavigableString(f"\n\n{placeholder}\n\n"))
    else:
        target.replace_with(NavigableString(""))


def _extract_image_info(figure: Tag) -> tuple[str, str, str, str]:
    """Return (wix_uri, align, alt, caption) from a figure element."""
    wix_uri = ""
    align = "center"
    alt = ""
    caption = ""

    # WIX URI from <wow-image id="..."> (most reliable)
    wow = figure.find("wow-image")
    if wow:
        wix_uri = wow.get("id", "")
        # Parse data-image-info JSON for alignType
        info_raw = wow.get("data-image-info", "")
        if info_raw:
            try:
                info = json.loads(info_raw)
                align = info.get("alignType", "center").lower()
            except (json.JSONDecodeError, AttributeError):
                pass

    # Fallback: img src → strip transforms
    if not wix_uri:
        img = figure.find("img")
        if img:
            src = img.get("src", "")
            if WIXSTATIC_CDN in src:
                uri = src.replace(WIXSTATIC_CDN, "")
                wix_uri = re.sub(r"/v1/.*", "", uri)

    # Alt text from <img alt="...">
    img = figure.find("img")
    if img:
        alt = img.get("alt", "")

    # Caption from <figcaption>
    cap_el = figure.find("figcaption")
    if cap_el:
        caption = cap_el.get_text(strip=True)

    return wix_uri, align, alt, caption


def _replace_doc_links_with_placeholders(body: Tag, docs: list[DocInfo]) -> None:
    """
    Replace <a href="https://docs.wixstatic.com/..."> links with placeholder text.
    The placeholder is later substituted with a local file link.
    """
    for a in body.find_all("a", href=re.compile(r"docs\.wixstatic\.com")):
        idx = len(docs)
        placeholder = f"___DOC_{idx}___"
        doc_url = a.get("href", "")
        link_text = a.get_text(strip=True)
        docs.append(DocInfo(doc_url=doc_url, link_text=link_text, placeholder=placeholder))
        a.replace_with(placeholder)


# ---------------------------------------------------------------------------
# Internal helpers — HTML → Markdown converter
# ---------------------------------------------------------------------------

# Tags we completely ignore (don't recurse into)
_SKIP_TAGS = {"script", "style", "button", "noscript", "svg", "path",
              "wow-image-placeholder", "wix-image"}

# Tags that are transparent wrappers (pass children through unchanged)
_PASSTHROUGH_TAGS = {"span", "div", "section", "article", "header", "footer",
                     "nav", "aside", "main", "wix-image", "figure-block"}


def _convert_body_to_markdown(body: Tag) -> str:
    """Convert the post body Tag to a markdown string."""
    md = _node_to_md(body)

    # Remove WIX duplicate link pattern: [text](URL)[URL](URL) → [text](URL)
    # WIX "link card" components sometimes render the URL as a second adjacent link.
    def _dedup_links(m: re.Match) -> str:
        url, link_text_2 = m.group(1), m.group(2)
        # Only remove if the second link's text IS the URL (or very similar)
        if link_text_2.rstrip("/") == url.rstrip("/") or link_text_2.startswith("http"):
            return f"]({url})"
        return m.group(0)
    md = re.sub(r"\]\(([^)]+)\)\[([^\]]+)\]\(\1\)", _dedup_links, md)

    # Collapse multiple consecutive <br> to a single one
    md = re.sub(r"(<br>){2,}", "<br>", md)

    # Remove trailing <br> just before a paragraph break
    md = re.sub(r"<br>(\s*\n\n)", r"\1", md)

    # Remove standalone <br> on its own line between paragraphs (WIX spacer divs)
    md = re.sub(r"\n\n<br>\n\n", "\n\n", md)
    md = re.sub(r"\n\n<br>\n", "\n\n", md)
    md = re.sub(r"\n<br>\n\n", "\n\n", md)

    # Collapse 3+ consecutive blank lines to 2
    md = re.sub(r"\n{3,}", "\n\n", md)

    # Strip trailing <br> tags
    md = re.sub(r"\s*<br>\s*$", "", md).rstrip()

    return md.strip()


def _node_to_md(node, in_blockquote: bool = False) -> str:
    """Recursively convert a BS4 node to a markdown string."""
    if isinstance(node, NavigableString):
        return str(node)

    if not isinstance(node, Tag):
        return ""

    tag = node.name
    if not tag:
        return ""

    if tag in _SKIP_TAGS:
        return ""

    children_md = lambda: "".join(_node_to_md(c, in_blockquote) for c in node.children)

    # ---- Block elements ----
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        text = children_md().strip()
        if not text:
            return ""
        return f"\n\n{'#' * level} {text}\n\n"

    if tag == "p":
        text = children_md().strip()
        # Skip empty paragraphs and WIX spacer paragraphs (only <br>, no real text)
        if not text or not re.sub(r"<br>", "", text).strip():
            return ""
        return f"\n\n{text}\n\n"

    if tag in ("ul", "ol"):
        return "\n" + children_md() + "\n"

    if tag == "li":
        return f"- {children_md().strip()}\n"

    if tag == "blockquote":
        inner = children_md().strip()
        lines = inner.split("\n")
        quoted = "\n".join((f"> {line}" if line.strip() else ">") for line in lines)
        return f"\n\n{quoted}\n\n"

    if tag == "hr":
        return "\n\n---\n\n"

    if tag == "br":
        return "<br>"

    # ---- Inline elements ----
    if tag in ("strong", "b"):
        inner = children_md()
        stripped = inner.strip()
        if not stripped:
            return ""
        # Preserve surrounding whitespace
        leading = inner[: len(inner) - len(inner.lstrip())]
        trailing = inner[len(inner.rstrip()):]
        return f"{leading}**{stripped}**{trailing}"

    if tag in ("em", "i"):
        inner = children_md()
        stripped = inner.strip()
        if not stripped:
            return ""
        leading = inner[: len(inner) - len(inner.lstrip())]
        trailing = inner[len(inner.rstrip()):]
        return f"{leading}*{stripped}*{trailing}"

    if tag == "u":
        inner = children_md().strip()
        return f"<u>{inner}</u>" if inner else ""

    if tag == "a":
        href = node.get("href", "")
        text = children_md().strip()
        if not text:
            text = href
        if not href:
            return text
        # Keep as-is; internal links are logged separately by the migrate step
        return f"[{text}]({href})"

    if tag == "img":
        # Bare <img> outside a figure — treat as inline
        src = node.get("src", "")
        alt = node.get("alt", "")
        if WIXSTATIC_CDN in src:
            uri = src.replace(WIXSTATIC_CDN, "")
            uri = re.sub(r"/v1/.*", "", uri)
            # Insert a placeholder so the image resolver can handle it
            return f"___INLINE_IMG_{uri}___"
        return f"![{alt}]({src})" if src else ""

    if tag == "figure":
        # Figures that were NOT replaced by placeholders (shouldn't happen, but handle gracefully)
        return children_md()

    if tag == "figcaption":
        # Already extracted as caption — skip during body walk
        return ""

    # ---- Passthrough / unknown ----
    return children_md()
