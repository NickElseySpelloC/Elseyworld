---
date: '2026-05-03T13:34:04+10:00'
title: 'Page Front Matter'
description: "Reference to the Congo front matter fields used in a page header."
showTableOfContents: true
showBreadcrumbs: true
---

These are the yaml format key / value pairs at the start of a markdown page. Front matter fields used across this site are documented below.

| Key | Type | Description | Used In |
|:--|:--|:--|:--|
| **title** | string | Page title displayed in headers and lists | All content types |
| **description** | string | Meta description for SEO and page summaries | All content types |
| **date** | datetime | Publication date (format: `2009-04-21T00:00:00.000+10:00`) | Blog posts, articles, resources |
| **draft** | boolean | Publication status (`true` = unpublished, `false` = published) | All content types |
| **author** | string | Post author attribution (e.g., `Nick Elsey`, `Lynn Elsey`) | Blog posts, articles |
| **layout** | string | Template to use: `simple`, `term`, or `list` | Category pages, resources, contact pages, section indexes |
| **thumbnail** | string | Page resource image filename for cards and headers (must be in same folder) | Blog posts, articles, resources |
| **categories** | array | Content taxonomy for grouping (e.g., `["Asia 2009", "Nick"]`) | Blog posts, articles |
| **aliases** | array | URL redirects from old paths (e.g., `["/post/old-url"]`) | All content types |
| **groupByYear** | boolean | Group list items by year (`true`/`false`) | Category pages, section indexes, resources |
| **defaultSortOrder** | string | Default sort direction: `asc` or `desc` | Category pages |
| **sortControl** | boolean | Enable user-facing sort controls | Category pages |
| **sortKey** | string | Specify field to sort by (e.g., `title`) | Resources section |
| **showBreadcrumbs** | boolean | Show the bread crumb trail at the top of the page. |
| **showTableOfContents** | boolean | Display table of contents in article | Resources, technical guides |
| **showDate** | boolean | Control date display | Contact pages, resources |
| **showReadingTime** | boolean | Control reading time estimate display | Contact pages, resources |
| **showAuthor** | boolean | Control author display | Cascade settings |
| **cascade** | object | Front matter properties to pass to all descendant pages | Section index pages |
| **authorName** | string | Author name (used in cascade, e.g., `"Lynn Elsey"`) | Articles section cascade |
| **authorImage** | string | Author photo path (used in cascade, e.g., `"img/people/lynn_elsey_author.jpg"`) | Articles section cascade |
| **authorBio** | string | Author biography (used in cascade) | Articles section cascade |
| **articleClass** | string | Custom CSS class for article content (e.g., `ew-prose-full`) | Contact pages |

If you want to cascade any of these settings to all child pages and folder, add this to the branch bundle _index page front matter:

```yaml
[cascade]
    showAuthor = true
```

### System wide defaults

Enable / disable system wide settings by default, toggle the relevant parameter in `/config/_default/params.toml`. For example:

```yaml
[article]
  showAuthor = false
```

### Additional authors

Multiple authors are  supported by Congo, so we created this file: `/layouts/partials/author.html`. This lets us the following block to the front matter of a branch bundle _index page to set this author for all child pages:

```yaml
[cascade]
  showAuthor = true
  authorName = "Lynn Elsey"
  authorImage = "img/lynn_author.jpg"
  authorBio = "I'm skilled at creating effective and engaging communications, targeted to maximise impact."
```

The _showAuthor_ field on any child page can be used to override and disable the author deisplay for that page.

### Common Front Matter Patterns by Content Type

**Blog Posts** (`/content/blog/**/index.md`):
```yaml
title: "Post Title"
description: "Post summary for SEO and cards"
date: 2009-04-21T00:00:00.000+10:00
author: Nick Elsey
draft: false
thumbnail: featured-image.jpg
categories:
  - Asia 2009
  - Nick
aliases:
  - /post/old-url
```

**Articles** (`/content/articles/**/index.md`):
```yaml
title: "Article Title"
description: "Article summary"
date: 2026-04-01T18:04:05+11:00
author: Lynn Elsey
draft: false
thumbnail: article-image.jpg
categories:
  - Careers
  - Lynn
```

**Category Pages** (`/content/categories/*/_index.md`):
```yaml
title: "Category Name"
description: "Category description"
layout: list
groupByYear: true
defaultSortOrder: asc
sortControl: true
aliases:
  - /old-category-url
```

**Resources** (`/content/resources/**/index.md`):
```yaml
title: "Resource Title"
description: "Resource description"
date: 2026-04-01T10:00:00+11:00
draft: false
layout: term
thumbnail: resource-image.jpg
showTableOfContents: true
showDate: false
showReadingTime: false
sortKey: title
```

**Contact Pages** (`/content/contact/*/index.md`):
```yaml
title: "Contact Page Title"
date: 2026-04-01T10:00:00+11:00
draft: false
layout: simple
showDate: false
showReadingTime: false
articleClass: ew-prose-full
```

**Section Indexes with Cascade** (`/content/articles/_index.html`):
```yaml
title: "Section Title"
layout: simple
groupByYear: false
cascade:
  showAuthor: true
  authorName: "Lynn Elsey"
  authorImage: "img/people/lynn_elsey_author.jpg"
  authorBio: "Author biography text"
```