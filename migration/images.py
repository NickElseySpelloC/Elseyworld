"""
Image and document resolution for the WIX → Hugo migration.

Resolution pipeline for each image:
  1. Download full-resolution image from WIX CDN (strip transform params first)
  2. Compute MD5 hash of downloaded bytes
  3. Look up hash in local fingerprints (media_fingerprints.json)
     - Match found → copy local original to Hugo bundle (preferred quality)
     - No match → save the CDN download under a hash-derived filename
  4. Log every image to image-migration-log.csv

Documents (PDF/DOC) use the same fingerprint lookup; only the URL format differs.
"""

import csv
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import requests

from migration.config import (
    FINGERPRINTS_PATH,
    IMAGE_LOG_PATH,
    WIXSTATIC_CDN,
    WIXDOC_CDN,
)


@dataclass
class ResolvedImage:
    filename: str           # local filename in the bundle folder
    match_type: str         # "local_match" | "cdn_download" | "error"


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _extension_from_uri(uri: str) -> str:
    """Extract file extension from a WIX URI or URL."""
    # WIX URIs look like: ebf3d7_abc~mv2.jpg  or  ebf3d7_abc~mv2_d_1600_1200_s_2.jpg
    # Strip query / fragment first
    uri = uri.split("?")[0].split("#")[0]
    # The real extension is after the last dot before any ~ or end
    base = uri.split("~")[0] if "~" in uri else uri
    suffix = Path(base).suffix.lstrip(".")
    return suffix.lower() if suffix else "jpg"


def _hash_from_uri(uri: str) -> str:
    """Return the hash portion of a WIX media URI (before the ~)."""
    return uri.split("~")[0] if "~" in uri else uri.split(".")[0]


class ImageResolver:
    """
    Resolves WIX CDN image/doc references to local files,
    copies them into the Hugo bundle directory, and writes a CSV log.
    """

    def __init__(self):
        self._fingerprints: dict[str, str] = {}
        self._session = requests.Session()
        self._session.headers["User-Agent"] = (
            "Mozilla/5.0 (compatible; ElseyMigration/1.0)"
        )
        self._log_rows: list[dict] = []

        # Load fingerprints
        if FINGERPRINTS_PATH.exists():
            with FINGERPRINTS_PATH.open(encoding="utf-8") as f:
                self._fingerprints = json.load(f)
            print(f"  Loaded {len(self._fingerprints):,} fingerprints from {FINGERPRINTS_PATH}")
        else:
            print(f"  WARNING: fingerprints file not found at {FINGERPRINTS_PATH}", file=sys.stderr)

    def resolve_image(
        self,
        wix_uri: str,
        output_dir: Path,
        post_slug: str,
    ) -> ResolvedImage:
        """
        Download the full-res image from WIX CDN, fingerprint-match to local file,
        copy to bundle. Returns ResolvedImage with the local filename.
        """
        cdn_url = f"{WIXSTATIC_CDN}{wix_uri}"
        return self._resolve(cdn_url, wix_uri, output_dir, post_slug, is_doc=False)

    def resolve_doc(
        self,
        doc_url: str,
        output_dir: Path,
        post_slug: str,
    ) -> ResolvedImage:
        """
        Download a WIX-hosted document (PDF/DOC), fingerprint-match, copy to bundle.
        """
        return self._resolve(doc_url, doc_url, output_dir, post_slug, is_doc=True)

    def resolve_cover_image(
        self,
        wix_uri: str,
        output_dir: Path,
        post_slug: str,
    ) -> str | None:
        """
        Resolve the cover/hero image (used as Hugo thumbnail).
        Returns the local filename or None on failure.
        Also writes a thumb.jpg copy for Congo CMS listing pages.
        """
        if not wix_uri:
            return None
        result = self.resolve_image(wix_uri, output_dir, post_slug)
        if result.match_type == "error":
            return None

        # Write thumb.jpg copy for Congo listing pages
        src_path = output_dir / result.filename
        thumb_path = output_dir / "thumb.jpg"
        if src_path.exists() and not thumb_path.exists():
            shutil.copy2(src_path, thumb_path)

        return result.filename

    def _resolve(
        self,
        cdn_url: str,
        wix_uri: str,
        output_dir: Path,
        post_slug: str,
        is_doc: bool,
    ) -> ResolvedImage:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download full-resolution content
        try:
            resp = self._session.get(cdn_url, timeout=30)
            resp.raise_for_status()
            data = resp.content
        except Exception as exc:
            note = f"Download failed: {exc}"
            self._log(cdn_url, "error", "", "", post_slug, note)
            print(f"    [ERROR] {note}", file=sys.stderr)
            return ResolvedImage(filename="", match_type="error")

        digest = _md5(data)

        # Try fingerprint match
        if digest in self._fingerprints:
            local_path = Path(self._fingerprints[digest])
            filename = local_path.name
            dest = output_dir / filename
            if not dest.exists():
                shutil.copy2(local_path, dest)
            self._log(cdn_url, "local_match", str(local_path), str(dest), post_slug, "")
            return ResolvedImage(filename=filename, match_type="local_match")

        # No match — save CDN download under a WIX-hash-derived filename
        if is_doc:
            # e.g., /ugd/f14443_b3f93067...pdf → f14443_b3f93067.pdf
            m = re.search(r"/ugd/([^/]+)$", cdn_url)
            raw_name = m.group(1) if m else Path(cdn_url).name
            filename = raw_name.split("?")[0]
        else:
            ext = _extension_from_uri(wix_uri)
            hash_part = _hash_from_uri(wix_uri)
            filename = f"{hash_part}.{ext}"

        dest = output_dir / filename
        dest.write_bytes(data)
        note = "No local fingerprint match — saved CDN download"
        self._log(cdn_url, "cdn_download", "", str(dest), post_slug, note)
        print(f"    [WARN] No local match for {wix_uri} — saved as {filename}", file=sys.stderr)
        return ResolvedImage(filename=filename, match_type="cdn_download")

    def _log(
        self,
        source_url: str,
        match_type: str,
        local_source: str,
        output_path: str,
        post_slug: str,
        notes: str,
    ) -> None:
        self._log_rows.append({
            "source_url": source_url,
            "match_type": match_type,
            "local_source": local_source,
            "output_path": output_path,
            "post_slug": post_slug,
            "notes": notes,
        })

    def flush_log(self) -> None:
        """Write all accumulated log rows to the CSV log file."""
        IMAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        write_header = not IMAGE_LOG_PATH.exists()
        with IMAGE_LOG_PATH.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["source_url", "match_type", "local_source",
                            "output_path", "post_slug", "notes"],
            )
            if write_header:
                writer.writeheader()
            writer.writerows(self._log_rows)
        self._log_rows.clear()

    def close(self) -> None:
        self.flush_log()
        self._session.close()
