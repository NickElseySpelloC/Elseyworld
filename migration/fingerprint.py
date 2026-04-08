"""
Phase 1: Media Fingerprinting

Scans all files under the media root directory, computes MD5 hashes,
and saves a lookup dictionary mapping hash -> local file path.

The hash key uses only the hex digest (no prefix/suffix) so it can be
matched against the hash portion of WIX CDN filenames, e.g.:
    ebf3d7_35a9dd254bd541b5bc9c00021ce8d836~mv2_d_1600_1200_s_2.jpg
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Usage:
    uv run python -m migration.fingerprint
    uv run python -m migration.fingerprint --media-root /path/to/media --output /path/to/out.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

DEFAULT_MEDIA_ROOT = Path.home() / "dev/elseyworld-static/media"
DEFAULT_OUTPUT = DEFAULT_MEDIA_ROOT / "media_fingerprints.json"

# File extensions to include (skip spreadsheets, DS_Store, etc.)
MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg",
    ".mp4", ".m4v", ".mov", ".avi",
    ".pdf", ".doc", ".docx",
}


def md5_of_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_fingerprints(media_root: Path) -> dict[str, str]:
    """Return dict mapping md5_hex -> absolute file path string."""
    fingerprints: dict[str, str] = {}
    files = [p for p in media_root.rglob("*") if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS]

    print(f"Scanning {len(files)} media files under {media_root} ...")
    duplicates = 0

    for i, path in enumerate(files, 1):
        digest = md5_of_file(path)
        if digest in fingerprints:
            print(f"  [WARN] duplicate hash {digest}: {fingerprints[digest]} vs {path}", file=sys.stderr)
            duplicates += 1
        else:
            fingerprints[digest] = str(path)

        if i % 100 == 0:
            print(f"  {i}/{len(files)} processed...")

    print(f"Done. {len(fingerprints)} unique hashes ({duplicates} duplicates skipped).")
    return fingerprints


def save_fingerprints(fingerprints: dict[str, str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(fingerprints, f, indent=2, sort_keys=True)
    print(f"Saved to {output_path}")


def load_fingerprints(output_path: Path) -> dict[str, str]:
    """Load previously saved fingerprints. Returns empty dict if file missing."""
    if not output_path.exists():
        return {}
    with output_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MD5 fingerprints for all media files.")
    parser.add_argument(
        "--media-root",
        type=Path,
        default=DEFAULT_MEDIA_ROOT,
        help=f"Root directory to scan (default: {DEFAULT_MEDIA_ROOT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    fingerprints = build_fingerprints(args.media_root)
    save_fingerprints(fingerprints, args.output)


if __name__ == "__main__":
    main()
