#!/usr/bin/env python3
"""
Wedding Vision Board Builder
=============================
Reads board-config.json + images/ → generates output/index.html

Usage:
  python3 build.py              # Build the board
  python3 build.py --validate   # Check all image files exist

To update text:   Edit board-config.json, then run python3 build.py
To update image:  Replace the file in images/, then run python3 build.py
"""

import json, base64, os, sys


# ── Helpers ────────────────────────────────────────────────────────────────

def load_image(path):
    """Load an image file and return a base64 data URI."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return f"data:{mime};base64,{data}"

def img_tag(img_cfg, style=""):
    """Generate an <img> tag from an image config dict."""
    src = load_image(img_cfg["file"])
    alt = img_cfg.get("alt", "")
    cap = img_cfg.get("caption", "")
    style_attr = f' style="{style}"' if style else ""
    return f'<img src="{src}" alt="{alt}" loading="lazy"{style_attr}>'

def img_frame(img_cfg, frame_style="", img_style="", caption=True):
    """Generate a full image frame div."""
    src      = load_image(img_cfg["file"])
    alt      = img_cfg.get("alt", "")
    cap_text = img_cfg.get("caption", "")
    frame_s  = f' style="{frame_style}"' if frame_style else ""
    img_s    = f' style="{img_style}"' if img_style else ""
    cap_html = f'\n      <div class="img-caption">{cap_text}</div>' if caption else ""
    return f'''    <div class="img-frame"{frame_s}>
      <img src="{src}" alt="{alt}" loading="lazy"{img_s}>{cap_html}
    </div>'''

def note_box(label, body):
    """Generate a note box with label and body."""
    body_html = body.replace("&", "&amp;").replace('"', "&quot;")
    label_html = label.replace("&", "&amp;")
    return f'''    <div class="note-box">
      <p class="note-label">{label_html}</p>
      <p class="note-body">{body_html}</p>
    </div>'''

def section_header(title):
    """Generate a section header with decorative rules."""
    return f'''  <div class="section-header">
    <div class="section-rule"></div>
    <h2 class="section-heading">{title}</h2>
    <div class="section-rule"></div>
  </div>'''

def brief_p(text):
    text_html = text.replace("&", "&amp;").replace('"', "&quot;")
    return f'  <p class="brief">{text_html}</p>'


# ── CSS ────────────────────────────────────────────────────────────────────

CSS = """
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  :root{
    --ivory:#F8F4EE;--pearl:#FDFAF6;--blush:#EAC8BF;--rose:#C8958A;
    --champ:#D4B896;--gold:#B8975A;--dblue:#8B9EB0;--navy:#1C2B3A;
    --text:#2A1F1A;--muted:#7A6A60;
  }
  html{scroll-behavior:smooth;}
  body{background:var(--ivory);color:var(--text);font-family:'Jost',sans-serif;font-weight:300;letter-spacing:.02em;overflow-x:hidden;}
  .hero{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:80px 24px 60px;background:var(--pearl);position:relative;overflow:hidden;}
  .hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 55% at 50% 30%,rgba(212,184,150,.18) 0%,transparent 70%);pointer-events:none;}
  .hero-eyebrow{font-size:.7rem;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);margin-bottom:28px;}
  .hero-title{font-family:'Cormorant Garamond',serif;font-size:clamp(3.2rem,9vw,7.5rem);font-weight:300;line-height:1;letter-spacing:-.01em;}
  .hero-title em{font-style:italic;color:var(--rose);}
  .hero-amp{font-family:'Cormorant Garamond',serif;font-size:clamp(2rem,5vw,4rem);font-weight:300;font-style:italic;color:var(--gold);display:block;margin:8px 0;}
  .hero-date{margin-top:32px;font-size:.8rem;letter-spacing:.25em;text-transform:uppercase;color:var(--muted);}
  .hero-tagline{margin-top:14px;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.1rem;color:var(--muted);font-weight:300;}
  .hero-rule{width:1px;height:80px;background:linear-gradient(to bottom,transparent,var(--gold),transparent);margin:48px auto 0;}
  nav{position:sticky;top:0;z-index:100;background:rgba(248,244,238,.96);backdrop-filter:blur(8px);border-bottom:1px solid rgba(184,151,90,.2);padding:0 24px;display:flex;align-items:center;justify-content:center;gap:28px;height:52px;overflow-x:auto;}
  nav a{font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);text-decoration:none;white-space:nowrap;transition:color .2s;}
  nav a:hover{color:var(--gold);}
  .palette-section{padding:80px 24px;text-align:center;background:var(--pearl);}
  .section-label{font-size:.65rem;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);margin-bottom:40px;}
  .swatches{display:flex;flex-wrap:wrap;justify-content:center;gap:12px 20px;max-width:700px;margin:0 auto;}
  .swatch{display:flex;flex-direction:column;align-items:center;gap:8px;}
  .swatch-dot{width:52px;height:52px;border-radius:50%;border:1px solid rgba(0,0,0,.06);}
  .swatch-name{font-size:.62rem;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);}
  .board-section{padding:100px 40px;max-width:1400px;margin:0 auto;}
  .divider{border:none;border-top:1px solid rgba(184,151,90,.12);}
  .section-header{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:20px;margin-bottom:60px;}
  .section-rule{height:1px;background:linear-gradient(to right,transparent,rgba(184,151,90,.4),transparent);}
  .section-heading{font-family:'Cormorant Garamond',serif;font-size:clamp(1.6rem,3vw,2.4rem);font-weight:300;text-align:center;white-space:nowrap;letter-spacing:.04em;}
  .section-heading em{font-style:italic;color:var(--rose);}
  .brief{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.05rem;line-height:1.75;color:var(--muted);max-width:640px;margin:0 auto 48px;text-align:center;}
  .img-frame{overflow:hidden;position:relative;background:#e8e2da;}
  .img-frame img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .6s;}
  .img-frame:hover img{transform:scale(1.03);}
  .img-caption{position:absolute;bottom:0;left:0;right:0;padding:20px 16px 14px;background:linear-gradient(transparent,rgba(26,20,15,.55));color:rgba(255,255,255,.9);font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;}
  .g2{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}
  .g-asym{display:grid;grid-template-columns:1.4fr 1fr;gap:16px;}
  .g-asym-r{display:grid;grid-template-columns:1fr 1.4fr;gap:16px;}
  .looks-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:900px;margin:0 auto;}
  .look-block{display:flex;flex-direction:column;gap:12px;}
  .look-label{font-size:.62rem;letter-spacing:.25em;text-transform:uppercase;color:var(--gold);text-align:center;padding-top:4px;}
  .look-note{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.88rem;color:var(--muted);text-align:center;line-height:1.5;}
  .note-box{padding:24px 28px;background:var(--pearl);border:1px solid rgba(184,151,90,.15);}
  .note-label{font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}
  .note-body{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.92rem;color:var(--muted);line-height:1.7;}
  .signage-note{padding:40px 36px;background:var(--pearl);border:1px solid rgba(184,151,90,.15);display:flex;flex-direction:column;gap:16px;justify-content:center;}
  .signage-heading{font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:300;line-height:1.2;}
  .signage-body{font-size:.82rem;line-height:1.8;color:var(--muted);font-weight:300;}
  .gold-rule{width:40px;height:1px;background:var(--gold);}
  .day-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:rgba(184,151,90,.2);max-width:1200px;margin:0 auto;}
  .day-panel{padding:52px 40px;text-align:center;}
  .day-num{font-family:'Cormorant Garamond',serif;font-size:.68rem;letter-spacing:.35em;text-transform:uppercase;color:var(--gold);margin-bottom:20px;}
  .day-title{font-family:'Cormorant Garamond',serif;font-size:1.9rem;font-weight:300;letter-spacing:.04em;margin-bottom:16px;}
  .day-sub{font-size:.68rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:400;margin-bottom:14px;}
  .day-body{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.97rem;color:var(--muted);line-height:1.9;}
  .cake-note-item{font-size:.82rem;color:var(--muted);line-height:1.7;padding-left:16px;border-left:1px solid var(--gold);margin-bottom:12px;font-weight:300;}
  .cake-note-item strong{color:var(--text);font-weight:400;display:block;margin-bottom:2px;text-transform:uppercase;font-size:.68rem;letter-spacing:.15em;}
  footer{padding:60px 24px;text-align:center;background:var(--pearl);border-top:1px solid rgba(184,151,90,.15);}
  .footer-monogram{font-family:'Cormorant Garamond',serif;font-size:2rem;font-style:italic;color:var(--gold);letter-spacing:.1em;}
  .footer-date{margin-top:8px;font-size:.65rem;letter-spacing:.3em;text-transform:uppercase;color:var(--muted);}
  @media(max-width:768px){
    .board-section{padding:60px 20px;}
    .g2,.g3,.looks-grid,.g-asym,.g-asym-r,.day-grid{grid-template-columns:1fr;}
    nav{gap:16px;}
  }
