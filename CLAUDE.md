# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MT Frame Studio — a hand-built static marketing site for a wedding & portrait photography studio (`mtframestudio.com`). No framework, no bundler, no package.json. Plain HTML + CSS + vanilla JS, plus two Python scripts that regenerate the images and gallery pages from source material.

## Running locally

The repo root **is** the site root (the README's `cd website` is stale — there's no `website/` subdir):

```bash
python build.py            # regenerate top-level HTML + sync gallery chrome
python -m http.server 8765
# http://127.0.0.1:8765
```

There is no test suite and no linter. `build.py` is idempotent — safe to run anytime.

## Regenerating images and galleries

Both scripts contain **hard-coded absolute paths** near the top that point to a specific sandbox (`/sessions/beautiful-jolly-darwin/mnt/MTFrameStudio Website/...`). They will not run on another machine without editing `SRC` / `ROOT` to point at the local originals folder.

```bash
python3 build_images.py      # slices originals → assets/images/<cat>/NN.jpg + NN-thumb.jpg, writes manifest.json
python3 build_galleries.py   # emits galleries/{weddings,portraits,maternity,events}.html
```

`build_images.py` depends on Pillow (`pip install Pillow`).

## Architecture

- **Top-level pages are built from `_src/` + `_partials/`**: sources live in `_src/index.html`, `_src/about.html`, `_src/investment.html`, `_src/contact.html`, `_src/404.html` with `{{NAV}}` / `{{FOOTER}}` placeholders. `build.py` injects the shared partials and writes the final HTML to repo root (where Pages serves it). Edit sources, never the generated top-level files — they get overwritten.
- **Gallery pages are hand-edited with chrome synced in**: `galleries/*.html` carry their own body/meta/JSON-LD but their `<nav>` and `<footer>` blocks get surgically replaced by `build.py`'s `sync_gallery_chrome()` so nav changes propagate. Full regeneration from `build_galleries.py`'s `CATS` spec is still available but opt-in (see note below).
- **Nav/footer live in `_partials/nav.html` and `_partials/footer.html`**: placeholders are `{{BASE}}` (path to site root), `{{GALLERIES}}` (path to galleries dir), and `{{ACTIVE_home|about|weddings|…}}`. Change navigation here once.
- **Image set is generated**: files under `assets/images/<category>/NN.jpg` and `NN-thumb.jpg` come from `build_images.py`'s `PLAN` list. Category folders and filenames mirror that list — keep them in sync. Image dimensions are written to `assets/images/manifest.json`.
- **Gallery CATS is out of sync with disk**: `build_galleries.py`'s `CATS` dict currently lists more images than exist on disk (weddings/maternity/events). Running `build_galleries.py` will emit gallery HTML referencing missing images and will also drop the hand-edited `<meta>` and JSON-LD blocks that are currently on the gallery pages. Trim `CATS` and fold the extra meta into the template before running it.
- **JS is a single vanilla IIFE**: `assets/js/main.js` (nav toggle, reveal-on-scroll, lightbox keyboard nav ←/→/Esc, contact form → `mtfs_inquiries` localStorage).
- **SEO**: per-page JSON-LD blocks (`LocalBusiness`, `WebSite`, `AboutPage`, `ContactPage`, `Service`, `ImageGallery`), plus `sitemap.xml` with `<image:image>` entries. When adding/removing gallery photos, regenerate gallery pages **and** hand-update `sitemap.xml`.
- **Deployment hint**: `.nojekyll` at the root — intended for GitHub Pages.

## External dependencies embedded in source

- **Behold.so Instagram widget** — feed ID `X5gVMeMYahrG5l8urKt4` in `index.html`, styled via CSS custom properties at the bottom of `assets/css/styles.css`. Changing the IG account = change the Behold feed, not the code.
- **Google Fonts** — Cormorant Garamond + Inter, loaded per page.

## Brand tokens

Ink `#0a0908`, ivory `#f7f3ec`, signature gold `#c9a961`. Cormorant (display) + Inter (UI). Defined as CSS custom properties at the top of `assets/css/styles.css`.
