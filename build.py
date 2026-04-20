"""Build the MT Frame Studio static site.

End-to-end pipeline:
  1. For each gallery (weddings, portraits, maternity, events):
       - Scan assets/images/<cat>/ for source JPGs (sorted alphabetically).
       - Read optional _captions.txt mapping filename -> caption.
       - Regenerate missing/stale thumbnails into assets/images/<cat>/thumbs/.
       - Render _src/galleries/<cat>.html -> galleries/<cat>.html with the
         figure list and JSON-LD ImageObject list injected.
  2. For each regular page (index/about/investment/contact/404):
       - Inject nav + footer partials and write to repo root.

Day-to-day update flow for the site owner:
  • Drop a new photo into assets/images/weddings/ (or any gallery folder).
    Name it in the order you want it to appear: 01.jpg, 02.jpg, 03.jpg...
  • Optional: add a caption in the folder's _captions.txt file.
  • Optional: drop a hero.jpg in the folder to override the hero image
    (default is the alphabetically first image).
  • Commit and push. GitHub Actions will rebuild everything, including
    thumbnails, and redeploy.

Run locally with: python build.py
"""
from __future__ import annotations

from pathlib import Path
import html
import re
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    print("error: Pillow is required. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "_partials"
SRC = ROOT / "_src"
IMAGES = ROOT / "assets" / "images"

# ---- Config -------------------------------------------------------------
# Regular (non-gallery) pages. Each entry: filename -> active nav key.
# None means don't inject a nav/footer (e.g. 404).
PAGES: dict[str, str | None] = {
    "index.html":      "home",
    "about.html":      "about",
    "investment.html": "investment",
    "contact.html":    "contact",
    "404.html":        None,
}

# Galleries. Every gallery has a source template in _src/galleries/<key>.html
# and an image folder at assets/images/<key>/.
GALLERIES: list[str] = ["weddings", "portraits", "maternity", "events"]

# Active-link keys that can appear in the nav.
NAV_KEYS = ["home", "about", "weddings", "portraits", "maternity", "events",
            "investment", "contact"]

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

# Thumbnail config: ~800px long edge, quality 78, progressive.
THUMB_MAX = 800
THUMB_QUALITY = 78

# ---- Partial rendering --------------------------------------------------

def render_partial(template: str, active_key: str | None, is_gallery: bool) -> str:
    """Fill {{BASE}}, {{GALLERIES}}, and {{ACTIVE_*}} in a nav/footer partial."""
    base = "../" if is_gallery else ""
    galleries = "" if is_gallery else "galleries/"
    out = template.replace("{{BASE}}", base).replace("{{GALLERIES}}", galleries)
    for key in NAV_KEYS:
        out = out.replace("{{ACTIVE_" + key + "}}", "active" if key == active_key else "")
    return out


# ---- Gallery discovery --------------------------------------------------

def list_gallery_images(gallery: str) -> list[Path]:
    """Return the source JPGs for a gallery, alphabetically sorted.

    Excludes:
      - thumbs/ subdirectory contents (derivatives)
      - legacy -thumb.jpg files (derivatives from the pre-2026 layout)
      - dotfiles and our config files (_captions.txt, hero.jpg stays)
    """
    folder = IMAGES / gallery
    if not folder.exists():
        return []
    images = []
    for p in folder.iterdir():
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.name.startswith("_"):
            continue
        if p.name == "hero.jpg":
            # hero.jpg is a special override — not part of the display grid
            continue
        if p.suffix.lower() not in IMAGE_EXTS:
            continue
        if p.stem.endswith("-thumb"):
            # legacy flat-layout thumbs, ignore
            continue
        images.append(p)
    images.sort(key=lambda p: p.name.lower())
    return images


def load_captions(gallery: str) -> dict[str, str]:
    """Parse _captions.txt in a gallery folder.

    Format: `filename: caption text` per line. Blank lines and lines
    starting with `#` are ignored. Missing captions get a sensible
    default at render time.
    """
    captions_file = IMAGES / gallery / "_captions.txt"
    if not captions_file.exists():
        return {}
    out: dict[str, str] = {}
    for line in captions_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        fname, caption = line.split(":", 1)
        out[fname.strip()] = caption.strip()
    return out


def default_caption(gallery: str, index: int) -> str:
    """Fallback caption for images not listed in _captions.txt.

    Example: default_caption('weddings', 7) -> 'Wedding photograph 7 · MT Frame Studio'
    The singular form ('Wedding') reads better as SEO alt text than 'Weddings'.
    """
    singular = {
        "weddings": "Wedding",
        "portraits": "Portrait",
        "maternity": "Maternity",
        "events": "Event",
    }.get(gallery, gallery.title())
    return f"{singular} photograph {index} · MT Frame Studio"


# ---- Thumbnail generation -----------------------------------------------

def ensure_thumb(source: Path, thumb: Path) -> bool:
    """Regenerate `thumb` from `source` if missing or stale.

    Returns True if a new thumbnail was written, False if the existing
    one is already up to date.
    """
    if thumb.exists() and thumb.stat().st_mtime >= source.stat().st_mtime:
        return False
    thumb.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        w, h = im.size
        if max(w, h) > THUMB_MAX:
            if w >= h:
                new_size = (THUMB_MAX, round(h * THUMB_MAX / w))
            else:
                new_size = (round(w * THUMB_MAX / h), THUMB_MAX)
            im = im.resize(new_size, Image.LANCZOS)
        im.save(thumb, "JPEG", quality=THUMB_QUALITY, optimize=True, progressive=True)
    return True


def image_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) for an image, via Pillow."""
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        return im.size


# ---- Gallery rendering --------------------------------------------------

def build_gallery(gallery: str, nav_tpl: str, footer_tpl: str) -> None:
    """Render _src/galleries/<gallery>.html into galleries/<gallery>.html.

    Injects the figure list, the JSON-LD ImageObject list, and the hero
    image path, plus the standard nav/footer partials.
    """
    src_path = SRC / "galleries" / f"{gallery}.html"
    if not src_path.exists():
        print(f"skip galleries/{gallery}.html (no _src/galleries/{gallery}.html)")
        return

    images = list_gallery_images(gallery)
    captions = load_captions(gallery)

    # Regenerate thumbnails as needed
    thumbs_dir = IMAGES / gallery / "thumbs"
    rebuilt = 0
    for img in images:
        if ensure_thumb(img, thumbs_dir / img.name):
            rebuilt += 1
    if rebuilt:
        print(f"  thumbs: regenerated {rebuilt}/{len(images)} for {gallery}")

    # Determine hero. Priority:
    #   1. assets/images/<gallery>/hero.jpg if present
    #   2. First image alphabetically
    hero_override = IMAGES / gallery / "hero.jpg"
    if hero_override.exists():
        hero_rel = f"../assets/images/{gallery}/hero.jpg"
    elif images:
        hero_rel = f"../assets/images/{gallery}/{images[0].name}"
    else:
        hero_rel = f"../assets/images/hero/{gallery}.jpg"  # final fallback

    # Figure markup
    fig_lines: list[str] = []
    schema_lines: list[str] = []
    for idx, img in enumerate(images, start=1):
        caption = captions.get(img.name) or default_caption(gallery, idx)
        caption_html = html.escape(caption, quote=True)
        try:
            w, h = image_dimensions(thumbs_dir / img.name)
        except (FileNotFoundError, OSError):
            w, h = (533, 800)
        fig_lines.append(
            f'    <figure data-full="../assets/images/{gallery}/{img.name}">\n'
            f'      <img src="../assets/images/{gallery}/thumbs/{img.name}" '
            f'alt="{caption_html}" loading="lazy" decoding="async" '
            f'width="{w}" height="{h}">\n'
            f'      <figcaption>{caption_html}</figcaption>\n'
            f'    </figure>'
        )
        # JSON-LD ImageObject entry. Escape quotes with &quot; since the
        # whole block is embedded as valid JSON inside <script type="application/ld+json">.
        name_json = caption.replace('"', '\\"').replace("&", "&amp;")
        schema_lines.append(
            f'  {{"@type":"ImageObject",'
            f'"url":"https://mtframestudio.com/assets/images/{gallery}/{img.name}",'
            f'"name":"{name_json}",'
            f'"creator":{{"@type":"Organization","name":"Megan &amp; Trent, MT Frame Studio"}}}}'
        )

    figures_block = "\n".join(fig_lines) if fig_lines else ""
    schema_block = ",\n".join(schema_lines)

    # Template fill
    src = src_path.read_text(encoding="utf-8")
    src = src.replace("{{GALLERY_FIGURES}}", figures_block)
    src = src.replace("{{SCHEMA_IMAGES}}", schema_block)
    src = src.replace("{{HERO_IMAGE}}", hero_rel)

    if "{{NAV}}" in src:
        src = src.replace("{{NAV}}", render_partial(nav_tpl, gallery, is_gallery=True))
    if "{{FOOTER}}" in src:
        src = src.replace("{{FOOTER}}", render_partial(footer_tpl, None, is_gallery=True))

    out_path = ROOT / "galleries" / f"{gallery}.html"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(src, encoding="utf-8")
    print(f"wrote galleries/{gallery}.html  ({len(images)} images)")


# ---- Regular page rendering ---------------------------------------------

def build_page(filename: str, active_key: str | None, nav_tpl: str, footer_tpl: str) -> None:
    src_path = SRC / filename
    if not src_path.exists():
        print(f"skip {filename} (not in _src/)")
        return
    src = src_path.read_text(encoding="utf-8")
    if "{{NAV}}" in src:
        src = src.replace("{{NAV}}", render_partial(nav_tpl, active_key, is_gallery=False))
    if "{{FOOTER}}" in src:
        src = src.replace("{{FOOTER}}", render_partial(footer_tpl, None, is_gallery=False))
    (ROOT / filename).write_text(src, encoding="utf-8")
    print(f"wrote {filename}")


# ---- Entry point --------------------------------------------------------

def main() -> int:
    if not PARTIALS.exists() or not SRC.exists():
        print("error: _partials/ or _src/ missing", file=sys.stderr)
        return 1

    nav_tpl = (PARTIALS / "nav.html").read_text(encoding="utf-8")
    footer_tpl = (PARTIALS / "footer.html").read_text(encoding="utf-8")

    # Regular pages
    for filename, active_key in PAGES.items():
        build_page(filename, active_key, nav_tpl, footer_tpl)

    # Galleries
    for gallery in GALLERIES:
        build_gallery(gallery, nav_tpl, footer_tpl)

    print("--- done ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
