---
date: '2026-05-03T13:34:04+10:00'
title: 'Short Code Reference'
description: "Reference to all the custom short codes used in this site."
showTableOfContents: true
showBreadcrumbs: true
---

Custom shortcodes are defined in `layouts/shortcodes/`. They are called in markdown content using `{{</* shortcode-name param="value" */>}}`.

## img-float

Floats an image left or right with text wrapping around it. No caption or figure wrapper — just the `<img>` tag with a float class applied.

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `src` | yes | — | Image path (relative to page or absolute) |
| `alt` | yes | — | Alt text for accessibility |
| `side` | yes | — | Float direction: `left` or `right` |
| `width` | no | — | Width as a plain number (treated as px) or any CSS value (e.g. `45%`) |
| `height` | no | — | Height as a plain number (treated as px) or any CSS value |
| `href` | no | — | Wraps the image in a link to this URL |

**Example**

```
{{</* img-float src="photo.jpg" alt="A photo" side="left" width="300" */>}}
```

---

## img-caption

Displays an image with a caption inside a `<figure>` element. Full-width (no float).

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `src` | yes | — | Image path |
| `alt` | yes | — | Alt text |
| `caption` | no | — | Caption text displayed below the image |
| `width` | no | — | Width as a plain number (px) or CSS value |
| `height` | no | — | Height as a plain number (px) or CSS value |
| `href` | no | — | Wraps the image in a link |

**Example**

```
{{</* img-caption src="photo.jpg" alt="A photo" caption="Standing at the summit." */>}}
```

---

## img-caption-float

Floats an image left or right with a caption, inside a `<figure>` element.

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `src` | yes | — | Image path |
| `alt` | yes | — | Alt text |
| `side` | yes | — | Float direction: `left` or `right` |
| `caption` | no | — | Caption text displayed below the image |
| `width` | no | — | Width as a plain number (px) or CSS value |
| `height` | no | — | Height as a plain number (px) or CSS value |
| `href` | no | — | Wraps the image in a link |

**Example**

```
{{</* img-caption-float src="photo.jpg" alt="A photo" side="right" width="40%" caption="The harbour at dawn." */>}}
```

---

## callout

Wraps inner markdown content in a styled callout box. Full-width, no float.

**Parameters:** none

**Inner content:** markdown (rendered as block content)

**Example**

```
{{</* callout */>}}
**Tip:** Always back up your files before making changes.
{{</* /callout */>}}
```

---

## callout-float

A callout box that floats left or right with text wrapping around it.

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `side` | no | `left` | Float direction: `left` or `right` |
| `width` | no | `65%` | Width of the callout box (any CSS value) |

**Inner content:** markdown (rendered as block content)

**Example**

```
{{</* callout-float side="right" width="40%" */>}}
This is a pull quote or sidebar note floating to the right.
{{</* /callout-float */>}}
```

---

## clear-float

Inserts a `<div>` that clears any active CSS floats. Use this after a sequence of floated images or callouts to prevent the float from affecting subsequent content.

**Parameters:** none

**Example**

```
{{</* img-float src="photo.jpg" alt="Photo" side="left" */>}}

Some text alongside the image...

{{</* clear-float */>}}

This paragraph is back to full width.
```

---

## contact-form

Renders a contact form powered by [Web3Forms](https://web3forms.com/). Submissions are sent to the configured email address via the Web3Forms API. Includes honeypot spam protection.

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `access_key` | yes | — | Web3Forms access key (from your Web3Forms account) |
| `subject` | no | `New message from ElseyWorld` | Subject line of the notification email |

**Example**

```
{{</* contact-form access_key="your-key-here" subject="Message from the contact page" */>}}
```

---

## github-projects

Fetches and displays a user's public GitHub repositories as a card grid, with a sort control. Forks and archived repos are excluded by default.

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `user` | no | Page param `githubUser`, or `NickElseySpelloC` | GitHub username to fetch repos for |
| `includeForks` | no | `false` | Set to `"true"` to include forked repos |
| `includeArchived` | no | `false` | Set to `"true"` to include archived repos |

**Page-level front matter params**

| Param | Description |
|:--|:--|
| `githubUser` | Default GitHub username (overrides the hardcoded fallback) |
| `githubExclude` | A list of repo names or URLs to hide from the output |

**Example**

```
{{</* github-projects user="NickElseySpelloC" */>}}
```

With exclusions in front matter:

```yaml
githubExclude:
  - my-private-looking-repo
  - https://github.com/NickElseySpelloC/old-project
```

---

## paypal-donate

Renders a PayPal Donate button linked to the site's PayPal account.

**Parameters**

| Parameter | Required | Default | Description |
|:--|:--|:--|:--|
| `message` | no | — | Text shown next to the button, also used as the PayPal item name |

**Example**

```
{{</* paypal-donate message="Support this site" */>}}
```
