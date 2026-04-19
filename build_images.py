"""Build web-ready images for MT Frame Studio site.

Categorizes originals into weddings / portraits / maternity / events / hero,
resizes to multiple sizes, and writes both a full-size display JPG
(~1800px longest edge, quality 82) and a thumb (~700px longest edge, quality 78).
"""
from pathlib import Path
from PIL import Image, ImageOps

SRC = Path("/sessions/beautiful-jolly-darwin/mnt/MTFrameStudio Website")
DST = SRC / "website/assets/images"
LOGO_SRC = SRC / "logos"

FULL_MAX = 1800
THUMB_MAX = 800
HERO_MAX = 2400

# (source filename, dest category, dest basename, caption)
PLAN = [
    # HEROES (used on landing/about/contact)
    ("1V1A5474-Enhanced-NR.jpg", "hero", "home",    "Golden hour on the coast"),
    ("1V1A5794.jpg",             "hero", "about",   "Snow Canyon, Utah"),
    ("1V1A5272.jpg",             "hero", "contact", "Winter light in Zion"),
    ("1V1A5619.jpg",             "hero", "investment", "Sunset at the shore"),

    # WEDDINGS & ENGAGEMENTS
    ("1V1A5924.jpg", "weddings", "01", "Snow Canyon engagement"),
    ("1V1A5926.jpg", "weddings", "02", "A stolen moment"),
    ("1V1A5495.jpg", "weddings", "03", "Winter whispers"),

    # PORTRAITS
    ("1V1A5474-Enhanced-NR.jpg", "portraits", "01", "Beach sunset portrait"),
    ("1V1A5640.jpg",             "portraits", "02", "Golden hour profile"),
    ("1V1A5541.jpg",             "portraits", "03", "Coastal evening"),
    ("1V1A5587.jpg",             "portraits", "04", "Reflections at dusk"),
    ("1V1A5551.jpg",             "portraits", "05", "Quiet breath"),
    ("1V1A5484.jpg",             "portraits", "06", "Into the waves"),
    ("1V1A5489-2.jpg",           "portraits", "07", "First snow"),
    ("1V1A5868.jpg",             "portraits", "08", "Red rock reflection"),
    ("1V1A5879.jpg",             "portraits", "09", "The adventurer"),
    ("1V1A8308.jpg",             "portraits", "10", "Summer siblings"),
    ("1V1A3669.jpg",             "portraits", "11", "Mother & son"),

    # MATERNITY
    ("1V1A3158.jpg", "maternity", "01", "Bridge at dawn"),
    ("1V1A8834.jpg", "maternity", "02", "Expecting joy"),
    ("1V1A8835.jpg", "maternity", "03", "The three of us"),
    ("1V1A8809.jpg", "maternity", "04", "Mommy to bee"),
    ("1V1A8994.jpg", "maternity", "05", "A little honey"),
    ("1V1A9137.jpg", "maternity", "06", "Welcome, Noah"),
    ("1V1A8687.jpg", "maternity", "07", "Mother & daughter"),
    ("1V1A8690.jpg", "maternity", "08", "Generations"),
    ("1V1A8694.jpg", "maternity", "09", "Sisters & the bump"),
    ("1V1A9379.jpg", "maternity", "10", "Best friends forever"),
    ("1V1A8680.jpg", "maternity", "11", "Garden trio"),
    ("1V1A8650.jpg", "maternity", "12", "Family portrait"),

    # EVENTS
    ("1V1A8597.jpg", "events", "01", "Mommy to Bee welcome"),
    ("1V1A8574.jpg", "events", "02", "Honey favor table"),
    ("1V1A8581.jpg", "events", "03", "Don't Say Baby"),
    ("1V1A8706.jpg", "events", "04", "Themed sweets"),
    ("1V1A8645.jpg", "events", "05", "The bridal party"),
    ("1V1A8728.jpg", "events", "06", "Garden gathering"),
    ("1V1A8856.jpg", "events", "07", "Four friends"),
    ("1V1A9257.jpg", "events", "08", "Table of laughter"),
    ("1V1A9288.jpg", "events", "09", "Under the tent"),
    ("1V1A9157.jpg", "events", "10", "Welcome cake"),
]

def resize(img, max_edge):
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    if max(w, h) <= max_edge:
        return img
    if w >= h:
        nw = max_edge
        nh = round(h * max_edge / w)
    else:
        nh = max_edge
        nw = round(w * max_edge / h)
    return img.resize((nw, nh), Image.LANCZOS)

def save_jpg(img, dest, quality):
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)

def process():
    manifest = []
    for src_name, cat, base, caption in PLAN:
        src = SRC / src_name
        if not src.exists():
            print(f"MISSING {src_name}")
            continue
        with Image.open(src) as im:
            if cat == "hero":
                full = resize(im, HERO_MAX)
                save_jpg(full, DST / "hero" / f"{base}.jpg", quality=82)
                print(f"hero/{base}.jpg  {full.size}")
            else:
                full = resize(im, FULL_MAX)
                thumb = resize(im, THUMB_MAX)
                save_jpg(full, DST / cat / f"{base}.jpg", quality=82)
                save_jpg(thumb, DST / cat / f"{base}-thumb.jpg", quality=78)
                w, h = full.size
                manifest.append({
                    "cat": cat, "base": base, "caption": caption,
                    "w": w, "h": h,
                })
                print(f"{cat}/{base}.jpg  {full.size}")

    # Logos
    for logo_name, out_name, max_edge in [
        ("IMG_0495.PNG", "mark.png", 512),
        ("IMG_0536.PNG", "horizontal.png", 900),
    ]:
        src = LOGO_SRC / logo_name
        if src.exists():
            with Image.open(src) as im:
                im = ImageOps.exif_transpose(im)
                w, h = im.size
                if max(w, h) > max_edge:
                    if w >= h:
                        im = im.resize((max_edge, round(h*max_edge/w)), Image.LANCZOS)
                    else:
                        im = im.resize((round(w*max_edge/h), max_edge), Image.LANCZOS)
                out = DST / "logo" / out_name
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, optimize=True)
                print(f"logo/{out_name}  {im.size}")

    # Favicon from mark
    mark = LOGO_SRC / "IMG_0495.PNG"
    if mark.exists():
        with Image.open(mark) as im:
            im = ImageOps.exif_transpose(im)
            im = im.resize((256, 256), Image.LANCZOS)
            im.save(DST / "logo" / "favicon-256.png", optimize=True)
            im32 = im.resize((32, 32), Image.LANCZOS)
            im32.save(DST / "logo" / "favicon.ico", format="ICO", sizes=[(32, 32)])
            print("favicons written")

    import json
    (DST / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nManifest: {len(manifest)} gallery entries")

if __name__ == "__main__":
    process()
