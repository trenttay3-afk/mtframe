# MT Frame Studio — Website

A hand-built, SEO-optimized static site for a wedding & portrait photography studio.

## What's here

```
website/
├── index.html                  Home
├── about.html                  Studio story + process
├── investment.html             Pricing tiers (Weddings + Portraits/Maternity)
├── contact.html                Inquiry form (saves to localStorage)
├── galleries/                  Four masonry galleries + lightbox
│   ├── weddings.html
│   ├── portraits.html
│   ├── maternity.html
│   └── events.html
├── admin/
│   ├── login.html              Demo login
│   └── dashboard.html          Stats, gallery editor, inquiries, help
├── assets/
│   ├── css/styles.css          Brand system (gold on black, Cormorant + Inter)
│   ├── js/main.js              Nav, reveal-on-scroll, lightbox, form handling
│   ├── js/admin.js             Demo auth, gallery CRUD, inquiry view
│   └── images/
│       ├── hero/               Hero backgrounds per page (2400px)
│       ├── weddings|portraits|maternity|events/
│       │                        Each image has a full (1800px) + thumb (800px)
│       └── logo/               mark.png, horizontal.png, favicons
├── robots.txt
├── sitemap.xml                 With image:image entries for every gallery photo
├── 404.html
├── build_images.py             Regenerates the image set from raw originals
└── build_galleries.py          Regenerates the four gallery pages
```

## Running locally

```bash
cd website
python3 -m http.server 8765
# then open http://127.0.0.1:8765
```

## Admin

Visit `/admin/login.html` (also linked in the footer) and sign in with:

```
username: admin
password: mtframe2026
```

The dashboard is a **functional prototype** — session, gallery edits, and
inquiries all persist in the browser's `localStorage` on this device only.
Before shipping to production, swap three things:

1. **Auth.** Replace the credential check in `assets/js/admin.js` with Firebase
   Auth, Supabase, or a real backend session.
2. **Gallery storage.** Replace the `mtfs_gallery` localStorage key with a
   database (Supabase/Firestore) and move uploads to S3 / Cloudinary.
3. **Inquiries.** Make the contact form POST to Formspree, Resend, or an API
   route that emails `mtframephotography@gmail.com`.

## Brand system

- **Palette:** ink `#0a0908`, ivory `#f7f3ec`, signature gold `#c9a961`
- **Type:** Cormorant Garamond (display) + Inter (UI)
- **Motion:** gentle ease on reveal, lightbox keyboard-nav (←/→/Esc)

## SEO coverage

- Per-page unique `<title>`, `<meta description>`, canonical URL, OG tags.
- JSON-LD: `LocalBusiness`, `Person`, `WebSite`, `AboutPage`, `ContactPage`,
  `Service`, and `ImageGallery` (with embedded `ImageObject`s).
- `sitemap.xml` with `<image:image>` for every gallery photo.
- `robots.txt` allows public pages, blocks `/admin/`.
- Responsive, accessible (semantic landmarks, alt text, keyboard lightbox).

## Live Instagram feed

The "Follow Along" section on the home page pulls directly from
[@mtframestudio](https://instagram.com/mtframestudio) via
[Behold.so](https://behold.so) (Feed ID `X5gVMeMYahrG5l8urKt4`). It
auto-refreshes when new posts go live — no code changes required.

To swap accounts or change feed layout, edit the feed in your Behold
dashboard. The widget is styled to match the site's black/gold palette
via CSS custom properties at the bottom of `assets/css/styles.css`.

## Regenerating assets

```bash
# Re-slice images from originals (in the folder above this one):
python3 build_images.py

# Re-emit the four gallery pages from the spec:
python3 build_galleries.py
```
