# Check-in online: cosa deve fare il gestionale

Il modulo di check-in sta sul sito (`/checkin/`, `/en/check-in/`,
`/fr/check-in/`, `/es/check-in/`, generato da `tools/build_pages.py`).
Il sito è statico e pubblico: non può salvare dati né conoscere il codice
della porta. Questi compiti spettano al gestionale sulla VPS
(`gestionale.meribnb.it`), che è sempre acceso anche quando il PC è spento.

Finché il gestionale non risponde, il modulo resta spento
(`CHECKIN_FORM_LIVE = False` nel generatore) e i pulsanti del sito portano
ancora a Jotform.

## 1. Indirizzo da esporre

```
POST https://gestionale.meribnb.it/api/checkin
Content-Type: multipart/form-data
```

- Deve rispondere in **HTTPS** (il sito è in HTTPS: una chiamata in HTTP
  verrebbe bloccata dal browser).
- **CORS**: nella risposta deve esserci
  `Access-Control-Allow-Origin: https://www.meribnb.it`. Il modulo invia un
  `multipart/form-data` senza intestazioni speciali, quindi il browser non fa
  la richiesta preliminare `OPTIONS`; gestirla comunque non fa danni.

## 2. Campi ricevuti

Nomi esatti dei campi, come li invia il modulo (verificati con una prova
reale):

| Campo | Obbligatorio | Note |
|---|---|---|
| `lang` | sì | `it`, `en`, `fr`, `es`: lingua di email e istruzioni |
| `arrival`, `departure` | sì | date `AAAA-MM-GG`, partenza dopo l'arrivo |
| `guests_count` | sì | da 1 a 4 |
| `arrival_time` | sì | `HH:MM` |
| `booking_ref` | no | numero di prenotazione Booking |
| `email`, `phone` | sì | |
| `guests[0][first_name]`, `[last_name]` | sì | ospite principale |
| `guests[0][sex]` | sì | `M` o `F` |
| `guests[0][birth_date]` | sì | `AAAA-MM-GG` |
| `guests[0][birth_country]`, `[birth_place]` | sì | testo libero |
| `guests[0][birth_province]` | no | sigla, solo se nato in Italia |
| `guests[0][citizenship]` | sì | testo libero |
| `guests[0][doc_type]` | sì | codici Alloggiati Web: `IDENT`, `PASOR`, `PATEN` |
| `guests[0][doc_number]`, `[doc_place]` | sì | |
| `guests[0][doc_front]` | sì | file immagine o PDF, max 10 MB |
| `guests[0][doc_back]` | no | file, max 10 MB |
| `guests[N][...]` (N = 1..3) | sì | accompagnatori: stessi dati anagrafici, senza documento |
| `guests[N][doc_photo]` | no | file, max 10 MB |
| `notes` | no | |
| `privacy_consent` | sì | vale `yes` |
| `website` | — | campo trappola anti-spam: deve arrivare **vuoto**, altrimenti scartare l'invio |

Attenzione: i campi file lasciati vuoti arrivano comunque, come file con nome
vuoto e 0 byte. Vanno ignorati.

## 3. Risposta attesa dal modulo

Successo (HTTP 200):

```json
{ "ok": true, "instructions": "Testo delle istruzioni.\n\nSecondo paragrafo." }
```

`instructions` è **testo semplice**: il sito lo mostra così com'è. Una riga
vuota separa i paragrafi e un a capo singolo viene mantenuto. Il sito non
interpreta HTML, quindi non c'è rischio di codice iniettato.

Errore (qualunque HTTP diverso da 200, oppure `ok: false`):

```json
{ "ok": false, "error": "breve descrizione" }
```

In caso di errore il sito mostra all'ospite "riprova o scrivici su WhatsApp".

## 4. Cosa deve fare il gestionale a ogni invio

1. **Controlli**: campi obbligatori, date coerenti, numero di schede ospiti
   uguale a `guests_count`, file solo immagini/PDF entro 10 MB.
2. **Verifica della prenotazione**: controllare che esista una prenotazione per
   la data di arrivo indicata (e, se il gestionale li ha, numero di
   prenotazione o cognome). Se non corrisponde, salvare comunque i dati ma
   **non** mostrare il codice della porta.
3. **Salvataggio**: dati degli ospiti nel database del gestionale; foto dei
   documenti in una cartella **non raggiungibile dal web**.
4. **Email al B&B** con tutti i dati, pronti per Alloggiati Web.
5. **Email all'ospite** nella sua lingua (`lang`) con le stesse istruzioni
   mostrate a schermo.
6. **Risposta** al modulo con le istruzioni (punto 3).

## 5. Istruzioni e codice della porta

- Il codice è unico e cambia raramente: va tenuto in un'impostazione del
  gestionale, modificabile dal pannello `/admin`. Mai scritto nel sito o
  nel repository del sito, che sono pubblici.
- Testo delle istruzioni in 4 lingue, con segnaposto tipo `{first_name}`,
  `{arrival}`, `{door_code}`, modificabile dal pannello.

### Attenzione: regole sull'identificazione degli ospiti

A novembre 2025 il Consiglio di Stato (sentenza 9101/2025) ha ribaltato la
sentenza del TAR Lazio e ha ripristinato l'obbligo di identificare gli ospiti
di persona ("de visu"). Mandare il codice in automatico a chi compila il
modulo, senza vedere l'ospite, rischia di non essere in regola. Le fonti
non sono d'accordo se basti un riconoscimento a distanza (videochiamata o
videocitofono): va verificato con un consulente o con la Questura.

Per questo il gestionale dovrebbe avere un'impostazione per scegliere quando
mostrare il codice:

- **immediato**: il codice compare subito dopo il modulo (come oggi con
  Jotform);
- **dopo conferma** (consigliato): subito l'ospite riceve le istruzioni per
  arrivare, senza codice. Il codice parte via email/WhatsApp dopo che il B&B
  ha verificato l'identità, di persona o in videochiamata, e ha premuto
  "conferma" nel pannello.

## 6. Sicurezza e privacy

- Limite di invii per indirizzo IP (contro abusi e spam) e un campo
  nascosto anti-bot.
- Non scrivere dati personali nei log del server.
- Foto dei documenti cancellate in automatico dopo la registrazione su
  Alloggiati Web (l'informativa sul sito lo promette). I dati degli ospiti
  vanno conservati solo per il tempo previsto dalla legge.
- L'informativa privacy mostrata nel modulo è una bozza: va fatta
  verificare da un consulente.

## 7. Accendere il modulo sul sito

Quando l'indirizzo del punto 1 risponde:

1. in `tools/build_pages.py` mettere `CHECKIN_FORM_LIVE = True`;
2. `python3 tools/build_pages.py`;
3. pubblicare. Tutti i pulsanti "Check-in online" del sito porteranno al
   nuovo modulo invece che a Jotform.
