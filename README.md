# B&B Lamarmora 18 — Sito web

Sito statico bilingue (italiano + inglese) per il B&B Lamarmora 18,
Via Lamarmora 18, Cagliari. Nessuna dipendenza: solo HTML, CSS e
JavaScript vanilla.

## Struttura

```
index.html          Pagina principale (italiano)
en/index.html       Versione inglese
css/style.css       Stile del sito
js/main.js          Menu mobile
assets/img/         Immagini (segnaposto SVG da sostituire con foto reali)
robots.txt          Autorizza i crawler dei motori di ricerca e delle AI
sitemap.xml         Mappa del sito con varianti hreflang
llms.txt            Riassunto della struttura pensato per gli assistenti AI
```

## Cose da personalizzare prima di andare online

1. **Dominio** — il sito è configurato per `https://www.meribnb.it/`
   (canonical, hreflang, Open Graph, sitemap, robots, llms.txt). Se cambi
   dominio in futuro, cerca `meribnb.it` in `index.html`, `en/index.html`,
   `sitemap.xml`, `robots.txt`, `llms.txt`.
2. **Foto reali** — sostituisci i segnaposto SVG in `assets/img/`
   (`hero.svg`, `room-castello.svg`, `room-marina.svg`) con fotografie vere
   (formato JPG/WebP, ~1600px di larghezza per la hero, ~800px per le stanze)
   e aggiorna i percorsi nei due `index.html`. Aggiungi anche
   `assets/img/og-cover.jpg` (1200×630) per le anteprime sui social.
3. **Contatti** — email `meri.bnb.cagliari@gmail.com` e telefono
   `+39 352 036 8357` (usato anche per i link `tel:` e WhatsApp `wa.me`).
   Per cambiarli in futuro cerca queste stringhe in `index.html`,
   `en/index.html` e `llms.txt`.
4. **Coordinate GPS** — verifica latitudine/longitudine nei blocchi JSON-LD
   (attualmente 39.2183, 9.1164, stima per Via Lamarmora, Castello).
5. **Nomi delle camere e testi** — "Camera Castello" e "Camera Marina" sono
   proposte: cambiali liberamente, ricordando di aggiornare anche i JSON-LD.
6. **Codici regionali** — se richiesto dalla normativa sarda, aggiungi nel
   footer il codice IUN/identificativo della struttura ricettiva.

## Ottimizzazione per motori di ricerca e AI

- **Schema.org JSON-LD**: `BedAndBreakfast` (con camere, servizi, geo,
  orari) e `FAQPage` su entrambe le pagine — è ciò che Google e gli
  assistenti AI leggono per rispondere a "B&B a Cagliari centro".
- **`llms.txt`**: riassunto in linguaggio naturale per i crawler AI.
- **`robots.txt`**: autorizza esplicitamente GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended e altri.
- **hreflang** IT/EN, canonical, Open Graph, sitemap.

## Pubblicazione

Il sito è 100% statico: puoi pubblicarlo gratis con **GitHub Pages**
(Settings → Pages → branch principale), oppure su Netlify / Cloudflare
Pages. Per provarlo in locale:

```bash
python3 -m http.server 8000
# poi apri http://localhost:8000
```
