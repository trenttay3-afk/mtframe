# MT Frame Studio — Website

A hand-built, SEO-optimized static site for a wedding & portrait photography studio.

## What's here

```
website/
├── index.html                  Home
├── about.html                  Studio story + process
├── investment.html             Pricing tiers (Weddings + Portraits/Maternity)
├── contact.html                Inquiry form (POSTs to Formspree)
├── galleries/                  Four masonry galleries + lightbox (generated)
│   ├── weddings.html
│   ├── portraits.html
│   ├── maternity.html
│   └── events.html
├── _partials/                  Nav + footer (shared across pages)
├── _src/                       Source templates — edit these, not the built HTML
│   ├── index.html, about.html, investment.html, contact.html, 404.html
│   └── galleries/{weddings,portraits,maternity,events}.html
├── assets/
│   ├── css/styles.css          Brand system (gold on black, Cormorant + Inter)
│   ├── js/main.js              Nav, reveal-on-scroll, lightbox, form handling
│   └── images/
│       ├── hero/               Hero backgrounds (legacy — galleries now use their own folder)
│       ├── weddings|portraits|maternity|events/
│       │    ├── 01.jpg, 02.jpg ...   Full-size photos (alphabetical = display order)
│       │    ├── thumbs/              Generated ~800px thumbnails
│       │    ├── hero.jpg             Optional — overrides the auto-picked hero
│       │    └── _captions.txt        Optional caption mapping
│       └── logo/
├── build.py                    One-shot builder: pages + galleries + thumbnails
├── robots.txt
├── sitemap.xml                 With image:image entries for every gallery photo
└── 404.html
```

## Adding or reordering photos

The galleries are **folder-driven**. To change what appears on the site:

1. Drop a new photo into the gallery folder, e.g. `assets/images/weddings/`.
2. Name it so the alphabetical order matches the display order — `01.jpg`,
   `02.jpg`, `03.jpg` ... (or `a-couple.jpg`, `b-winter.jpg`, whatever you like).
3. Optional: add a caption for it in the folder's `_captions.txt` file:
   ```
   01.jpg: Snow Canyon engagement
   02.jpg: A stolen moment
   ```
   Any photo not listed there gets a sensible default caption.
4. Optional: drop a `hero.jpg` in the folder to override the hero background
   (otherwise the first image alphabetically becomes the hero).
5. Commit and push. GitHub Actions runs `build.py`, which regenerates
   thumbnails, gallery HTML, and schema.org metadata, and redeploys.

To **remove** a photo, just delete the file from the folder.
To **reorder**, rename the files so the alphabetical order matches the order
you want.

## Building locally

```bash
cd website
pip install Pillow
python3 build.py
python3 -m http.server 8765
# then open http://127.0.0.1:8765
```

`build.py` renders every `_src/` template into the matching top-level HTML
file, scans each gallery folder, regenerates missing/stale thumbnails into
`thumbs/`, and emits the four gallery pages with fresh schema.org markup.

## Brand system

- **Palette:** ink `#0a0908`, ivory `#f7f3ec`, signature gold `#c9a961`
- **Type:** Cormorant Garamond (display) + Inter (UI)
- **Motion:** gentle ease on reveal, lightbox keyboard-nav (←/→/Esc)

## SEO coverage

- Per-page unique `<title>`, `<meta description>`, canonical URL, OG tags.
- JSON-LD: `LocalBusiness`, `Person`, `WebSite`, `AboutPage`, `ContactPage`,
  `Service`, and `ImageGallery` (with embedded `ImageObject`s auto-generated
  from each folder's contents).
- `sitemap.xml` with `<image:image>` for every gallery photo.
- Responsive, accessible (semantic landmarks, alt text, keyboard lightbox).

## Live Instagram feed

The "Follow Along" section on the home page pulls directly from
[@mtframestudio](https://instagram.com/mtframestudio) via
[Behold.so](https://behold.so) (Feed ID `X5gVMeMYahrG5l8urKt4`). It
auto-refreshes when new posts go live — no code changes required.

To swap accounts or change feed layout, edit the feed in your Behold
dashboard. The widget is styled to match the site's black/gold palette
via CSS custom properties at the bottom of `assets/css/styles.css`.

## Contact form

The inquiry form POSTs to [Formspree](https://formspree.io) endpoint
`xjgjowon`. Inquiries land in `mtframephotography@gmail.com`.
Spam is filtered by a hidden honeypot field + Akismet. reCAPTCHA must stay
**off** in the Formspree settings — it breaks AJAX submissions.
