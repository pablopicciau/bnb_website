# Schede da compilare: dati e testi pronti da copiare

Da usare per i passi della parte 4 di [`seo-piano.md`](seo-piano.md). Regola
d'oro: **gli stessi dati, scritti allo stesso modo, ovunque**.

## Dati identici ovunque

| Campo | Valore |
|-------|--------|
| Nome | B&B Merì |
| Indirizzo | Via Alberto Lamarmora 18, 09124 Cagliari CA, Italia |
| Quartiere | Castello (centro storico) |
| Telefono | +39 352 036 8357 (anche WhatsApp) |
| Email | meri.bnb.cagliari@gmail.com |
| Sito | https://www.meribnb.it/ |
| CIN | IT092009C2000U6994 |
| Check-in / check-out | 15:00–20:00 / entro le 10:30 |
| Coordinate | 39.2183, 9.1164 (**stima da verificare** sul portone) |

## Google Search Console

1. Proprietà **Prefisso URL**: `https://www.meribnb.it/` (non serve accedere
   al DNS). Metodo di verifica **Tag HTML**: copiare solo il codice tra le
   virgolette di `content="..."`.
2. Incollarlo in `tools/build_pages.py`, riga `GOOGLE_SITE_VERIFICATION = ""`
   (su GitHub: aprire il file sul ramo `main`, matita ✏️, incollare tra le
   virgolette, *Commit changes*). In 2–5 minuti il sito si aggiorna da solo;
   poi premere **Verifica** in Search Console.
3. **Sitemap** → `sitemap.xml`.
4. **Controllo URL** → "Richiedi indicizzazione", in quest'ordine (Google ne
   accetta una decina al giorno; le altre arrivano comunque con la sitemap):
   1. https://www.meribnb.it/
   2. https://www.meribnb.it/parcheggi/
   3. https://www.meribnb.it/cosa-vedere-a-castello/
   4. https://www.meribnb.it/en/
   5. https://www.meribnb.it/en/parking/
   6. https://www.meribnb.it/en/things-to-see-in-castello/
   7. https://www.meribnb.it/fr/
   8. https://www.meribnb.it/es/
   9. https://www.meribnb.it/fr/stationnement/
   10. https://www.meribnb.it/es/aparcamiento/
   11. https://www.meribnb.it/fr/que-voir-a-castello/
   12. https://www.meribnb.it/es/que-ver-en-castello/

## Bing Webmaster Tools

bing.com/webmasters → **Importa da Google Search Console** (dopo che Search
Console è verificata). Poi bingplaces.com → importare la scheda da Google
Business Profile.

## Google Business Profile

- **Categoria principale**: Bed and breakfast.
- **Sito web**: https://www.meribnb.it/
- **Descrizione** (703 caratteri, il massimo è 750; Google non vuole link né
  offerte e sconti nella descrizione):

> B&B Merì è un piccolo bed & breakfast a conduzione familiare nel cuore di
> Castello, il quartiere storico fortificato di Cagliari. La Camera
> Matrimoniale ha bagno privato con doccia, aria condizionata e
> riscaldamento, Wi-Fi gratuito, biancheria e set di cortesia; l'acqua del
> rubinetto è potabile. La Cattedrale è a 2 minuti a piedi, il Bastione di
> Saint Remy a 3, la Torre dell'Elefante a 4, Via Roma e il porto a 10.
> Dall'aeroporto: treno fino a Piazza Matteotti, poi bus CTM 7, che ferma
> davanti al portone. Castello è zona a traffico limitato: sul nostro sito
> trovate la guida ai parcheggi vicini. Check-in dalle 15:00 alle 20:00,
> check-out entro le 10:30. Colazione non inclusa, animali non ammessi.

- **Servizi da spuntare**: Wi-Fi gratuito, aria condizionata, riscaldamento,
  bagno privato, asciugacapelli, articoli da toeletta, servizio navetta su
  richiesta, non fumatori, animali non ammessi, colazione non inclusa.
- **Foto**: tutte quelle vere della camera e del bagno, più esterno, portone,
  via e vista dal quartiere (con nomi di file descrittivi, per esempio
  `bb-meri-cagliari-portone.jpg`).
- **Primo aggiornamento** da pubblicare sulla scheda (qui l'offerta è ammessa):

> Prenotate direttamente al B&B Merì: chiamando il +39 352 036 8357 avete il
> 10% di sconto rispetto alla tariffa di Booking. Siamo nel cuore di Castello,
> a 3 minuti dal Bastione di Saint Remy.

## Apple Business Connect

businessconnect.apple.com → stessi dati della tabella in alto, categoria
"Bed and breakfast", stessa descrizione (anche abbreviata).

## Instagram / Facebook (bio)

- IT (117 caratteri): `B&B nel cuore di Castello, Cagliari 🏰 Camera con bagno privato · Prenota diretto e risparmi il 10% 📞 +39 352 036 8357`
- EN (121 caratteri): `B&B in Cagliari's old town (Castello) 🏰 Double room, private bathroom · Book direct by phone, save 10% 📞 +39 352 036 8357`
- Link nella bio: https://www.meribnb.it/

## Messaggio per chiedere una recensione (a fine soggiorno, su WhatsApp)

> Ciao [nome], grazie di essere stati da noi al B&B Merì! Se vi siete
> trovati bene, ci aiutereste moltissimo con una recensione su Google:
> [link breve della scheda]. Bastano due righe. Un saluto da Castello!

> Hi [name], thank you for staying with us at B&B Merì! If you enjoyed your
> stay, a short Google review would help us a lot: [short link]. Just a
> couple of lines is perfect. Greetings from Castello!

## Dopo aver creato le schede

Copiare i loro link in `SAME_AS` in `tools/build_pages.py` (scheda Google
Maps, Booking, Airbnb, TripAdvisor, Instagram, Facebook): il sito si aggiorna
da solo e dice a Google e alle AI che sono tutti la stessa struttura.
