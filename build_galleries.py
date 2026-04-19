"""Generate the four gallery pages from a category spec.

Runs locally at build time. Gallery pages live at website/galleries/*.html
and load images from ../assets/images/<cat>/NN.jpg (+ -thumb.jpg).
"""
from pathlib import Path

ROOT = Path("/sessions/beautiful-jolly-darwin/mnt/MTFrameStudio Website/website")
OUT  = ROOT / "galleries"
OUT.mkdir(exist_ok=True)

CATS = {
    "weddings": {
        "title": "Weddings & Engagements",
        "hero_text": "Weddings",
        "headline": "Weddings & <em>Engagements</em>",
        "lede": "Editorial, unhurried wedding stories. From quiet elopements in Zion to candlelit evenings in Newport, we photograph weddings the way we hope you'll remember them — honestly.",
        "seo_title": "Wedding Photography Portfolio · MT Frame Studio",
        "seo_desc":  "A portfolio of wedding and engagement photography by MT Frame Studio. Editorial, timeless imagery for couples across New England and beyond.",
        "hero_img": "../assets/images/weddings/04.jpg",
        "images": [
            ("01", "Snow Canyon engagement"),
            ("02", "A stolen moment"),
            ("03", "Winter whispers"),
            ("04", "Mountain embrace"),
            ("05", "Held close in the hills"),
        ],
    },
    "portraits": {
        "title": "Portraits",
        "hero_text": "Portraits",
        "headline": "Portraits <em>&amp;</em> Lifestyle",
        "lede": "Individuals, couples, siblings, and families. Portrait sessions at golden hour, in winter light, and everywhere the light happens to be generous that day.",
        "seo_title": "Portrait Photography · Portfolio · MT Frame Studio",
        "seo_desc":  "A portrait photography portfolio — individuals, couples, families, and siblings. Natural, editorial work by MT Frame Studio.",
        "hero_img": "../assets/images/portraits/02.jpg",
        "images": [
            ("01", "Sunset at the shore"),
            ("02", "A quiet profile"),
            ("03", "Golden hour dreaming"),
            ("04", "Barefoot at the tide"),
            ("05", "Last light"),
            ("06", "Into the sky"),
            ("07", "Looking up"),
            ("08", "Red rock reflection"),
            ("09", "The adventurer"),
            ("10", "Summer siblings"),
            ("11", "Brothers & sisters"),
        ],
    },
    "maternity": {
        "title": "Maternity",
        "hero_text": "Maternity",
        "headline": "Maternity <em>&amp;</em> Motherhood",
        "lede": "Pregnancy, in all its quiet magnitude. Sessions that honor the body, the couple, and the generations gathering around a new soul.",
        "seo_title": "Maternity Photography · Portfolio · MT Frame Studio",
        "seo_desc":  "Maternity and motherhood photography portfolio by MT Frame Studio. Editorial, intimate pregnancy sessions.",
        "hero_img": "../assets/images/maternity/01.jpg",
        "images": [
            ("01", "A tender embrace"),
            ("02", "Expecting joy"),
            ("03", "The three of us"),
            ("04", "Mommy to bee"),
            ("05", "A little honey"),
            ("06", "Welcome, Noah"),
            ("07", "Mother & daughter"),
            ("08", "Generations"),
            ("09", "Sisters & the bump"),
            ("10", "Best friends forever"),
            ("11", "Garden trio"),
            ("12", "Family portrait"),
        ],
    },
    "events": {
        "title": "Events",
        "hero_text": "Events",
        "headline": "Events <em>&amp;</em> Celebrations",
        "lede": "Baby showers, family gatherings, engagement parties. The details, the laughter, the tables and the people around them.",
        "seo_title": "Event Photography · Portfolio · MT Frame Studio",
        "seo_desc":  "Event photography portfolio — baby showers, celebrations, and gatherings by MT Frame Studio.",
        "hero_img": "../assets/images/events/01.jpg",
        "images": [
            ("01", "Mommy to Bee"),
            ("02", "Honey favor table"),
            ("03", "Don't Say Baby"),
            ("04", "Sweet details"),
            ("05", "The bridal party"),
            ("06", "Garden gathering"),
            ("07", "Gathered for Noah"),
            ("08", "Table of laughter"),
            ("09", "Under the tent"),
            ("10", "Welcome-home cake"),
        ],
    },
}

NAV = """
<nav class="nav">
  <a class="nav__brand" href="../index.html">
    <img src="../assets/images/logo/mark.png" alt="">
    <div><span>MT Frame Studio</span><small>Weddings &amp; Portraits</small></div>
  </a>
  <button class="nav__toggle" aria-label="Menu"><span></span><span></span><span></span></button>
  <ul class="nav__links">
    <li><a href="../index.html">Home</a></li>
    <li><a href="../about.html">About</a></li>
    <li><a href="weddings.html" class="{ACTIVE_W}">Weddings</a></li>
    <li><a href="portraits.html" class="{ACTIVE_P}">Portraits</a></li>
    <li><a href="maternity.html" class="{ACTIVE_M}">Maternity</a></li>
    <li><a href="events.html" class="{ACTIVE_E}">Events</a></li>
    <li><a href="../investment.html">Investment</a></li>
    <li><a href="../contact.html" class="nav__cta">Inquire</a></li>
  </ul>
</nav>
"""

