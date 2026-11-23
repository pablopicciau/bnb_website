# B&B Merì — Sito web

Sito statico in quattro lingue (italiano, inglese, francese, spagnolo) per il
B&B Merì, Via Alberto Lamarmora 18, Cagliari. Nessuna dipendenza: solo HTML,
CSS e JavaScript vanilla, pubblicato con GitHub Pages su
`https://www.meribnb.it/`.

Il piano per farsi trovare su Google, Bing e dagli assistenti AI (cosa è già
fatto e cosa resta da fare a mano) è in [`docs/seo-piano.md`](docs/seo-piano.md).

## Struttura

```
index.html                          Home in italiano               ┐
en/ fr/ es/index.html               Home in inglese, francese, spagnolo │
parcheggi/index.html                Guida ai parcheggi (IT)        │
en/parking/ fr/stationnement/ es/aparcamiento/   … (EN, FR, ES)    │ generati da
cosa-vedere-a-castello/index.html   Guida "cosa vedere" (IT)       │ tools/build_pages.py
en/things-to-see-in-castello/ fr/que-voir-a-castello/              │
es/que-ver-en-castello/             … (EN, FR, ES)                 │
sitemap.xml                         Mappa del sito, con foto e date │
llms.txt                            Riassunto per gli assistenti AI │
assets/img/ottimizzate/             Foto WebP e copertina social    │
<chiave>.txt                        Chiave IndexNow                 ┘
tools/build_pages.py                Tutti i testi delle 4 lingue + generatore
tools/lastmod.json                  Data di ultima modifica di ogni pagina (automatico)
tools/check_seo.py                  Controlli SEO automatici
tools/indexnow.py                   Avvisa Bing & co. quando una pagina cambia
.github/workflows/aggiorna-sito.yml Automazione su GitHub (vedi sotto)
404.html                            Pagina "non trovata"
css/style.css                       Stile del sito
js/main.js                          Menu mobile, galleria foto, schede parcheggi
assets/img/                         Logo, icone, illustrazioni
assets/img/camera-matrimoniale/     Foto della camera (vedi sotto)
robots.txt                          Autorizza i crawler dei motori di ricerca e delle AI
site.webmanifest, favicon.ico       Icone per browser e telefoni
_config.yml                         Cosa NON pubblicare (strumenti e documenti interni)
CNAME                               Dominio personalizzato per GitHub Pages
```

## Aggiornamento automatico

A ogni modifica sul ramo `main` GitHub esegue da solo
`.github/workflows/aggiorna-sito.yml`, che:

1. rigenera tutte le pagine, le foto ottimizzate, `sitemap.xml` e `llms.txt`;
2. esegue i controlli SEO (`tools/check_seo.py`): se qualcosa non va il
   controllo diventa rosso, il sito non viene toccato e arriva un'email;
3. salva le pagine rigenerate con un commit automatico;
4. appena il sito pubblicato è aggiornato, avvisa Bing (e quindi ChatGPT,
   Copilot, DuckDuckGo) con IndexNow.

Il primo di ogni mese rifà i controlli e avvisa se le tariffe dei parcheggi
hanno più di 6 mesi. Lo stato si vede nella scheda **Actions** del repository.

## Modificare i testi

Le pagine **non vanno modificate a mano**: tutti i testi stanno in
`tools/build_pages.py`, una sezione per lingua (`T` home, `P` parcheggi,
`G` guida "cosa vedere", `C` check-in). Basta modificare quel file, anche dal
sito di GitHub: al salvataggio parte l'aggiornamento automatico.

Per provare in locale:

```bash
python3 tools/build_pages.py
```

```bash
python3 tools/check_seo.py
```

Pillow (`pip install pillow`) serve solo per creare le versioni WebP delle
foto nuove e la copertina social; senza Pillow lo script funziona lo stesso e
ci pensa GitHub. Le tariffe dei parcheggi sono state verificate a ottobre 2026
(fonti in `SOURCES`, mese in `PARKING_CHECKED`). Contatti, link del check-in,
indirizzo, coordinate, codici di verifica e profili social sono in cima allo
script (`PHONE`, `WHATSAPP`, `EMAIL`, `CHECKIN_URL`, `CIN`, `GEO`,
`GOOGLE_SITE_VERIFICATION`, `BING_SITE_VERIFICATION`, `SAME_AS`).

## Foto della Camera Matrimoniale

Basta caricare le foto nella cartella `assets/img/camera-matrimoniale/`
(anche dal sito di GitHub: *Add file → Upload files*) e, se serve, cambiare
l'ordine in `ordine.txt`. In pochi minuti la galleria si aggiorna in tutte le
lingue, con le foto scritte direttamente nella pagina (visibili a Google
Immagini e agli assistenti AI). Dettagli nel file `LEGGIMI.md` dentro la
cartella.

## Da completare

1. **Coordinate GPS** — `GEO` in cima allo script è una stima
   (39.2183, 9.1164): verificala su Google Maps.
2. **Profili ufficiali** — aggiungi in `SAME_AS` i link alla scheda Google
   Maps, a Booking.com, Airbnb, Instagram... appena esistono.
3. **Search Console e Bing Webmaster Tools** — vedi `docs/seo-piano.md`.

## Ottimizzazione per motori di ricerca e AI

- **Dati strutturati schema.org** (un grafo per pagina): `BedAndBreakfast`
  con foto, camere, servizi, orari, contatti e CIN; `WebSite`, `WebPage`,
  `FAQPage`, `BreadcrumbList`, `ParkingFacility`, `Article` e `TouristTrip`.
- **Foto nell'HTML** con testo alternativo in 4 lingue, versioni WebP e
  sitemap delle immagini; copertina JPG 1200×630 per WhatsApp e Facebook.
- **`llms.txt`** generato dagli stessi dati delle pagine.
- **`robots.txt`** che autorizza motori di ricerca e crawler AI.
- **hreflang** IT/EN/FR/ES, canonical, Open Graph, sitemap con date reali.
- **IndexNow** e controlli SEO automatici a ogni modifica.

## Provare in locale

```bash
python3 -m http.server 8000
```

Poi apri http://localhost:8000
