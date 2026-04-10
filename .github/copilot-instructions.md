# ElseyWorld – Copilot Instructions

## Project Overview

ElseyWorld is a personal/family website at `https://elseyworks.com/` built with **Hugo** using the **Congo** theme (`themes/congo/`). It publishes travel blog posts and magazine-style articles by Nick and Lynn Elsey.

The repo also contains a **Python migration toolset** (`migration/`) used to fetch and migrate content from a legacy CMS.

---

## Hugo / Congo

- Theme: `themes/congo/` — do not edit theme files directly. Override via Hugo's lookup order by placing files in the corresponding `layouts/` or `assets/` path.
- Config: `config/_default/` — split across `hugo.toml`, `params.toml`, `languages.en.toml`, `menus.en.toml`, `markup.toml`, `module.toml`.
- Base URL: `https://elseyworks.com/`
- Color scheme: `congo` (light default, auto dark-mode switching enabled)
- Custom CSS: **`assets/css/custom.css`** — Congo bundles this automatically; no config change needed. Always add styles here, never inline or in theme files.
- Custom shortcodes: **`layouts/shortcodes/`**
- Custom partials: **`layouts/partials/`**
- Static assets: `static/` (copied verbatim), `assets/` (processed by Hugo pipes)

### Content Structure

```
content/
  blog/          # Nick's travel blog posts
  articles/      # Lynn's magazine-style articles (sub-sections: business, careers, food-travel, health, magazines)
  categories/    # Taxonomy term pages (_index.md with title/description)
  resources/     # Site resources/guides
```

- Most content pages use `_index.md` (branch bundles), not `index.md`.
- Category pages (`content/categories/*/_index.md`) use `layout: list`.
- Images are co-located with their content page as page resources.

### Shortcodes

| Shortcode | Purpose |
|-----------|---------|
| `img-float` | Float an image left/right with text wrap |
| `img-caption` | Image with caption, full-width |
| `img-caption-float` | Image with caption, floating |

### Special Skills

/fix-headings:
When I enter this in the prompt, fix anny headings in the current markdown file, as follows:

1. If the text is a single line delininated by double-asterisks and followed by a blank line, convert it to an H2 heading (##).
2. If the text is a single line delininated by triple-asterisks and followed by a non-blank line, convert it to an H3 heading (###).

For example, the following markdown:

```markdown
**Second time around**

With passion on her side. studying law was easier and Janke excelled. She was offered a summer clerkship at Phillips Fox, where she was exposed to life in a large law firm.

***Using business for change***

Writing the report inspired Janke to focus on Indigenous copyright and IP issues. She realised she wanted to provide legal services to Indigenous clients, helping empower them to be creative and to prosper in business. So, she set out on her own.
```

would become:

```markdown
## Second time around

With passion on her side. studying law was easier and Janke excelled. She was offered a summer clerkship at Phillips Fox, where she was exposed to life in a large law firm.

### Using business for change

Writing the report inspired Janke to focus on Indigenous copyright and IP issues. She realised she wanted to provide legal services to Indigenous clients, helping empower them to be creative and to prosper in business. So, she set out on her own.
```


### CSS Conventions

- All custom styles go in `assets/css/custom.css`.
- The file is divided into labelled sections: Grid System, Image Floats, Card Component, Author Bio, Section Spacing, Content Width
- Use `!important` sparingly — only to beat Tailwind utility specificity when necessary.
- Tailwind's `.prose` class sets `max-width: 65ch`; override explicitly when full-width is needed.
- Category/list page article entries: `article.mt-6.max-w-prose` — already overridden to `max-width: 100%`.

---

## Python (Migration Tooling)

- Package manager: **`uv`** (never `pip`).
- Virtual environment: `.venv/` — activate with `source .venv/bin/activate`.
- Entry point: `main.py`; migration modules in `migration/`.
- Runtime: Python ≥ 3.13.
- Key dependencies: `beautifulsoup4`, `playwright`, `requests`.
- Run scripts as modules: `python -m migration.fetch`, etc.

---

## General Conventions

- Prefer editing existing files over creating new ones.
- Do not create summary or changelog markdown files unless explicitly asked.
- Do not add comments or docstrings to code that wasn't changed.
- Hugo `public/` is build output — never edit files there directly.
- The `.venv/` and `public/` directories should be ignored in searches.
