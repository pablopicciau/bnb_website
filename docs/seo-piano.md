# Piano per farsi trovare: Google, Bing e assistenti AI

**B&B Merì — Via Alberto Lamarmora 18, Castello, Cagliari · novembre 2026**

Questo documento spiega cosa conta oggi per comparire nelle ricerche (Google,
Bing, Google Maps) e nelle risposte degli assistenti AI (ChatGPT, Gemini,
Copilot, Perplexity...), cosa è già stato fatto sul sito e cosa resta da fare
a voi, in ordine di importanza.

---

## 0. In breve

- **Sul sito è già fatto quasi tutto ciò che si può fare dal codice** (parte 3):
  foto visibili a Google e alle AI, dati strutturati completi, testi e titoli
  riscritti, una nuova guida "Cosa vedere a Castello" in 4 lingue, date reali
  nella sitemap, `llms.txt` sempre aggiornato, controlli automatici e avviso
  immediato a Bing a ogni modifica.
- **Il passo che conta di più ora è fuori dal sito** (parte 4): Google Search
  Console, il profilo Google Business (la scheda su Google Maps), Bing
  Webmaster Tools e le recensioni. Per una struttura ricettiva sono questi a
  decidere se comparite nella mappa di Google e se le AI vi citano.
- **Obiettivo realistico**: per ricerche generiche come "b&b cagliari"
  dominano Booking, Airbnb e le schede di Google Maps. Il sito deve vincere su:
  1. ricerche per nome ("B&B Merì", "Meri Cagliari");
  2. ricerche precise ("b&b Castello Cagliari", "dove parcheggiare a Castello",
     "cosa vedere a Castello");
  3. domande agli assistenti AI ("un B&B nel centro storico di Cagliari con
     bagno privato"), con dati corretti;
  4. prenotazione diretta (−10% al telefono) di chi vi ha già trovato su Booking.

---

## 1. Da dove partivamo (analisi del sito)

**Cosa andava già bene:** sito statico e leggero, quattro lingue collegate
correttamente (hreflang), dati strutturati di base, domande frequenti, una
guida ai parcheggi molto utile e originale (è il tipo di contenuto che Google
premia), `robots.txt` aperto ai crawler AI e un primo `llms.txt`.

**Problemi trovati e come sono stati risolti:**

| # | Problema | Perché conta | Soluzione |
|---|----------|--------------|-----------|
| 1 | In una ricerca di prova sul web per "B&B Merì Cagliari" e per "meribnb.it" il sito non compariva: compaiono solo portali di prenotazione (bedandbreakfast.eu, lodging-world.com), e allo stesso indirizzo risulta anche un'altra struttura (Bianca Dimora) | Probabilmente il sito non è ancora (ben) indicizzato, e serve distinguersi bene dall'altra struttura | Search Console, Bing, IndexNow, collegamento dal profilo Google (parte 4) |
| 2 | Le foto della camera arrivavano via JavaScript dall'API di GitHub | I crawler AI non eseguono JavaScript e non vedevano nessuna foto; inoltre l'API di GitHub ha un limite di 60 richieste l'ora per visitatore | Foto scritte direttamente nella pagina, con descrizioni in 4 lingue, versioni WebP leggere e sitemap delle immagini |
| 3 | Copertina social in formato SVG | WhatsApp, Facebook e Google non mostrano le immagini SVG: link condivisi senza foto | Copertina JPG 1200×630 creata dalla prima foto orizzontale della camera |
| 4 | Meta description di oltre 200 caratteri | Google le taglia dopo circa 155: si perdeva il messaggio | Riscritte (circa 150 caratteri) con il vantaggio concreto: −10% prenotando per telefono |
| 5 | Meta keywords | Google le ignora; Bing le considera un possibile segnale di spam | Tolte |
| 6 | Stessa data di modifica (29/10/2026) per tutte le pagine nella sitemap | Google e Bing usano la data per decidere quando ripassare: se non è vera, la ignorano | Data reale calcolata in automatico per ogni pagina |
| 7 | Dati strutturati con immagine SVG, entità non collegate, senza "WebSite" né "breadcrumb" | Meno chiarezza per Google e le AI su chi siete, cosa offrite e come sono fatte le pagine | Un "grafo" schema.org completo per pagina (parte 3) |
| 8 | La colazione (non inclusa) non era scritta nelle pagine | Per un "B&B" è la prima domanda di ospiti e AI: senza risposta, le AI tirano a indovinare | Riquadro "In breve" e nuove domande frequenti |
| 9 | Nessuna pagina per "cosa vedere" | Sono ricerche frequenti di chi sceglie dove dormire, e argomenti su cui un host del posto è credibile | Nuova guida "Cosa vedere a Castello" in 4 lingue |
| 10 | In `ordine.txt` due foto erano scambiate rispetto alle note: il bagno compariva al 3º posto | Prima impressione della camera | Corretto: terza foto ora è "tavolino, finestra e angolo caffè" |
| 11 | Strumenti e documenti interni (`tools/`, `docs/`, `README.md`) pubblicati sul sito | Pagine inutili per i motori, informazioni interne esposte | Esclusi dalla pubblicazione (`_config.yml`) |
| 12 | Nessun controllo automatico | Un link rotto o un errore nei dati strutturati poteva passare inosservato | Controlli SEO automatici a ogni modifica (parte 5) |
| 13 | Coordinate GPS stimate | Coordinate sbagliate = indicazioni sbagliate nelle mappe e nelle AI | **Da verificare voi** (parte 4, punto 9) |

---

## 2. Come funziona oggi la ricerca, nel vostro caso

- **Google** (risultati classici, riquadri AI "AI Overviews"/"AI Mode", Google
  Maps). Per chi cerca un alloggio a Cagliari il primo blocco è spesso la
  **mappa con le schede Google Business**: lì contano scheda completa,
  recensioni, foto e vicinanza. Le risposte AI di Google usano lo stesso
  indice e la stessa scheda.
- **Bing** non è solo Bing: i suoi risultati alimentano anche **Copilot,
  DuckDuckGo, Yahoo, Ecosia** e, in parte, la ricerca di **ChatGPT**. Per
  questo conviene essere ben presenti anche lì (e IndexNow lo avvisa subito).
- **Assistenti AI** (ChatGPT, Gemini, Claude, Perplexity...): leggono le pagine
  con i loro crawler (autorizzati nel vostro `robots.txt`) e premiano
  informazioni **chiare, verificabili e coerenti tra più fonti**: sito, scheda
  Google, Booking, TripAdvisor, recensioni. Se il sito dice una cosa e Booking
  un'altra, l'AI si fida meno di entrambi.
- **Cosa non conta più (o quasi):** meta keywords, ripetere parole chiave,
  pagine "doppione" per ogni variante di ricerca, testi generati in massa.

---

## 3. Cosa è già stato fatto sul sito

### 3.1 Tecnica
- Foto della camera direttamente nell'HTML, con testo alternativo in 4 lingue,
  dimensioni dichiarate e versioni WebP più leggere (dal 30% al 90% di peso
  in meno; sul telefono quasi sempre oltre il 70%);
  le foto non visibili si caricano solo quando servono.
- Copertina JPG 1200×630 per WhatsApp, Facebook e simili, con descrizione.
- Meta `robots` con anteprima immagini grande (`max-image-preview:large`).
- Titoli e descrizioni riscritti e verificati in tutte le pagine.
- Il titolo principale (H1) della home ora contiene anche
  "Bed & Breakfast · Castello, Cagliari" (stesso aspetto grafico di prima).
- Icone per browser e telefoni (favicon, icona iPhone, manifest).
- Sitemap con le **date vere** di ultima modifica e con le foto.
- Pagina 404 con collegamenti nelle 4 lingue; menu sistemato per 7 voci.
- `robots.txt` aggiornato con i crawler attuali di motori di ricerca e AI.

### 3.2 Dati strutturati (schema.org)
Ogni pagina contiene un unico grafo che collega:
- **BedAndBreakfast**: nome e nomi alternativi ("B&B Meri" senza accento,
  "Merì Bed & Breakfast"), indirizzo, coordinate, telefono, email, foto reali,
  logo, orari di check-in/out, animali e fumo non ammessi, lingue, CIN,
  servizi, camere (`HotelRoom` con letto, capienza e foto), contatto per le
  prenotazioni, quartiere (Castello) e, quando li aggiungerete, i profili
  ufficiali (`sameAs`).
- **WebSite**: aiuta Google a mostrare "B&B Merì" come nome del sito nei risultati.
- **WebPage** con data di modifica e immagine principale.
- **FAQPage** (13 domande per lingua), **BreadcrumbList** sulle guide,
  **ParkingFacility** per i parcheggi, **Article + TouristTrip** (con le 12
  tappe) per la guida "cosa vedere".

Non sono state inserite valutazioni o recensioni nei dati strutturati: Google
non le accetta quando sono gestite dalla struttura stessa (o copiate da
Booking) e può penalizzarle.

### 3.3 Contenuti
- **"In breve"** in home: indirizzo, camere, orari, colazione (non inclusa),
  servizi, animali, prenotazione diretta con sconto, CIN. Sono le risposte
  che ospiti e assistenti AI cercano per prime, scritte in modo da poter
  essere citate così come sono.
- **5 nuove domande frequenti** per lingua: colazione, come prenotare e sconto
  diretto, capienza, Wi-Fi e aria condizionata, cosa vedere.
- **Nuova guida "Cosa vedere a Castello, a piedi dal B&B"** in 4 lingue:
  8 tappe in Castello con tempi a piedi, 4 mete appena fuori (Marina,
  anfiteatro, Poetto, Molentargius), consigli pratici e pulsanti "Percorso dal
  B&B" su Google Maps. Indirizzi: `/cosa-vedere-a-castello/`,
  `/en/things-to-see-in-castello/`, `/fr/que-voir-a-castello/`,
  `/es/que-ver-en-castello/`.
  **Rileggetela**: è scritta con informazioni pubbliche e verificate per
  quanto possibile, ma voi conoscete il quartiere meglio di chiunque.
- Collegamenti interni alla guida da menu, piè di pagina, sezione Posizione e FAQ.

### 3.4 Per gli assistenti AI
- `llms.txt` (il "biglietto da visita" per le AI) ora è **generato
  automaticamente dagli stessi dati delle pagine**: fatti chiave in italiano e
  inglese, tutte le FAQ, come arrivare, parcheggi con tariffe, cosa vedere,
  foto con descrizione, elenco delle pagine. Non può più restare indietro.
- Tutti i crawler AI principali sono autorizzati (`robots.txt`).

---

## 4. Cosa dovete fare voi (in ordine di importanza)

> Tempo totale: circa mezza giornata, più la verifica postale/telefonica di
> Google che può richiedere qualche giorno.

### 1. Pubblicare le modifiche e sistemare GitHub (10 minuti)
1. Unire il ramo `claude/seo-motori-ricerca-ai` a `main` (pull request →
   *Merge*): GitHub Pages pubblica il sito dal ramo `main`.
2. **Settings → General → Default branch**: impostate `main` (oggi il ramo
   predefinito è un ramo di lavoro `claude/...`, e il controllo mensile
   automatico parte solo dal ramo predefinito).
3. **Settings → Pages**: controllate che "Enforce HTTPS" sia attivo.
4. Aprite `https://meribnb.it` (senza www): deve portare a
   `https://www.meribnb.it/`. Se non lo fa, va sistemato il DNS del dominio.
5. Scheda **Actions**: dopo ogni modifica deve comparire "Aggiorna sito" con
   la spunta verde. Solo se fallisce al passo "Salva le pagine rigenerate" per
   un problema di permessi: **Settings → Actions → General → Workflow
   permissions** → "Read and write permissions".

### 2. Google Search Console (30 minuti) — priorità massima
1. Andate su search.google.com/search-console e aggiungete la proprietà
   **Dominio** `meribnb.it` (verifica con un record TXT nel DNS: è la più
   completa). In alternativa "Prefisso URL" `https://www.meribnb.it/` con il
   metodo "Tag HTML": copiate il codice in `GOOGLE_SITE_VERIFICATION` in cima a
   `tools/build_pages.py` e salvate: il sito si aggiorna da solo.
2. **Sitemap** → inviate `https://www.meribnb.it/sitemap.xml`.
3. **Controllo URL** → incollate la home e le guide e premete "Richiedi
   indicizzazione" (home IT ed EN, parcheggi, cosa vedere).
4. Dopo 1–2 settimane controllate "Pagine": devono risultare indicizzate le 12
   pagine della sitemap.

### 3. Profilo Google Business (1 ora + verifica) — priorità massima
È la scheda che compare su Google Maps e nella ricerca: per un B&B è il canale
più importante in assoluto.
1. business.google.com → crea o rivendica "B&B Merì" (attenzione a eventuali
   schede doppie o a quella di un'altra struttura allo stesso indirizzo).
2. Categoria principale: **Bed and breakfast**.
3. Nome, indirizzo e telefono **identici** al sito:
   "B&B Merì", "Via Alberto Lamarmora 18, 09124 Cagliari CA",
   "+39 352 036 8357".
4. Sito web: `https://www.meribnb.it/`.
5. Orari di check-in/check-out, servizi (Wi-Fi gratuito, aria condizionata,
   niente animali...), descrizione che citi Castello e il centro storico.
6. Almeno 10 foto vere: camera, bagno, porta antica, ingresso e portone,
   la via, la vista dal quartiere.
7. Completata la verifica, copiate il link della scheda (Condividi → copia
   link) in `SAME_AS` in `tools/build_pages.py`.

### 4. Bing Webmaster Tools e Bing Places (15 minuti)
1. bing.com/webmasters → "Importa da Google Search Console": importa sito e
   sitemap in un clic. (IndexNow è già attivo e funziona anche senza account.)
2. bingplaces.com → importate la scheda da Google Business.
   Bing alimenta Copilot, DuckDuckGo e in parte ChatGPT.

### 5. Apple Business Connect (15 minuti)
businessconnect.apple.com → la scheda su Apple Mappe, che usano Siri e gli
iPhone. Stessi dati identici.

### 6. Booking, Airbnb, TripAdvisor e social: dati identici ovunque
- Nome sempre **"B&B Merì"**, stesso indirizzo, stesso telefono, stesso CIN.
- Nella descrizione citate "Castello, centro storico di Cagliari".
- Profili Instagram/Facebook con il link al sito.
- Mettete i link di tutti questi profili in `SAME_AS`: dicono a Google e alle
  AI che sono la stessa struttura.

### 7. Recensioni (sempre)
- Chiedete a ogni ospite soddisfatto una recensione su **Google** (dal profilo
  Business c'è il link breve da mandare su WhatsApp a fine soggiorno).
- Rispondete a tutte, anche su Booking: le AI leggono anche le risposte.
- Mai recensioni false o "scambiate".

### 8. Foto
- Servono foto vere anche di **esterno, portone, via, vista**: oggi ci sono
  solo interni.
- Le tre foto chiamate `file_0000…` hanno il formato dei file scaricati da
  ChatGPT e due sembrano molto ritoccate: se sono state elaborate con l'AI,
  assicuratevi che rappresentino fedelmente la camera, o sostituitele con
  foto vere. Google e Booking possono rifiutare foto non realistiche e gli
  ospiti lo notano.
- La prima foto orizzontale di `ordine.txt` diventa la copertina social.

### 9. Verifiche di dati
- **Coordinate**: su Google Maps tasto destro esattamente sul portone →
  clic sui numeri → incollateli in `GEO` in `tools/build_pages.py`.
- Dalle foto si vedono **portafinestra con balconcino, angolo caffè con
  macchina e bollitore, tavolino con due sedie, scrivania, soffitti con travi a
  vista, porta antica**. Se confermate, aggiungeteli ai servizi della camera
  (`room1` → `amenities` e `ld_rooms`): sono dettagli che la gente cerca e che
  le AI riportano. Un portale scrive anche che la camera ha il balcone.
- Le **lingue parlate** (oggi i dati dicono italiano, inglese, francese,
  spagnolo): tenete solo quelle che parlate davvero con gli ospiti.

### 10. Farsi citare da siti locali
Chiedete di essere elencati, con link al sito, su portali turistici locali e
regionali, associazioni di B&B, blog e guide di Cagliari. Pochi link da siti
del territorio valgono più di tanti link qualsiasi. Mai comprare link.

---

## 5. L'automazione: cosa succede da solo

Ogni volta che modificate qualcosa sul ramo `main` (un testo in
`tools/build_pages.py`, una foto caricata, `ordine.txt`...), GitHub esegue
`.github/workflows/aggiorna-sito.yml`:

1. **Rigenera** pagine, foto ottimizzate, copertina, sitemap e `llms.txt`.
2. **Controlla** (`tools/check_seo.py`): titoli e descrizioni, canonical,
   lingue collegate, un solo H1, foto con descrizione, link e ancore interne,
   dati strutturati, sitemap, robots, `llms.txt`. Se trova un errore il
   controllo diventa **rosso**, il sito non viene toccato e GitHub vi manda
   un'email con la spiegazione in italiano.
3. **Salva** le pagine rigenerate e fa ripubblicare il sito.
4. **Avvisa Bing & co. (IndexNow)** appena il sito pubblicato è aggiornato,
   solo per le pagine cambiate davvero.

Il **primo di ogni mese** rifà i controlli e, se le tariffe dei parcheggi
hanno più di 6 mesi, vi manda un promemoria (controllo rosso). Dopo averle
verificate, aggiornate `PARKING_CHECKED` in `tools/build_pages.py`.

Per vedere cosa è successo: scheda **Actions** del repository.

---

## 6. Misurare i risultati

| Dove | Cosa guardare | Ogni quanto |
|------|---------------|-------------|
| Search Console → Pagine | Tutte e 12 le pagine indicizzate | dopo 2 settimane, poi ogni mese |
| Search Console → Rendimento | Ricerche con "meri", "castello", "parcheggio", "cosa vedere"; clic e posizione media | ogni mese |
| Profilo Google Business → Rendimento | Chiamate, richieste di indicazioni, clic sul sito | ogni mese |
| Bing Webmaster Tools | Pagine indicizzate, ricerche | ogni mese |
| Prenotazioni dirette | Chiedete sempre "Come ci avete trovato?" e segnatelo | sempre |

**Prova mensile con gli assistenti AI.** Fate queste domande a ChatGPT,
Gemini, Copilot e Perplexity e annotate se citano Merì e se i dati sono
giusti (orari, colazione, sconto, parcheggio):
1. "Consigliami un B&B nel quartiere Castello a Cagliari con bagno privato"
2. "B&B Merì Cagliari: com'è e come si prenota?"
3. "Dove parcheggiare vicino a Castello a Cagliari?"
4. "Cosa vedere a piedi nel quartiere Castello di Cagliari?"
5. "Small B&B in Cagliari old town with private bathroom"
6. "Is breakfast included at B&B Merì in Cagliari?"

Se un'AI riporta un dato sbagliato, quasi sempre lo ha preso da un'altra fonte
(Booking, una vecchia scheda): correggete lì.

**Obiettivi realistici:** entro 1 mese, sito indicizzato e primo risultato
per il nome; entro 3 mesi, scheda Google con almeno 10 recensioni e le guide
(parcheggi e cosa vedere) che portano visite; entro 6 mesi, Merì citato dalle
AI per le domande sul B&B a Castello.

---

## 7. Calendario

- **Questa settimana:** punti 1–4 della parte 4 (GitHub, Search Console,
  profilo Google, Bing).
- **Entro un mese:** Apple Business Connect, profili coerenti e `SAME_AS`,
  coordinate, foto di esterni, prime recensioni Google, rilettura della guida.
- **Mesi 2–3:** un contenuto nuovo scritto da voi (parte 8), citazioni locali,
  prova mensile con le AI.
- **Ogni mese:** Search Console, risposte alle recensioni, prova AI.
- **Ogni 6 mesi:** tariffe dei parcheggi (arriva il promemoria automatico),
  foto, servizi e prezzi su tutti i portali.

---

## 8. Prossimi contenuti (solo con la vostra esperienza)

Google e le AI premiano ciò che solo voi potete raccontare. Idee, in ordine:
1. **Dove mangiare a Castello e alla Marina**: i vostri posti preferiti, con
   cosa ordinare e perché.
2. **Arrivare dal porto e dalla stazione** (traghetti, treni), passo per passo.
3. **Chi siamo**: chi vi accoglie, una foto, da quanto ospitate, le lingue che
   parlate. Rende il sito più affidabile per Google e per gli ospiti.
4. **Cagliari in 2 giorni** partendo da Castello, e i periodi migliori
   dell'anno (eventi, Sant'Efisio, estate).
5. Le domande che vi fanno davvero gli ospiti: aggiungetele alle FAQ.

Tutti i testi vanno in `tools/build_pages.py`: basta descrivere cosa si vuole
aggiungere a chi gestisce il sito (o a Claude) e il resto è automatico.

---

## 9. Cosa evitare

- Recensioni false, "comprate" o scambiate; voti copiati da Booking nei dati
  strutturati.
- Testi generati in massa o pagine doppione per ogni parola chiave.
- Foto che non corrispondono alla realtà.
- Nome, indirizzo o telefono scritti in modo diverso tra sito e portali.
- Bloccare i crawler AI se volete essere citati dalle AI.
- Cambiare gli indirizzi (URL) delle pagine esistenti: se proprio serve,
  chiedete un reindirizzamento.

---

## 10. Dove sta cosa

| Cosa | Dove |
|------|------|
| Tutti i testi (4 lingue) | `tools/build_pages.py` (`T`, `P`, `G`, `C`) |
| Codici di verifica Google/Bing | `GOOGLE_SITE_VERIFICATION`, `BING_SITE_VERIFICATION` |
| Profili ufficiali (Google Maps, Booking...) | `SAME_AS` |
| Coordinate | `GEO` |
| Data verifica tariffe parcheggi | `PARKING_CHECKED` |
| Descrizioni delle foto | `PHOTO_ALT` (e note in `ordine.txt`) |
| Foto e ordine | `assets/img/camera-matrimoniale/` |
| Controlli SEO | `tools/check_seo.py` |
| Avviso a Bing (IndexNow) | `tools/indexnow.py` |
| Automazione | `.github/workflows/aggiorna-sito.yml` |
