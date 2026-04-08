# Elseyworld Content Migration Brief

This document describes the procedure to migrate the contents of the elseyworld.com website to Hugo and the Congo theme.

The elseyworld.com website is currently hosted by WIX. Due to the way WIX renders content, the site cannot be extracted using httrack
so you will need to extract html content directly from the live site.

Images rendered by WIX in the client broweser are transformed (e.g. shrunk to the required size), so I have downloaded
original files and saved to the local file system. These files will be used during the migration as described below.

## Migration Strategy

The migration will be done in 2 phases:

1. **Media Fingerprinting**: Generate MD5 hash fingerprints of all downloaded media files.
2. **HTML Migration**: Copy blog content to the local repo and copy related media files from the local cache.

After phase 1 is complete, please stop and ask me to review before proceeding to phase 2.

During phase 2, please migrate one blog post or article for each Category 2 and then stop and ask me for review.

## Available Resources

The following resources are available to you for this migration.

| Resource | Location |
| --- | --- |
| Live website where you'll extract the html content from | https://www.elseyworld.com/ |
| Originals of the media used in web site | `~/dev/elseyworld-static/media/` |
| Hugo project content output folder | `~/dev/Elseyworld/content/` |

# Phase 1: media Fingerprinting

During the migration of ElseyWorld content from WIX to Hugo Markdown, all media references need to be resolved from
WIX CDN URLs to local image files. This section describes the image resolution strategy.

## The Problem

WIX stores images on its CDN using obfuscated hash-based filenames, for example:

```
https://static.wixstatic.com/media/ebf3d7_35a9dd254bd541b5bc9c00021ce8d836~mv2_d_1600_1200_s_2.jpg
```

These hashed filenames bear no relationship to the original filenames that were uploaded to WIX
(e.g. `lax.jpg`). WIX also appends transform parameters to serve
resized/compressed versions:

```
/v1/fill/w_350,h_228,al_c,q_80,usm_0.66_1.00_0.01,enc_avif,quality_auto/ebf3d7_da3824d221444c828e861cfd5b4f389d~mv2_d_3000_1955_s_2.jpg
```

These transform parameters must be stripped to retrieve the full-resolution original from the CDN.

Note that documents (PDF and DOC files) appear to be stored differently. For example the https://www.elseyworld.com/post/the-wild-west page
includes a link to a PDF document:

  <a ... href="https://docs.wixstatic.com/ugd/f14443_b3f93067539a4381a99aa83d7dbc9756.pdf" >

The downloaded original of this file is here:
`~/dev/elseyworld-static/media/doc/the-wild-west-decanter-magazine.pdf`

## Media Resolution Strategy

Use MD5 hash fingerprinting to match WIX CDN images to local originals. This works because
WIX stores byte-identical copies of the originally uploaded files on its CDN.

Before processing any HTML content (phase 2 below), scan all media files under `~/dev/elseyworld-static/media/`
recursively and compute an MD5 hash for each file. Store results in a lookup dictionary:

```python
{
  "ebf3d7_35a9dd254bd541...": "/Users/nick/dev/elseyworld-static/media/image/weeroona-cottage-016.jpg",
  ...
}
```

Save this JSON file here: `/Users/nick/dev/elseyworld-static/media/media_fingerprints.json`


# Phase 2: HTML Migration

In this phase, we will migrate all the html "blog" pages linked from the _all posts_ page: https://www.elseyworld.com/blog

## Content location reference

| WIX Category | Category listing page | Category 1 | Category 2 | Save Location |
| --- | --- | --- | --- | --- |
| Asia 2009 | elseyworld.com/blog/categories/asia-2009 | Nick | Asia 2009 | content/blog/asia-2009/<page-slug>/ |
| Australia 2002 Trip 1 | elseyworld.com/blog/categories/australia-2002-trip-1 | Nick | Australia 2002 Trip 1 | content/blog/australia-2002-trip-1/<page-slug>/ |
| Australia 2002 Trip 1 | elseyworld.com/blog/categories/australia-2002-trip-2 | Nick | Australia 2002 Trip 2 | content/blog/australia-2002-trip-2/<page-slug>/ |
| Australia 2009 | elseyworld.com/blog/categories/australia-2009 | Nick | Australia 2009 | content/blog/australia-2009/<page-slug>/ |
| Lynn-Business | elseyworld.com/blog/categories/lynn-business | Lynn | business | content/articles/business/<page-slug>/ |
| Lynn-Careers | elseyworld.com/blog/categories/lynn-careers | Lynn | careers | content/articles/careers/<page-slug>/ |
| Lynn-Food & Travel | elseyworld.com/blog/categories/lynn-food-travel | Lynn | Food & Travel | content/articles/food-travel/<page-slug>/ |
| Lynn-Health | elseyworld.com/blog/categories/lynn-health | Lynn | health | content/articles/health/<page-slug>/ |
| Lynn-Magazines | elseyworld.com/blog/categories/lynn-magazines | Lynn | magazines | content/articles/magazines/<page-slug>/ |
| Moving to DC | elseyworld.com/blog/categories/moving-to-dc | Nick | Moving to DC | content/blog/moving-to-dc/<page-slug>/ |
| South Pacific 1997 | elseyworld.com/blog/categories/south-pacific-1997 | Nick | South Pacific 1997 | content/blog/south-pacific-1997/<page-slug>/ |

All the target partent folders under content/blog and content/articles have been created already.

## Step 1: Extract content

Build a list of all the posts listed on the _all posts_ page. Beware that WIX paginates this listing page - you will need to scroll down to get all the items (there are approximately 86 in total).

