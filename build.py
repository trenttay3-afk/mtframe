"""Build the static site from _src/ + _partials/.

Reads each source page from _src/, injects the shared nav + footer partials
with the correct active link and path prefixes, and writes the final HTML
to the repo root (where GitHub Pages serves it from).

For /galleries/*.html we do NOT regenerate the whole page (their hand-edited
meta and JSON-LD would be lost). Instead we surgically replace the <nav> and
<footer> blocks in-place so nav/footer changes still propagate. Full gallery
regeneration from the CATS spec is still available via build_galleries.py.

Usage:  python build.py
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).parent
PARTIALS = ROOT / "_partials"
SRC = ROOT / "_src"

# Map of source filename -> (page_key, is_gallery_dir).
# page_key is used to set the active nav link. is_gallery_dir is True for
# pages that live under /galleries/ (changes the BASE / GALLERIES prefixes).
PAGES = {
    "index.html":      ("home",       False),
    "about.html":      ("about",      False),
    "investment.html": ("investment", False),
    "contact.html":    ("contact",    False),
    "404.html":        (None,         False),  # no nav/footer to inject
}

# Gallery pages we sync chrome into (see sync_gallery_chrome).
GALLERIES = [
    ("weddings.html",  "weddings"),
    ("portraits.html", "portraits"),
    ("maternity.html", "maternity"),
    ("events.html",    "events"),
]

# Active-link keys that can appear in the nav.
NAV_KEYS = ["home", "about", "weddings", "portraits", "maternity", "events",
            "investment", "contact"]


def render_partial(template: str, active_key: str | None, is_gallery: bool) -> str:
    """Fill {{BASE}}, {{GALLERIES}}, and {{ACTIVE_*}} in a partial."""
    base = "../" if is_gallery else ""
    galleries = "" if is_gallery else "galleries/"
    out = template.replace("{{BASE}}", base).replace("{{GALLERIES}}", galleries)
    for key in NAV_KEYS:
        token = "{{ACTIVE_" + key + "}}"
        out = out.replace(token, "active" if key == active_key else "")
    return out


def build_page(src_path: Path, nav_tpl: str, footer_tpl: str,
               page_key: str | None, is_gallery: bool) -> None:
    src = src_path.read_text(encoding="utf-8")

    # Pages without nav/footer (like 404) get passed through unchanged.
    if "{{NAV}}" in src:
        nav = render_partial(nav_tpl, page_key, is_gallery)
        src = src.replace("{{NAV}}", nav)
    if "{{FOOTER}}" in src:
        footer = render_partial(footer_tpl, None, is_gallery)
        src = src.replace("{{FOOTER}}", footer)

    out_path = ROOT / src_path.name
    out_path.write_text(src, encoding="utf-8")
    print(f"wrote {src_path.name}")


def main() -> int:
    if not PARTIALS.exists() or not SRC.exists():
        print("error: _partials/ or _src/ missing", file=sys.stderr)
        return 1

    nav_tpl = (PARTIALS / "nav.html").read_text(encoding="utf-8")
    footer_tpl = (PARTIALS / "footer.html").read_text(encoding="utf-8")

    for filename, (page_key, is_gallery) in PAGES.items():
        src_path = SRC / filename
        if not src_path.exists():
            print(f"skip {filename} (not in _src/)")
            continue
        build_page(src_path, nav_tpl, footer_tpl, page_key, is_gallery)

    sync_gallery_chrome(nav_tpl, footer_tpl)
    print("--- done ---")
    return 0


def sync_gallery_chrome(nav_tpl: str, footer_tpl: str) -> None:
    """In-place swap the <nav> and <footer> blocks on each gallery page
    with the rendered partials. Everything else (meta tags, JSON-LD,
    masonry, hero) is left untouched."""
    nav_re = re.compile(r'<nav class="nav"[\s\S]*?</nav>')
    footer_re = re.compile(r'<footer class="footer">[\s\S]*?</footer>')

    galleries_dir = ROOT / "galleries"
    for filename, active_key in GALLERIES:
        path = galleries_dir / filename
        if not path.exists():
            print(f"skip galleries/{filename} (missing)")
            continue
        html = path.read_text(encoding="utf-8")

        nav = render_partial(nav_tpl, active_key, is_gallery=True).strip()
        footer = render_partial(footer_tpl, None, is_gallery=True).strip()

        # Use lambda form so \\1, \\g<...> etc. in the replacement aren't
        # interpreted as backreferences.
        new_html, n_nav = nav_re.subn(lambda _: nav, html, count=1)
        new_html, n_footer = footer_re.subn(lambda _: footer, new_html, count=1)

        if n_nav == 0 or n_footer == 0:
            print(f"warn: galleries/{filename} missing expected "
                  f"nav ({n_nav}) or footer ({n_footer}) block; skipping")
            continue

        if new_html != html:
            path.write_text(new_html, encoding="utf-8")
            print(f"synced chrome: galleries/{filename}")
        else:
            print(f"unchanged:     galleries/{filename}")


if __name__ == "__main__":
    sys.exit(main())
