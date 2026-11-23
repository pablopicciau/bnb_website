#!/usr/bin/env python3
"""Controlla che il sito sia in regola per Google, Bing e gli assistenti AI.

    python3 tools/check_seo.py                  # dopo build_pages.py
    python3 tools/check_seo.py --strict-dates   # anche le tariffe parcheggi "scadute" sono un errore

Per ogni pagina della sitemap controlla: titolo e descrizione (presenti, di
lunghezza giusta, diversi da pagina a pagina), canonical, versioni nelle altre
lingue (hreflang, in entrambe le direzioni), un solo H1, foto con testo
alternativo e dimensioni, link interni e ancore (#...) esistenti, dati
strutturati leggibili. Poi controlla sitemap.xml, robots.txt, llms.txt e il
file della chiave IndexNow.

Esce con codice 1 se trova errori: su GitHub il controllo automatico diventa
rosso e arriva un'email. Usa solo la libreria standard di Python.
"""
import datetime
import importlib.util
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("build_pages", ROOT / "tools" / "build_pages.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
SITE = build.SITE

TITLE_MAX = 70          # oltre, Google taglia il titolo
DESC_MIN, DESC_MAX = 70, 170
GITHUB = os.environ.get("GITHUB_ACTIONS") == "true"

errors, warnings = [], []


def error(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


class Page(HTMLParser):
    """Raccoglie dalla pagina cio' che serve ai controlli."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = None
        self._in_title = False
        self.meta = {}
        self.canonical = None
        self.hreflang = {}
        self.h1 = 0
        self.ids = set()
        self.links = []
        self.images = []
        self.srcsets = []
        self.jsonld = []
        self._in_jsonld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title, self._buf = True, []
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link":
            relv = (a.get("rel") or "").lower()
            if relv == "canonical":
                self.canonical = a.get("href")
            elif relv == "alternate" and a.get("hreflang"):
                self.hreflang[a["hreflang"]] = a.get("href")
            elif a.get("href") and relv in ("icon", "apple-touch-icon", "manifest", "stylesheet"):
                self.links.append(a["href"])
        elif tag == "h1":
            self.h1 += 1
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img":
            self.images.append(a)
        elif tag == "source" and a.get("srcset"):
            self.srcsets.append(a["srcset"])
        elif tag == "script":
            if a.get("type") == "application/ld+json":
                self._in_jsonld, self._buf = True, []
            elif a.get("src"):
                self.links.append(a["src"])

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.title = "".join(self._buf).strip()
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._buf))
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_title or self._in_jsonld:
            self._buf.append(data)


def local_path(url):
    """File del sito che corrisponde a un indirizzo (None se esterno)."""
    if not url.startswith(SITE):
        return None
    path = unquote(urlparse(url).path)
    target = ROOT / path.lstrip("/")
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def check_page(url, page, pages):
    name = url.replace(SITE, "/")
    if not page.title:
        error(f"{name}: manca il titolo (<title>)")
    elif len(page.title) > TITLE_MAX:
        warn(f"{name}: titolo lungo {len(page.title)} caratteri (meglio entro {TITLE_MAX}): {page.title}")
    desc = page.meta.get("description", "")
    if not desc:
        error(f"{name}: manca la meta description")
    elif not DESC_MIN <= len(desc) <= DESC_MAX:
        warn(f"{name}: description di {len(desc)} caratteri (meglio {DESC_MIN}-{DESC_MAX})")
    if "noindex" in page.meta.get("robots", ""):
        error(f"{name}: la pagina e' nella sitemap ma ha noindex")
    if page.canonical != url:
        error(f"{name}: canonical {page.canonical!r} diverso dall'indirizzo della pagina")
    if page.h1 != 1:
        error(f"{name}: {page.h1} titoli H1 (deve essercene uno)")
    if not page.lang:
        error(f"{name}: manca la lingua (<html lang>)")
    elif page.hreflang.get(page.lang) != url:
        error(f"{name}: hreflang della propria lingua ({page.lang}) non punta a se stessa")
    if "x-default" not in page.hreflang:
        error(f"{name}: manca hreflang x-default")
    for lang, alt in page.hreflang.items():
        other = pages.get(alt)
        if other is None:
            error(f"{name}: hreflang {lang} punta a {alt}, che non e' nella sitemap")
        elif lang != "x-default" and other.hreflang.get(page.lang) != url:
            error(f"{name}: la versione {lang} non rimanda a questa pagina (hreflang non reciproco)")
    for key in ("og:title", "og:description", "og:image", "og:url"):
        if not page.meta.get(key):
            error(f"{name}: manca {key} (anteprima social)")
    og_image = page.meta.get("og:image", "")
    if og_image.endswith(".svg"):
        warn(f"{name}: og:image e' un SVG, che WhatsApp e Facebook non mostrano")
    elif og_image and (local_path(og_image) is None or not local_path(og_image).exists()):
        error(f"{name}: l'immagine og:image {og_image} non esiste")

    for img in page.images:
        src = img.get("src", "")
        if "alt" not in img:
            error(f"{name}: foto senza testo alternativo (alt): {src}")
        if not (img.get("width") and img.get("height")):
            warn(f"{name}: foto senza width/height (la pagina 'salta' mentre carica): {src}")
        target = local_path(urljoin(url, src))
        if target is not None and not target.exists():
            error(f"{name}: foto mancante {src}")
    for srcset in page.srcsets:
        for part in srcset.split(","):
            src = part.strip().split(" ")[0]
            target = local_path(urljoin(url, src))
            if target is not None and not target.exists():
                error(f"{name}: versione ottimizzata mancante {src}")

    for href in page.links:
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(url, href)
        target = local_path(absolute.split("#")[0])
        if target is None:
            continue
        if not target.exists():
            error(f"{name}: link interno rotto {href}")
            continue
        fragment = urlparse(absolute).fragment
        if fragment and target.suffix == ".html":
            other = pages.get(absolute.split("#")[0]) or parse(target)
            if fragment not in other.ids:
                error(f"{name}: il link {href} punta a un'ancora #{fragment} che non esiste")

    if not page.jsonld:
        error(f"{name}: nessun dato strutturato (JSON-LD)")
    for block in page.jsonld:
        if "@@" in block:
            error(f"{name}: segnaposto non sostituito nei dati strutturati")
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            error(f"{name}: dati strutturati non validi ({e})")
            continue
        if data.get("@context") != "https://schema.org":
            error(f"{name}: dati strutturati senza @context schema.org")
        for node in data.get("@graph", [data]):
            if "@type" not in node:
                error(f"{name}: nodo dei dati strutturati senza @type")


def check_parking_date(strict):
    year, month = map(int, build.PARKING_CHECKED.split("-"))
    now = datetime.date.today()
    age = (now.year - year) * 12 + now.month - month
    if age > 6:
        msg = (f"le tariffe dei parcheggi sono state verificate {age} mesi fa ({build.PARKING_CHECKED}): "
               "ricontrollale (fonti in SOURCES) e aggiorna PARKING_CHECKED in tools/build_pages.py")
        (error if strict else warn)(msg)


def main():
    strict = "--strict-dates" in sys.argv
    sitemap_file = ROOT / "sitemap.xml"
    if not sitemap_file.exists():
        sys.exit("manca sitemap.xml: lancia prima python3 tools/build_pages.py")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9",
          "image": "http://www.google.com/schemas/sitemap-image/1.1"}
    tree = ET.parse(sitemap_file)
    pages, urls = {}, []
    for entry in tree.getroot().findall("s:url", ns):
        url = entry.find("s:loc", ns).text
        lastmod = entry.find("s:lastmod", ns)
        urls.append(url)
        if lastmod is None or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod.text or ""):
            error(f"sitemap: data lastmod mancante o non valida per {url}")
        for img in entry.findall("image:image/image:loc", ns):
            target = local_path(img.text)
            if target is None or not target.exists():
                error(f"sitemap: foto inesistente {img.text}")
        path = local_path(url)
        if path is None or not path.exists():
            error(f"sitemap: la pagina {url} non esiste")
            continue
        pages[url] = parse(path)

    for url, page in pages.items():
        check_page(url, page, pages)

    for kind in ("title", "description"):
        seen = {}
        for url, page in pages.items():
            value = page.title if kind == "title" else page.meta.get("description")
            if value and value in seen:
                error(f"{kind} uguale in due pagine: {seen[value]} e {url}")
            seen[value] = url

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").exists() else ""
    if f"Sitemap: {SITE}sitemap.xml" not in robots:
        error("robots.txt: manca la riga Sitemap")
    if re.search(r"(?im)^disallow:\s*/\s*$", robots):
        error("robots.txt: contiene 'Disallow: /' (blocca tutto il sito)")

    llms = ROOT / "llms.txt"
    if not llms.exists():
        error("manca llms.txt")
    else:
        text = llms.read_text(encoding="utf-8")
        for url in urls:
            if f"({url})" not in text:
                error(f"llms.txt: manca la pagina {url}")

    key_file = ROOT / f"{build.INDEXNOW_KEY}.txt"
    if not key_file.exists() or key_file.read_text(encoding="utf-8").strip() != build.INDEXNOW_KEY:
        error("manca il file della chiave IndexNow (lo scrive build_pages.py)")

    check_parking_date(strict)

    for msg in warnings:
        print(f"::warning::{msg}" if GITHUB else f"AVVISO: {msg}")
    for msg in errors:
        print(f"::error::{msg}" if GITHUB else f"ERRORE: {msg}")
    print(f"Controllate {len(pages)} pagine: {len(errors)} errori, {len(warnings)} avvisi.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
