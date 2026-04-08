"""Shared constants and category mapping for the WIX → Hugo migration."""
from pathlib import Path

HUGO_ROOT = Path.home() / "dev/Elseyworld"
MEDIA_ROOT = Path.home() / "dev/elseyworld-static/media"
FINGERPRINTS_PATH = MEDIA_ROOT / "media_fingerprints.json"
IMAGE_LOG_PATH = HUGO_ROOT / "migration" / "image-migration-log.csv"
INTERNAL_LINKS_LOG_PATH = HUGO_ROOT / "migration" / "internal-links-log.csv"

BASE_URL = "https://www.elseyworld.com"
WIXSTATIC_CDN = "https://static.wixstatic.com/media/"
WIXDOC_CDN = "https://docs.wixstatic.com/"

# WIX category slug → migration config
CATEGORY_MAP: dict[str, dict] = {
    "asia-2009":             {"cat1": "Nick", "cat2": "Asia 2009",             "output_dir": "content/blog/asia-2009"},
    "australia-2002-trip-1": {"cat1": "Nick", "cat2": "Australia 2002 Trip 1", "output_dir": "content/blog/australia-2002-trip-1"},
    "australia-2002-trip-2": {"cat1": "Nick", "cat2": "Australia 2002 Trip 2", "output_dir": "content/blog/australia-2002-trip-2"},
    "australia-2009":        {"cat1": "Nick", "cat2": "Australia 2009",        "output_dir": "content/blog/australia-2009"},
    "lynn-business":         {"cat1": "Lynn", "cat2": "business",              "output_dir": "content/articles/business"},
    "lynn-careers":          {"cat1": "Lynn", "cat2": "careers",               "output_dir": "content/articles/careers"},
    "lynn-food-travel":      {"cat1": "Lynn", "cat2": "Food & Travel",         "output_dir": "content/articles/food-travel"},
    "lynn-health":           {"cat1": "Lynn", "cat2": "health",                "output_dir": "content/articles/health"},
    "lynn-magazines":        {"cat1": "Lynn", "cat2": "magazines",             "output_dir": "content/articles/magazines"},
    "moving-to-dc":          {"cat1": "Nick", "cat2": "Moving to DC",          "output_dir": "content/blog/moving-to-dc"},
    "south-pacific-1997":    {"cat1": "Nick", "cat2": "South Pacific 1997",    "output_dir": "content/blog/south-pacific-1997"},
}

IGNORED_CATEGORIES = {"Nick Elsey", "Lynn Elsey"}
AUTHOR_MAP = {"Nick": "Nick Elsey", "Lynn": "Lynn Elsey"}
