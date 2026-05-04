#!/usr/bin/env python3
"""
Build script for Michael Harmon's site.

Reads content from page folders (home/, stories/, etc.) and generates
a static HTML site into _site/.

Run from repo root:  python3 _build/build.py
"""

import os
import re
import shutil
from html import escape
from pathlib import Path

import yaml

# ─── Paths ───────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "_build"
SITE = ROOT / "_site"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}


# ─── Markdown → HTML ─────────────────────────────────────────────────────────

def md_inline(text: str) -> str:
    """Convert inline markdown (links, bold, italic) to HTML. Escapes first."""
    text = escape(text)

    def link_repl(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(("/", "#", "mailto:")):
            return f'<a href="{url}">{label}</a>'
        return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def md_to_html(md: str) -> str:
    """Convert a block of markdown to HTML paragraphs."""
    paras = [p.strip() for p in md.strip().split("\n\n") if p.strip()]
    return "\n".join(f"<p>{md_inline(p)}</p>" for p in paras)


# ─── Image discovery ─────────────────────────────────────────────────────────

def scan_images(page_dir: Path) -> tuple[str | None, list[str]]:
    """
    Scan <page_dir>/images/ for image files.
    Returns (hero_filename, [sorted grid filenames]).
    hero.* is extracted separately and not included in the grid.
    """
    img_dir = page_dir / "images"
    if not img_dir.is_dir():
        return None, []

    hero = None
    grid = []
    for f in sorted(img_dir.iterdir()):
        if f.suffix.lower() not in IMAGE_EXTS:
            continue
        if f.stem.lower() == "hero":
            hero = f.name
        else:
            grid.append(f.name)

    return hero, grid


def copy_page_images(slug: str) -> None:
    src = ROOT / slug / "images"
    if not src.is_dir():
        return
    dest = SITE / "images" / slug
    dest.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.suffix.lower() in IMAGE_EXTS:
            shutil.copy2(f, dest / f.name)


# ─── HTML layout ─────────────────────────────────────────────────────────────

GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?'
    'family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&'
    'family=Libre+Franklin:wght@300;400;500;600;700&'
    'display=swap">'
)


def render_nav(config: dict, current_path: str) -> str:
    items = []
    for item in config["nav"]:
        cls = ' class="active"' if item["path"] == current_path else ""
        items.append(f'<a href="{item["path"]}"{cls}>{escape(item["label"])}</a>')
    return "\n      ".join(items)


def render_page(config: dict, *, title: str, current_path: str, body: str) -> str:
    site_name = escape(config["site_name"])
    full_title = escape(title) if current_path == "/" else f"{escape(title)} | {site_name}"
    nav = render_nav(config, current_path)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  {GOOGLE_FONTS}
  <link rel="stylesheet" href="/style.css">
</head>
<body id="top">
  <header>
    <div class="header-inner">
      <a class="site-name" href="/">{site_name}</a>
      <button class="menu-toggle" aria-label="Open menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <nav>
        <button class="nav-close" aria-label="Close menu">&times;</button>
        {nav}
      </nav>
    </div>
    <div class="nav-backdrop"></div>
  </header>

  <div class="page-content">
    <main>
{body}
    </main>

    <footer>
      <a class="back-to-top" href="#top">Back to top <span>&#8963;</span></a>
      <p class="copyright">{escape(config.get("copyright", ""))}</p>
    </footer>
  </div>

  <script>
    document.querySelectorAll('nav a').forEach(function(a) {{
      a.addEventListener('click', function(e) {{
        if (a.pathname === location.pathname) return;
        e.preventDefault();
        document.querySelector('.page-content').classList.add('leaving');
        setTimeout(function() {{ location.href = a.href; }}, 250);
      }});
    }});
    window.addEventListener('pageshow', function(e) {{
      if (e.persisted) document.querySelector('.page-content').classList.remove('leaving');
    }});
    var hdr = document.querySelector('header');
    window.addEventListener('scroll', function() {{
      hdr.classList.toggle('hidden', window.scrollY > 400);
    }}, {{ passive: true }});
    var io = new IntersectionObserver(function(entries) {{
      entries.forEach(function(e) {{
        e.target.style.opacity = Math.min(1, e.intersectionRatio * 1.4);
      }});
    }}, {{ threshold: [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1] }});
    document.querySelectorAll('.scroll-fade').forEach(function(el) {{
      el.style.opacity = 0;
      io.observe(el);
    }});
    var mt = document.querySelector('.menu-toggle');
    var nc = document.querySelector('.nav-close');
    var nb = document.querySelector('.nav-backdrop');
    function setNav(open) {{
      document.body.classList.toggle('nav-open', open);
      mt.setAttribute('aria-expanded', open);
    }}
    mt.addEventListener('click', function() {{ setNav(true); }});
    nc.addEventListener('click', function() {{ setNav(false); }});
    nb.addEventListener('click', function() {{ setNav(false); }});
  </script>
