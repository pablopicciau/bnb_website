# B&B Merì — Sito web

Sito statico in quattro lingue (italiano, inglese, francese, spagnolo) per il
B&B Merì, Via Alberto Lamarmora 18, Cagliari. Nessuna dipendenza: solo HTML,
CSS e JavaScript vanilla, pubblicato con GitHub Pages su
`https://www.meribnb.it/`.

## Struttura

```
index.html                    Home in italiano            ┐
en/index.html                 Home in inglese             │
fr/index.html                 Home in francese            │
es/index.html                 Home in spagnolo            │ generate da
parcheggi/index.html          Guida ai parcheggi (IT)     │ tools/build_pages.py
en/parking/index.html         Guida ai parcheggi (EN)     │
fr/stationnement/index.html   Guida ai parcheggi (FR)     │
es/aparcamiento/index.html    Guida ai parcheggi (ES)     │
sitemap.xml                   Mappa del sito              ┘
tools/build_pages.py          Tutti i testi delle 4 lingue + generatore
404.html                      Pagina "non trovata"
css/style.css                 Stile del sito
js/main.js                    Menu mobile e galleria foto
assets/img/                   Logo, illustrazioni, immagini
assets/img/camera-matrimoniale/   Foto della camera (vedi sotto)
robots.txt                    Autorizza i crawler dei motori di ricerca e delle AI
llms.txt                      Riassunto pensato per gli assistenti AI
CNAME                         Dominio personalizzato per GitHub Pages
```

## Modificare i testi

Le quattro home **non vanno modificate a mano**: tutti i testi stanno in
`tools/build_pages.py`, una sezione per lingua. Dopo una modifica:

```bash
python3 tools/build_pages.py
```

Lo script rigenera le home, le guide ai parcheggi e `sitemap.xml`, così le
lingue restano sempre allineate. I testi della guida ai parcheggi sono nel
dizionario `P`; posizioni per le mappe e schede in `SPOTS`. Le tariffe dei
parcheggi sono state verificate a ottobre 2026 (fonti in `SOURCES`):
ricontrollale ogni tanto. Contatti, link del check-in e indirizzo sono
in cima allo script (costanti `PHONE`, `WHATSAPP`, `EMAIL`, `CHECKIN_URL`,
`CIN`).

## Foto della Camera Matrimoniale

Basta caricare le foto nella cartella `assets/img/camera-matrimoniale/`
(anche dal sito di GitHub: *Add file → Upload files*). La galleria le mostra
da sola, in ordine di nome file, in tutte le lingue. Dettagli nel file
`LEGGIMI.md` dentro la cartella.

## Da completare

1. **Coordinate GPS** — nei dati strutturati c'è una stima
   (39.2183, 9.1164): verificala in `structured_data()` dello script.
2. **Copertina social** — `assets/img/og-cover.svg` funziona, ma una foto
   JPG 1200×630 rende meglio su WhatsApp e Facebook.

## Ottimizzazione per motori di ricerca e AI

- **Schema.org JSON-LD**: `BedAndBreakfast` (camere, servizi, lingue,
  posizione, orari) e `FAQPage` in ogni lingua.
- **`llms.txt`**: riassunto in linguaggio naturale per i crawler AI.
- **`robots.txt`**: autorizza esplicitamente GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended e altri.
- **hreflang** IT/EN/FR/ES, canonical, Open Graph, sitemap.

## Provare in locale

```bash
python3 -m http.server 8000
# poi apri http://localhost:8000
```