For each item (for example https://www.elseyworld.com/post/a-weekend-in-verona) extract the following:

* The page title (e.g. "A weekend in Verona")
* The page slug (e.g. "a-weekend-in-verona")
* The publish date (e.g. 17/01/2020)
* The page content, including image references (e.g. <img src="https://static.wixstatic.com/media/f14443_07dd231f37f3432ebfc2c901b109dfed~mv2.jpg....), taking note of whether the images is floated left, right or is inline.
* Basic text formatting (headings, bold, italics, underline, hyperlinks).
* WIX category title. This can be found at the end of the page (e.g. Lynn-Food & Travel) and this links to a WIX category page (e.g. elseyworld.com/blog/categories/lynn-food-travel ). See the _content location reference_ table above for valid WIX categories.

Write the content to _index.md file in under the Save Location specified above. In our example, the content would be written to `~/dev/Elseyworld/content/articles/food-travel/a-weekend-in-verona/_index.md`

In the markdown file:

* Transfer the page title, description and date to the matching front matter fields (use yaml style)
* If Category 1 = Nick, set the author field to Nick Elsey, otherwise to Lynn Elsey
* Set the categories front matter field to the Category 1 and Category 2 value.
* Set the description field to the snippet shown on the _all posts_ page for this entry.

For our exmple article, the fron matter would look like this:

```yaml
---
title: A weekend in Verona
description: "The home of medieval and Renaissance palaces, a Roman arena and Shakespeare’s star-crossed lovers, Verona is a compact..."
date: 2020-01-17T00:00:00.000+10:00
author: Lynn Elsey
draft: false
thumbnail: <see below>
categories:
  - Lynn
  - Food & Travel
---
```

Other points to note when generating the markdown file from the WIX html:

* Carry over the basic text formatting (headings, bold, italics, underline, hyperlinks)
* If the original WIX page has links to other pages in the elseyworld site, recreate these but also generate a log file so that I can review these later.
* Ignore crazy levels of nested <div> tags in the original. Try and keep the markdown file as simple as possible.
* See below for details on image treatment.

## Step 2: For Each WIX media URL Found in HTML

1. **Strip the WIX transform parameters** from the URL to get the base CDN URL:
   - Remove everything from `/v1/` onwards
   - Example: `https://static.wixstatic.com/media/ebf3d7_35a9...~mv2.jpg/v1/fill/w_350,...` 
   - Becomes: `https://static.wixstatic.com/media/ebf3d7_35a9...~mv2.jpg`

2. **Download the full-resolution image** from the base CDN URL

3. **Compute the MD5 hash** of the downloaded image

4. **Look up the hash** in the local lookup table (media_fingerprints.json):
   - ✅ **Match found** → use the local original file (preferred — highest quality, already on disk). Copy this file to the page's bundle folder and preserve the local filename.
   - ❌ **No match** → fall back to the full-resolution CDN download (see Step 3)

## Step 3: Fallback for Unmatched Images

If no local match is found (image may have been edited or re-uploaded in WIX):

1. Use the full-resolution CDN download from Step 2 (already downloaded)
2. Generate a filename from the WIX hash, e.g. `ebf3d7_35a9dd254bd541b5bc9c00021ce8d836.jpg`
3. Log the unmatched image so it can be reviewed manually later

## Step 4: Copy Images to Hugo Project

All resolved images (whether matched locally or downloaded from CDN) should be copied to the content bundle folder that the image relates to.

## Step 5: Output Image Reference for Markdown

Once the image is in place, reference it in the Hugo Markdown using either:

**Standard Markdown** (full-width block image):
```markdown
![Weeroona Cottage](australia-2002-trip-2-02.jpg)
```

**Floated image shortcode** (where the original HTML used float styling):
```markdown
{{< img-float src="australia-2002-trip-2-02.jpg" side="left" alt="Weeroona Cottage" >}}
```

**Floated captioned image shortcode** (where the original HTML used float styling):
```markdown
{{< img-caption-float src="australia-2002-trip-2-02.jpg" side="left" caption="Weeroona Cottage" alt="Weeroona Cottage" >}}
```

## Step 6: Set image thumbnail

Inspect the _all posts_ page and determine the image used as the thumbnail for each article. The image should be one of the images already saved in the
bumdle folder. Set the thumbnail field in the page's front matter to that file name:

```yaml
---
title: Sydney, and getting there
description: "For a little bit of exotic excitement, Lynn and I start off this vacation approximately 2,000 miles apart."
date: 2002-04-10T00:00:00.000+10:00
author: Nick Elsey
draft: false
thumbnail: australia-2002-trip-2-02.jpg
categories:
  - Nick
  - Australia 2002 Trip 2
---
```

## Image Logging Requirements

Produce a migration log file (`image-migration-log.csv`) with one row per image processed:

| Column | Description |
| --- | --- |
| `source_url` | Original WIX CDN URL |
| `match_type` | `local_match`, `cdn_download`, or `error` |
| `local_source` | Path to matched local file (if applicable) |
| `output_path` | Final path in Hugo project |
| `post_slug` | The blog post this image belongs to |
| `notes` | Any warnings or issues |

This log allows manual review of any unmatched or problematic images after the migration runs.

## Important Notes on Image Processing

- **Do not use the low-res AVIF versions** served by WIX transform URLs — always strip transforms
  and fetch the full-resolution original
- **Prefer local originals over CDN downloads** — they are highest quality and avoid network
  dependency
- **Keep the WIX subscription active** until the migration is complete and verified — the CDN
  fallback depends on those URLs still being live
- **Thumb images for Congo CMS**: If a post has a designated cover/hero image, copy it into the
  page bundle as `thumb.jpg` in addition to its regular copy, so Congo's listing page picks it up
  automatically

## Final Point

I have created a couple of example pages as illustration:

  content/blog/australia-2002-trip-2/sydney-and-getting-there
  content/blog/south-pacific-1997/portland-la

