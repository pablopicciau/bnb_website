# B&B Merì — Sito web

Sito statico in quattro lingue (italiano, inglese, francese, spagnolo) per il
B&B Merì, Via Alberto Lamarmora 18, Cagliari. Nessuna dipendenza: solo HTML,
CSS e JavaScript vanilla, pubblicato con GitHub Pages su
`https://www.meribnb.it/`.

## Struttura

```
index.html                    Home in italiano      ┐
en/index.html                 Home in inglese       │ generate da
fr/index.html                 Home in francese      │ tools/build_pages.py
es/index.html                 Home in spagnolo      │
sitemap.xml                   Mappa del sito        ┘
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

Lo script rigenera `index.html`, `en/`, `fr/`, `es/` e `sitemap.xml`, così le
lingue restano sempre allineate. Contatti, link del check-in e indirizzo sono
in cima allo script (costanti `PHONE`, `WHATSAPP`, `EMAIL`, `CHECKIN_URL`).

## Foto della Camera Matrimoniale

Basta caricare le foto nella cartella `assets/img/camera-matrimoniale/`
(anche dal sito di GitHub: *Add file → Upload files*). La galleria le mostra
da sola, in ordine di nome file, in tutte le lingue. Dettagli nel file
`LEGGIMI.md` dentro la cartella.

## Da completare

1. **CIN** — nel footer c'è un segnaposto (`IT092009XXXXXXXXX`): appena
   rilasciato, sostituiscilo in `tools/build_pages.py` e rigenera.
2. **Coordinate GPS** — nei dati strutturati c'è una stima
   (39.2183, 9.1164): verificala in `structured_data()` dello script.
3. **Copertina social** — `assets/img/og-cover.svg` funziona, ma una foto
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
