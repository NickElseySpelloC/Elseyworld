"""
Phase 2: WIX → Hugo content migration.

Usage:
    # Migrate one post per category (default — stops for review)
    uv run python -m migration.migrate --mode one-per-category

    # Process a single category only
    uv run python -m migration.migrate --mode one-per-category --category south-pacific-1997

    # Migrate all posts across all categories
    uv run python -m migration.migrate --mode all

    # Re-process posts even if _index.md already exists
    uv run python -m migration.migrate --mode one-per-category --overwrite
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from migration.config import (
    HUGO_ROOT,
    BASE_URL,
    WIXSTATIC_CDN,
    WIXDOC_CDN,
    CATEGORY_MAP,
    IGNORED_CATEGORIES,
    AUTHOR_MAP,
    INTERNAL_LINKS_LOG_PATH,
)
from migration.fetch import WixFetcher
from migration.images import ImageResolver
from migration.parser import (
    PostCard,
    PostData,
    parse_listing,
    parse_post,
)


# ---------------------------------------------------------------------------
# Front matter rendering
# ---------------------------------------------------------------------------

def _render_frontmatter(post: PostData, cat_config: dict, thumbnail: str) -> str:
    cat1 = cat_config["cat1"]
    cat2 = cat_config["cat2"]
    author = AUTHOR_MAP.get(cat1, cat1)

    # Escape double-quotes in description
    description = post.description.replace('"', '\\"')

    lines = [
        "---",
        f'title: {_yaml_str(post.title)}',
        f'description: "{description}"',
        f"date: {post.date_iso}",
        f"author: {author}",
        "draft: false",
    ]
    if thumbnail:
        lines.append(f"thumbnail: {thumbnail}")
    lines += [
        "categories:",
        f"  - {cat2}",
        f"  - {cat1}",
        "---",
    ]
    return "\n".join(lines) + "\n"


def _yaml_str(text: str) -> str:
    """Wrap a YAML string value in quotes only if it contains special characters."""
    if any(c in text for c in ('"', "'", ":", "#", "{", "}", "[", "]", "|", ">")):
        escaped = text.replace('"', '\\"')
        return f'"{escaped}"'
    return text


# ---------------------------------------------------------------------------
# Markdown body assembly — resolve placeholders
# ---------------------------------------------------------------------------

def _assemble_markdown(
    post: PostData,
    resolver: ImageResolver,
    output_dir: Path,
    internal_links_log: list[dict],
) -> str:
    """
    Replace image/doc placeholders in the markdown body with final markdown,
    and collect any internal links for logging.
    """
    body = post.markdown_body

    # Resolve images
    for img_info in post.images:
        if not img_info.wix_uri:
            body = body.replace(img_info.placeholder, "")
            continue

        result = resolver.resolve_image(img_info.wix_uri, output_dir, post.slug)
        filename = result.filename

        if not filename:
            body = body.replace(img_info.placeholder, "")
            continue

        md = _image_markdown(filename, img_info.align, img_info.alt, img_info.caption)
        body = body.replace(img_info.placeholder, md)

    # Resolve inline image placeholders (bare <img> tags outside figures)
    for match in re.findall(r"___INLINE_IMG_([^_]+(?:~[^_]*)?)___", body):
        wix_uri = match
        result = resolver.resolve_image(wix_uri, output_dir, post.slug)
        filename = result.filename
        md = f"![{filename}]({filename})" if filename else ""
        body = body.replace(f"___INLINE_IMG_{wix_uri}___", md)

    # Resolve documents
    for doc_info in post.docs:
        result = resolver.resolve_doc(doc_info.doc_url, output_dir, post.slug)
        filename = result.filename
        if filename:
            md = f"[{doc_info.link_text}]({filename})"
        else:
            md = doc_info.link_text
        body = body.replace(doc_info.placeholder, md)

    # Log internal elseyworld.com links (keep original URLs in markdown)
    for m in re.finditer(r"\[([^\]]*)\]\((https?://(?:www\.)?elseyworld\.com[^)]*)\)", body):
        link_text, href = m.group(1), m.group(2)
        internal_links_log.append({
            "post_slug": post.slug,
            "link_text": link_text,
            "original_url": href,
            "notes": "Internal link — review and update to Hugo path",
        })

    return body


def _image_markdown(filename: str, align: str, alt: str, caption: str) -> str:
    """
    Return the appropriate Hugo markdown / shortcode for an image.
    Per brief: default to standard inline markdown when align is 'center' or unknown.
    """
    if align in ("left", "right"):
        if caption:
            return (
                f'\n\n{{{{< img-caption-float src="{filename}" side="{align}" '
                f'caption="{_escape_attr(caption)}" alt="{_escape_attr(alt)}" >}}}}\n\n'
            )
        else:
            return (
                f'\n\n{{{{< img-float src="{filename}" side="{align}" '
                f'alt="{_escape_attr(alt)}" >}}}}\n\n'
            )
    else:
        # Inline / centered
        if caption:
            return (
                f'\n\n{{{{< img-caption src="{filename}" '
                f'caption="{_escape_attr(caption)}" alt="{_escape_attr(alt)}" >}}}}\n\n'
            )
        else:
            display_alt = alt or filename
            return f"\n\n![{display_alt}]({filename})\n\n"


def _escape_attr(text: str) -> str:
    return text.replace('"', "&quot;")


# ---------------------------------------------------------------------------
# Core migration logic
# ---------------------------------------------------------------------------

def _output_dir_for_post(slug: str, cat_config: dict) -> Path:
    return HUGO_ROOT / cat_config["output_dir"] / slug


def _post_exists(slug: str, cat_config: dict) -> bool:
    return (_output_dir_for_post(slug, cat_config) / "_index.md").exists()


def _validate_category_slugs(category_slugs: list[str], url: str) -> str | None:
    """
    From the post's category links, find the one mapped in CATEGORY_MAP.
    Returns the category slug or None (prints an error and halts on unknown).
    """
    # Build a normalised set for ignored slugs: "Nick Elsey" → "nick-elsey"
    ignored_slugs = {s.lower().replace(" ", "-") for s in IGNORED_CATEGORIES}

    mapped = []
    for slug in category_slugs:
        if slug in CATEGORY_MAP:
            mapped.append(slug)
        elif slug in ignored_slugs:
            pass  # silently skip
        else:
            # Unknown slug → must halt
            print(
                f"\n[HALT] Post {url} has unrecognised category slug: '{slug}'\n"
                f"  Please add it to CATEGORY_MAP in config.py or verify it should be ignored.",
                file=sys.stderr,
            )
            sys.exit(1)
    return mapped[0] if mapped else None


def migrate_post(
    post_card: PostCard,
    fetcher: WixFetcher,
    resolver: ImageResolver,
    cat_slug: str,
    internal_links_log: list[dict],
    overwrite: bool = False,
) -> bool:
    """
    Migrate a single post. Returns True on success.
    """
    cat_config = CATEGORY_MAP[cat_slug]
    slug = post_card.slug

    if not overwrite and _post_exists(slug, cat_config):
        print(f"  Skipping {slug} (already exists; use --overwrite to re-process)")
        return False

    print(f"  Fetching post: {post_card.url}")
    html = fetcher.fetch_post_page(post_card.url)

    post = parse_post(html, post_card.url)

    # Description: prefer listing page excerpt (what's shown on the all-posts page).
    # Fall back to JSON-LD description, truncated to avoid dumping full post text.
    if post_card.description:
        post.description = post_card.description
    elif post.description and len(post.description) > 300:
        post.description = post.description[:297] + "..."

    # Validate that the post doesn't belong to an *unknown* category
    # (i.e. a category not in our map and not in the ignored list).
    # The authoritative category for routing is always cat_slug (from the listing page).
    _validate_category_slugs(post.category_slugs, post.url)

    output_dir = _output_dir_for_post(slug, cat_config)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve cover image (thumbnail)
    print(f"    Resolving cover image ...")
    thumbnail = resolver.resolve_cover_image(post.cover_image_uri, output_dir, slug)

    # Resolve all body images and assemble final markdown
    print(f"    Resolving {len(post.images)} body image(s) and {len(post.docs)} doc(s) ...")
    final_body = _assemble_markdown(post, resolver, output_dir, internal_links_log)

    # Write _index.md
    frontmatter = _render_frontmatter(post, cat_config, thumbnail or "")
    md_path = output_dir / "_index.md"
    md_path.write_text(frontmatter + "\n" + final_body + "\n", encoding="utf-8")
    print(f"    Written: {md_path.relative_to(HUGO_ROOT)}")

    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate WIX blog posts to Hugo markdown files."
    )
    parser.add_argument(
        "--mode",
        choices=["one-per-category", "all"],
        default="one-per-category",
        help="Migration mode (default: one-per-category)",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Process only this WIX category slug (e.g. south-pacific-1997)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-process posts even if _index.md already exists",
    )
    args = parser.parse_args()

    # Determine which categories to process
    if args.category:
        if args.category not in CATEGORY_MAP:
            print(f"Unknown category: {args.category}. Valid options: {list(CATEGORY_MAP)}", file=sys.stderr)
            sys.exit(1)
        categories = {args.category: CATEGORY_MAP[args.category]}
    else:
        categories = CATEGORY_MAP

    internal_links_log: list[dict] = []
    results: dict[str, list[str]] = {"ok": [], "skipped": [], "error": []}

    resolver = ImageResolver()

    try:
        with WixFetcher() as fetcher:
            for cat_slug, cat_config in categories.items():
                print(f"\n{'='*60}")
                print(f"Category: {cat_slug}  ({cat_config['cat2']})")
                print(f"{'='*60}")

                # Fetch listing page to get post cards
                print(f"  Fetching category listing ...")
                listing_html = fetcher.fetch_category_listing(cat_slug)
                post_cards = parse_listing(listing_html)

                if not post_cards:
                    print(f"  [WARN] No posts found for category {cat_slug}")
                    continue

                print(f"  Found {len(post_cards)} post(s) in category")

                # In one-per-category mode, take just the first post
                if args.mode == "one-per-category":
                    post_cards = post_cards[:1]

                for card in post_cards:
                    print(f"\n  Post: {card.slug}")
                    try:
                        ok = migrate_post(
                            card, fetcher, resolver, cat_slug,
                            internal_links_log, overwrite=args.overwrite,
                        )
                        if ok:
                            results["ok"].append(card.slug)
                        else:
                            results["skipped"].append(card.slug)
                    except SystemExit:
                        raise
                    except Exception as exc:
                        print(f"  [ERROR] Failed to migrate {card.slug}: {exc}", file=sys.stderr)
                        import traceback
                        traceback.print_exc()
                        results["error"].append(card.slug)

    finally:
        resolver.close()
        _write_internal_links_log(internal_links_log)

    # Summary
    print(f"\n{'='*60}")
    print(f"Migration complete.")
    print(f"  Migrated:  {len(results['ok'])} post(s): {results['ok']}")
    print(f"  Skipped:   {len(results['skipped'])} post(s)")
    print(f"  Errors:    {len(results['error'])} post(s): {results['error']}")
    if internal_links_log:
        print(f"  Internal links logged: {len(internal_links_log)} (see {INTERNAL_LINKS_LOG_PATH})")


def _write_internal_links_log(rows: list[dict]) -> None:
    if not rows:
        return
    INTERNAL_LINKS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INTERNAL_LINKS_LOG_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["post_slug", "link_text", "original_url", "notes"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Internal links log: {INTERNAL_LINKS_LOG_PATH}")


if __name__ == "__main__":
    main()
