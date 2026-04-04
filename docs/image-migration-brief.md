When you're ready to add your other migration guidelines, the key topics I'd suggest covering in the broader brief are:

HTML to Markdown conversion rules — how to handle WIX's div-heavy markup
Front matter extraction — where to get title, date, author, categories from the WIX HTML
Float image detection — how to identify when to use img-float vs standard Markdown image
Content folder structure — page bundle naming conventions, which content goes where
What to skip — WIX navigation, comments, "Recent Posts" sidebars etc.


# Claude Code Brief: Image Migration Strategy
_ElseyWorld WIX → Hugo Migration_

---

## Overview

During the migration of ElseyWorld blog content from WIX to Hugo Markdown, all image references
need to be resolved from WIX CDN URLs to local image files. This document describes the image
resolution strategy.

---

## The Problem

WIX stores images on its CDN using obfuscated hash-based filenames, for example:

```
https://static.wixstatic.com/media/ebf3d7_35a9dd254bd541b5bc9c00021ce8d836~mv2_d_1600_1200_s_2.jpg
```

These hashed filenames bear no relationship to the original filenames that were uploaded to WIX
(e.g. `Australia 2002 Trip 2 - 02.jpg`). WIX also appends transform parameters to serve
resized/compressed versions:

```
/v1/fill/w_350,h_263,al_c,q_80,usm_0.66_1.00_0.01,enc_avif,quality_auto/ebf3d7_...jpg
```

These transform parameters must be stripped to retrieve the full-resolution original from the CDN.

---

## Available Resources

| Resource | Location |
|---|---|
| Original images (exported from WIX Media Manager) | `~/dev/elseyworld-static/media/` |
| HTTrack-downloaded HTML pages | `~/dev/elseyworld-static/` |
| Hugo project content output folder | `~/dev/Elseyworld/content/` |
| Hugo project image output folder | `~/dev/Elseyworld/static/images/` |

The original images are organised in subfolders by topic/trip, e.g:
```
~/dev/elseyworld-static/media/
├── Australia 2002 Trip 2/
│   ├── Australia 2002 Trip 2 - 01.jpg
│   ├── Australia 2002 Trip 2 - 02.jpg
│   └── ...
├── Asia 2009/
│   └── ...
└── ...
```

---

## Image Resolution Strategy

Use MD5 hash fingerprinting to match WIX CDN images to local originals. This works because
WIX stores byte-identical copies of the originally uploaded files on its CDN.

### Step 1: Build a Local Image Hash Lookup Table

Before processing any HTML content, scan all files under `~/dev/elseyworld-static/media/`
recursively and compute an MD5 hash for each image file. Store results in a lookup dictionary:

```python
{
  "a1b2c3d4e5f6...": "/Users/nick/dev/elseyworld-static/media/Australia 2002 Trip 2/Australia 2002 Trip 2 - 02.jpg",
  ...
}
```

### Step 2: For Each WIX Image URL Found in HTML

1. **Strip the WIX transform parameters** from the URL to get the base CDN URL:
   - Remove everything from `/v1/` onwards
   - Example: `https://static.wixstatic.com/media/ebf3d7_35a9...~mv2.jpg/v1/fill/w_350,...` 
   - Becomes: `https://static.wixstatic.com/media/ebf3d7_35a9...~mv2.jpg`

2. **Download the full-resolution image** from the base CDN URL

3. **Compute the MD5 hash** of the downloaded image

4. **Look up the hash** in the local lookup table:
   - ✅ **Match found** → use the local original file (preferred — highest quality, already on disk)
   - ❌ **No match** → fall back to the full-resolution CDN download (see Step 3)

### Step 3: Fallback for Unmatched Images

If no local match is found (image may have been edited or re-uploaded in WIX):

1. Use the full-resolution CDN download from Step 2 (already downloaded)
2. Generate a filename from the WIX hash, e.g. `ebf3d7_35a9dd254bd541b5bc9c00021ce8d836.jpg`
3. Log the unmatched image so it can be reviewed manually later

### Step 4: Copy Images to Hugo Project

All resolved images (whether matched locally or downloaded from CDN) should be copied to the
Hugo project's static image folder, organised by content section:

```
~/dev/Elseyworld/static/images/blog/<post-slug>/
```

For example, the Weeroona Cottage image for the "Sydney and Getting There" post would go to:
```
~/dev/Elseyworld/static/images/blog/sydney-and-getting-there/australia-2002-trip-2-02.jpg
```

**Filename sanitisation rules:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Preserve the original file extension

### Step 5: Output Image Reference for Markdown

Once the image is in place, reference it in the Hugo Markdown using either:

**Standard Markdown** (full-width block image):
```markdown
![Weeroona Cottage](/images/blog/sydney-and-getting-there/australia-2002-trip-2-02.jpg)
```

**Floated image shortcode** (where the original HTML used float styling — see separate brief):
```markdown
{{< img-float src="/images/blog/sydney-and-getting-there/australia-2002-trip-2-02.jpg" side="left" alt="Weeroona Cottage" >}}
```

---

## Logging Requirements

Produce a migration log file (`image-migration-log.csv`) with one row per image processed:

| Column | Description |
|---|---|
| `source_url` | Original WIX CDN URL |
| `match_type` | `local_match`, `cdn_download`, or `error` |
| `local_source` | Path to matched local file (if applicable) |
| `output_path` | Final path in Hugo project |
| `post_slug` | The blog post this image belongs to |
| `notes` | Any warnings or issues |

This log allows manual review of any unmatched or problematic images after the migration runs.

---

## Important Notes

- **Do not use the low-res AVIF versions** served by WIX transform URLs — always strip transforms
  and fetch the full-resolution original
- **Prefer local originals over CDN downloads** — they are highest quality and avoid network
  dependency
- **Keep the WIX subscription active** until the migration is complete and verified — the CDN
  fallback depends on those URLs still being live
- **Thumb images for Congo CMS**: If a post has a designated cover/hero image, copy it into the
  page bundle as `thumb.jpg` in addition to its regular copy, so Congo's listing page picks it up
  automatically
