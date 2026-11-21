# Foto della Camera Matrimoniale

Carica qui le foto della camera (anche dal sito di GitHub: *Add file → Upload
files*). In pochi minuti il sito si aggiorna da solo: GitHub rigenera le
pagine, inserisce le foto nella galleria della scheda "Camera Matrimoniale" in
tutte le lingue e ne crea versioni leggere (WebP) in `assets/img/ottimizzate/`.

Le foto sono scritte direttamente nella pagina: così le vedono anche Google
Immagini e gli assistenti AI (ChatGPT, Gemini, Perplexity...), non solo chi
visita il sito.

## Cambiare l'ordine delle foto

Apri il file `ordine.txt` (qui in questa cartella), premi la matita ✏️ per
modificarlo e sposta le righe: la prima riga è la prima foto che si vede.
Poi premi "Commit changes". Il sito si aggiorna in pochi minuti.

Le foto nuove che non sono ancora in `ordine.txt` compaiono in fondo:
se vuoi metterle prima, aggiungi una riga col loro nome nel punto giusto.

**La prima foto orizzontale dell'elenco diventa la copertina** che si vede
quando il sito viene condiviso su WhatsApp, Facebook e simili.

## Descrivere le foto

Dopo il nome del file, in `ordine.txt`, scrivi dopo il simbolo `#` cosa si
vede nella foto (per esempio `# bagno con doccia`). Per le foto nuove questa
nota diventa la descrizione in italiano letta da Google e dagli screen reader.
Le descrizioni curate nelle 4 lingue delle foto attuali sono in
`tools/build_pages.py` (dizionario `PHOTO_ALT`): quando aggiungi una foto,
conviene aggiungere lì anche la sua descrizione in inglese, francese e
spagnolo.

## Regole per le foto

- Formati: JPG, PNG o WEBP (no HEIC: dall'iPhone esporta/condividi come JPG).
- Peso consigliato: sotto 1 MB a foto (puoi ridurle gratis su squoosh.app).
- Foto vere e fedeli alla camera: niente immagini generate o "ricostruite"
  con l'intelligenza artificiale (Google, Booking e gli ospiti lo notano).
- Per togliere una foto basta eliminarla da questa cartella
  (e, per ordine, anche la sua riga in `ordine.txt`).