FOOTER = """
<footer class="footer">
  <div class="footer__grid">
    <div>
      <div class="footer__brand">
        <img src="../assets/images/logo/mark.png" alt="">
        <div><span>MT Frame Studio</span><small>Weddings &amp; Portraits</small></div>
      </div>
      <p style="font-size:.9rem;">Editorial, timeless photography for couples and families. New England-based.</p>
    </div>
    <div><h4>Galleries</h4><ul>
      <li><a href="weddings.html">Weddings</a></li>
      <li><a href="portraits.html">Portraits</a></li>
      <li><a href="maternity.html">Maternity</a></li>
      <li><a href="events.html">Events</a></li>
    </ul></div>
    <div><h4>Studio</h4><ul>
      <li><a href="../about.html">About</a></li>
      <li><a href="../investment.html">Investment</a></li>
      <li><a href="../contact.html">Contact</a></li>
      <li><a href="../admin/login.html">Client / Admin</a></li>
    </ul></div>
    <div><h4>Connect</h4><ul>
      <li><a href="mailto:mtframephotography@gmail.com">mtframephotography@gmail.com</a></li>
      <li><a href="https://instagram.com/mtframestudio" target="_blank" rel="noopener">@mtframestudio</a></li>
      <li>New England &amp; beyond</li>
    </ul></div>
  </div>
  <div class="footer__copy">© <span data-year></span> MT Frame Studio · All photographs © Megan &amp; Trent.</div>
</footer>
"""

def render(cat_key, cat):
    images_html = []
    for name, cap in cat["images"]:
        images_html.append(f'''    <figure data-full="../assets/images/{cat_key}/{name}.jpg">
      <img src="../assets/images/{cat_key}/{name}-thumb.jpg" alt="{cap}" loading="lazy">
      <figcaption>{cap}</figcaption>
    </figure>''')
    images_markup = "\n".join(images_html)

    nav = NAV.replace("{ACTIVE_W}", "active" if cat_key == "weddings" else "") \
             .replace("{ACTIVE_P}", "active" if cat_key == "portraits" else "") \
             .replace("{ACTIVE_M}", "active" if cat_key == "maternity" else "") \
             .replace("{ACTIVE_E}", "active" if cat_key == "events" else "")

    # Image object JSON-LD for each photo (helps Google Images)
    schema_images = "\n".join([
        f'''  {{"@type":"ImageObject","url":"https://mtframestudio.com/assets/images/{cat_key}/{n}.jpg","name":"{c}","creator":{{"@type":"Organization","name":"Megan &amp; Trent — MT Frame Studio"}}}}{"," if i < len(cat["images"])-1 else ""}'''
        for i, (n, c) in enumerate(cat["images"])
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cat['seo_title']}</title>
<meta name="description" content="{cat['seo_desc']}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://mtframestudio.com/galleries/{cat_key}.html">
<meta property="og:title" content="{cat['seo_title']}">
<meta property="og:description" content="{cat['seo_desc']}">
<meta property="og:url" content="https://mtframestudio.com/galleries/{cat_key}.html">
<meta property="og:image" content="https://mtframestudio.com/assets/images/{cat_key}/01.jpg">
<meta property="og:type" content="website">
<link rel="icon" href="../assets/images/logo/favicon.ico">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/styles.css">

<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"ImageGallery",
  "name":"{cat['title']} · MT Frame Studio",
  "description":"{cat['seo_desc']}",
  "image":[
{schema_images}
  ]
}}
</script>
</head>
<body>

{nav}

<header class="hero hero--page">
  <div class="hero__bg" style="background-image:url('{cat['hero_img']}')"></div>
  <div class="hero__inner">
    <span class="hero__tag">{cat['hero_text']}</span>
    <h1>{cat['headline']}</h1>
  </div>
</header>

<section class="section">
  <div class="container center max-readable reveal" style="margin-bottom:3rem;">
    <span class="eyebrow">Selected Work</span>
    <span class="rule"></span>
    <p class="lead">{cat['lede']}</p>
  </div>

  <div class="container">
    <div class="masonry reveal">
{images_markup}
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="container center max-readable reveal">
    <span class="eyebrow">Like what you see?</span>
    <h2>Let's chat about your session.</h2>
    <p>We take a small, deliberate number of bookings each year so every client gets our full attention.
       Send an inquiry &mdash; we'll reply within 48 hours.</p>
    <a href="../contact.html" class="btn btn--solid">Begin Your Inquiry</a>
  </div>
</section>

<!-- Lightbox -->
<div class="lightbox" aria-hidden="true">
  <button class="lightbox__close" aria-label="Close">✕</button>
  <button class="lightbox__prev" aria-label="Previous">‹</button>
  <button class="lightbox__next" aria-label="Next">›</button>
  <img src="" alt="">
  <div class="lightbox__cap"></div>
</div>

{FOOTER}

<script src="../assets/js/main.js"></script>
</body>
</html>
"""
    (OUT / f"{cat_key}.html").write_text(html)
    print(f"wrote galleries/{cat_key}.html  ({len(cat['images'])} images)")

for key, cat in CATS.items():
    render(key, cat)
