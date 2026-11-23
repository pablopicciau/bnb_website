#!/usr/bin/env python3
"""Avvisa i motori di ricerca che alcune pagine sono cambiate (IndexNow).

IndexNow e' il sistema con cui Bing, Yandex, Seznam e Naver vengono a
rileggere subito le pagine nuove o modificate. Bing a sua volta alimenta
ChatGPT (ricerca), Copilot, DuckDuckGo, Yahoo ed Ecosia. Google non usa
IndexNow: per Google valgono la sitemap e Search Console.

    python3 tools/indexnow.py --since COMMIT   # solo le pagine cambiate da COMMIT
    python3 tools/indexnow.py                  # tutte le pagine della sitemap
    python3 tools/indexnow.py --wait           # prima aspetta che il sito pubblicato sia aggiornato
    python3 tools/indexnow.py --dry-run        # mostra cosa invierebbe, senza inviare

Le pagine cambiate si trovano confrontando le date <lastmod> di sitemap.xml
con quelle della versione di sitemap.xml al commit indicato. Lo lancia da
solo il controllo automatico di GitHub (.github/workflows/aggiorna-sito.yml).
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_pages", ROOT / "tools" / "build_pages.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

ENDPOINT = "https://api.indexnow.org/indexnow"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
USER_AGENT = "meribnb-indexnow/1.0"


def lastmods(xml_text):
    root = ET.fromstring(xml_text)
    return {u.find("s:loc", NS).text: (u.find("s:lastmod", NS).text if u.find("s:lastmod", NS) is not None else "")
            for u in root.findall("s:url", NS)}


def old_sitemap(commit):
    """sitemap.xml com'era al commit indicato (None se non disponibile)."""
    if not commit or set(commit) == {"0"}:
        return None
    try:
        return subprocess.run(["git", "show", f"{commit}:sitemap.xml"], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def changed_urls(since):
    current = lastmods((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    before = old_sitemap(since)
    if before is None:
        return list(current), True
    try:
        previous = lastmods(before)
    except ET.ParseError:
        return list(current), True
    return [url for url, date in current.items() if previous.get(url) != date], False


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def wait_until_live(max_minutes):
    """Aspetta che il sito pubblicato abbia la stessa sitemap del repository."""
    local = (ROOT / "sitemap.xml").read_bytes()
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            if fetch(f"{build.SITE}sitemap.xml?nocache={int(time.time())}") == local:
                print("Il sito pubblicato e' aggiornato.")
                return True
        except (urllib.error.URLError, TimeoutError) as e:
            print("Sito non raggiungibile per ora:", e)
        if time.time() > deadline:
            return False
        print("Il sito pubblicato non e' ancora aggiornato, riprovo tra 30 secondi...")
        time.sleep(30)


def submit(urls):
    host = urlparse(build.SITE).netloc
    body = json.dumps({
        "host": host,
        "key": build.INDEXNOW_KEY,
        "keyLocation": f"{build.SITE}{build.INDEXNOW_KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--since", help="commit di partenza: invia solo le pagine cambiate da allora")
    parser.add_argument("--wait", action="store_true", help="aspetta che il sito pubblicato sia aggiornato")
    parser.add_argument("--dry-run", action="store_true", help="non inviare nulla")
    args = parser.parse_args()

    urls, everything = changed_urls(args.since)
    if not urls:
        print("Nessuna pagina cambiata: niente da segnalare.")
        return
    urls.append(f"{build.SITE}llms.txt")
    print(("Tutte le pagine" if everything else "Pagine cambiate") + f" ({len(urls)}):")
    for url in urls:
        print("  ", url)
    if args.dry_run:
        return
    if args.wait and not wait_until_live(15):
        print("::warning::Il sito pubblicato non si e' aggiornato entro 15 minuti: invio comunque.")
    status, detail = submit(urls)
    if status in (200, 202):
        print(f"IndexNow: segnalazione accettata (HTTP {status}).")
    else:
        # Non blocca nulla: la sitemap resta comunque il canale principale
        print(f"::warning::IndexNow ha risposto HTTP {status}. {detail}")


if __name__ == "__main__":
    sys.exit(main())