"""


# ── Section builders ────────────────────────────────────────────────────────

def build_palette(palette):
    swatches = ""
    for s in palette:
        border = ";border:1px solid #e0d9d0" if s.get("border") else ""
        swatches += f'''
    <div class="swatch">
      <div class="swatch-dot" style="background:{s['hex']}{border};"></div>
      <span class="swatch-name">{s['name']}</span>
    </div>'''
    return f'''<section class="palette-section" id="palette">
  <p class="section-label">The Palette</p>
  <div class="swatches">{swatches}
  </div>
</section>'''


def build_day_overview(cfg):
    m = cfg["meta"]
    d = cfg["day_overview"]
    panels_html = ""
    bg_colors = [f"background:var(--ivory)", f"background:var(--pearl);border-left:1px solid rgba(184,151,90,.2);border-right:1px solid rgba(184,151,90,.2)", f"background:var(--ivory)"]
    for i, phase in enumerate(d["phases"]):
        panels_html += f'''
    <div class="day-panel" style="{bg_colors[i]}">
      <p class="day-num">{phase['number']}</p>
      <h3 class="day-title">{phase['title']}</h3>
      <div style="width:32px;height:1px;background:var(--gold);margin:0 auto 20px;"></div>
      <p class="day-sub">{phase['setting']}</p>
      <p class="day-body">{phase['description']}</p>
    </div>'''
    return f'''<section class="board-section" id="overview">
  {section_header("The <em>" + d['title'].split()[-1] + "</em>")}
  <p class="brief">{d['brief']}</p>
  <div class="day-grid">{panels_html}
  </div>
</section>'''


def build_arrival(cfg):
    s = cfg["sections"]["arrival"]
    imgs = s["images"]
    db   = s["design_brief"]
    body = db["body"].replace("\n\n", "<br><br>").replace("\n", "<br>").replace("&", "&amp;").replace('"', "&quot;")
    return f'''<section class="board-section" id="arrival">
  {section_header("Arrival &amp; <em>Welcome</em>")}
  {brief_p(s['brief'])}
  <div class="g2" style="margin-bottom:16px;">
{img_frame(imgs[0], "aspect-ratio:4/3")}
{img_frame(imgs[1], "aspect-ratio:4/3")}
  </div>
  <div class="signage-note">
    <div class="gold-rule"></div>
    <h3 class="signage-heading">{db['heading']}</h3>
    <p class="signage-body">{body}</p>
  </div>
</section>'''


def build_ceremony(cfg):
    s    = cfg["sections"]["ceremony"]
    imgs = s["images"]
    fk   = s["first_kiss"]
    notes_html = "\n".join(note_box(n["label"], n["body"]) for n in s["notes"])
    fk_body = fk["body"].replace("&", "&amp;")
    return f'''<section class="board-section" id="ceremony">
  {section_header("The <em>Ceremony</em>")}
  {brief_p(s['brief'])}
  <div class="g-asym" style="margin-bottom:16px;">
{img_frame(imgs[0], "aspect-ratio:2/3")}
    <div style="display:flex;flex-direction:column;gap:16px;">
{img_frame(imgs[1], "aspect-ratio:4/3")}
{img_frame(imgs[2], "aspect-ratio:4/3")}
    </div>
  </div>
  <div class="g3" style="margin-bottom:16px;">
{notes_html}
  </div>
  <div style="width:100%;aspect-ratio:3/4;max-height:90vh;overflow:hidden;" class="img-frame">
    <img src="{load_image(fk['image']['file'])}" alt="{fk['image']['alt']}" loading="lazy"
         style="width:100%;height:100%;object-fit:contain;background:#080808;">
    <div class="img-caption">{fk['image']['caption']}</div>
  </div>
  <div class="note-box" style="margin-top:16px;text-align:center;max-width:600px;margin-inline:auto;">
    <p class="note-label">{fk['label']}</p>
    <div class="gold-rule" style="margin:10px auto;"></div>
    <p class="note-body">{fk_body}</p>
  </div>
</section>'''


def build_cocktail(cfg):
    s    = cfg["sections"]["cocktail"]
    imgs = s["images"]
    notes_html = "\n".join(note_box(n["label"], n["body"]) for n in s["notes"])
    return f'''<section class="board-section" id="cocktail">
  {section_header("Cocktail <em>Hour</em>")}
  {brief_p(s['brief'])}
  <div class="g2" style="margin-bottom:16px;">
{img_frame(imgs[0], "aspect-ratio:4/3")}
{img_frame(imgs[1], "aspect-ratio:4/3")}
  </div>
  <div class="g3">
{notes_html}
  </div>
</section>'''


def build_looks(cfg):
    s = cfg["sections"]["looks"]
    items_html = ""
    for item in s["items"]:
        note = item["note"].replace("\n\n", "<br><br>").replace("\n", "<br>").replace("&", "&amp;")
        label = item["label"].replace("&", "&amp;")
        items_html += f'''
    <div class="look-block">
{img_frame(item['image'], 'aspect-ratio:2/3')}
      <p class="look-label">{label}</p>
      <p class="look-note">{note}</p>
    </div>'''
    return f'''<section class="board-section" id="looks">
  {section_header("The <em>Looks</em>")}
  {brief_p(s['brief'])}
  <div class="looks-grid">{items_html}
  </div>
</section>'''


def build_entryway(cfg):
    s    = cfg["sections"]["entryway"]
    imgs = s["images"]
    notes_html = "\n".join(note_box(n["label"], n["body"]) for n in s["notes"])
    return f'''<section class="board-section" id="entryway">
  {section_header("The <em>Entryway</em>")}
  {brief_p(s['brief'])}
  <div class="g2" style="margin-bottom:16px;">
{img_frame(imgs[0], "aspect-ratio:4/3")}
{img_frame(imgs[1], "aspect-ratio:4/3")}
  </div>
  <div class="g2">
{notes_html}
  </div>
</section>'''


def build_reception(cfg):
    s    = cfg["sections"]["reception"]
    imgs = s["images"]
    m    = cfg["meta"]
    room_items = "".join(f"<li>— {r}</li>" for r in s["room_notes"])
    sw   = s["sweetheart_note"].replace("&", "&amp;")
    df   = s["dance_floor_text"]
    lines_html = "<br>".join(df["lines"])
    return f'''<section class="board-section" id="reception">
  {section_header("The <em>Reception</em>")}
  {brief_p(s['brief'])}
  <div class="g3" style="margin-bottom:16px;">
    <div class="note-box">
      <p class="note-label">The Room</p>
      <ul style="list-style:none;font-size:.82rem;color:var(--muted);line-height:2;font-weight:300;">{room_items}</ul>
    </div>
    <div class="note-box">
      <p class="note-label">The Sweetheart Stage</p>
      <p class="note-body">{sw}</p>
    </div>
{img_frame(imgs[0], "min-height:280px")}
  </div>
  <div class="g2">
{img_frame(imgs[1], "aspect-ratio:16/9")}
    <div style="display:flex;flex-direction:column;gap:16px;justify-content:center;padding:40px 36px;background:var(--navy);">
      <p style="font-family:'Cormorant Garamond',serif;font-size:.68rem;letter-spacing:.35em;text-transform:uppercase;color:var(--champ);">{df['heading']}</p>
      <div style="width:32px;height:1px;background:var(--gold);"></div>
      <p style="font-family:'Cormorant Garamond',serif;font-size:clamp(1.4rem,2.5vw,2rem);font-weight:300;color:var(--ivory);line-height:1.4;">{lines_html}</p>
      <p style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.95rem;color:rgba(248,244,238,.6);line-height:1.8;">{df['subline'].replace('&', '&amp;')}</p>
    </div>
  </div>
</section>'''


def build_tables(cfg):
    s    = cfg["sections"]["tables"]
    imgs = s["images"]
    notes_html = "\n".join(note_box(n["label"], n["body"]) for n in s["notes"])
    return f'''<section class="board-section" id="tables">
  {section_header("The <em>Tables</em>")}
  {brief_p(s['brief'])}
  <div style="margin-bottom:16px;">
{img_frame(imgs[0], "aspect-ratio:4/3")}
  </div>
  <div class="g3">
{notes_html}
  </div>
</section>'''


def build_cake(cfg):
    s    = cfg["sections"]["cake"]
    imgs = s["images"]
    items_html = ""
    for item in s["brief_items"]:
        items_html += f'''        <div class="cake-note-item"><strong>{item['label']}</strong>{item['body']}</div>\n'''
    return f'''<section class="board-section" id="cake">
  {section_header("The <em>Cake</em>")}
  {brief_p(s['brief'])}
  <div class="g2">
{img_frame(imgs[0], "aspect-ratio:2/3")}
    <div style="display:flex;flex-direction:column;gap:16px;">
{img_frame(imgs[1], "aspect-ratio:4/3")}
      <div class="note-box" style="flex:1;display:flex;flex-direction:column;gap:12px;">
        <p class="note-label" style="font-size:.68rem;">The Brief</p>
{items_html}      </div>
    </div>
  </div>
</section>'''


# ── Main build ──────────────────────────────────────────────────────────────

def validate(config):
    """Check all image files referenced in config exist."""
    missing = []
    def check(img):
        if not os.path.exists(img["file"]):
            missing.append(img["file"])

    for section_key, section in config["sections"].items():
        for img in section.get("images", []):
            check(img)
        if "first_kiss" in section:
            check(section["first_kiss"]["image"])
        if "items" in section:
            for item in section["items"]:
                check(item["image"])

    if missing:
        print("❌ Missing image files:")
        for m in missing: print(f"   {m}")
        return False
    print(f"✓ All image files found")
    return True


def build(config):
    m = config["meta"]

    nav_links = [
        ("#palette",  "Palette"),
        ("#overview", "Day Overview"),
        ("#arrival",  "Arrival"),
        ("#ceremony", "Ceremony"),
        ("#cocktail", "Cocktail Hour"),
        ("#looks",    "The Looks"),
        ("#entryway", "Entryway"),
        ("#reception","Reception"),
        ("#tables",   "Tables"),
        ("#cake",     "The Cake"),
    ]
    nav_html = "\n  ".join(f'<a href="{href}">{label}</a>' for href, label in nav_links)

    palette_swatches = "".join(
        f'''
    <div class="swatch">
      <div class="swatch-dot" style="background:{s['hex']}{';border:1px solid #e0d9d0' if s.get('border') else ''};"></div>
      <span class="swatch-name">{s['name']}</span>
    </div>''' for s in config["palette"]
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{m['title_groom']} & {m['title_bride']} — Wedding Vision Board {m['date'].split()[-1]}</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<section class="hero">
  <p class="hero-eyebrow">White Wedding Vision Board · {m['location']} · {m['date'].split()[-1]}</p>
  <h1 class="hero-title">{m['title_groom']} <span class="hero-amp">&amp;</span> <em>{m['title_bride']}</em></h1>
  <p class="hero-date">{m['date']} · {m['location']}</p>
  <p class="hero-tagline">{m['subtitle']}</p>
  <div class="hero-rule"></div>
</section>

<nav>
  {nav_html}
</nav>

<section class="palette-section" id="palette">
  <p class="section-label">The Palette</p>
  <div class="swatches">{palette_swatches}
  </div>
</section>

<hr class="divider">

{build_day_overview(config)}

<hr class="divider">

{build_arrival(config)}

<hr class="divider">

{build_ceremony(config)}

<hr class="divider">

{build_cocktail(config)}

<hr class="divider">

{build_looks(config)}

<hr class="divider">

{build_entryway(config)}

<hr class="divider">

{build_reception(config)}

<hr class="divider">

{build_tables(config)}

<hr class="divider">

{build_cake(config)}

<footer>
  <p class="footer-monogram">O &amp; T · K</p>
  <p class="footer-date">{m['title_groom']} &amp; {m['title_bride']} · {m['location']} · {m['date']}</p>
  <p style="margin-top:16px;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.9rem;color:var(--muted);">{m['subtitle']}</p>
</footer>

</body>
</html>"""

    os.makedirs("output", exist_ok=True)
    with open("output/index.html", "w") as f:
        f.write(html)
    size = os.path.getsize("output/index.html")
    print(f"✓ Board built: output/index.html ({size/1024/1024:.1f}MB)")


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    config_path = "board-config.json"
    if not os.path.exists(config_path):
        print(f"❌ {config_path} not found. Run from the wedding-board/ directory.")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    if "--validate" in sys.argv:
        ok = validate(config)
        sys.exit(0 if ok else 1)

    print("Building wedding board...")
    ok = validate(config)
    if not ok:
        sys.exit(1)
    build(config)