</body>
</html>
"""


def write_page(path: str, html: str) -> None:
    if path == "/":
        out = SITE / "index.html"
    else:
        out = SITE / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  wrote {out.relative_to(SITE)}")


# ─── Page builders ───────────────────────────────────────────────────────────

def build_home(config: dict) -> None:
    text = (ROOT / "home" / "text.md").read_text(encoding="utf-8")
    hero, others = scan_images(ROOT / "home")
    portrait = next((f for f in others if f.lower().startswith("portrait")), None)

    heading = escape(config.get("home_heading", config["site_name"]))
    tagline = escape(config.get("tagline", ""))
    tagline_html = f'<p class="nameplate-tagline">{tagline}</p>' if tagline else ""

    nameplate = f"""    <section class="nameplate">
      <h1 class="nameplate-name">{heading}</h1>
      {tagline_html}
    </section>"""

    hero_html = ""
    if hero:
        hero_html = f"""    <div class="hero home-hero">
      <img src="/images/home/{hero}" alt="">
    </div>"""

    portrait_html = ""
    if portrait:
        portrait_html = (
            f'        <div class="portrait">'
            f'<img src="/images/home/{portrait}" alt="Portrait of {escape(config["site_name"])}">'
            f'</div>'
        )

    body = f"""{nameplate}
{hero_html}
    <section class="bio-band scroll-fade">
      <div class="bio-inner">
{portrait_html}
        <div class="bio-text">
{md_to_html(text)}
        </div>
      </div>
    </section>"""

    write_page("/", render_page(config, title=config["site_name"], current_path="/", body=body))
    copy_page_images("home")


def build_work(config: dict) -> None:
    intro = (ROOT / "work" / "text.md").read_text(encoding="utf-8")
    items_path = ROOT / "work" / "work.yml"
    items = yaml.safe_load(items_path.read_text(encoding="utf-8")) or []

    def item_html(s: dict, *, featured: bool = False) -> str:
        kicker = escape(s.get("kicker", "")) if s.get("kicker") else ""
        title = escape(s["title"])
        dek = escape(s.get("dek", ""))
        publication = escape(s.get("publication", ""))
        date = escape(s.get("date", ""))
        co_byline = escape(s.get("co_byline", "")) if s.get("co_byline") else ""
        link = escape(s["link"])

        byline_parts = []
        if publication:
            byline_parts.append(f'<span class="story-pub">{publication}</span>')
        if date:
            byline_parts.append(f'<span class="story-date">{date}</span>')
        byline = " · ".join(byline_parts)
        co_html = f'<p class="story-co">{co_byline}</p>' if co_byline else ""

        kicker_html = f'<p class="story-kicker">{kicker}</p>' if kicker else ""

        image = s.get("image")
        image_html = ""
        if image:
            image_html = (
                f'<a class="story-image" href="{link}" target="_blank" rel="noopener">'
                f'<img src="/images/work/{escape(image)}" alt="" loading="lazy">'
                f'</a>'
            )

        cls = "story story-featured" if featured else "story"
        return f"""      <article class="{cls}">
        {image_html}
        <div class="story-text">
          {kicker_html}
          <h2 class="story-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></h2>
          <p class="story-dek">{dek}</p>
          <p class="story-byline">{byline}</p>
          {co_html}
        </div>
      </article>"""

    if not items:
        list_html = '<p class="stories-empty">More coming soon.</p>'
    else:
        featured = next((s for s in items if s.get("featured")), None)
        rest = [s for s in items if s is not featured]
        parts = []
        if featured:
            parts.append(item_html(featured, featured=True))
        if rest:
            cards = "\n".join(item_html(s) for s in rest)
            parts.append(f'      <div class="story-grid">\n{cards}\n      </div>')
        list_html = "\n".join(parts)

    body = f"""    <section class="page-head">
      <p class="page-kicker">By Michael Harmon</p>
      <h1 class="page-title">Work</h1>
      <div class="page-intro">
{md_to_html(intro)}
      </div>
    </section>

    <section class="stories scroll-fade">
{list_html}
    </section>"""

    write_page("/work", render_page(config, title="Work", current_path="/work", body=body))
    copy_page_images("work")


def build_photos(config: dict) -> None:
    intro = (ROOT / "photos" / "text.md").read_text(encoding="utf-8")
    _, grid = scan_images(ROOT / "photos")

    if grid:
        items = [
            f'      <a href="/images/photos/{f}" class="grid-item">'
            f'<img src="/images/photos/{f}" alt="" loading="lazy"></a>'
            for f in grid
        ]
        grid_html = '    <div class="image-grid">\n' + '\n'.join(items) + '\n    </div>'
    else:
        grid_html = '    <p class="stories-empty">Photographs coming soon.</p>'

    body = f"""    <section class="page-head">
      <h1 class="page-title">Photos</h1>
      <div class="page-intro">
{md_to_html(intro)}
      </div>
    </section>
{grid_html}
    <div class="lightbox" hidden>
      <button class="lb-close" aria-label="Close">&times;</button>
      <button class="lb-prev" aria-label="Previous">&lsaquo;</button>
      <div class="lb-image"><img src="" alt=""></div>
      <button class="lb-next" aria-label="Next">&rsaquo;</button>
    </div>
    <script>
    (function() {{
      var items = document.querySelectorAll('.grid-item');
      if (!items.length) return;
      var lb = document.querySelector('.lightbox');
      var img = lb.querySelector('.lb-image img');
      var idx = 0;
      function show(i) {{
        idx = (i + items.length) % items.length;
        img.src = items[idx].href;
        lb.hidden = false;
        document.body.style.overflow = 'hidden';
      }}
      function close() {{
        lb.hidden = true;
        document.body.style.overflow = '';
      }}
      items.forEach(function(a, i) {{
        a.addEventListener('click', function(e) {{ e.preventDefault(); show(i); }});
      }});
      lb.querySelector('.lb-close').addEventListener('click', close);
      lb.querySelector('.lb-prev').addEventListener('click', function() {{ show(idx - 1); }});
      lb.querySelector('.lb-next').addEventListener('click', function() {{ show(idx + 1); }});
      lb.addEventListener('click', function(e) {{ if (e.target === lb) close(); }});
      document.addEventListener('keydown', function(e) {{
        if (lb.hidden) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowLeft') show(idx - 1);
        else if (e.key === 'ArrowRight') show(idx + 1);
      }});
    }})();
    </script>"""

    write_page("/photos", render_page(config, title="Photos", current_path="/photos", body=body))
    copy_page_images("photos")


def build_contact(config: dict) -> None:
    text = (ROOT / "contact" / "text.md").read_text(encoding="utf-8")
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    email = lines[0] if lines else ""
    rest = "\n\n".join(lines[1:])
    _, images = scan_images(ROOT / "contact")
    photo = images[0] if images else None

    photo_html = ""
    if photo:
        photo_html = f'      <div class="contact-photo"><img src="/images/contact/{photo}" alt=""></div>'

    body = f"""    <section class="page-head">
      <h1 class="page-title">Contact</h1>
    </section>

    <section class="contact-simple scroll-fade">
{photo_html}
      <div class="contact-body">
        <p class="contact-email"><a href="mailto:{escape(email)}">{escape(email)}</a></p>
{md_to_html(rest)}
      </div>
    </section>"""

    write_page("/contact", render_page(config, title="Contact", current_path="/contact", body=body))
    copy_page_images("contact")


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    os.chdir(ROOT)

    config = yaml.safe_load((ROOT / "config.yml").read_text(encoding="utf-8"))

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    shutil.copy2(BUILD / "style.css", SITE / "style.css")

    print("Building pages:")
    build_home(config)
    build_work(config)
    build_photos(config)
    build_contact(config)

    print(f"\nDone. Site built to {SITE}")


if __name__ == "__main__":
    main()
