#!/usr/bin/env python3
"""Genera il sito B&B Merì in quattro lingue (IT, EN, FR, ES).

Tutti i testi stanno nei dizionari qui sotto (T = home, P = parcheggi,
G = guida "cosa vedere", C = check-in), una sezione per lingua.
Per cambiare qualcosa: modifica i testi e rilancia

    python3 tools/build_pages.py

Lo script riscrive:
  - le home (index.html, en/, fr/, es/)
  - la guida ai parcheggi (parcheggi/, en/parking/, fr/stationnement/, es/aparcamiento/)
  - la guida "cosa vedere a Castello" (cosa-vedere-a-castello/, en/..., fr/..., es/...)
  - sitemap.xml (con le foto e la data di ultima modifica di ogni pagina)
  - llms.txt (il riassunto per gli assistenti AI, con gli stessi dati delle pagine)
  - le versioni ottimizzate delle foto (WebP) e la copertina per i social (serve Pillow)
cosi' le quattro lingue, i dati strutturati e llms.txt restano sempre allineati.

Su GitHub lo script parte da solo a ogni modifica (.github/workflows/aggiorna-sito.yml).
"""
import datetime
import hashlib
import os
import json
import posixpath
import re
import struct
from html import escape, unescape
from pathlib import Path
from urllib.parse import quote, quote_plus
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent

SITE = "https://www.meribnb.it/"
PHONE = "352 036 8357"
PHONE_INTL = "+39 352 036 8357"
TEL = "+393520368357"
WHATSAPP = "393520368357"
EMAIL = "meri.bnb.cagliari@gmail.com"
CHECKIN_URL = "https://form.jotform.com/262836960089066"
CIN = "IT092009C2000U6994"   # Codice Identificativo Nazionale della struttura

# Check-in online sul sito. Il modulo invia i dati al gestionale (VPS), che
# li salva, manda le email e risponde con le istruzioni da mostrare.
# Finche' il gestionale non e' pronto resta spento: i pulsanti portano a
# CHECKIN_URL (Jotform). Messo a True, tutti i pulsanti portano al modulo.
# Anteprima senza accenderlo: MERI_PREVIEW=1 python3 tools/build_pages.py
CHECKIN_FORM_LIVE = False
CHECKIN_API = "https://gestionale.meribnb.it/api/checkin"
STREET = "Via Alberto Lamarmora 18"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=Via+Alberto+Lamarmora+18%2C+Cagliari"
# Coordinate del portone, usate nei dati strutturati. Sono una STIMA da
# verificare: su Google Maps tasto destro sul portone -> clic sui numeri
# (es. 39.21830, 9.11640) per copiarli, poi incollali qui.
GEO = (39.2183, 9.1164)

# ---------------------------------------------- motori di ricerca e AI --
# Codici di verifica (facoltativi). Google Search Console -> metodo "Tag HTML":
# copia solo il valore tra le virgolette di content="...". Bing Webmaster
# Tools -> "Meta tag" msvalidate.01, idem. Vuoti = nessun tag nella pagina.
GOOGLE_SITE_VERIFICATION = ""
BING_SITE_VERIFICATION = ""

# Profili ufficiali della struttura su altri siti: scheda Google Maps,
# Booking.com, Airbnb, TripAdvisor, Instagram, Facebook... Dicono a Google e
# agli assistenti AI che sono tutti la stessa struttura. Uno per riga, tra
# virgolette e con la virgola finale, per esempio:
#   SAME_AS = [
#       "https://www.booking.com/hotel/it/nome-della-struttura.html",
#       "https://www.instagram.com/nomeprofilo/",
#   ]
SAME_AS = []

# Chiave IndexNow: serve ad avvisare Bing (che alimenta anche ChatGPT,
# Copilot e DuckDuckGo) e Yandex quando una pagina cambia. Lo script scrive il
# file <chiave>.txt nella cartella principale del sito; l'avviso lo manda
# tools/indexnow.py, lanciato in automatico da GitHub.
INDEXNOW_KEY = "ac72737aca2d53c2b5fee6041e87b117"

# Mese in cui sono state verificate le tariffe dei parcheggi (vedi SOURCES).
# Il controllo mensile automatico avvisa quando hanno piu' di 6 mesi.
PARKING_CHECKED = "2026-10"

# Data di pubblicazione della guida "cosa vedere a Castello" (resta fissa)
GUIDE_PUBLISHED = "2026-11-22"

LANGS = ["it", "en", "fr", "es"]
try:
    TZ = ZoneInfo("Europe/Rome")
except Exception:   # Windows senza il pacchetto tzdata: ora italiana invernale
    TZ = datetime.timezone(datetime.timedelta(hours=1))


# ---------------------------------------------------------------- testi --

T = {
    # ===================================================== ITALIANO =====
    "it": {
        "lang_name": "Italiano",
        "og_locale": "it_IT",
        "region": "Sardegna",
        "title": "B&B Merì — B&B a Castello, nel centro storico di Cagliari",
        "description": "Camera matrimoniale con bagno privato nel quartiere Castello di Cagliari, a 3 minuti dal Bastione di Saint Remy. Wi-Fi e aria condizionata. −10% prenotando per telefono.",
        "og_description": "Camere con bagno privato nel quartiere Castello, centro storico di Cagliari. A pochi passi dal Bastione di Saint Remy.",
        "ids": {"rooms": "stanze", "amenities": "servizi", "location": "posizione",
                "arrival": "come-arrivare", "faq": "faq", "contact": "contatti"},
        "nav": {"rooms": "Le Stanze", "amenities": "Servizi", "location": "Posizione", "parking": "Parcheggi",
                "guide": "Cosa vedere", "arrival": "Come arrivare", "faq": "FAQ", "book": "Prenota"},
        "home_crumb": "B&B Merì",
        "gallery_label": "Foto della Camera Matrimoniale",
        "photo_word": "foto",
        "facts_title": "In breve",
        "facts": [
            ("Dove", "Via Alberto Lamarmora 18, 09124 Cagliari — quartiere Castello, centro storico"),
            ("Camere", "Camera Matrimoniale con bagno privato, fino a 2 ospiti (la Camera con Cucina al momento non è disponibile)"),
            ("Check-in", "dalle 15:00 alle 20:00, anche online prima dell'arrivo"),
            ("Check-out", "entro le 10:30"),
            ("Colazione", "non inclusa"),
            ("Servizi", "Wi-Fi gratuito, aria condizionata e riscaldamento, acqua potabile dal rubinetto, transfer su richiesta"),
            ("Animali", "non ammessi"),
            ("Prenotazioni", f"dirette per telefono o WhatsApp al {PHONE_INTL} o via email; prenotando per telefono, 10% di sconto rispetto a Booking"),
            ("Codice CIN", CIN),
        ],
        "guide_link": "Cosa vedere a piedi da qui: il nostro itinerario di Castello →",
        "nav_label": "Navigazione principale",
        "menu_open": "Apri menu",
        "hero_eyebrow": "Bed &amp; Breakfast · Castello, Cagliari",
        "h1": "Dormi nel cuore antico<br>di Cagliari",
        "checkin_title": "Check-in online",
        "checkin_sub": "Hai già prenotato? Registra qui i tuoi dati prima dell'arrivo",
        "hero_sub": "Camere con bagno privato in Via Alberto Lamarmora 18, tra i vicoli del quartiere Castello. Il Bastione di Saint Remy, la Cattedrale e i migliori ristoranti della città a pochi passi dalla porta.",
        "cta_primary": "Contattaci per prenotare",
        "cta_secondary": "Scopri le stanze",
        "highlights_label": "Punti di forza",
        "badges": ["Bagno privato in ogni camera", "Acqua potabile dal rubinetto",
                   "Transfer su richiesta", "Wi-Fi e aria condizionata"],
        "intro_eyebrow": "Benvenuti",
        "intro_h2": "Una casa nel quartiere più bello della città",
        "intro_p": [
            "Merì è un piccolo bed &amp; breakfast a conduzione familiare nel cuore di <strong>Castello</strong>, il quartiere fortificato che domina Cagliari dall'alto. Poche stanze, ognuna con <strong>bagno privato</strong>, e tanta cura: vi accogliamo personalmente, vi consigliamo dove mangiare e cosa vedere, e vi lasciamo la libertà di sentirvi a casa.",
            "Uscendo dal portone siete già nella Cagliari più autentica: botteghe artigiane, terrazze panoramiche sul golfo, caffè storici e la spiaggia del Poetto a un quarto d'ora.",
        ],
        "rooms_eyebrow": "Le Stanze",
        "rooms_h2": "Due camere, ognuna con il suo carattere",
        "room1": {
            "name": "Camera Matrimoniale",
            "alt": "Camera Matrimoniale con bagno privato nel quartiere Castello",
            "tagline": "Matrimoniale · max 2 ospiti · bagno privato",
            "text": "Nel cuore di Castello, luminosa e accogliente. Letto matrimoniale e bagno privato con doccia: tutto il necessario per un soggiorno comodo.",
            "amenities": ["Bagno privato con doccia", "Aria condizionata e riscaldamento",
                          "Wi-Fi veloce gratuito", "Biancheria e set di cortesia"],
            "button": "Prenota",
        },
        "room2": {
            "name": "Camera con Cucina",
            "alt": "Camera con cucina non disponibile: il gatto di casa dorme davanti alla porta",
            "badge": "Non disponibile",
            "tagline": "Matrimoniale · angolo cottura · bagno privato",
            "text": "Camera con angolo cottura attrezzato, comoda per soggiorni più lunghi e per chi ama l'indipendenza.",
            "amenities": ["Bagno privato con doccia", "Angolo cottura attrezzato",
                          "Aria condizionata e riscaldamento", "Wi-Fi veloce gratuito"],
            "unavailable": "Attualmente non disponibile — torniamo presto!",
        },
        "amen_eyebrow": "Servizi",
        "amen_h2": "Tutto quello che serve, niente di superfluo",
        "amenities": [
            ("🛁", "Bagno privato", "In ogni camera, con doccia, asciugacapelli e set di cortesia."),
            ("💧", "Acqua pura dal rubinetto", "Fresca e potabile, dal rubinetto al bicchiere: bevi bene, senza bottiglie di plastica."),
            ("🚐", "Transfer su richiesta", "Da e per la struttura, da concordare in anticipo."),
            ("📶", "Wi-Fi gratuito", "Connessione veloce in tutta la struttura."),
            ("❄️", "Aria condizionata", "Climatizzazione autonoma in ogni camera."),
            ("🗝️", "Check-in flessibile", "Accoglienza personale e check-in online."),
        ],
        "loc_eyebrow": "Posizione",
        "loc_h2": "Via Alberto Lamarmora 18, quartiere Castello",
        "loc_p": "Siamo nel cuore del centro storico di Cagliari, su una delle vie più caratteristiche di Castello. Tutto il meglio della città si raggiunge a piedi.",
        "distances": [("Bastione di Saint Remy", "3 min a piedi"),
                      ("Cattedrale di Santa Maria", "2 min a piedi"),
                      ("Torre dell'Elefante", "4 min a piedi"),
                      ("Via Roma e porto", "10 min a piedi"),
                      ("Spiaggia del Poetto", "15 min in bus o auto"),
                      ("Aeroporto di Cagliari-Elmas", "15 min in auto")],
        "maps_button": "Apri in Google Maps",
        "arr_eyebrow": "Come arrivare",
        "arr_h2": "Aeroporto, treno e auto",
        "arr_intro": "Castello è una <strong>zona a traffico limitato (ZTL)</strong>: in auto non si arriva fino al portone. Ecco i modi più comodi per raggiungerci.",
        "arrival": [
            ("✈️", "Dall'aeroporto in treno", "Dalla stazione Elmas Aeroporto, a pochi passi dal terminal, il treno vi porta in circa 10 minuti alla stazione di Cagliari in <strong>Piazza Matteotti</strong> (biglietto circa €1,30, una corsa ogni 20 minuti circa)."),
            ("🚌", "Poi il bus 7", "Davanti alla stazione prendete il bus CTM <strong>linea 7</strong>: sale in Castello e ferma proprio davanti a casa."),
            ("🅿️", "Arrivi in auto? Ecco dove parcheggiare", "Castello è ZTL: lasciate l'auto fuori dal quartiere. Il parcheggio gratuito più vicino è in <strong>Viale Buoncammino</strong>; a pagamento ci sono le aree e il multipiano di <strong>Viale Regina Elena</strong>, collegati a Castello da ascensori pubblici. <a class=\"text-link\" href=\"{parking}\">Leggi la guida completa ai parcheggi, con mappe e tariffe →</a>"),
            ("🚐", "Transfer su richiesta", "Preferite essere accompagnati? Organizziamo il transfer da e per la struttura: chiedetecelo in anticipo."),
        ],
        "arr_note": "Orari e tariffe sono indicativi: verificateli prima del viaggio.",
        "faq_eyebrow": "Domande frequenti",
        "faq_h2": "Buono a sapersi",
        "faq": [
            ("Come arrivo dall'aeroporto?", "In treno da Elmas Aeroporto alla stazione di Cagliari in Piazza Matteotti (circa 10 minuti), poi bus CTM linea 7, che ferma proprio davanti a casa."),
            ("Castello è ZTL? Dove parcheggio?", "Sì, Castello è zona a traffico limitato: non entrate in auto nel quartiere. Il parcheggio gratuito più vicino è in Viale Buoncammino; a pagamento ci sono le aree e il multipiano di Viale Regina Elena, collegati a Castello da ascensori pubblici. Tutti i dettagli, con mappe e tariffe, sono nella nostra guida ai parcheggi: https://www.meribnb.it/parcheggi/"),
            ("A che ora sono il check-in e il check-out?", "Il check-in è dalle 15:00 alle 20:00; per orari diversi basta avvisarci. Il check-out è entro le 10:30. Potete fare il check-in online in anticipo dal pulsante in cima alla pagina."),
            ("La colazione è inclusa?", "No, la colazione non è inclusa nel prezzo. Nei dintorni ci sono bar e caffè dove fare colazione, a pochi minuti a piedi."),
            ("Come si prenota? C'è uno sconto prenotando direttamente?", f"Sì: prenotando per telefono al {PHONE} avete il 10% di sconto rispetto alla tariffa di Booking. Potete scriverci anche su WhatsApp allo stesso numero o via email a {EMAIL}: rispondiamo in giornata."),
            ("Le camere hanno il bagno privato?", "Sì, ogni camera ha il bagno privato con doccia, asciugacapelli e set di cortesia."),
            ("Quante persone può ospitare la camera?", "La Camera Matrimoniale ospita fino a 2 persone, con un letto matrimoniale. La Camera con Cucina al momento non è disponibile."),
            ("Ci sono Wi-Fi e aria condizionata?", "Sì: il Wi-Fi è gratuito e veloce in tutta la struttura, e ogni camera ha aria condizionata e riscaldamento autonomi."),
            ("Il transfer è disponibile?", "Sì, su richiesta: scriveteci in anticipo per organizzarlo."),
            ("L'acqua del rubinetto è potabile?", "Sì, l'acqua del rubinetto è potabile: fresca e buona da bere."),
            ("Cosa c'è da vedere vicino al B&B?", "Siete nel cuore di Castello: la Cattedrale è a 2 minuti a piedi, il Bastione di Saint Remy a 3 e la Torre dell'Elefante a 4. Trovate l'itinerario completo a piedi, con tempi e mappe, nella nostra guida: https://www.meribnb.it/cosa-vedere-a-castello/"),
            ("Quanto dista la spiaggia?", "La spiaggia del Poetto, 8 km di sabbia bianca, dista circa 6 km: 15 minuti in bus o 10 in auto."),
            ("Sono ammessi animali?", "Al momento non possiamo accogliere animali domestici."),
        ],
        "contact_eyebrow": "Prenota",
        "contact_h2": "Contattaci direttamente per prenotare",
        "discount": "−10% rispetto a Booking",
        "contact_p": f"Per avere uno <strong>sconto del 10% rispetto alla tariffa di Booking</strong>, prenota chiamandoci al <strong>{PHONE}</strong>. Puoi anche scriverci su WhatsApp allo stesso numero oppure via email: rispondiamo in giornata.",
        "phone_label": PHONE,
        "whatsapp_text": "Salve, vorrei prenotare al B&B Merì",
        "mail_subject": "Prenotazione B&B Merì",
        "address_line": "Via Alberto Lamarmora 18, 09124 Cagliari (CA) — Sardegna, Italia",
        "footer_label": "Link del footer",
        "rights": "Tutti i diritti riservati",
        "ld_description": "Bed & Breakfast nel quartiere Castello, centro storico di Cagliari: camere con bagno privato, Wi-Fi gratuito, aria condizionata, acqua potabile dal rubinetto e transfer su richiesta.",
        "ld_amenities": ["Wi-Fi gratuito", "Aria condizionata", "Bagno privato in camera",
                         "Acqua potabile dal rubinetto", "Transfer su richiesta",
                         "Posizione in centro storico"],
        "ld_rooms": [
            ("Camera Matrimoniale", "Camera matrimoniale con bagno privato e aria condizionata, nel quartiere Castello.", ["Bagno privato", "Aria condizionata"]),
            ("Camera con Cucina", "Camera matrimoniale con angolo cottura e bagno privato, nel quartiere Castello. Attualmente non disponibile.", ["Bagno privato", "Angolo cottura"]),
        ],
        "ld_bed": "Letto matrimoniale",
    },

    # ====================================================== ENGLISH =====
    "en": {
        "lang_name": "English",
        "og_locale": "en_GB",
        "region": "Sardinia",
        "title": "B&B Merì — B&B in Castello, Cagliari's historic centre",
        "description": "Double room with private bathroom in Cagliari's Castello quarter, a 3-minute walk from the Bastione di Saint Remy. Free Wi-Fi, A/C. 10% off when you book by phone.",
        "og_description": "Rooms with private bathroom in the Castello district, Cagliari's historic centre. Steps from the Bastione di Saint Remy.",
        "ids": {"rooms": "rooms", "amenities": "amenities", "location": "location",
                "arrival": "getting-here", "faq": "faq", "contact": "contact"},
        "nav": {"rooms": "Rooms", "amenities": "Amenities", "location": "Location", "parking": "Parking",
                "guide": "Things to see", "arrival": "Getting here", "faq": "FAQ", "book": "Book"},
        "home_crumb": "B&B Merì",
        "gallery_label": "Photos of the Double Room",
        "photo_word": "photo",
        "facts_title": "At a glance",
        "facts": [
            ("Where", "Via Alberto Lamarmora 18, 09124 Cagliari — Castello district, historic centre"),
            ("Rooms", "Double Room with private bathroom, up to 2 guests (the Room with Kitchenette is currently unavailable)"),
            ("Check-in", "3:00 PM to 8:00 PM, also online before you arrive"),
            ("Check-out", "by 10:30 AM"),
            ("Breakfast", "not included"),
            ("Amenities", "free Wi-Fi, air conditioning and heating, drinkable tap water, transfer on request"),
            ("Pets", "not allowed"),
            ("Bookings", f"direct by phone or WhatsApp on {PHONE_INTL} or by email; book by phone for 10% off the Booking.com rate"),
            ("CIN code", CIN),
        ],
        "guide_link": "Things to see on foot from here: our Castello walking tour →",
        "nav_label": "Main navigation",
        "menu_open": "Open menu",
        "hero_eyebrow": "Bed &amp; Breakfast · Castello, Cagliari",
        "h1": "Sleep in the ancient heart<br>of Cagliari",
        "checkin_title": "Online check-in",
        "checkin_sub": "Already booked? Register your details here before you arrive",
        "hero_sub": "Rooms with private bathroom at Via Alberto Lamarmora 18, among the lanes of the Castello district. The Bastione di Saint Remy, the Cathedral and the city's best restaurants just steps from the door.",
        "cta_primary": "Contact us to book",
        "cta_secondary": "See the rooms",
        "highlights_label": "Highlights",
        "badges": ["Private bathroom in every room", "Drinkable tap water",
                   "Transfer on request", "Wi-Fi and air conditioning"],
        "intro_eyebrow": "Welcome",
        "intro_h2": "A home in the city's most beautiful quarter",
        "intro_p": [
            "Merì is a small, family-run bed &amp; breakfast in the heart of <strong>Castello</strong>, the fortified quarter overlooking Cagliari from above. Just a few rooms, each with a <strong>private bathroom</strong>, and a lot of care: we welcome you personally, share our favourite restaurants and sights, and leave you free to feel at home.",
            "Step out of the front door and you're already in the most authentic Cagliari: artisan workshops, panoramic terraces over the gulf, historic cafés — and Poetto beach just fifteen minutes away.",
        ],
        "rooms_eyebrow": "The Rooms",
        "rooms_h2": "Two rooms, each with its own character",
        "room1": {
            "name": "Double Room",
            "alt": "Double Room with private bathroom in the Castello district",
            "tagline": "Double · up to 2 guests · private bathroom",
            "text": "In the heart of Castello, bright and welcoming. Double bed and private bathroom with shower: everything you need for a comfortable stay.",
            "amenities": ["Private bathroom with shower", "Air conditioning and heating",
                          "Fast free Wi-Fi", "Linen and toiletries provided"],
            "button": "Book",
        },
        "room2": {
            "name": "Room with Kitchenette",
            "alt": "Room with kitchenette unavailable: the house cat is napping by the door",
            "badge": "Unavailable",
            "tagline": "Double · kitchenette · private bathroom",
            "text": "A room with a fully equipped kitchenette, handy for longer stays and for those who like their independence.",
            "amenities": ["Private bathroom with shower", "Equipped kitchenette",
                          "Air conditioning and heating", "Fast free Wi-Fi"],
            "unavailable": "Currently unavailable — back soon!",
        },
        "amen_eyebrow": "Amenities",
        "amen_h2": "Everything you need, nothing you don't",
        "amenities": [
            ("🛁", "Private bathroom", "In every room, with shower, hairdryer and toiletries."),
            ("💧", "Pure water on tap", "Fresh and drinkable, straight from the tap to your glass: stay hydrated, plastic-free."),
            ("🚐", "Transfer on request", "To and from the property, arranged in advance."),
            ("📶", "Free Wi-Fi", "Fast connection throughout the property."),
            ("❄️", "Air conditioning", "Independent climate control in every room."),
            ("🗝️", "Flexible check-in", "Personal welcome and online check-in."),
        ],
        "loc_eyebrow": "Location",
        "loc_h2": "Via Alberto Lamarmora 18, Castello district",
        "loc_p": "We are in the heart of Cagliari's historic centre, on one of the most characteristic streets of Castello. The best of the city is within walking distance.",
        "distances": [("Bastione di Saint Remy", "3 min walk"),
                      ("Cathedral of Santa Maria", "2 min walk"),
                      ("Elephant Tower", "4 min walk"),
                      ("Via Roma and the port", "10 min walk"),
                      ("Poetto beach", "15 min by bus or car"),
                      ("Cagliari-Elmas Airport", "15 min by car")],
        "maps_button": "Open in Google Maps",
        "arr_eyebrow": "Getting here",
        "arr_h2": "Airport, train and car",
        "arr_intro": "Castello is a <strong>limited-traffic zone (ZTL)</strong>: you can't drive up to the front door. Here are the easiest ways to reach us.",
        "arrival": [
            ("✈️", "From the airport by train", "From Elmas Aeroporto station, a short walk from the terminal, the train takes you in about 10 minutes to Cagliari station in <strong>Piazza Matteotti</strong> (ticket about €1.30, a train roughly every 20 minutes)."),
            ("🚌", "Then bus no. 7", "In front of the station, take CTM bus <strong>line 7</strong>: it climbs up to Castello and stops right outside our door."),
            ("🅿️", "Coming by car? Here's where to park", "Castello is a ZTL: leave the car outside the quarter. The nearest free parking is on <strong>Viale Buoncammino</strong>; paid options are the street areas and the multi-storey car park on <strong>Viale Regina Elena</strong>, linked to Castello by public lifts. <a class=\"text-link\" href=\"{parking}\">Read our full parking guide, with maps and prices →</a>"),
            ("🚐", "Transfer on request", "Rather be picked up? We can arrange a transfer to and from the property: just ask us in advance."),
        ],
        "arr_note": "Times and prices are indicative: please check them before you travel.",
        "faq_eyebrow": "Frequently asked questions",
        "faq_h2": "Good to know",
        "faq": [
            ("How do I get there from the airport?", "By train from Elmas Aeroporto to Cagliari station in Piazza Matteotti (about 10 minutes), then CTM bus line 7, which stops right outside our door."),
            ("Is Castello a ZTL? Where can I park?", "Yes, Castello is a limited-traffic zone: please don't drive into the quarter. The nearest free parking is on Viale Buoncammino; paid options are the street areas and the multi-storey car park on Viale Regina Elena, linked to Castello by public lifts. All the details, with maps and prices, are in our parking guide: https://www.meribnb.it/en/parking/"),
            ("What are the check-in and check-out times?", "Check-in is from 3:00 PM to 8:00 PM; just let us know if you need a different time. Check-out is by 10:30 AM. You can complete online check-in in advance using the button at the top of the page."),
            ("Is breakfast included?", "No, breakfast is not included in the price. There are bars and cafés for breakfast a few minutes' walk away."),
            ("How do I book? Is there a discount for booking direct?", f"Yes: book by phone on {PHONE_INTL} and you get 10% off the Booking.com rate. You can also message us on WhatsApp at the same number or email us at {EMAIL}: we reply within the day."),
            ("Do the rooms have a private bathroom?", "Yes, every room has a private bathroom with shower, hairdryer and toiletries."),
            ("How many guests can the room sleep?", "The Double Room sleeps up to 2 guests in a double bed. The Room with Kitchenette is currently unavailable."),
            ("Is there Wi-Fi and air conditioning?", "Yes: free, fast Wi-Fi throughout the property, and every room has its own air conditioning and heating."),
            ("Is a transfer available?", "Yes, on request: write to us in advance to arrange it."),
            ("Is the tap water drinkable?", "Yes, the tap water is drinkable: fresh and good to drink."),
            ("What is there to see near the B&B?", "You're in the heart of Castello: the Cathedral is a 2-minute walk away, the Bastione di Saint Remy 3 minutes and the Elephant Tower 4. Our guide has the full walking tour, with times and maps: https://www.meribnb.it/en/things-to-see-in-castello/"),
            ("How far is the beach?", "Poetto beach, 8 km of white sand, is about 6 km away: 15 minutes by bus or 10 by car."),
            ("Are pets allowed?", "Unfortunately we cannot accommodate pets at the moment."),
        ],
        "contact_eyebrow": "Book",
        "contact_h2": "Contact us directly to book",
        "discount": "10% off the Booking.com rate",
        "contact_p": f"For a <strong>10% discount on the Booking.com rate</strong>, book by calling us on <strong>{PHONE_INTL}</strong>. You can also message us on WhatsApp at the same number or send us an email: we reply within the day.",
        "phone_label": PHONE_INTL,
        "whatsapp_text": "Hello, I would like to book at B&B Merì",
        "mail_subject": "Booking — B&B Merì",
        "address_line": "Via Alberto Lamarmora 18, 09124 Cagliari (CA) — Sardinia, Italy",
        "footer_label": "Footer links",
        "rights": "All rights reserved",
        "ld_description": "Bed & Breakfast in the Castello district, the historic centre of Cagliari, Sardinia: rooms with private bathroom, free Wi-Fi, air conditioning, drinkable tap water and transfer on request.",
        "ld_amenities": ["Free Wi-Fi", "Air conditioning", "Private en-suite bathroom",
                         "Drinkable tap water", "Transfer on request",
                         "Historic centre location"],
        "ld_rooms": [
            ("Double Room", "Double room with private bathroom and air conditioning, in the Castello district.", ["Private bathroom", "Air conditioning"]),
            ("Room with Kitchenette", "Double room with kitchenette and private bathroom, in the Castello district. Currently unavailable.", ["Private bathroom", "Kitchenette"]),
        ],
        "ld_bed": "Double bed",
    },

    # ===================================================== FRANÇAIS =====
    "fr": {
        "lang_name": "Français",
        "og_locale": "fr_FR",
        "region": "Sardaigne",
        "title": "B&B Merì — Chambre d'hôtes à Castello, Cagliari",
        "description": "Chambre double avec salle de bains privative dans le quartier de Castello à Cagliari, à 3 min du Bastion de Saint-Remy. Wi-Fi, clim. −10 % en réservant par téléphone.",
        "og_description": "Chambres avec salle de bains privative dans le quartier de Castello, centre historique de Cagliari. À deux pas du Bastion de Saint-Remy.",
        "ids": {"rooms": "chambres", "amenities": "services", "location": "emplacement",
                "arrival": "acces", "faq": "faq", "contact": "contact"},
        "nav": {"rooms": "Chambres", "amenities": "Services", "location": "Emplacement", "parking": "Parkings",
                "guide": "À voir", "arrival": "Accès", "faq": "FAQ", "book": "Réserver"},
        "home_crumb": "B&B Merì",
        "gallery_label": "Photos de la chambre double",
        "photo_word": "photo",
        "facts_title": "En bref",
        "facts": [
            ("Adresse", "Via Alberto Lamarmora 18, 09124 Cagliari — quartier de Castello, centre historique"),
            ("Chambres", "Chambre double avec salle de bains privative, jusqu'à 2 personnes (la chambre avec kitchenette est actuellement indisponible)"),
            ("Arrivée", "de 15 h à 20 h, check-in possible en ligne avant l'arrivée"),
            ("Départ", "avant 10 h 30"),
            ("Petit-déjeuner", "non inclus"),
            ("Services", "Wi-Fi gratuit, climatisation et chauffage, eau du robinet potable, transfert sur demande"),
            ("Animaux", "non acceptés"),
            ("Réservations", f"en direct par téléphone ou WhatsApp au {PHONE_INTL} ou par e-mail ; en réservant par téléphone, −10 % par rapport au tarif Booking"),
            ("Code CIN", CIN),
        ],
        "guide_link": "À voir à pied depuis ici : notre itinéraire dans Castello →",
        "nav_label": "Navigation principale",
        "menu_open": "Ouvrir le menu",
        "hero_eyebrow": "Chambres d'hôtes · Castello, Cagliari",
        "h1": "Dormez au cœur antique<br>de Cagliari",
        "checkin_title": "Check-in en ligne",
        "checkin_sub": "Vous avez déjà réservé ? Enregistrez ici vos informations avant votre arrivée",
        "hero_sub": "Des chambres avec salle de bains privative Via Alberto Lamarmora 18, dans les ruelles du quartier de Castello. Le Bastion de Saint-Remy, la cathédrale et les meilleurs restaurants de la ville à deux pas de la porte.",
        "cta_primary": "Contactez-nous pour réserver",
        "cta_secondary": "Découvrir les chambres",
        "highlights_label": "Points forts",
        "badges": ["Salle de bains privative dans chaque chambre", "Eau du robinet potable",
                   "Transfert sur demande", "Wi-Fi et climatisation"],
        "intro_eyebrow": "Bienvenue",
        "intro_h2": "Une maison dans le plus beau quartier de la ville",
        "intro_p": [
            "Merì est une petite maison d'hôtes familiale au cœur de <strong>Castello</strong>, le quartier fortifié qui domine Cagliari. Peu de chambres, chacune avec <strong>salle de bains privative</strong>, et beaucoup d'attention : nous vous accueillons personnellement, vous conseillons où manger et quoi visiter, et vous laissons la liberté de vous sentir chez vous.",
            "En passant la porte, vous êtes déjà dans la Cagliari la plus authentique : ateliers d'artisans, terrasses panoramiques sur le golfe, cafés historiques — et la plage du Poetto à un quart d'heure.",
        ],
        "rooms_eyebrow": "Les chambres",
        "rooms_h2": "Deux chambres, chacune avec son caractère",
        "room1": {
            "name": "Chambre double",
            "alt": "Chambre double avec salle de bains privative dans le quartier de Castello",
            "tagline": "Double · 2 personnes max · salle de bains privative",
            "text": "Au cœur de Castello, lumineuse et accueillante. Lit double et salle de bains privative avec douche : tout le nécessaire pour un séjour confortable.",
            "amenities": ["Salle de bains privative avec douche", "Climatisation et chauffage",
                          "Wi-Fi rapide gratuit", "Linge et produits d'accueil fournis"],
            "button": "Réserver",
        },
        "room2": {
            "name": "Chambre avec kitchenette",
            "alt": "Chambre avec kitchenette indisponible : le chat de la maison dort devant la porte",
            "badge": "Indisponible",
            "tagline": "Double · kitchenette · salle de bains privative",
            "text": "Une chambre avec kitchenette équipée, pratique pour les longs séjours et pour ceux qui aiment leur indépendance.",
            "amenities": ["Salle de bains privative avec douche", "Kitchenette équipée",
                          "Climatisation et chauffage", "Wi-Fi rapide gratuit"],
            "unavailable": "Actuellement indisponible — à bientôt !",
        },
        "amen_eyebrow": "Services",
        "amen_h2": "Tout le nécessaire, rien de superflu",
        "amenities": [
            ("🛁", "Salle de bains privative", "Dans chaque chambre, avec douche, sèche-cheveux et produits d'accueil."),
            ("💧", "Eau pure au robinet", "Fraîche et potable, du robinet à votre verre : hydratez-vous, sans plastique."),
            ("🚐", "Transfert sur demande", "Depuis et vers la maison, à organiser à l'avance."),
            ("📶", "Wi-Fi gratuit", "Connexion rapide dans toute la maison."),
            ("❄️", "Climatisation", "Climatisation individuelle dans chaque chambre."),
            ("🗝️", "Check-in flexible", "Accueil personnalisé et check-in en ligne."),
        ],
        "loc_eyebrow": "Emplacement",
        "loc_h2": "Via Alberto Lamarmora 18, quartier de Castello",
        "loc_p": "Nous sommes au cœur du centre historique de Cagliari, dans l'une des rues les plus caractéristiques de Castello. Le meilleur de la ville se découvre à pied.",
        "distances": [("Bastion de Saint-Remy", "3 min à pied"),
                      ("Cathédrale Sainte-Marie", "2 min à pied"),
                      ("Tour de l'Éléphant", "4 min à pied"),
                      ("Via Roma et le port", "10 min à pied"),
                      ("Plage du Poetto", "15 min en bus ou en voiture"),
                      ("Aéroport de Cagliari-Elmas", "15 min en voiture")],
        "maps_button": "Ouvrir dans Google Maps",
        "arr_eyebrow": "Accès",
        "arr_h2": "Aéroport, train et voiture",
        "arr_intro": "Castello est une <strong>zone à trafic limité (ZTL)</strong> : impossible d'arriver en voiture jusqu'à la porte. Voici les moyens les plus simples de nous rejoindre.",
        "arrival": [
            ("✈️", "Depuis l'aéroport en train", "Depuis la gare Elmas Aeroporto, à quelques pas du terminal, le train vous amène en 10 minutes environ à la gare de Cagliari, <strong>Piazza Matteotti</strong> (billet d'environ 1,30 €, un train toutes les 20 minutes environ)."),
            ("🚌", "Puis le bus n° 7", "Devant la gare, prenez le bus CTM <strong>ligne 7</strong> : il monte à Castello et s'arrête juste devant chez nous."),
            ("🅿️", "Vous venez en voiture ? Où se garer", "Castello est en ZTL : laissez la voiture hors du quartier. Le parking gratuit le plus proche se trouve sur le <strong>Viale Buoncammino</strong> ; côté payant, il y a les zones et le parking à étages du <strong>Viale Regina Elena</strong>, reliés à Castello par des ascenseurs publics. <a class=\"text-link\" href=\"{parking}\">Lire notre guide complet du stationnement, avec cartes et tarifs →</a>"),
            ("🚐", "Transfert sur demande", "Vous préférez être accompagnés ? Nous organisons le transfert depuis et vers la maison : demandez-le-nous à l'avance."),
        ],
        "arr_note": "Horaires et tarifs sont indicatifs : vérifiez-les avant votre voyage.",
        "faq_eyebrow": "Questions fréquentes",
        "faq_h2": "Bon à savoir",
        "faq": [
            ("Comment venir depuis l'aéroport ?", "En train d'Elmas Aeroporto à la gare de Cagliari, Piazza Matteotti (10 minutes environ), puis bus CTM ligne 7, qui s'arrête juste devant chez nous."),
            ("Castello est-il en ZTL ? Où se garer ?", "Oui, Castello est une zone à trafic limité : n'entrez pas en voiture dans le quartier. Le parking gratuit le plus proche se trouve sur le Viale Buoncammino ; côté payant, il y a les zones et le parking à étages du Viale Regina Elena, reliés à Castello par des ascenseurs publics. Tous les détails, avec cartes et tarifs, sont dans notre guide du stationnement : https://www.meribnb.it/fr/stationnement/"),
            ("Quels sont les horaires d'arrivée et de départ ?", "L'arrivée se fait de 15 h à 20 h ; pour un autre horaire, prévenez-nous. Le départ se fait avant 10 h 30. Vous pouvez faire le check-in en ligne à l'avance grâce au bouton en haut de la page."),
            ("Le petit-déjeuner est-il inclus ?", "Non, le petit-déjeuner n'est pas inclus dans le prix. Il y a des bars et des cafés pour le petit-déjeuner à quelques minutes à pied."),
            ("Comment réserver ? Y a-t-il une remise en réservant en direct ?", f"Oui : en réservant par téléphone au {PHONE_INTL}, vous bénéficiez de 10 % de remise par rapport au tarif Booking. Vous pouvez aussi nous écrire sur WhatsApp au même numéro ou par e-mail à {EMAIL} : nous répondons dans la journée."),
            ("Les chambres ont-elles une salle de bains privative ?", "Oui, chaque chambre dispose d'une salle de bains privative avec douche, sèche-cheveux et produits d'accueil."),
            ("Combien de personnes peut accueillir la chambre ?", "La chambre double accueille jusqu'à 2 personnes, avec un lit double. La chambre avec kitchenette est actuellement indisponible."),
            ("Y a-t-il le Wi-Fi et la climatisation ?", "Oui : Wi-Fi gratuit et rapide dans toute la maison, et chaque chambre a sa climatisation et son chauffage individuels."),
            ("Un transfert est-il possible ?", "Oui, sur demande : écrivez-nous à l'avance pour l'organiser."),
            ("L'eau du robinet est-elle potable ?", "Oui, l'eau du robinet est potable : fraîche et bonne à boire."),
            ("Que voir près du B&B ?", "Vous êtes au cœur de Castello : la cathédrale est à 2 minutes à pied, le Bastion de Saint-Remy à 3 et la Tour de l'Éléphant à 4. Notre guide propose l'itinéraire complet à pied, avec temps de marche et cartes : https://www.meribnb.it/fr/que-voir-a-castello/"),
            ("À quelle distance est la plage ?", "La plage du Poetto, 8 km de sable blanc, est à environ 6 km : 15 minutes en bus ou 10 en voiture."),
            ("Les animaux sont-ils acceptés ?", "Pour le moment, nous ne pouvons malheureusement pas accueillir d'animaux."),
        ],
        "contact_eyebrow": "Réserver",
        "contact_h2": "Contactez-nous directement pour réserver",
        "discount": "−10 % par rapport à Booking",
        "contact_p": f"Pour bénéficier d'une <strong>remise de 10 % par rapport au tarif Booking</strong>, réservez en nous appelant au <strong>{PHONE_INTL}</strong>. Vous pouvez aussi nous écrire sur WhatsApp au même numéro ou par e-mail : nous répondons dans la journée.",
        "phone_label": PHONE_INTL,
        "whatsapp_text": "Bonjour, je souhaite réserver au B&B Merì",
        "mail_subject": "Réservation — B&B Merì",
        "address_line": "Via Alberto Lamarmora 18, 09124 Cagliari (CA) — Sardaigne, Italie",
        "footer_label": "Liens du pied de page",
        "rights": "Tous droits réservés",
        "ld_description": "Chambres d'hôtes dans le quartier de Castello, centre historique de Cagliari (Sardaigne) : chambres avec salle de bains privative, Wi-Fi gratuit, climatisation, eau du robinet potable et transfert sur demande.",
        "ld_amenities": ["Wi-Fi gratuit", "Climatisation", "Salle de bains privative",
                         "Eau du robinet potable", "Transfert sur demande", "Centre historique"],
        "ld_rooms": [
            ("Chambre double", "Chambre double avec salle de bains privative et climatisation, dans le quartier de Castello.", ["Salle de bains privative", "Climatisation"]),
            ("Chambre avec kitchenette", "Chambre double avec kitchenette et salle de bains privative, dans le quartier de Castello. Actuellement indisponible.", ["Salle de bains privative", "Kitchenette"]),
        ],
        "ld_bed": "Lit double",
    },

    # ====================================================== ESPAÑOL =====
    "es": {
        "lang_name": "Español",
        "og_locale": "es_ES",
        "region": "Cerdeña",
        "title": "B&B Merì — B&B en Castello, centro histórico de Cagliari",
        "description": "Habitación doble con baño privado en el barrio de Castello de Cagliari, a 3 min del Bastión de Saint Remy. Wi-Fi, aire acondicionado. −10 % reservando por teléfono.",
        "og_description": "Habitaciones con baño privado en el barrio de Castello, centro histórico de Cagliari. A pocos pasos del Bastión de Saint Remy.",
        "ids": {"rooms": "habitaciones", "amenities": "servicios", "location": "ubicacion",
                "arrival": "como-llegar", "faq": "faq", "contact": "contacto"},
        "nav": {"rooms": "Habitaciones", "amenities": "Servicios", "location": "Ubicación", "parking": "Aparcar",
                "guide": "Qué ver", "arrival": "Cómo llegar", "faq": "FAQ", "book": "Reservar"},
        "home_crumb": "B&B Merì",
        "gallery_label": "Fotos de la habitación doble",
        "photo_word": "foto",
        "facts_title": "En resumen",
        "facts": [
            ("Dónde", "Via Alberto Lamarmora 18, 09124 Cagliari — barrio de Castello, centro histórico"),
            ("Habitaciones", "Habitación doble con baño privado, hasta 2 huéspedes (la habitación con cocina no está disponible por ahora)"),
            ("Check-in", "de 15:00 a 20:00, también online antes de llegar"),
            ("Check-out", "antes de las 10:30"),
            ("Desayuno", "no incluido"),
            ("Servicios", "Wi-Fi gratis, aire acondicionado y calefacción, agua potable del grifo, traslado bajo petición"),
            ("Animales", "no admitidos"),
            ("Reservas", f"directas por teléfono o WhatsApp al {PHONE_INTL} o por e-mail; reservando por teléfono, 10 % de descuento sobre la tarifa de Booking"),
            ("Código CIN", CIN),
        ],
        "guide_link": "Qué ver a pie desde aquí: nuestro itinerario por Castello →",
        "nav_label": "Navegación principal",
        "menu_open": "Abrir menú",
        "hero_eyebrow": "Bed &amp; Breakfast · Castello, Cagliari",
        "h1": "Duerme en el corazón antiguo<br>de Cagliari",
        "checkin_title": "Check-in online",
        "checkin_sub": "¿Ya has reservado? Registra aquí tus datos antes de llegar",
        "hero_sub": "Habitaciones con baño privado en Via Alberto Lamarmora 18, entre las callejuelas del barrio de Castello. El Bastión de Saint Remy, la catedral y los mejores restaurantes de la ciudad a pocos pasos de la puerta.",
        "cta_primary": "Contáctanos para reservar",
        "cta_secondary": "Ver las habitaciones",
        "highlights_label": "Puntos fuertes",
        "badges": ["Baño privado en cada habitación", "Agua potable del grifo",
                   "Traslado bajo petición", "Wi-Fi y aire acondicionado"],
        "intro_eyebrow": "Bienvenidos",
        "intro_h2": "Una casa en el barrio más bonito de la ciudad",
        "intro_p": [
            "Merì es un pequeño bed &amp; breakfast familiar en el corazón de <strong>Castello</strong>, el barrio amurallado que domina Cagliari desde lo alto. Pocas habitaciones, cada una con <strong>baño privado</strong>, y mucho cariño: te recibimos personalmente, te aconsejamos dónde comer y qué ver, y te dejamos la libertad de sentirte como en casa.",
            "Al salir por la puerta ya estás en la Cagliari más auténtica: talleres artesanos, terrazas panorámicas sobre el golfo, cafés históricos y la playa del Poetto a un cuarto de hora.",
        ],
        "rooms_eyebrow": "Las habitaciones",
        "rooms_h2": "Dos habitaciones, cada una con su carácter",
        "room1": {
            "name": "Habitación doble",
            "alt": "Habitación doble con baño privado en el barrio de Castello",
            "tagline": "Doble · máx. 2 personas · baño privado",
            "text": "En el corazón de Castello, luminosa y acogedora. Cama doble y baño privado con ducha: todo lo necesario para una estancia cómoda.",
            "amenities": ["Baño privado con ducha", "Aire acondicionado y calefacción",
                          "Wi-Fi rápido gratis", "Ropa de cama y artículos de aseo"],
            "button": "Reservar",
        },
        "room2": {
            "name": "Habitación con cocina",
            "alt": "Habitación con cocina no disponible: el gato de la casa duerme delante de la puerta",
            "badge": "No disponible",
            "tagline": "Doble · cocina · baño privado",
            "text": "Habitación con cocina equipada, cómoda para estancias largas y para quien valora su independencia.",
            "amenities": ["Baño privado con ducha", "Cocina equipada",
                          "Aire acondicionado y calefacción", "Wi-Fi rápido gratis"],
            "unavailable": "Actualmente no disponible — ¡volvemos pronto!",
        },
        "amen_eyebrow": "Servicios",
        "amen_h2": "Todo lo que necesitas, nada superfluo",
        "amenities": [
            ("🛁", "Baño privado", "En cada habitación, con ducha, secador de pelo y artículos de aseo."),
            ("💧", "Agua pura del grifo", "Fresca y potable, del grifo al vaso: hidrátate sin plásticos."),
            ("🚐", "Traslado bajo petición", "Desde y hacia el alojamiento, a acordar con antelación."),
            ("📶", "Wi-Fi gratis", "Conexión rápida en todo el alojamiento."),
            ("❄️", "Aire acondicionado", "Climatización independiente en cada habitación."),
            ("🗝️", "Check-in flexible", "Recibimiento personal y check-in online."),
        ],
        "loc_eyebrow": "Ubicación",
        "loc_h2": "Via Alberto Lamarmora 18, barrio de Castello",
        "loc_p": "Estamos en el corazón del centro histórico de Cagliari, en una de las calles más características de Castello. Lo mejor de la ciudad está a un paseo.",
        "distances": [("Bastión de Saint Remy", "3 min a pie"),
                      ("Catedral de Santa María", "2 min a pie"),
                      ("Torre del Elefante", "4 min a pie"),
                      ("Via Roma y el puerto", "10 min a pie"),
                      ("Playa del Poetto", "15 min en autobús o coche"),
                      ("Aeropuerto de Cagliari-Elmas", "15 min en coche")],
        "maps_button": "Abrir en Google Maps",
        "arr_eyebrow": "Cómo llegar",
        "arr_h2": "Aeropuerto, tren y coche",
        "arr_intro": "Castello es una <strong>zona de tráfico limitado (ZTL)</strong>: en coche no se llega hasta la puerta. Estas son las formas más cómodas de llegar.",
        "arrival": [
            ("✈️", "Desde el aeropuerto en tren", "Desde la estación Elmas Aeroporto, a pocos pasos de la terminal, el tren te lleva en unos 10 minutos a la estación de Cagliari en <strong>Piazza Matteotti</strong> (billete de aprox. 1,30 €, un tren cada 20 minutos aprox.)."),
            ("🚌", "Después, el autobús 7", "Delante de la estación, toma el autobús CTM <strong>línea 7</strong>: sube a Castello y para justo delante de casa."),
            ("🅿️", "¿Vienes en coche? Dónde aparcar", "Castello es ZTL: deja el coche fuera del barrio. El aparcamiento gratuito más cercano está en el <strong>Viale Buoncammino</strong>; de pago están las zonas y el aparcamiento de varias plantas del <strong>Viale Regina Elena</strong>, conectados con Castello por ascensores públicos. <a class=\"text-link\" href=\"{parking}\">Lee nuestra guía completa de aparcamiento, con mapas y tarifas →</a>"),
            ("🚐", "Traslado bajo petición", "¿Prefieres que te acompañemos? Organizamos el traslado desde y hacia el alojamiento: pídenoslo con antelación."),
        ],
        "arr_note": "Horarios y precios son orientativos: compruébalos antes del viaje.",
        "faq_eyebrow": "Preguntas frecuentes",
        "faq_h2": "Bueno saberlo",
        "faq": [
            ("¿Cómo llego desde el aeropuerto?", "En tren desde Elmas Aeroporto hasta la estación de Cagliari en Piazza Matteotti (unos 10 minutos) y después el autobús CTM línea 7, que para justo delante de casa."),
            ("¿Castello es ZTL? ¿Dónde aparco?", "Sí, Castello es zona de tráfico limitado: no entres en coche en el barrio. El aparcamiento gratuito más cercano está en el Viale Buoncammino; de pago están las zonas y el aparcamiento de varias plantas del Viale Regina Elena, conectados con Castello por ascensores públicos. Todos los detalles, con mapas y tarifas, están en nuestra guía de aparcamiento: https://www.meribnb.it/es/aparcamiento/"),
            ("¿A qué hora son el check-in y el check-out?", "El check-in es de 15:00 a 20:00; si necesitas otro horario, avísanos. El check-out es antes de las 10:30. Puedes hacer el check-in online con antelación desde el botón de arriba de la página."),
            ("¿El desayuno está incluido?", "No, el desayuno no está incluido en el precio. Cerca hay bares y cafeterías para desayunar, a pocos minutos a pie."),
            ("¿Cómo se reserva? ¿Hay descuento reservando directamente?", f"Sí: reservando por teléfono al {PHONE_INTL} tienes un 10 % de descuento sobre la tarifa de Booking. También puedes escribirnos por WhatsApp al mismo número o por e-mail a {EMAIL}: respondemos en el día."),
            ("¿Las habitaciones tienen baño privado?", "Sí, cada habitación tiene baño privado con ducha, secador de pelo y artículos de aseo."),
            ("¿Cuántas personas caben en la habitación?", "La habitación doble aloja hasta 2 personas, con una cama de matrimonio. La habitación con cocina no está disponible por ahora."),
            ("¿Hay Wi-Fi y aire acondicionado?", "Sí: Wi-Fi gratis y rápido en todo el alojamiento, y cada habitación tiene aire acondicionado y calefacción independientes."),
            ("¿Hay servicio de traslado?", "Sí, bajo petición: escríbenos con antelación para organizarlo."),
            ("¿El agua del grifo es potable?", "Sí, el agua del grifo es potable: fresca y buena para beber."),
            ("¿Qué se puede ver cerca del B&B?", "Estás en el corazón de Castello: la catedral está a 2 minutos a pie, el Bastión de Saint Remy a 3 y la Torre del Elefante a 4. En nuestra guía tienes el itinerario completo a pie, con tiempos y mapas: https://www.meribnb.it/es/que-ver-en-castello/"),
            ("¿A qué distancia está la playa?", "La playa del Poetto, 8 km de arena blanca, está a unos 6 km: 15 minutos en autobús o 10 en coche."),
            ("¿Se admiten animales?", "Por el momento, lamentablemente no podemos alojar animales."),
        ],
        "contact_eyebrow": "Reservar",
        "contact_h2": "Contáctanos directamente para reservar",
        "discount": "−10 % respecto a Booking",
        "contact_p": f"Para obtener un <strong>descuento del 10 % sobre la tarifa de Booking</strong>, reserva llamándonos al <strong>{PHONE_INTL}</strong>. También puedes escribirnos por WhatsApp al mismo número o por e-mail: respondemos en el día.",
        "phone_label": PHONE_INTL,
        "whatsapp_text": "Hola, me gustaría reservar en el B&B Merì",
        "mail_subject": "Reserva — B&B Merì",
        "address_line": "Via Alberto Lamarmora 18, 09124 Cagliari (CA) — Cerdeña, Italia",
        "footer_label": "Enlaces del pie de página",
        "rights": "Todos los derechos reservados",
        "ld_description": "Bed & Breakfast en el barrio de Castello, centro histórico de Cagliari (Cerdeña): habitaciones con baño privado, Wi-Fi gratis, aire acondicionado, agua potable del grifo y traslado bajo petición.",
        "ld_amenities": ["Wi-Fi gratis", "Aire acondicionado", "Baño privado",
                         "Agua potable del grifo", "Traslado bajo petición", "Centro histórico"],
        "ld_rooms": [
            ("Habitación doble", "Habitación doble con baño privado y aire acondicionado, en el barrio de Castello.", ["Baño privado", "Aire acondicionado"]),
            ("Habitación con cocina", "Habitación doble con cocina equipada y baño privado, en el barrio de Castello. No disponible por ahora.", ["Baño privado", "Cocina"]),
        ],
        "ld_bed": "Cama de matrimonio",
    },
}


# ------------------------------------------------- pagina parcheggi --
#
# Dati verificati a ottobre 2026 su fonti pubbliche (vedi SOURCES): tariffe,
# orari e ascensori possono cambiare, per questo la pagina invita sempre a
# controllare i cartelli sul posto.

# Dove si trova la pagina parcheggi in ogni lingua (cartella del sito)
HOME_DIR = {"it": "", "en": "en", "fr": "fr", "es": "es"}
PARK_DIR = {"it": "parcheggi", "en": "en/parking", "fr": "fr/stationnement", "es": "es/aparcamiento"}
GUIDE_DIR = {"it": "cosa-vedere-a-castello", "en": "en/things-to-see-in-castello",
             "fr": "fr/que-voir-a-castello", "es": "es/que-ver-en-castello"}
CHECKIN_DIR = {"it": "checkin", "en": "en/check-in", "fr": "fr/check-in", "es": "es/check-in"}
PAGE_DIRS = {"home": HOME_DIR, "parking": PARK_DIR, "guide": GUIDE_DIR, "checkin": CHECKIN_DIR}

# Destinazione del percorso a piedi su Google Maps
DEST = "Via Alberto Lamarmora 18, 09124 Cagliari"

# Ogni parcheggio/ascensore: scheda in cui compare, ricerca per la mappa,
# punto di partenza del percorso a piedi fino al B&B, via (per i dati strutturati).
SPOTS = {
    "buoncammino": {"tab": "free", "map": "Porta Cristina, Cagliari", "from": "Porta Cristina, Cagliari", "street": "Viale Buon Cammino"},
    "blue_free":   {"tab": "free", "map": None, "from": None, "street": None},
    "re_alta":     {"tab": "paid", "map": "Viale Regina Elena, 09121 Cagliari", "from": "Viale Regina Elena, 09121 Cagliari", "street": "Viale Regina Elena"},
    "re_bassa":    {"tab": "paid", "map": "Viale Regina Elena, 09124 Cagliari", "from": "Viale Regina Elena, 09124 Cagliari", "street": "Viale Regina Elena"},
    "multipiano":  {"tab": "paid", "map": "APCOA Parking Regina Elena, Viale Regina Elena 17, Cagliari", "from": "APCOA Parking Regina Elena, Viale Regina Elena 17, Cagliari", "street": "Viale Regina Elena 17"},
    "blue_paid":   {"tab": "paid", "map": None, "from": None, "street": None},
    "lift_palazzo": {"tab": "lifts", "map": "Terrapieno, Viale Regina Elena 14, Cagliari", "from": "Piazza Palazzo, Cagliari", "street": None},
    "lift_remy":   {"tab": "lifts", "map": "Bastione di Saint Remy, Cagliari", "from": "Bastione di Saint Remy, Cagliari", "street": None},
}
TABS = ["free", "paid", "lifts", "tips"]
FACILITIES = ["buoncammino", "re_alta", "re_bassa", "multipiano"]   # nei dati strutturati

SOURCES = [
    ("APCOA – Parcheggio Regina Elena", "https://www.apcoa.it/sosta-breve/sedi/cagliari/regina-elena"),
    ("APCOA – Area Regina Elena Alta", "https://www.apcoa.it/sosta-breve/sedi/cagliari/area-regina-elena-alta"),
    ("APCOA – Area Regina Elena Bassa 2", "https://www.apcoa.it/parcheggi-in/cagliari/area-regina-elena-bassa-2/"),
    ("Telepass – Strisce blu a Cagliari", "https://www.telepass.com/en/consumer/services/street-parking/cagliari"),
    ("Comune di Cagliari – Ascensori di Castello", "https://www.comune.cagliari.it/portale/page/it/riaperti_al_pubblico_gli_ascensori_di_castello?contentId=NVT176097"),
    ("Museo Archeologico Nazionale – Come raggiungerci", "https://museinazionalicagliari.cultura.gov.it/visita/come-raggiungerci/come-raggiungerci/"),
]

P = {
    # ===================================================== ITALIANO =====
    "it": {
        "title": "Dove parcheggiare a Cagliari vicino a Castello — B&B Merì",
        "description": "Dove parcheggiare vicino a Castello, a Cagliari: gratis in Viale Buoncammino, aree e multipiano in Viale Regina Elena, ascensori pubblici, ZTL. Tariffe e mappe.",
        "og_description": "Parcheggi gratuiti e a pagamento vicino a Castello, ascensori, ZTL e mappe: la guida del B&B Merì.",
        "back": "Torna alla home",
        "eyebrow": "Guida ai parcheggi · Castello, Cagliari",
        "h1": "Dove parcheggiare<br>vicino a Castello",
        "intro": "Castello è una <strong>zona a traffico limitato (ZTL)</strong>: le auto dei visitatori non possono entrare nel quartiere. La buona notizia è che appena fuori dalle mura ci sono parcheggi gratuiti e a pagamento, collegati al B&amp;B da brevi passeggiate e ascensori pubblici. Qui trovi tutto, con mappe e tariffe.",
        "satnav_title": "Prima di partire: nel navigatore imposta il parcheggio, non l'indirizzo del B&amp;B",
        "satnav_text": "Se imposti Via Alberto Lamarmora 18 il navigatore può portarti dentro la ZTL, sorvegliata da telecamere che fanno multe. Scegli uno dei parcheggi qui sotto e usa il pulsante «Percorso a piedi» per l'ultimo tratto.",
        "quick_title": "In breve: quale scegliere",
        "quick": [
            ("💸", "Vuoi spendere zero", "Viale Buoncammino: strisce bianche gratuite, circa 10 minuti a piedi quasi in piano.", "buoncammino"),
            ("🪙", "Vuoi spendere poco", "Area Regina Elena Alta: massimo €2,50 al giorno, poi ascensori fino a Castello.", "re_alta"),
            ("🛡️", "Vuoi un posto coperto, aperto 24 ore", "Multipiano Regina Elena: circa €1,70 l'ora, massimo €10 al giorno.", "multipiano"),
        ],
        "map_title": "Mappa",
        "tabs_label": "Tipi di parcheggio",
        "tabs": {"free": "Parcheggi gratuiti", "paid": "Parcheggi a pagamento",
                 "lifts": "Ascensori per Castello", "tips": "Consigli utili"},
        "tab_intro": {
            "free": "Gratis, ma da cercare: in alta stagione conviene arrivare presto o la sera.",
            "paid": "Le soluzioni più comode lungo Viale Regina Elena, sotto le mura di Castello. Tariffe indicative.",
            "lifts": "Dai parcheggi di Viale Regina Elena si sale in Castello senza fatica con gli ascensori pubblici.",
            "tips": "Piccoli consigli per arrivare senza stress.",
        },
        "spots": {
            "buoncammino": ("Viale Buoncammino", "Gratuito",
                [("Costo", "gratis sulle strisce bianche"), ("A piedi fino al B&B", "circa 10 minuti, quasi tutto in piano"), ("Entrata in Castello", "Porta Cristina → Piazza Arsenale")],
                "Il viale panoramico sul crinale, con vista su tutta la città: è il parcheggio gratuito più vicino. Cerca posto il più vicino possibile a <strong>Porta Cristina</strong>, poi entra a piedi in Castello da Piazza Arsenale. Attenzione: su una parte del viale le strisce sono <strong>blu, cioè a pagamento</strong>. In alta stagione può essere pieno."),
            "blue_free": ("Strisce blu, gratis in certi orari", "Gratis la sera e la domenica",
                [("Gratis", "domenica e festivi; dal lunedì al sabato 13–16 e 20–9"), ("A pagamento", "lunedì–sabato 9–13 e 16–20")],
                "Le strisce blu si pagano solo in certe fasce orarie. Se arrivi la sera o nel fine settimana puoi lasciare l'auto anche sulle strisce blu vicine a Castello (Viale Buoncammino, Viale Regina Elena) senza pagare: ricordati però di pagare quando inizia la fascia a pagamento. Controlla sempre il cartello dell'area."),
            "re_alta": ("Area Regina Elena Alta (APCOA)", "Il più economico",
                [("Costo", "€0,50 la prima ora, poi €1 l'ora — massimo €2,50 al giorno"), ("Si paga", "lunedì–sabato 9–13 e 16–20"), ("A piedi fino al B&B", "circa 10 minuti con gli ascensori")],
                "Stalli blu all'aperto nella parte alta di Viale Regina Elena, sotto le mura di Castello. Con il tetto di €2,50 al giorno è l'opzione a pagamento più conveniente se resti più giorni. Da qui sali in Castello con gli ascensori pubblici."),
            "re_bassa": ("Aree Regina Elena Bassa 1 e 2 (APCOA)", "A pagamento",
                [("Costo", "Bassa 1: €1 l'ora, massimo €8 al giorno · Bassa 2: €0,50 la prima ora, poi €1, massimo €7,50"), ("Si paga", "lunedì–sabato 9–13 e 16–20"), ("A piedi fino al B&B", "circa 10–15 minuti con gli ascensori")],
                "Altri stalli blu nella parte bassa di Viale Regina Elena: utili quando la Regina Elena Alta è piena."),
            "multipiano": ("Parcheggio multipiano Regina Elena (APCOA)", "Coperto · 24 ore",
                [("Costo", "circa €1,70 l'ora, massimo €10 al giorno"), ("Orari", "aperto 24 ore su 24"), ("Indirizzo", "Viale Regina Elena 17"), ("A piedi fino al B&B", "circa 10 minuti con gli ascensori")],
                "Parcheggio coperto ai piedi delle mura: la scelta più comoda e tranquilla se lasci l'auto per tutto il soggiorno. Usciti dal parcheggio, gli ascensori pubblici di Viale Regina Elena portano in Castello."),
            "blue_paid": ("Strisce blu in centro", "A pagamento",
                [("Costo", "circa €1 l'ora (in alcune zone €0,50 la prima ora), massimo €10 al giorno"), ("Si paga", "lunedì–sabato 9–13 e 16–20; domenica e festivi gratis"), ("Come pagare", "al parcometro o con un'app (per esempio Telepass o MoneyGo)")],
                "Ci sono anche su parte di Viale Buoncammino e nelle vie intorno a Castello. Le tariffe cambiano da zona a zona: leggi sempre il cartello."),
            "lift_palazzo": ("Ascensori ex Unione Sarda → Piazza Palazzo", "Il più vicino al B&B",
                [("Partenza", "Viale Regina Elena, all'altezza del Terrapieno"), ("Arrivo", "Piazza Palazzo, accanto alla Cattedrale: a pochi passi dal B&B"), ("Costo", "gratuito")],
                "Due ascensori in sequenza: il primo sale da Viale Regina Elena al Terrapieno, il secondo, panoramico, arriva in Piazza Palazzo. È il collegamento più diretto con il B&amp;B. D'estate possono fermarsi nelle ore più calde."),
            "lift_remy": ("Ascensore di Saint Remy → Bastione", "Gratuito",
                [("Partenza", "Viale Regina Elena, nei giardini sotto le mura, a circa 100 m da Piazza Costituzione"), ("Arrivo", "Bastione di Saint Remy, poi pochi minuti a piedi"), ("Costo", "gratuito")],
                "Porta sulla grande terrazza del Bastione di Saint Remy, a pochi minuti a piedi dal B&amp;B. Anche questo d'estate può fermarsi nelle ore più calde."),
        },
        "buttons": {"show": "Mostra sulla mappa", "open": "Apri in Google Maps", "walk": "Percorso a piedi fino al B&B"},
        "tips": [
            ("🧭", "Navigatore", "Imposta come destinazione il parcheggio scelto, non l'indirizzo del B&amp;B: eviti di entrare per errore nella ZTL."),
            ("🚫", "ZTL e telecamere", "Non entrare in auto in Castello: gli accessi sono controllati da telecamere. Anche i posti di Piazza Indipendenza sono riservati ai residenti."),
            ("🌙", "Arrivo la sera o nel weekend", "Le strisce blu sono gratis la domenica, nei festivi e dal lunedì al sabato dalle 20 alle 9 e dalle 13 alle 16."),
            ("🌡️", "Ascensori fermi?", "D'estate gli ascensori possono fermarsi nelle ore più calde. Si può salire a piedi lungo Via Ubaldo Badas, oppure parcheggiare in Viale Buoncammino, che è già alla quota di Castello."),
            ("🧳", "Valigie pesanti", "Possiamo organizzare un transfer su richiesta: scrivici prima dell'arrivo."),
            ("💬", "Dubbi?", f"Scrivici su WhatsApp al {PHONE}: ti diciamo dove conviene parcheggiare in quel momento."),
        ],
        "updated": "Informazioni verificate a ottobre 2026 su fonti pubbliche (APCOA, Telepass, Comune di Cagliari). Tariffe, orari e funzionamento degli ascensori possono cambiare: controlla sempre i cartelli sul posto.",
        "sources_label": "Fonti",
        "help_title": "Serve una mano?",
        "help_text": "Scrivici prima di partire: ti consigliamo il parcheggio migliore per il tuo orario di arrivo. Su richiesta organizziamo anche il transfer.",
    },

    # ====================================================== ENGLISH =====
    "en": {
        "title": "Where to park in Cagliari near Castello — B&B Merì",
        "description": "Where to park near Castello in Cagliari: free on Viale Buoncammino, paid areas and car park on Viale Regina Elena, public lifts, ZTL rules. Prices and maps.",
        "og_description": "Free and paid parking near Castello, lifts, ZTL and maps: the B&B Merì parking guide.",
        "back": "Back to the home page",
        "eyebrow": "Parking guide · Castello, Cagliari",
        "h1": "Where to park<br>near Castello",
        "intro": "Castello is a <strong>limited-traffic zone (ZTL)</strong>: visitors' cars can't enter the quarter. The good news is that just outside the walls there are free and paid car parks, linked to the B&amp;B by short walks and public lifts. Here's everything you need, with maps and prices.",
        "satnav_title": "Before you set off: put the car park in your sat-nav, not the B&amp;B address",
        "satnav_text": "If you enter Via Alberto Lamarmora 18, your sat-nav may take you into the ZTL, where cameras issue fines. Pick one of the car parks below and use the «Walking route» button for the last stretch.",
        "quick_title": "In short: which one to choose",
        "quick": [
            ("💸", "Spend nothing", "Viale Buoncammino: free white-line spaces, about a 10-minute, mostly flat walk.", "buoncammino"),
            ("🪙", "Spend little", "Regina Elena Alta area: €2.50 per day maximum, then lifts up to Castello.", "re_alta"),
            ("🛡️", "Covered and open 24/7", "Regina Elena multi-storey car park: about €1.70 per hour, €10 per day maximum.", "multipiano"),
        ],
        "map_title": "Map",
        "tabs_label": "Parking types",
        "tabs": {"free": "Free parking", "paid": "Paid parking",
                 "lifts": "Lifts to Castello", "tips": "Useful tips"},
        "tab_intro": {
            "free": "Free, but you need to find a space: in high season it's best to arrive early or in the evening.",
            "paid": "The most convenient options along Viale Regina Elena, below the walls of Castello. Prices are indicative.",
            "lifts": "From the car parks on Viale Regina Elena you can go up to Castello effortlessly with the public lifts.",
            "tips": "A few tips for a stress-free arrival.",
        },
        "spots": {
            "buoncammino": ("Viale Buoncammino", "Free",
                [("Cost", "free on white lines"), ("Walk to the B&B", "about 10 minutes, mostly flat"), ("Way into Castello", "Porta Cristina → Piazza Arsenale")],
                "The panoramic avenue along the ridge, with views over the whole city: it's the nearest free parking. Look for a space as close as possible to <strong>Porta Cristina</strong>, then walk into Castello through Piazza Arsenale. Watch out: on part of the avenue the lines are <strong>blue, which means paid</strong>. In high season it can be full."),
            "blue_free": ("Blue lines, free at certain times", "Free evenings and Sundays",
                [("Free", "Sundays and public holidays; Monday–Saturday 1–4 PM and 8 PM–9 AM"), ("Paid", "Monday–Saturday 9 AM–1 PM and 4–8 PM")],
                "Blue-line spaces are only paid at certain times. If you arrive in the evening or at the weekend you can also leave the car on the blue lines near Castello (Viale Buoncammino, Viale Regina Elena) for free — just remember to pay when the paid hours start. Always check the sign for that area."),
            "re_alta": ("Regina Elena Alta area (APCOA)", "Cheapest",
                [("Cost", "€0.50 the first hour, then €1 per hour — €2.50 per day maximum"), ("Paid hours", "Monday–Saturday 9 AM–1 PM and 4–8 PM"), ("Walk to the B&B", "about 10 minutes using the lifts")],
                "Open-air blue-line spaces on the upper part of Viale Regina Elena, below the walls of Castello. With its €2.50 daily cap, it's the best-value paid option if you stay several days. From here, go up to Castello with the public lifts."),
            "re_bassa": ("Regina Elena Bassa 1 and 2 areas (APCOA)", "Paid",
                [("Cost", "Bassa 1: €1 per hour, €8 per day maximum · Bassa 2: €0.50 the first hour, then €1, €7.50 maximum"), ("Paid hours", "Monday–Saturday 9 AM–1 PM and 4–8 PM"), ("Walk to the B&B", "about 10–15 minutes using the lifts")],
                "More blue-line spaces on the lower part of Viale Regina Elena: handy when Regina Elena Alta is full."),
            "multipiano": ("Regina Elena multi-storey car park (APCOA)", "Covered · 24/7",
                [("Cost", "about €1.70 per hour, €10 per day maximum"), ("Hours", "open 24/7"), ("Address", "Viale Regina Elena 17"), ("Walk to the B&B", "about 10 minutes using the lifts")],
                "A covered car park at the foot of the walls: the easiest, most worry-free choice if you leave the car for your whole stay. Once outside, the public lifts on Viale Regina Elena take you up to Castello."),
            "blue_paid": ("Blue lines in the centre", "Paid",
                [("Cost", "about €1 per hour (in some areas €0.50 the first hour), €10 per day maximum"), ("Paid hours", "Monday–Saturday 9 AM–1 PM and 4–8 PM; free on Sundays and public holidays"), ("How to pay", "at the parking meter or with an app (for example Telepass or MoneyGo)")],
                "You'll also find them on part of Viale Buoncammino and in the streets around Castello. Prices vary from area to area: always read the sign."),
            "lift_palazzo": ("Former Unione Sarda lifts → Piazza Palazzo", "Closest to the B&B",
                [("From", "Viale Regina Elena, by the Terrapieno"), ("To", "Piazza Palazzo, next to the Cathedral: a few steps from the B&B"), ("Cost", "free")],
                "Two lifts in a row: the first goes up from Viale Regina Elena to the Terrapieno, the second, a panoramic one, arrives in Piazza Palazzo. It's the most direct link to the B&amp;B. In summer they may stop during the hottest hours."),
            "lift_remy": ("Saint Remy lift → Bastion", "Free",
                [("From", "Viale Regina Elena, in the gardens below the walls, about 100 m from Piazza Costituzione"), ("To", "Bastione di Saint Remy, then a few minutes on foot"), ("Cost", "free")],
                "It takes you up to the great terrace of the Bastione di Saint Remy, a few minutes' walk from the B&amp;B. In summer it may also stop during the hottest hours."),
        },
        "buttons": {"show": "Show on the map", "open": "Open in Google Maps", "walk": "Walking route to the B&B"},
        "tips": [
            ("🧭", "Sat-nav", "Set the car park you've chosen as your destination, not the B&amp;B address: that way you won't drive into the ZTL by mistake."),
            ("🚫", "ZTL and cameras", "Don't drive into Castello: the entrances are monitored by cameras. The spaces in Piazza Indipendenza are reserved for residents too."),
            ("🌙", "Arriving in the evening or at the weekend", "Blue lines are free on Sundays, public holidays and Monday to Saturday from 8 PM to 9 AM and from 1 to 4 PM."),
            ("🌡️", "Lifts not running?", "In summer the lifts may stop during the hottest hours. You can walk up along Via Ubaldo Badas, or park on Viale Buoncammino, which is already at Castello's level."),
            ("🧳", "Heavy luggage", "We can arrange a transfer on request: write to us before you arrive."),
            ("💬", "Any questions?", f"Message us on WhatsApp at {PHONE_INTL}: we'll tell you the best place to park at that moment."),
        ],
        "updated": "Information checked in October 2026 against public sources (APCOA, Telepass, Comune di Cagliari). Prices, times and lift operation may change: always check the signs on site.",
        "sources_label": "Sources",
        "help_title": "Need a hand?",
        "help_text": "Write to us before you set off: we'll suggest the best car park for your arrival time. We can also arrange a transfer on request.",
    },

    # ===================================================== FRANÇAIS =====
    "fr": {
        "title": "Où se garer à Cagliari près de Castello — B&B Merì",
        "description": "Où se garer près de Castello à Cagliari : gratuit sur le Viale Buoncammino, zones et parking du Viale Regina Elena, ascenseurs, ZTL. Tarifs et cartes.",
        "og_description": "Parkings gratuits et payants près de Castello, ascenseurs, ZTL et cartes : le guide du B&B Merì.",
        "back": "Retour à l'accueil",
        "eyebrow": "Guide du stationnement · Castello, Cagliari",
        "h1": "Où se garer<br>près de Castello",
        "intro": "Castello est une <strong>zone à trafic limité (ZTL)</strong> : les voitures des visiteurs ne peuvent pas entrer dans le quartier. Bonne nouvelle : juste au pied des remparts, il y a des parkings gratuits et payants, reliés à la maison par de courtes promenades et des ascenseurs publics. Voici tout ce qu'il faut savoir, avec cartes et tarifs.",
        "satnav_title": "Avant de partir : dans le GPS, indiquez le parking, pas l'adresse du B&amp;B",
        "satnav_text": "Si vous saisissez Via Alberto Lamarmora 18, le GPS peut vous faire entrer dans la ZTL, surveillée par des caméras qui verbalisent. Choisissez l'un des parkings ci-dessous et utilisez le bouton « Itinéraire à pied » pour le dernier tronçon.",
        "quick_title": "En bref : lequel choisir",
        "quick": [
            ("💸", "Ne rien dépenser", "Viale Buoncammino : places gratuites (lignes blanches), environ 10 minutes à pied, presque à plat.", "buoncammino"),
            ("🪙", "Dépenser peu", "Zone Regina Elena Alta : 2,50 € par jour maximum, puis ascenseurs jusqu'à Castello.", "re_alta"),
            ("🛡️", "Couvert et ouvert 24 h/24", "Parking à étages Regina Elena : environ 1,70 € de l'heure, 10 € par jour maximum.", "multipiano"),
        ],
        "map_title": "Carte",
        "tabs_label": "Types de stationnement",
        "tabs": {"free": "Parkings gratuits", "paid": "Parkings payants",
                 "lifts": "Ascenseurs vers Castello", "tips": "Conseils utiles"},
        "tab_intro": {
            "free": "Gratuits, mais il faut trouver une place : en haute saison, mieux vaut arriver tôt ou le soir.",
            "paid": "Les solutions les plus pratiques le long du Viale Regina Elena, sous les remparts de Castello. Tarifs indicatifs.",
            "lifts": "Depuis les parkings du Viale Regina Elena, on monte à Castello sans effort grâce aux ascenseurs publics.",
            "tips": "Quelques conseils pour arriver sans stress.",
        },
        "spots": {
            "buoncammino": ("Viale Buoncammino", "Gratuit",
                [("Coût", "gratuit sur les lignes blanches"), ("À pied jusqu'au B&B", "environ 10 minutes, presque à plat"), ("Entrée dans Castello", "Porta Cristina → Piazza Arsenale")],
                "L'avenue panoramique sur la crête, avec vue sur toute la ville : c'est le parking gratuit le plus proche. Cherchez une place au plus près de la <strong>Porta Cristina</strong>, puis entrez à pied dans Castello par la Piazza Arsenale. Attention : sur une partie de l'avenue, les lignes sont <strong>bleues, donc payantes</strong>. En haute saison, il peut être complet."),
            "blue_free": ("Lignes bleues, gratuites à certaines heures", "Gratuit le soir et le dimanche",
                [("Gratuit", "dimanche et jours fériés ; du lundi au samedi 13 h–16 h et 20 h–9 h"), ("Payant", "lundi–samedi 9 h–13 h et 16 h–20 h")],
                "Les places à lignes bleues ne sont payantes qu'à certaines heures. Si vous arrivez le soir ou le week-end, vous pouvez aussi laisser la voiture gratuitement sur les lignes bleues près de Castello (Viale Buoncammino, Viale Regina Elena) : pensez simplement à payer quand la plage payante commence. Vérifiez toujours le panneau de la zone."),
            "re_alta": ("Zone Regina Elena Alta (APCOA)", "Le moins cher",
                [("Coût", "0,50 € la première heure, puis 1 € de l'heure — 2,50 € par jour maximum"), ("Heures payantes", "lundi–samedi 9 h–13 h et 16 h–20 h"), ("À pied jusqu'au B&B", "environ 10 minutes avec les ascenseurs")],
                "Places à lignes bleues en plein air dans la partie haute du Viale Regina Elena, sous les remparts de Castello. Avec son plafond de 2,50 € par jour, c'est l'option payante la plus avantageuse pour plusieurs jours. De là, montez à Castello avec les ascenseurs publics."),
            "re_bassa": ("Zones Regina Elena Bassa 1 et 2 (APCOA)", "Payant",
                [("Coût", "Bassa 1 : 1 € de l'heure, 8 € par jour maximum · Bassa 2 : 0,50 € la première heure, puis 1 €, 7,50 € maximum"), ("Heures payantes", "lundi–samedi 9 h–13 h et 16 h–20 h"), ("À pied jusqu'au B&B", "environ 10–15 minutes avec les ascenseurs")],
                "D'autres places à lignes bleues dans la partie basse du Viale Regina Elena : pratiques quand la Regina Elena Alta est pleine."),
            "multipiano": ("Parking à étages Regina Elena (APCOA)", "Couvert · 24 h/24",
                [("Coût", "environ 1,70 € de l'heure, 10 € par jour maximum"), ("Horaires", "ouvert 24 h/24"), ("Adresse", "Viale Regina Elena 17"), ("À pied jusqu'au B&B", "environ 10 minutes avec les ascenseurs")],
                "Un parking couvert au pied des remparts : le choix le plus pratique et le plus serein si vous laissez la voiture pendant tout le séjour. À la sortie, les ascenseurs publics du Viale Regina Elena vous montent à Castello."),
            "blue_paid": ("Lignes bleues en centre-ville", "Payant",
                [("Coût", "environ 1 € de l'heure (dans certaines zones 0,50 € la première heure), 10 € par jour maximum"), ("Heures payantes", "lundi–samedi 9 h–13 h et 16 h–20 h ; gratuit le dimanche et les jours fériés"), ("Paiement", "à l'horodateur ou avec une application (par exemple Telepass ou MoneyGo)")],
                "Vous en trouverez aussi sur une partie du Viale Buoncammino et dans les rues autour de Castello. Les tarifs varient selon la zone : lisez toujours le panneau."),
            "lift_palazzo": ("Ascenseurs de l'ancienne Unione Sarda → Piazza Palazzo", "Le plus proche du B&B",
                [("Départ", "Viale Regina Elena, à hauteur du Terrapieno"), ("Arrivée", "Piazza Palazzo, à côté de la cathédrale : à deux pas du B&B"), ("Coût", "gratuit")],
                "Deux ascenseurs à la suite : le premier monte du Viale Regina Elena au Terrapieno, le second, panoramique, arrive Piazza Palazzo. C'est la liaison la plus directe avec le B&amp;B. En été, ils peuvent s'arrêter aux heures les plus chaudes."),
            "lift_remy": ("Ascenseur de Saint-Remy → Bastion", "Gratuit",
                [("Départ", "Viale Regina Elena, dans les jardins sous les remparts, à environ 100 m de la Piazza Costituzione"), ("Arrivée", "Bastion de Saint-Remy, puis quelques minutes à pied"), ("Coût", "gratuit")],
                "Il mène à la grande terrasse du Bastion de Saint-Remy, à quelques minutes à pied du B&amp;B. En été, il peut lui aussi s'arrêter aux heures les plus chaudes."),
        },
        "buttons": {"show": "Voir sur la carte", "open": "Ouvrir dans Google Maps", "walk": "Itinéraire à pied jusqu'au B&B"},
        "tips": [
            ("🧭", "GPS", "Indiquez comme destination le parking choisi, pas l'adresse du B&amp;B : vous éviterez d'entrer par erreur dans la ZTL."),
            ("🚫", "ZTL et caméras", "N'entrez pas en voiture dans Castello : les accès sont surveillés par des caméras. Les places de la Piazza Indipendenza sont aussi réservées aux résidents."),
            ("🌙", "Arrivée le soir ou le week-end", "Les lignes bleues sont gratuites le dimanche, les jours fériés et du lundi au samedi de 20 h à 9 h et de 13 h à 16 h."),
            ("🌡️", "Ascenseurs à l'arrêt ?", "En été, les ascenseurs peuvent s'arrêter aux heures les plus chaudes. Vous pouvez monter à pied par la Via Ubaldo Badas, ou vous garer sur le Viale Buoncammino, déjà au niveau de Castello."),
            ("🧳", "Bagages lourds", "Nous pouvons organiser un transfert sur demande : écrivez-nous avant votre arrivée."),
            ("💬", "Une question ?", f"Écrivez-nous sur WhatsApp au {PHONE_INTL} : nous vous dirons où il vaut mieux se garer à ce moment-là."),
        ],
        "updated": "Informations vérifiées en octobre 2026 auprès de sources publiques (APCOA, Telepass, Comune di Cagliari). Tarifs, horaires et fonctionnement des ascenseurs peuvent changer : vérifiez toujours les panneaux sur place.",
        "sources_label": "Sources",
        "help_title": "Besoin d'un coup de main ?",
        "help_text": "Écrivez-nous avant de partir : nous vous conseillerons le meilleur parking selon votre heure d'arrivée. Nous pouvons aussi organiser un transfert sur demande.",
    },

    # ====================================================== ESPAÑOL =====
    "es": {
        "title": "Dónde aparcar en Cagliari cerca de Castello — B&B Merì",
        "description": "Dónde aparcar cerca de Castello en Cagliari: gratis en el Viale Buoncammino, zonas y parking del Viale Regina Elena, ascensores, ZTL. Tarifas y mapas.",
        "og_description": "Aparcamientos gratuitos y de pago cerca de Castello, ascensores, ZTL y mapas: la guía del B&B Merì.",
        "back": "Volver a la página principal",
        "eyebrow": "Guía de aparcamiento · Castello, Cagliari",
        "h1": "Dónde aparcar<br>cerca de Castello",
        "intro": "Castello es una <strong>zona de tráfico limitado (ZTL)</strong>: los coches de los visitantes no pueden entrar en el barrio. La buena noticia es que justo fuera de las murallas hay aparcamientos gratuitos y de pago, conectados con el B&amp;B por paseos cortos y ascensores públicos. Aquí tienes todo, con mapas y tarifas.",
        "satnav_title": "Antes de salir: en el navegador pon el aparcamiento, no la dirección del B&amp;B",
        "satnav_text": "Si pones Via Alberto Lamarmora 18, el navegador puede meterte en la ZTL, vigilada por cámaras que multan. Elige uno de los aparcamientos de abajo y usa el botón «Ruta a pie» para el último tramo.",
        "quick_title": "En resumen: cuál elegir",
        "quick": [
            ("💸", "No gastar nada", "Viale Buoncammino: plazas gratuitas de rayas blancas, unos 10 minutos a pie casi en llano.", "buoncammino"),
            ("🪙", "Gastar poco", "Zona Regina Elena Alta: 2,50 € al día como máximo y luego ascensores hasta Castello.", "re_alta"),
            ("🛡️", "Cubierto y abierto 24 horas", "Aparcamiento de varias plantas Regina Elena: aprox. 1,70 € la hora, 10 € al día como máximo.", "multipiano"),
        ],
        "map_title": "Mapa",
        "tabs_label": "Tipos de aparcamiento",
        "tabs": {"free": "Aparcamientos gratuitos", "paid": "Aparcamientos de pago",
                 "lifts": "Ascensores a Castello", "tips": "Consejos útiles"},
        "tab_intro": {
            "free": "Gratis, pero hay que encontrar sitio: en temporada alta conviene llegar pronto o por la noche.",
            "paid": "Las opciones más cómodas a lo largo del Viale Regina Elena, bajo las murallas de Castello. Tarifas orientativas.",
            "lifts": "Desde los aparcamientos del Viale Regina Elena se sube a Castello sin esfuerzo con los ascensores públicos.",
            "tips": "Unos consejos para llegar sin estrés.",
        },
        "spots": {
            "buoncammino": ("Viale Buoncammino", "Gratuito",
                [("Precio", "gratis en las rayas blancas"), ("A pie hasta el B&B", "unos 10 minutos, casi todo en llano"), ("Entrada a Castello", "Porta Cristina → Piazza Arsenale")],
                "La avenida panorámica sobre la colina, con vistas a toda la ciudad: es el aparcamiento gratuito más cercano. Busca sitio lo más cerca posible de la <strong>Porta Cristina</strong> y entra a pie en Castello por la Piazza Arsenale. Atención: en una parte de la avenida las rayas son <strong>azules, es decir, de pago</strong>. En temporada alta puede estar lleno."),
            "blue_free": ("Rayas azules, gratis a ciertas horas", "Gratis por la noche y los domingos",
                [("Gratis", "domingos y festivos; de lunes a sábado 13–16 h y 20–9 h"), ("De pago", "lunes–sábado 9–13 h y 16–20 h")],
                "Las plazas de rayas azules solo se pagan en ciertas franjas horarias. Si llegas por la noche o el fin de semana, también puedes dejar el coche gratis en las rayas azules cerca de Castello (Viale Buoncammino, Viale Regina Elena): eso sí, recuerda pagar cuando empiece la franja de pago. Mira siempre el cartel de la zona."),
            "re_alta": ("Zona Regina Elena Alta (APCOA)", "La más económica",
                [("Precio", "0,50 € la primera hora, luego 1 € la hora — 2,50 € al día como máximo"), ("Horario de pago", "lunes–sábado 9–13 h y 16–20 h"), ("A pie hasta el B&B", "unos 10 minutos con los ascensores")],
                "Plazas de rayas azules al aire libre en la parte alta del Viale Regina Elena, bajo las murallas de Castello. Con su tope de 2,50 € al día, es la opción de pago más económica si te quedas varios días. Desde aquí se sube a Castello con los ascensores públicos."),
            "re_bassa": ("Zonas Regina Elena Bassa 1 y 2 (APCOA)", "De pago",
                [("Precio", "Bassa 1: 1 € la hora, 8 € al día como máximo · Bassa 2: 0,50 € la primera hora, luego 1 €, 7,50 € como máximo"), ("Horario de pago", "lunes–sábado 9–13 h y 16–20 h"), ("A pie hasta el B&B", "unos 10–15 minutos con los ascensores")],
                "Más plazas de rayas azules en la parte baja del Viale Regina Elena: útiles cuando la Regina Elena Alta está llena."),
            "multipiano": ("Aparcamiento de varias plantas Regina Elena (APCOA)", "Cubierto · 24 horas",
                [("Precio", "aprox. 1,70 € la hora, 10 € al día como máximo"), ("Horario", "abierto 24 horas"), ("Dirección", "Viale Regina Elena 17"), ("A pie hasta el B&B", "unos 10 minutos con los ascensores")],
                "Aparcamiento cubierto al pie de las murallas: la opción más cómoda y tranquila si dejas el coche toda la estancia. Al salir, los ascensores públicos del Viale Regina Elena te suben a Castello."),
            "blue_paid": ("Rayas azules en el centro", "De pago",
                [("Precio", "aprox. 1 € la hora (en algunas zonas 0,50 € la primera hora), 10 € al día como máximo"), ("Horario de pago", "lunes–sábado 9–13 h y 16–20 h; gratis domingos y festivos"), ("Cómo pagar", "en el parquímetro o con una app (por ejemplo Telepass o MoneyGo)")],
                "También las hay en parte del Viale Buoncammino y en las calles alrededor de Castello. Las tarifas cambian según la zona: lee siempre el cartel."),
            "lift_palazzo": ("Ascensores de la antigua Unione Sarda → Piazza Palazzo", "El más cercano al B&B",
                [("Salida", "Viale Regina Elena, a la altura del Terrapieno"), ("Llegada", "Piazza Palazzo, junto a la catedral: a pocos pasos del B&B"), ("Precio", "gratuito")],
                "Dos ascensores seguidos: el primero sube del Viale Regina Elena al Terrapieno y el segundo, panorámico, llega a la Piazza Palazzo. Es la conexión más directa con el B&amp;B. En verano pueden pararse en las horas de más calor."),
            "lift_remy": ("Ascensor de Saint Remy → Bastión", "Gratuito",
                [("Salida", "Viale Regina Elena, en los jardines bajo las murallas, a unos 100 m de Piazza Costituzione"), ("Llegada", "Bastión de Saint Remy y luego unos minutos a pie"), ("Precio", "gratuito")],
                "Lleva a la gran terraza del Bastión de Saint Remy, a pocos minutos a pie del B&amp;B. En verano también puede pararse en las horas de más calor."),
        },
        "buttons": {"show": "Ver en el mapa", "open": "Abrir en Google Maps", "walk": "Ruta a pie hasta el B&B"},
        "tips": [
            ("🧭", "Navegador", "Pon como destino el aparcamiento elegido, no la dirección del B&amp;B: así no entrarás por error en la ZTL."),
            ("🚫", "ZTL y cámaras", "No entres en coche en Castello: los accesos están vigilados por cámaras. Las plazas de la Piazza Indipendenza también están reservadas a los residentes."),
            ("🌙", "Llegada por la noche o el fin de semana", "Las rayas azules son gratis los domingos, los festivos y de lunes a sábado de 20 a 9 h y de 13 a 16 h."),
            ("🌡️", "¿Ascensores parados?", "En verano los ascensores pueden pararse en las horas de más calor. Puedes subir a pie por la Via Ubaldo Badas o aparcar en el Viale Buoncammino, que ya está a la altura de Castello."),
            ("🧳", "Maletas pesadas", "Podemos organizar un traslado bajo petición: escríbenos antes de llegar."),
            ("💬", "¿Dudas?", f"Escríbenos por WhatsApp al {PHONE_INTL}: te diremos dónde conviene aparcar en ese momento."),
        ],
        "updated": "Información comprobada en octubre de 2026 en fuentes públicas (APCOA, Telepass, Comune di Cagliari). Tarifas, horarios y funcionamiento de los ascensores pueden cambiar: mira siempre los carteles en el lugar.",
        "sources_label": "Fuentes",
        "help_title": "¿Necesitas ayuda?",
        "help_text": "Escríbenos antes de salir: te recomendamos el mejor aparcamiento según tu hora de llegada. Bajo petición también organizamos el traslado.",
    },
}


# ------------------------------------- guida "cosa vedere a Castello" --
#
# Itinerario a piedi dal B&B. I tempi sono indicativi, a passo tranquillo.
# Ogni tappa: gruppo ("castello" = il giro del quartiere, "beyond" = appena
# fuori), ricerca per la mappa e mezzo per il percorso dal B&B.

STOPS = {
    "cattedrale":     {"group": "castello", "map": "Cattedrale di Santa Maria, Piazza Palazzo, Cagliari", "mode": "walking"},
    "palazzo":        {"group": "castello", "map": "Palazzo Regio, Piazza Palazzo, Cagliari", "mode": "walking"},
    "san_pancrazio":  {"group": "castello", "map": "Torre di San Pancrazio, Cagliari", "mode": "walking"},
    "cittadella":     {"group": "castello", "map": "Cittadella dei Musei, Piazza Arsenale, Cagliari", "mode": "walking"},
    "porta_cristina": {"group": "castello", "map": "Porta Cristina, Cagliari", "mode": "walking"},
    "santa_croce":    {"group": "castello", "map": "Bastione di Santa Croce, Cagliari", "mode": "walking"},
    "elefante":       {"group": "castello", "map": "Torre dell'Elefante, Cagliari", "mode": "walking"},
    "saint_remy":     {"group": "castello", "map": "Bastione di Saint Remy, Cagliari", "mode": "walking"},
    "marina":         {"group": "beyond", "map": "Via Roma, Cagliari", "mode": "walking", "icon": "⚓"},
    "anfiteatro":     {"group": "beyond", "map": "Anfiteatro romano di Cagliari", "mode": "walking", "icon": "🏛️"},
    "poetto":         {"group": "beyond", "map": "Spiaggia del Poetto, Cagliari", "mode": "transit", "icon": "🏖️"},
    "molentargius":   {"group": "beyond", "map": "Parco naturale regionale Molentargius-Saline, Cagliari", "mode": "driving", "icon": "🦩"},
}

G = {
    # ===================================================== ITALIANO =====
    "it": {
        "title": "Cosa vedere a Castello (Cagliari): giro a piedi — B&B Merì",
        "description": "Itinerario a piedi nel quartiere Castello di Cagliari dal B&B Merì: Cattedrale, Bastione di Saint Remy, torri pisane, musei e dintorni, con tempi e mappe.",
        "og_description": "Un giro a piedi tra i luoghi più belli di Castello, partendo dal portone del B&B Merì.",
        "crumb": "Cosa vedere a Castello",
        "eyebrow": "Guida · Castello, Cagliari",
        "h1": "Cosa vedere a Castello,<br>a piedi dal B&amp;B",
        "intro": "Castello è il quartiere fortificato che i Pisani costruirono nel Duecento sulla collina che domina Cagliari. In sardo si chiama <em>Casteddu</em>, lo stesso nome che i sardi danno a tutta la città. Dal nostro portone, in Via Alberto Lamarmora 18, si gira tutto a piedi: ecco l'itinerario che consigliamo, con i tempi a piedi dal B&amp;B.",
        "before_title": "Prima di uscire",
        "before_text": "Castello è in salita e le strade sono lastricate: meglio scarpe comode. D'estate i bastioni danno il meglio la mattina presto e al tramonto. Orari e biglietti di chiese, torri e musei cambiano spesso: controllateli prima della visita.",
        "route_title": "Il giro di Castello, tappa per tappa",
        "route_intro": "Un anello di circa 2 km nel quartiere: con calma e qualche visita, ci vuole mezza giornata. I tempi indicati sono a piedi dal B&amp;B.",
        "beyond_title": "Appena fuori da Castello",
        "beyond_intro": "Quando avete visto Castello, ecco dove andare: dal quartiere sul porto fino alla spiaggia.",
        "stops": {
            "cattedrale": ("Cattedrale di Santa Maria", "2 min a piedi",
                "Il Duomo di Cagliari, in Piazza Palazzo, ha origini pisane del Duecento; la facciata in stile romanico pisano è stata rifatta nel Novecento. All'interno, i due pulpiti di Mastro Guglielmo, ricavati da un pulpito scolpito nel XII secolo per il Duomo di Pisa, e la cripta dei Martiri, scavata nella roccia."),
            "palazzo": ("Palazzo Regio e Palazzo di Città", "2 min a piedi",
                "Sulla stessa piazza si affacciano il Palazzo Regio, antica residenza dei viceré che all'inizio dell'Ottocento ospitò la corte dei Savoia, e il Palazzo di Città, il vecchio municipio, oggi sede di mostre dei Musei Civici."),
            "san_pancrazio": ("Torre di San Pancrazio", "5 min a piedi",
                "Costruita dai Pisani nel 1305 nella parte più alta di Castello, è la gemella della Torre dell'Elefante. Quando è aperta si può salire in cima: la vista spazia sulla città, sul golfo e sugli stagni."),
            "cittadella": ("Cittadella dei Musei", "7 min a piedi",
                "In Piazza Arsenale, negli spazi dell'antico arsenale, ci sono il Museo Archeologico Nazionale, con i bronzetti nuragici e alcune statue dei Giganti di Mont'e Prama, e la Pinacoteca Nazionale. È il posto giusto per scoprire la storia della Sardegna."),
            "porta_cristina": ("Porta Cristina e Viale Buoncammino", "10 min a piedi",
                "Da Piazza Arsenale si esce dalle mura passando per Porta Cristina, una porta neoclassica dell'Ottocento, e si arriva sul Viale Buoncammino: un viale alberato sul crinale, con vista sulla città e sugli stagni."),
            "santa_croce": ("Bastione di Santa Croce e l'ex Ghetto", "5 min a piedi",
                "Sul lato ovest delle mura, il Bastione di Santa Croce è una terrazza panoramica amatissima al tramonto. Accanto ci sono l'ex Ghetto degli Ebrei, oggi spazio espositivo, e la Basilica di Santa Croce, costruita dove sorgeva la sinagoga."),
            "elefante": ("Torre dell'Elefante", "4 min a piedi",
                "Costruita nel 1307 da Giovanni Capula, lo stesso architetto della Torre di San Pancrazio, deve il nome alla piccola statua di un elefante in marmo sulla facciata. Era una delle porte di Castello: passandoci sotto si scende verso la parte bassa della città."),
            "saint_remy": ("Bastione di Saint Remy", "3 min a piedi",
                "Il simbolo di Cagliari, costruito tra fine Ottocento e inizio Novecento: una grande scalinata lo collega a Piazza Costituzione. Dalla Terrazza Umberto I la vista abbraccia i tetti di Villanova e della Marina, il porto e il Golfo degli Angeli."),
            "marina": ("Quartiere Marina e Via Roma", "10 min a piedi",
                "Scendendo da Castello si arriva alla Marina, il quartiere tra le mura e il porto, con vicoli pieni di trattorie e botteghe. Sotto i portici di Via Roma si passeggia guardando le navi nel porto."),
            "anfiteatro": ("Anfiteatro romano e Orto Botanico", "15 min a piedi",
                "L'anfiteatro, del II secolo d.C., è in gran parte scavato nella roccia del colle. A pochi passi c'è l'Orto Botanico dell'Università, un'oasi verde con piante mediterranee e tropicali."),
            "poetto": ("Spiaggia del Poetto e Sella del Diavolo", "15 min in bus o in auto",
                "Il Poetto è la spiaggia della città: circa 8 km di sabbia chiara, con chioschi e stabilimenti. All'estremità verso Marina Piccola, il promontorio della Sella del Diavolo ha sentieri panoramici con viste splendide sul golfo."),
            "molentargius": ("Parco di Molentargius", "15 min in auto",
                "Tra la città e il Poetto, il parco naturale di Molentargius-Saline protegge stagni e antiche saline dove vivono i fenicotteri rosa. Si visita a piedi o in bicicletta."),
        },
        "buttons": {"open": "Apri in Google Maps", "route": "Percorso dal B&B"},
        "tips_title": "Consigli utili",
        "tips": [
            ("🌅", "Il tramonto", "Il posto più bello è il Bastione di Santa Croce, con il sole che scende sullo stagno di Santa Gilla."),
            ("🛗", "Ascensori pubblici", "Dalla parte bassa della città si sale in Castello con gli ascensori gratuiti di Viale Regina Elena: dove sono e come funzionano lo trovate nella nostra <a class=\"text-link\" href=\"{parking}#lifts\">guida ai parcheggi</a>."),
            ("☀️", "D'estate", "Nelle ore più calde scegliete musei e chiese; i bastioni danno il meglio la mattina presto e al tramonto. Riempite la borraccia prima di uscire: l'acqua del rubinetto del B&amp;B è potabile."),
            ("🎉", "Sant'Efisio, 1º maggio", "Il 1º maggio Cagliari celebra Sant'Efisio con una lunga processione di costumi tradizionali da tutta la Sardegna: se siete in città, non perdetela."),
            ("💬", "Chiedete a noi", f"Vi diamo volentieri consigli su cosa vedere e dove mangiare: scriveteci su WhatsApp al {PHONE}."),
        ],
        "updated": "Guida aggiornata a novembre 2026. Orari, aperture e biglietti possono cambiare: verificateli sui siti ufficiali prima della visita.",
        "help_title": "Volete un consiglio su misura?",
        "help_text": "Scriveteci: vi suggeriamo cosa vedere in base al tempo che avete e dove mangiare a Castello e dintorni.",
    },

    # ====================================================== ENGLISH =====
    "en": {
        "title": "Things to see in Castello, Cagliari: walking tour — B&B Merì",
        "description": "A walking tour of Cagliari's Castello quarter from B&B Merì: the Cathedral, Bastione di Saint Remy, Pisan towers, museums and more, with times and maps.",
        "og_description": "A walk through the highlights of Castello, starting from the front door of B&B Merì.",
        "crumb": "Things to see in Castello",
        "eyebrow": "Guide · Castello, Cagliari",
        "h1": "Things to see in Castello,<br>on foot from the B&amp;B",
        "intro": "Castello is the fortified quarter the Pisans built in the 13th century on the hill overlooking Cagliari. In Sardinian it's called <em>Casteddu</em>, the same name Sardinians use for the whole city. From our front door at Via Alberto Lamarmora 18 you can see it all on foot: here is the walk we recommend, with walking times from the B&amp;B.",
        "before_title": "Before you set off",
        "before_text": "Castello is hilly and the streets are paved with stone: wear comfortable shoes. In summer the bastions are at their best early in the morning and at sunset. Opening hours and tickets for churches, towers and museums change often: check them before your visit.",
        "route_title": "The Castello walk, stop by stop",
        "route_intro": "A loop of about 2 km around the quarter: at a relaxed pace, with a few visits, it takes half a day. Times shown are on foot from the B&amp;B.",
        "beyond_title": "Just outside Castello",
        "beyond_intro": "Once you've seen Castello, here's where to go next: from the harbour quarter to the beach.",
        "stops": {
            "cattedrale": ("Cathedral of Santa Maria", "2 min walk",
                "Cagliari's cathedral, on Piazza Palazzo, dates back to the Pisans in the 13th century; its Pisan Romanesque façade was rebuilt in the 20th century. Inside, don't miss the two pulpits by Master Guglielmo, made from a single pulpit carved in the 12th century for Pisa Cathedral, and the Crypt of the Martyrs, cut into the rock."),
            "palazzo": ("Palazzo Regio and Palazzo di Città", "2 min walk",
                "On the same square stand the Palazzo Regio, the former viceroys' residence that hosted the Savoy court in the early 19th century, and the Palazzo di Città, the old town hall, now used for exhibitions by the city museums."),
            "san_pancrazio": ("San Pancrazio Tower", "5 min walk",
                "Built by the Pisans in 1305 on the highest part of Castello, it is the twin of the Elephant Tower. When it's open you can climb to the top for views over the city, the gulf and the lagoons."),
            "cittadella": ("Cittadella dei Musei", "7 min walk",
                "On Piazza Arsenale, in the old arsenal, you'll find the National Archaeological Museum, with Nuragic bronze figurines and some of the Giants of Mont'e Prama, and the National Art Gallery. It's the place to discover the history of Sardinia."),
            "porta_cristina": ("Porta Cristina and Viale Buoncammino", "10 min walk",
                "From Piazza Arsenale you leave the walls through Porta Cristina, a 19th-century neoclassical gate, and reach Viale Buoncammino: a tree-lined avenue along the ridge with views over the city and the lagoons."),
            "santa_croce": ("Bastione di Santa Croce and the old Ghetto", "5 min walk",
                "On the west side of the walls, the Bastione di Santa Croce is a panoramic terrace much loved at sunset. Next to it are the former Jewish Ghetto, now an exhibition space, and the Basilica of Santa Croce, built where the synagogue once stood."),
            "elefante": ("Elephant Tower", "4 min walk",
                "Built in 1307 by Giovanni Capula, the architect of the San Pancrazio Tower, it takes its name from the small marble elephant on its façade. It was one of Castello's gates: walk through it to head down to the lower town."),
            "saint_remy": ("Bastione di Saint Remy", "3 min walk",
                "Cagliari's landmark, built between the late 19th and early 20th centuries, with a grand staircase rising from Piazza Costituzione. From the Terrazza Umberto I the view takes in the rooftops of Villanova and Marina, the port and the Gulf of Angels."),
            "marina": ("Marina quarter and Via Roma", "10 min walk",
                "Walking down from Castello you reach Marina, the quarter between the walls and the port, with lanes full of trattorias and small shops. Under the arcades of Via Roma you can stroll while watching the ships in the harbour."),
            "anfiteatro": ("Roman Amphitheatre and Botanical Garden", "15 min walk",
                "The amphitheatre, from the 2nd century AD, is largely carved into the rock of the hill. A few steps away is the University Botanical Garden, a green oasis with Mediterranean and tropical plants."),
            "poetto": ("Poetto beach and Sella del Diavolo", "15 min by bus or car",
                "Poetto is the city's beach: about 8 km of pale sand with kiosks and beach clubs. At the Marina Piccola end, the Sella del Diavolo headland has panoramic trails with superb views over the gulf."),
            "molentargius": ("Molentargius park", "15 min by car",
                "Between the city and Poetto, the Molentargius-Saline nature park protects lagoons and old salt pans where pink flamingos live. You can explore it on foot or by bike."),
        },
        "buttons": {"open": "Open in Google Maps", "route": "Route from the B&B"},
        "tips_title": "Useful tips",
        "tips": [
            ("🌅", "Sunset", "The best spot is the Bastione di Santa Croce, with the sun going down over the Santa Gilla lagoon."),
            ("🛗", "Public lifts", "From the lower town you can ride up to Castello with the free lifts on Viale Regina Elena: where they are and how they work is in our <a class=\"text-link\" href=\"{parking}#lifts\">parking guide</a>."),
            ("☀️", "In summer", "In the hottest hours, choose museums and churches; the bastions are best early in the morning and at sunset. Fill your bottle before you go out: the tap water at the B&amp;B is drinkable."),
            ("🎉", "Sant'Efisio, 1 May", "On 1 May Cagliari celebrates Saint Ephysius with a long procession of traditional costumes from all over Sardinia: if you're in town, don't miss it."),
            ("💬", "Ask us", f"We're happy to suggest what to see and where to eat: message us on WhatsApp at {PHONE_INTL}."),
        ],
        "updated": "Guide updated in November 2026. Opening hours, access and tickets may change: please check the official websites before your visit.",
        "help_title": "Would you like tailored advice?",
        "help_text": "Write to us: we'll suggest what to see based on the time you have, and where to eat in and around Castello.",
    },

    # ===================================================== FRANÇAIS =====
    "fr": {
        "title": "Que voir à Castello (Cagliari) : balade à pied — B&B Merì",
        "description": "Itinéraire à pied dans le quartier de Castello à Cagliari depuis le B&B Merì : cathédrale, Bastion de Saint-Remy, tours pisanes, musées, avec temps et cartes.",
        "og_description": "Une balade à pied parmi les plus beaux lieux de Castello, au départ de la porte du B&B Merì.",
        "crumb": "Que voir à Castello",
        "eyebrow": "Guide · Castello, Cagliari",
        "h1": "Que voir à Castello,<br>à pied depuis le B&amp;B",
        "intro": "Castello est le quartier fortifié que les Pisans ont bâti au XIIIe siècle sur la colline qui domine Cagliari. En sarde, on l'appelle <em>Casteddu</em>, le même nom que les Sardes donnent à toute la ville. Depuis notre porte, Via Alberto Lamarmora 18, tout se visite à pied : voici l'itinéraire que nous conseillons, avec les temps de marche depuis le B&amp;B.",
        "before_title": "Avant de partir",
        "before_text": "Castello est en pente et les rues sont pavées : prévoyez des chaussures confortables. En été, les bastions sont à leur meilleur tôt le matin et au coucher du soleil. Les horaires et les billets des églises, tours et musées changent souvent : vérifiez-les avant la visite.",
        "route_title": "La balade dans Castello, étape par étape",
        "route_intro": "Une boucle d'environ 2 km dans le quartier : tranquillement, avec quelques visites, comptez une demi-journée. Les temps indiqués sont à pied depuis le B&amp;B.",
        "beyond_title": "Juste à côté de Castello",
        "beyond_intro": "Une fois Castello visité, voici où aller : du quartier du port jusqu'à la plage.",
        "stops": {
            "cattedrale": ("Cathédrale Sainte-Marie", "2 min à pied",
                "La cathédrale de Cagliari, sur la Piazza Palazzo, remonte aux Pisans du XIIIe siècle ; sa façade de style roman pisan a été refaite au XXe siècle. À l'intérieur, ne manquez pas les deux chaires de Maître Guglielmo, tirées d'une chaire sculptée au XIIe siècle pour la cathédrale de Pise, ni la crypte des Martyrs, creusée dans la roche."),
            "palazzo": ("Palazzo Regio et Palazzo di Città", "2 min à pied",
                "Sur la même place se dressent le Palazzo Regio, ancienne résidence des vice-rois qui accueillit la cour de Savoie au début du XIXe siècle, et le Palazzo di Città, l'ancien hôtel de ville, qui accueille aujourd'hui des expositions des musées municipaux."),
            "san_pancrazio": ("Tour de San Pancrazio", "5 min à pied",
                "Construite par les Pisans en 1305 dans la partie la plus haute de Castello, c'est la jumelle de la Tour de l'Éléphant. Quand elle est ouverte, on peut monter au sommet : la vue s'étend sur la ville, le golfe et les étangs."),
            "cittadella": ("Cittadella dei Musei", "7 min à pied",
                "Sur la Piazza Arsenale, dans l'ancien arsenal, se trouvent le Musée archéologique national, avec les bronzes nuragiques et certaines statues des Géants de Mont'e Prama, et la Pinacothèque nationale. L'endroit idéal pour découvrir l'histoire de la Sardaigne."),
            "porta_cristina": ("Porta Cristina et Viale Buoncammino", "10 min à pied",
                "Depuis la Piazza Arsenale, on sort des remparts par la Porta Cristina, une porte néoclassique du XIXe siècle, pour rejoindre le Viale Buoncammino : une avenue arborée sur la crête, avec vue sur la ville et les étangs."),
            "santa_croce": ("Bastion de Santa Croce et l'ancien ghetto", "5 min à pied",
                "Sur le côté ouest des remparts, le Bastion de Santa Croce est une terrasse panoramique très appréciée au coucher du soleil. Juste à côté se trouvent l'ancien ghetto juif, aujourd'hui espace d'exposition, et la basilique Santa Croce, bâtie à l'emplacement de la synagogue."),
            "elefante": ("Tour de l'Éléphant", "4 min à pied",
                "Construite en 1307 par Giovanni Capula, l'architecte de la Tour de San Pancrazio, elle doit son nom à la petite statue d'éléphant en marbre de sa façade. C'était l'une des portes de Castello : en passant dessous, on descend vers la ville basse."),
            "saint_remy": ("Bastion de Saint-Remy", "3 min à pied",
                "Le symbole de Cagliari, construit entre la fin du XIXe et le début du XXe siècle et relié à la Piazza Costituzione par un grand escalier. Depuis la terrasse Umberto I, la vue embrasse les toits de Villanova et de la Marina, le port et le golfe des Anges."),
            "marina": ("Quartier de la Marina et Via Roma", "10 min à pied",
                "En descendant de Castello, on arrive à la Marina, le quartier entre les remparts et le port, avec ses ruelles pleines de trattorias et de boutiques. Sous les arcades de la Via Roma, on se promène face aux bateaux du port."),
            "anfiteatro": ("Amphithéâtre romain et jardin botanique", "15 min à pied",
                "L'amphithéâtre, du IIe siècle après J.-C., est en grande partie creusé dans la roche de la colline. À deux pas se trouve le jardin botanique de l'université, une oasis de verdure avec des plantes méditerranéennes et tropicales."),
            "poetto": ("Plage du Poetto et Sella del Diavolo", "15 min en bus ou en voiture",
                "Le Poetto est la plage de la ville : environ 8 km de sable clair, avec kiosques et établissements de plage. Côté Marina Piccola, le promontoire de la Sella del Diavolo offre des sentiers panoramiques avec de superbes vues sur le golfe."),
            "molentargius": ("Parc de Molentargius", "15 min en voiture",
                "Entre la ville et le Poetto, le parc naturel de Molentargius-Saline protège des étangs et d'anciens marais salants où vivent les flamants roses. On le découvre à pied ou à vélo."),
        },
        "buttons": {"open": "Ouvrir dans Google Maps", "route": "Itinéraire depuis le B&B"},
        "tips_title": "Conseils utiles",
        "tips": [
            ("🌅", "Coucher de soleil", "Le plus bel endroit est le Bastion de Santa Croce, avec le soleil qui se couche sur l'étang de Santa Gilla."),
            ("🛗", "Ascenseurs publics", "Depuis la ville basse, on monte à Castello avec les ascenseurs gratuits du Viale Regina Elena : où ils se trouvent et comment ils fonctionnent, c'est dans notre <a class=\"text-link\" href=\"{parking}#lifts\">guide du stationnement</a>."),
            ("☀️", "En été", "Aux heures les plus chaudes, privilégiez musées et églises ; les bastions sont à leur meilleur tôt le matin et au coucher du soleil. Remplissez votre gourde avant de sortir : l'eau du robinet du B&amp;B est potable."),
            ("🎉", "Sant'Efisio, 1er mai", "Le 1er mai, Cagliari fête saint Éphyse avec une longue procession de costumes traditionnels venus de toute la Sardaigne : si vous êtes en ville, ne la manquez pas."),
            ("💬", "Demandez-nous", f"Nous vous conseillons volontiers sur ce qu'il faut voir et où manger : écrivez-nous sur WhatsApp au {PHONE_INTL}."),
        ],
        "updated": "Guide mis à jour en novembre 2026. Horaires, ouvertures et billets peuvent changer : vérifiez-les sur les sites officiels avant votre visite.",
        "help_title": "Envie d'un conseil sur mesure ?",
        "help_text": "Écrivez-nous : nous vous suggérons quoi voir selon le temps dont vous disposez, et où manger à Castello et aux alentours.",
    },

    # ====================================================== ESPAÑOL =====
    "es": {
        "title": "Qué ver en Castello (Cagliari): paseo a pie — B&B Merì",
        "description": "Itinerario a pie por el barrio de Castello en Cagliari desde el B&B Merì: catedral, Bastión de Saint Remy, torres pisanas, museos y alrededores, con tiempos y mapas.",
        "og_description": "Un paseo a pie por los rincones más bonitos de Castello, saliendo de la puerta del B&B Merì.",
        "crumb": "Qué ver en Castello",
        "eyebrow": "Guía · Castello, Cagliari",
        "h1": "Qué ver en Castello,<br>a pie desde el B&amp;B",
        "intro": "Castello es el barrio fortificado que los pisanos construyeron en el siglo XIII sobre la colina que domina Cagliari. En sardo se llama <em>Casteddu</em>, el mismo nombre que los sardos dan a toda la ciudad. Desde nuestra puerta, en Via Alberto Lamarmora 18, todo se recorre a pie: este es el itinerario que recomendamos, con los tiempos a pie desde el B&amp;B.",
        "before_title": "Antes de salir",
        "before_text": "Castello está en cuesta y las calles son de piedra: mejor llevar calzado cómodo. En verano, los bastiones lucen más temprano por la mañana y al atardecer. Los horarios y las entradas de iglesias, torres y museos cambian a menudo: compruébalos antes de la visita.",
        "route_title": "El paseo por Castello, parada a parada",
        "route_intro": "Un recorrido circular de unos 2 km por el barrio: con calma y alguna visita, lleva media jornada. Los tiempos indicados son a pie desde el B&amp;B.",
        "beyond_title": "Justo fuera de Castello",
        "beyond_intro": "Cuando hayas visto Castello, aquí tienes adónde ir: del barrio del puerto a la playa.",
        "stops": {
            "cattedrale": ("Catedral de Santa María", "2 min a pie",
                "La catedral de Cagliari, en la Piazza Palazzo, tiene origen pisano del siglo XIII; su fachada de estilo románico pisano se rehízo en el siglo XX. Dentro destacan los dos púlpitos del Maestro Guglielmo, obtenidos de un púlpito tallado en el siglo XII para la catedral de Pisa, y la cripta de los Mártires, excavada en la roca."),
            "palazzo": ("Palazzo Regio y Palazzo di Città", "2 min a pie",
                "En la misma plaza se asoman el Palazzo Regio, antigua residencia de los virreyes que a principios del siglo XIX acogió a la corte de los Saboya, y el Palazzo di Città, el antiguo ayuntamiento, hoy sede de exposiciones de los museos municipales."),
            "san_pancrazio": ("Torre de San Pancrazio", "5 min a pie",
                "Construida por los pisanos en 1305 en la parte más alta de Castello, es la gemela de la Torre del Elefante. Cuando está abierta se puede subir a lo alto: la vista abarca la ciudad, el golfo y las lagunas."),
            "cittadella": ("Cittadella dei Musei", "7 min a pie",
                "En la Piazza Arsenale, en el antiguo arsenal, están el Museo Arqueológico Nacional, con los bronces nurágicos y algunas estatuas de los Gigantes de Mont'e Prama, y la Pinacoteca Nacional. Es el lugar perfecto para descubrir la historia de Cerdeña."),
            "porta_cristina": ("Porta Cristina y Viale Buoncammino", "10 min a pie",
                "Desde la Piazza Arsenale se sale de las murallas por la Porta Cristina, una puerta neoclásica del siglo XIX, y se llega al Viale Buoncammino: una avenida arbolada sobre la colina, con vistas a la ciudad y a las lagunas."),
            "santa_croce": ("Bastión de Santa Croce y el antiguo gueto", "5 min a pie",
                "En el lado oeste de las murallas, el Bastión de Santa Croce es una terraza panorámica muy querida al atardecer. Al lado están el antiguo gueto judío, hoy espacio de exposiciones, y la basílica de Santa Croce, construida donde estaba la sinagoga."),
            "elefante": ("Torre del Elefante", "4 min a pie",
                "Construida en 1307 por Giovanni Capula, el arquitecto de la Torre de San Pancrazio, debe su nombre a la pequeña estatua de un elefante de mármol de su fachada. Era una de las puertas de Castello: pasando por debajo se baja hacia la parte baja de la ciudad."),
            "saint_remy": ("Bastión de Saint Remy", "3 min a pie",
                "El símbolo de Cagliari, construido entre finales del siglo XIX y principios del XX y unido a la Piazza Costituzione por una gran escalinata. Desde la Terrazza Umberto I la vista abarca los tejados de Villanova y la Marina, el puerto y el golfo de los Ángeles."),
            "marina": ("Barrio de la Marina y Via Roma", "10 min a pie",
                "Bajando de Castello se llega a la Marina, el barrio entre las murallas y el puerto, con callejuelas llenas de trattorias y tiendas. Bajo los soportales de la Via Roma se pasea mirando los barcos del puerto."),
            "anfiteatro": ("Anfiteatro romano y Jardín Botánico", "15 min a pie",
                "El anfiteatro, del siglo II d. C., está excavado en gran parte en la roca de la colina. A pocos pasos está el Jardín Botánico de la Universidad, un oasis verde con plantas mediterráneas y tropicales."),
            "poetto": ("Playa del Poetto y Sella del Diavolo", "15 min en autobús o en coche",
                "El Poetto es la playa de la ciudad: unos 8 km de arena clara, con quioscos y establecimientos de playa. En el extremo de Marina Piccola, el promontorio de la Sella del Diavolo tiene senderos panorámicos con vistas espléndidas sobre el golfo."),
            "molentargius": ("Parque de Molentargius", "15 min en coche",
                "Entre la ciudad y el Poetto, el parque natural de Molentargius-Saline protege lagunas y antiguas salinas donde viven los flamencos rosas. Se recorre a pie o en bicicleta."),
        },
        "buttons": {"open": "Abrir en Google Maps", "route": "Ruta desde el B&B"},
        "tips_title": "Consejos útiles",
        "tips": [
            ("🌅", "El atardecer", "El mejor sitio es el Bastión de Santa Croce, con el sol poniéndose sobre la laguna de Santa Gilla."),
            ("🛗", "Ascensores públicos", "Desde la parte baja de la ciudad se sube a Castello con los ascensores gratuitos del Viale Regina Elena: dónde están y cómo funcionan lo tienes en nuestra <a class=\"text-link\" href=\"{parking}#lifts\">guía de aparcamiento</a>."),
            ("☀️", "En verano", "En las horas de más calor, elige museos e iglesias; los bastiones lucen más temprano por la mañana y al atardecer. Llena tu botella antes de salir: el agua del grifo del B&amp;B es potable."),
            ("🎉", "San Efisio, 1 de mayo", "El 1 de mayo Cagliari celebra a San Efisio con una larga procesión de trajes tradicionales de toda Cerdeña: si estás en la ciudad, no te la pierdas."),
            ("💬", "Pregúntanos", f"Te aconsejamos con gusto qué ver y dónde comer: escríbenos por WhatsApp al {PHONE_INTL}."),
        ],
        "updated": "Guía actualizada en noviembre de 2026. Horarios, aperturas y entradas pueden cambiar: compruébalos en las webs oficiales antes de la visita.",
        "help_title": "¿Quieres un consejo a medida?",
        "help_text": "Escríbenos: te sugerimos qué ver según el tiempo que tengas y dónde comer en Castello y alrededores.",
    },
}


# ------------------------------------------------ foto della camera --
#
# Le foto stanno in GALLERY (le carica chi gestisce il sito, anche dal sito di
# GitHub); l'ordine e' in ordine.txt nella stessa cartella. Lo script le mette
# direttamente nella pagina (cosi' le vedono anche Google Immagini e gli
# assistenti AI) e, se c'e' Pillow, ne crea versioni WebP piu' leggere in
# OPTIMIZED piu' la copertina per i social (1200x630).
#
# PHOTO_ALT: descrizione di ogni foto nelle 4 lingue (testo alternativo, letto
# da Google e dagli screen reader). Per una foto nuova non elencata qui si usa
# la nota scritta in ordine.txt dopo il "#" (in italiano), altrimenti una
# descrizione generica.

GALLERY = "assets/img/camera-matrimoniale"
OPTIMIZED = "assets/img/ottimizzate"
WIDTHS = (640, 1280)
IMAGE_RE = re.compile(r".+\.(jpe?g|png|webp|gif)$", re.I)

PHOTO_ALT = {
    "file_00000000fc3881f4b83c3b7bc0432fc9.jpg": {
        "it": "Camera Matrimoniale del B&B Merì: letto matrimoniale, soffitto con travi in legno, portafinestra e tavolino con due sedie",
        "en": "Double Room at B&B Merì: double bed, wooden-beamed ceiling, French window and a small table with two chairs",
        "fr": "Chambre double du B&B Merì : lit double, plafond à poutres en bois, porte-fenêtre et petite table avec deux chaises",
        "es": "Habitación doble del B&B Merì: cama de matrimonio, techo con vigas de madera, puerta balconera y mesita con dos sillas",
    },
    "IMG-20261007-WA0036.jpg": {
        "it": "Letto matrimoniale con due comodini e lampade, sotto un quadro artigianale in legno con una città sotto la luna",
        "en": "Double bed with two bedside tables and lamps, beneath a handmade wooden artwork of a town under the moon",
        "fr": "Lit double avec deux tables de chevet et lampes, sous un tableau artisanal en bois représentant une ville sous la lune",
        "es": "Cama de matrimonio con dos mesitas de noche y lámparas, bajo un cuadro artesanal de madera con una ciudad bajo la luna",
    },
    "file_00000000545881f489d19ce6cf378508.jpg": {
        "it": "Tavolino con due sedie, portafinestra con tende e angolo caffè con bollitore nella Camera Matrimoniale",
        "en": "Small table with two chairs, French window with curtains and a coffee corner with kettle in the Double Room",
        "fr": "Petite table avec deux chaises, porte-fenêtre avec rideaux et coin café avec bouilloire dans la chambre double",
        "es": "Mesita con dos sillas, puerta balconera con cortinas y rincón de café con hervidor en la habitación doble",
    },
    "IMG-20260818-WA0034.jpg": {
        "it": "Il letto matrimoniale visto di fronte, con copriletto verde salvia e cuscini bianchi",
        "en": "The double bed seen from the front, with a sage-green bedspread and white pillows",
        "fr": "Le lit double vu de face, avec couvre-lit vert sauge et oreillers blancs",
        "es": "La cama de matrimonio vista de frente, con colcha verde salvia y almohadas blancas",
    },
    "IMG-20261007-WA0035.jpg": {
        "it": "Porta antica in legno a due ante sotto un arco in mattoni a vista",
        "en": "Antique double wooden door beneath an exposed brick arch",
        "fr": "Porte ancienne en bois à deux battants sous un arc en briques apparentes",
        "es": "Puerta antigua de madera de dos hojas bajo un arco de ladrillo visto",
    },
    "IMG-20260620-WA0005.jpg": {
        "it": "Il quadro in legno sopra il letto illuminato di notte: una luna sopra un profilo di case",
        "en": "The wooden artwork above the bed lit up at night: a moon over a skyline of houses",
        "fr": "Le tableau en bois au-dessus du lit, éclairé la nuit : une lune au-dessus de silhouettes de maisons",
        "es": "El cuadro de madera sobre la cama iluminado de noche: una luna sobre un perfil de casas",
    },
    "IMG-20260620-WA0027.jpg": {
        "it": "Bagno privato con doccia, lavabo e soffitto in legno",
        "en": "Private bathroom with shower, washbasin and wooden ceiling",
        "fr": "Salle de bains privative avec douche, lavabo et plafond en bois",
        "es": "Baño privado con ducha, lavabo y techo de madera",
    },
    "file_00000000a1048246ab7bd8f2feb175b6.jpg": {
        "it": "Bagno privato con WC, bidet e asciugamani puliti",
        "en": "Private bathroom with toilet, bidet and fresh towels",
        "fr": "Salle de bains privative avec WC, bidet et serviettes propres",
        "es": "Baño privado con inodoro, bidé y toallas limpias",
    },
}


# ----------------------------------------------------------- utilita' --

def url_of(folder):
    """Indirizzo completo di una cartella del sito ('' = home italiana)."""
    return SITE + (folder + "/" if folder else "")


def rel(from_dir, to_dir):
    """Link relativo dalla cartella `from_dir` alla cartella `to_dir`."""
    r = posixpath.relpath(to_dir or ".", from_dir or ".")
    return "./" if r == "." else r + "/"


def checkin_attrs(lang, folder):
    """Attributi del link al check-in: modulo del sito se acceso, altrimenti Jotform."""
    if CHECKIN_FORM_LIVE:
        return f'href="{rel(folder, CHECKIN_DIR[lang])}"'
    return f'href="{CHECKIN_URL}" target="_blank" rel="noopener"'


def asset_prefix(folder):
    """Prefisso per css/js/immagini a partire da una cartella."""
    return "" if not folder else rel(folder, "")


def asset_version(rel_path):
    """Impronta del file: cambia quando il file cambia, cosi' i browser
    scaricano subito la versione nuova invece di usare quella in memoria."""
    return hashlib.sha1((ROOT / rel_path).read_bytes()).hexdigest()[:8]


def attr(text):
    return escape(text, quote=True)


def plain(html_text):
    """Testo senza tag, per i dati strutturati."""
    return unescape(re.sub(r"<[^>]+>", "", html_text))


def linkify(escaped_text):
    """Rende cliccabili gli indirizzi https:// in un testo gia' escapato."""
    return re.sub(r"https://[^\s<]+[^\s<.,;:]",
                  lambda m: f'<a href="{m.group(0)}">{m.group(0)}</a>', escaped_text)


def json_ld(data):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def maps_search(query):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(query)


def maps_embed(query):
    return "https://www.google.com/maps?q=" + quote_plus(query) + "&z=16&output=embed"


def maps_walk(origin):
    return ("https://www.google.com/maps/dir/?api=1&origin=" + quote_plus(origin)
            + "&destination=" + quote_plus(DEST) + "&travelmode=walking")


def maps_from_bnb(destination, mode="walking"):
    """Percorso su Google Maps dal B&B a un luogo (a piedi, in bus o in auto)."""
    return ("https://www.google.com/maps/dir/?api=1&origin=" + quote_plus(DEST)
            + "&destination=" + quote_plus(destination) + "&travelmode=" + mode)


def today():
    return datetime.datetime.now(TZ).date().isoformat()


# ------------------------------------------------- foto: dimensioni --

SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def jpeg_orientation(data):
    """Orientamento EXIF di una foto JPEG (1 = dritta; 5-8 = ruotata di 90 gradi)."""
    i = data.find(b"Exif\x00\x00")
    if i < 0 or i > 65536:
        return 1
    tiff = data[i + 6:]
    big = tiff[:2] == b"MM"
    order = "big" if big else "little"
    try:
        ifd = int.from_bytes(tiff[4:8], order)
        count = int.from_bytes(tiff[ifd:ifd + 2], order)
        for k in range(count):
            entry = tiff[ifd + 2 + 12 * k: ifd + 14 + 12 * k]
            if int.from_bytes(entry[0:2], order) == 0x0112:
                return int.from_bytes(entry[8:10], order)
    except (ValueError, IndexError):
        pass
    return 1


def image_size(path):
    """(larghezza, altezza) di una foto JPEG/PNG/GIF/WebP come la mostra il
    browser, senza librerie esterne. None se il formato non e' riconosciuto."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", data[6:10])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X":
            return (int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            b = data[21:25]
            return (1 + (((b[1] & 0x3F) << 8) | b[0]),
                    1 + (((b[3] & 0x0F) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6)))
        return None
    if data[:2] == b"\xff\xd8":
        i, n = 2, len(data)
        while i + 9 < n:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker == 0xFF:
                i += 1
                continue
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            if marker in SOF_MARKERS:
                h = int.from_bytes(data[i + 5:i + 7], "big")
                w = int.from_bytes(data[i + 7:i + 9], "big")
                return (h, w) if jpeg_orientation(data) >= 5 else (w, h)
            i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    return None


def natural_key(name):
    """Ordine "naturale": foto2 prima di foto10, maiuscole indifferenti."""
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", name.lower())]


# ------------------------------------------------- foto: galleria --

def gallery_photos():
    """Foto della camera nell'ordine di ordine.txt (quelle non elencate in fondo).

    Ogni foto: nome del file, percorso nel sito, dimensioni, impronta del
    contenuto e la nota scritta in ordine.txt dopo il "#"."""
    folder = ROOT / GALLERY
    if not folder.is_dir():
        return []
    wanted, notes = [], {}
    order_file = folder / "ordine.txt"
    if order_file.exists():
        for line in order_file.read_text(encoding="utf-8").splitlines():
            name, _, note = line.partition("#")
            name = name.strip().lower()
            if name:
                wanted.append(name)
                notes[name] = note.strip()
    photos = []
    for path in folder.iterdir():
        if not (path.is_file() and IMAGE_RE.match(path.name)):
            continue
        size = image_size(path)
        if not size:
            print("attenzione: formato non riconosciuto, foto saltata:", path.name)
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
        photos.append({
            "name": path.name,
            "path": path,
            "rel": f"{GALLERY}/{path.name}",
            "w": size[0],
            "h": size[1],
            "sha": hashlib.sha1(path.read_bytes()).hexdigest(),
            "slug": f"{Path(GALLERY).name}-{slug}",
            "note": notes.get(path.name.lower(), ""),
            "variants": [],
        })

    def rank(ph):
        n = ph["name"].lower()
        return (wanted.index(n) if n in wanted else len(wanted), natural_key(ph["name"]))

    return sorted(photos, key=rank)


def pillow():
    """Il modulo Image di Pillow, oppure None se Pillow non e' installato."""
    try:
        from PIL import Image, ImageOps   # noqa: F401
        return Image
    except ImportError:
        return None


def optimize_photos(photos):
    """Crea (se mancano) le versioni WebP delle foto in OPTIMIZED, piu' la
    copertina per i social, e cancella quelle che non servono piu'.
    Restituisce la copertina: {"rel", "w", "h", "photo"}."""
    Image = pillow()
    if Image:
        from PIL import ImageOps
    keep = set()

    for ph in photos:
        widths = sorted({min(w, ph["w"]) for w in WIDTHS})
        for w in widths:
            rel_path = f"{OPTIMIZED}/{ph['slug']}-{ph['sha'][:6]}-{w}.webp"
            keep.add(rel_path)
            out = ROOT / rel_path
            if not out.exists() and Image:
                out.parent.mkdir(parents=True, exist_ok=True)
                with Image.open(ph["path"]) as im:
                    im = ImageOps.exif_transpose(im).convert("RGB")
                    h = round(im.height * w / im.width)
                    im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=78, method=6)
                print("creata", rel_path)
            if out.exists():
                ph["variants"].append((rel_path, w))

    cover = None
    if photos:
        # La prima foto orizzontale nell'ordine scelto in ordine.txt
        ph = next((p for p in photos if p["w"] > p["h"]), photos[0])
        rel_path = f"{OPTIMIZED}/copertina-{ph['sha'][:6]}.jpg"
        keep.add(rel_path)
        out = ROOT / rel_path
        if not out.exists() and Image:
            out.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(ph["path"]) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im = ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.55))
                im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
            print("creata", rel_path)
        if out.exists():
            cover = {"rel": rel_path, "w": 1200, "h": 630, "photo": ph}
        else:
            cover = {"rel": ph["rel"], "w": ph["w"], "h": ph["h"], "photo": ph}

    folder = ROOT / OPTIMIZED
    if folder.is_dir():
        for f in folder.iterdir():
            if f.is_file() and f"{OPTIMIZED}/{f.name}" not in keep:
                f.unlink()
                print("cancellata", f"{OPTIMIZED}/{f.name}")
    return cover


def photo_alt(ph, lang, index):
    """Testo alternativo di una foto nella lingua scelta."""
    alts = PHOTO_ALT.get(ph["name"], {})
    if alts.get(lang):
        return alts[lang]
    room = T[lang]["room1"]["name"]
    if lang == "it" and ph["note"]:
        return f"{room} del B&B Merì — {ph['note']}"
    return f"{room} — B&B Merì, Cagliari ({T[lang]['photo_word']} {index + 1})"


def abs_url(rel_path):
    return SITE + quote(rel_path)


# ------------------------------------------------- dati strutturati --
#
# Un unico "grafo" schema.org per pagina: la struttura (BedAndBreakfast), il
# sito (WebSite), la pagina (WebPage) e cio' che contiene (FAQ, parcheggi,
# itinerario). Gli @id collegano le parti tra loro e tra le pagine.

BNB_ID = SITE + "#bnb"
WEBSITE_ID = SITE + "#website"
LASTMOD_TOKEN = "@@LASTMOD@@"   # sostituito con la data di ultima modifica


def graph(*nodes):
    return json_ld({"@context": "https://schema.org", "@graph": [n for n in nodes if n]})


def postal_address(lang):
    return {
        "@type": "PostalAddress",
        "streetAddress": STREET,
        "addressLocality": "Cagliari",
        "addressRegion": T[lang]["region"],
        "postalCode": "09124",
        "addressCountry": "IT",
    }


def bnb_entity(lang, photos, full=True):
    """La struttura. `full=False`: versione breve per le pagine secondarie."""
    t = T[lang]

    def feature(name):
        return {"@type": "LocationFeatureSpecification", "name": name, "value": True}

    bnb = {
        "@type": "BedAndBreakfast",
        "@id": BNB_ID,
        "name": "B&B Merì",
        "url": url_of(HOME_DIR[lang]),
        "telephone": PHONE_INTL,
        "email": EMAIL,
        "address": postal_address(lang),
    }
    if photos:
        bnb["image"] = [abs_url(ph["rel"]) for ph in photos]
    if not full:
        return bnb
    rooms = []
    for i, (name, desc, feats) in enumerate(t["ld_rooms"]):
        room = {
            "@type": "HotelRoom",
            "name": name,
            "description": desc,
            "bed": {"@type": "BedDetails", "numberOfBeds": 1, "typeOfBed": t["ld_bed"]},
            "occupancy": {"@type": "QuantitativeValue", "maxValue": 2, "unitCode": "C62"},
            "amenityFeature": [feature(n) for n in feats],
        }
        if i == 0 and photos:
            room["image"] = [abs_url(ph["rel"]) for ph in photos]
        rooms.append(room)
    bnb.update({
        "alternateName": ["B&B Meri", "Merì Bed & Breakfast", "Merì B&B Cagliari"],
        "description": t["ld_description"],
        "logo": SITE + "assets/img/logo-512.png",
        "priceRange": "€€",
        "currenciesAccepted": "EUR",
        "checkinTime": "15:00",
        "checkoutTime": "10:30",
        "numberOfRooms": len(rooms),
        "petsAllowed": False,
        "smokingAllowed": False,
        "availableLanguage": ["Italian", "English", "French", "Spanish"],
        "identifier": {"@type": "PropertyValue", "propertyID": "CIN", "value": CIN},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "hasMap": MAPS_URL,
        "containedInPlace": {"@type": "Place", "name": "Castello, Cagliari",
                             "containedInPlace": {"@type": "City", "name": "Cagliari"}},
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "reservations",
            "telephone": PHONE_INTL,
            "email": EMAIL,
            "availableLanguage": ["Italian", "English", "French", "Spanish"],
        },
        "amenityFeature": [feature(n) for n in t["ld_amenities"]],
        "containsPlace": rooms,
    })
    if SAME_AS:
        bnb["sameAs"] = list(SAME_AS)
    return bnb


def website_entity():
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": SITE,
        "name": "B&B Merì",
        "alternateName": ["Merì Bed & Breakfast", "meribnb.it"],
        "inLanguage": LANGS,
        "publisher": {"@id": BNB_ID},
    }


def webpage_entity(lang, folder, title, description, cover_url=None, crumbs=False, about=None):
    url = url_of(folder)
    page = {
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": title,
        "description": description,
        "inLanguage": lang,
        "isPartOf": {"@id": WEBSITE_ID},
        "about": about or {"@id": BNB_ID},
        "dateModified": LASTMOD_TOKEN,
    }
    if cover_url:
        page["primaryImageOfPage"] = {"@type": "ImageObject", "url": cover_url}
    if crumbs:
        page["breadcrumb"] = {"@id": url + "#breadcrumb"}
    return page


def breadcrumb_entity(lang, folder, name):
    url = url_of(folder)
    return {
        "@type": "BreadcrumbList",
        "@id": url + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": T[lang]["home_crumb"], "item": url_of(HOME_DIR[lang])},
            {"@type": "ListItem", "position": 2, "name": name, "item": url},
        ],
    }


def home_structured_data(lang, photos, cover_url):
    t = T[lang]
    folder = HOME_DIR[lang]
    faq = {
        "@type": "FAQPage",
        "@id": url_of(folder) + "#faq",
        "inLanguage": lang,
        "isPartOf": {"@id": WEBSITE_ID},
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in t["faq"]
        ],
    }
    return [("BedAndBreakfast, WebSite, WebPage, FAQ", graph(
        bnb_entity(lang, photos),
        website_entity(),
        webpage_entity(lang, folder, t["title"], t["description"], cover_url),
        faq,
    ))]


def parking_structured_data(lang, pt, photos):
    folder = PARK_DIR[lang]
    page = webpage_entity(lang, folder, pt["title"], pt["description"], crumbs=True)
    page["mainEntity"] = {
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "ParkingFacility",
                    "name": pt["spots"][key][0],
                    "description": plain(pt["spots"][key][3]),
                    "address": {"@type": "PostalAddress", "streetAddress": SPOTS[key]["street"],
                                "addressLocality": "Cagliari", "addressCountry": "IT"},
                },
            }
            for i, key in enumerate(FACILITIES)
        ],
    }
    return [("WebPage, BreadcrumbList, ParkingFacility", graph(
        page,
        breadcrumb_entity(lang, folder, plain(pt["h1"].replace("<br>", " "))),
        bnb_entity(lang, photos, full=False),
        website_entity(),
    ))]


def guide_structured_data(lang, gt, photos, cover_url):
    folder = GUIDE_DIR[lang]
    url = url_of(folder)
    castello = {"@type": "Place", "name": "Castello, Cagliari",
                "address": {"@type": "PostalAddress", "addressLocality": "Cagliari", "addressCountry": "IT"}}
    page = webpage_entity(lang, folder, gt["title"], gt["description"], cover_url, crumbs=True, about=castello)
    article = {
        "@type": "Article",
        "@id": url + "#article",
        "headline": plain(gt["h1"].replace("<br>", " ")),
        "description": gt["description"],
        "inLanguage": lang,
        "datePublished": GUIDE_PUBLISHED,
        "dateModified": LASTMOD_TOKEN,
        "author": {"@type": "Organization", "name": "B&B Merì", "url": SITE},
        "publisher": {"@id": BNB_ID},
        "mainEntityOfPage": {"@id": url + "#webpage"},
        "about": {"@id": url + "#itinerary"},
    }
    if cover_url:
        article["image"] = cover_url
    trip = {
        "@type": "TouristTrip",
        "@id": url + "#itinerary",
        "name": plain(gt["route_title"]),
        "description": plain(gt["route_intro"]),
        "provider": {"@id": BNB_ID},
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "TouristAttraction",
                        "name": gt["stops"][key][0],
                        "description": plain(gt["stops"][key][2]),
                        "address": {"@type": "PostalAddress", "addressLocality": "Cagliari", "addressCountry": "IT"},
                    },
                }
                for i, key in enumerate(STOPS)
            ],
        },
    }
    return [("WebPage, BreadcrumbList, Article, TouristTrip", graph(
        page,
        breadcrumb_entity(lang, folder, gt["crumb"]),
        article,
        trip,
        bnb_entity(lang, photos, full=False),
        website_entity(),
    ))]


# ------------------------------------------------- parti in comune --

ROBOTS_INDEX = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"


def head(lang, folder, alt_dirs, title, description, og_description, ld_blocks, cover,
         robots=ROBOTS_INDEX, og_type="website"):
    """Inizio della pagina: titolo, descrizione, lingue, anteprima social,
    icone e dati strutturati. `cover` e' l'immagine per i social."""
    p = asset_prefix(folder)
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{l}" href="{url_of(alt_dirs[l])}">' for l in LANGS)
    verify = ""
    if GOOGLE_SITE_VERIFICATION:
        verify += f'\n  <meta name="google-site-verification" content="{attr(GOOGLE_SITE_VERIFICATION)}">'
    if BING_SITE_VERIFICATION:
        verify += f'\n  <meta name="msvalidate.01" content="{attr(BING_SITE_VERIFICATION)}">'
    og_alternates = "".join(
        f'\n  <meta property="og:locale:alternate" content="{T[l]["og_locale"]}">' for l in LANGS if l != lang)
    if cover:
        image = f"""
  <meta property="og:image" content="{abs_url(cover["rel"])}">
  <meta property="og:image:width" content="{cover["w"]}">
  <meta property="og:image:height" content="{cover["h"]}">
  <meta property="og:image:alt" content="{attr(photo_alt(cover["photo"], lang, 0))}">"""
    else:
        image = f'\n  <meta property="og:image" content="{SITE}assets/img/og-cover.svg">'
    ld = "\n\n".join(
        f"""  <!-- Dati strutturati: {name} -->
  <script type="application/ld+json">
{data}
  </script>""" for name, data in ld_blocks)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Pagina generata da tools/build_pages.py: modifica i testi li', non qui. -->
  <title>{escape(title)}</title>
  <meta name="description" content="{attr(description)}">
  <meta name="robots" content="{robots}">{verify}
  <link rel="canonical" href="{url_of(folder)}">
{alternates}
  <link rel="alternate" hreflang="x-default" href="{url_of(alt_dirs["it"])}">

  <!-- Anteprima sui social e nelle chat (Open Graph) -->
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{attr(title)}">
  <meta property="og:description" content="{attr(og_description)}">
  <meta property="og:url" content="{url_of(folder)}">{image}
  <meta property="og:locale" content="{T[lang]["og_locale"]}">{og_alternates}
  <meta property="og:site_name" content="B&amp;B Merì">
  <meta name="twitter:card" content="summary_large_image">

  <meta name="theme-color" content="#f7f2ea">
  <link rel="icon" href="{p}favicon.ico" sizes="32x32">
  <link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
  <link rel="manifest" href="{p}site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}css/style.css?v={asset_version("css/style.css")}">

{ld}
</head>
<body>
"""


def page_href(lang, folder, page, target):
    """Link dal menu verso un'altra pagina (o "#top" se e' la pagina stessa)."""
    if page == target:
        return '"#top" aria-current="page"'
    return f'"{rel(folder, PAGE_DIRS[target][lang])}"'


def site_header(lang, folder, page):
    """Intestazione con menu. `page`: "home", "parking", "guide" o "checkin"."""
    t = T[lang]
    ids, nav = t["ids"], t["nav"]
    p = asset_prefix(folder)
    home = "" if page == "home" else rel(folder, HOME_DIR[lang])
    dirs = PAGE_DIRS[page]
    lang_switch = "".join(
        f'<a href="{rel(folder, dirs[l])}" hreflang="{l}" lang="{l}"'
        + (' aria-current="page"' if l == lang else "")
        + f'>{l.upper()}</a>'
        for l in LANGS)
    return f"""
<header class="site-header" id="top">
  <div class="container header-inner">
    <a href="{home or '#top'}" class="logo" aria-label="B&amp;B Merì — home">
      <img class="logo-mark" src="{p}assets/img/logo-mark.svg" alt="" width="46" height="46">
      <span class="logo-text">Merì <em>Bed &amp; Breakfast · Cagliari</em></span>
    </a>
    <nav class="main-nav" aria-label="{attr(t["nav_label"])}">
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="{attr(t["menu_open"])}">
        <span></span><span></span><span></span>
      </button>
      <ul id="nav-menu" class="nav-menu">
        <li><a href="{home}#{ids["rooms"]}">{nav["rooms"]}</a></li>
        <li><a href="{home}#{ids["amenities"]}">{nav["amenities"]}</a></li>
        <li><a href="{home}#{ids["arrival"]}">{nav["arrival"]}</a></li>
        <li><a href={page_href(lang, folder, page, "parking")}>{nav["parking"]}</a></li>
        <li><a href={page_href(lang, folder, page, "guide")}>{nav["guide"]}</a></li>
        <li><a href="{home}#{ids["faq"]}">{nav["faq"]}</a></li>
        <li><a href="{home}#{ids["contact"]}" class="nav-cta">{nav["book"]}</a></li>
        <li class="lang-switch">{lang_switch}</li>
      </ul>
    </nav>
  </div>
</header>
"""


def site_footer(lang, folder, page):
    t = T[lang]
    ids, nav = t["ids"], t["nav"]
    p = asset_prefix(folder)
    home = "" if page == "home" else rel(folder, HOME_DIR[lang])
    dirs = PAGE_DIRS[page]
    whatsapp = f"https://wa.me/{WHATSAPP}?text={quote(t['whatsapp_text'])}"
    other_langs = "\n      ".join(
        f'<a href="{rel(folder, dirs[l])}" hreflang="{l}" lang="{l}">{T[l]["lang_name"]}</a>'
        for l in LANGS if l != lang)
    return f"""
<footer class="site-footer">
  <div class="container footer-inner">
    <div>
      <p class="footer-logo"><img src="{p}assets/img/logo-mark.svg" alt="" width="34" height="34"> B&amp;B Merì</p>
      <p>{t["address_line"]}</p>
      <p><a href="tel:{TEL}">{PHONE_INTL}</a> · <a href="{attr(whatsapp)}" target="_blank" rel="noopener">WhatsApp</a></p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="footer-cin">CIN: {CIN}</p>
    </div>
    <nav aria-label="{attr(t["footer_label"])}">
      <a href="{home}#{ids["rooms"]}">{nav["rooms"]}</a>
      <a href="{home}#{ids["amenities"]}">{nav["amenities"]}</a>
      <a href="{home}#{ids["location"]}">{nav["location"]}</a>
      <a href="{home}#{ids["arrival"]}">{nav["arrival"]}</a>
      <a href={page_href(lang, folder, page, "parking")}>{nav["parking"]}</a>
      <a href={page_href(lang, folder, page, "guide")}>{nav["guide"]}</a>
      <a href="{home}#{ids["faq"]}">{nav["faq"]}</a>
      <a {checkin_attrs(lang, folder)}>{t["checkin_title"]}</a>
      {other_langs}
    </nav>
  </div>
  <div class="container footer-legal">
    <p>© 2026 B&amp;B Merì · {t["rights"]}</p>
  </div>
</footer>

<script src="{p}js/main.js?v={asset_version("js/main.js")}" defer></script>
</body>
</html>
"""


# --------------------------------------------------------- home page --

def gallery_html(lang, folder, photos):
    """Galleria della Camera Matrimoniale: tutte le foto sono nella pagina
    (Google e gli assistenti AI le vedono), il JavaScript le fa scorrere."""
    t = T[lang]
    p = asset_prefix(folder)
    if not photos:
        return (f'          <figure class="room-media">\n'
                f'            <img src="{p}assets/img/room-castello.svg" alt="{attr(t["room1"]["alt"])}" width="800" height="600" loading="lazy">\n'
                f'          </figure>')
    slides = []
    for i, ph in enumerate(photos):
        srcset = ", ".join(f"{p}{rel_path} {w}w" for rel_path, w in ph["variants"])
        source = (f'<source type="image/webp" srcset="{srcset}" sizes="(max-width: 900px) 100vw, 520px">'
                  if srcset else "")
        hidden = "" if i == 0 else " hidden"
        slides.append(
            f'            <picture class="gallery-slide"{hidden}>{source}'
            f'<img src="{p}{quote(ph["rel"])}" alt="{attr(photo_alt(ph, lang, i))}" '
            f'width="{ph["w"]}" height="{ph["h"]}" loading="lazy" decoding="async"></picture>')
    slides = "\n".join(slides)
    return (f'          <figure class="room-media room-gallery" data-gallery aria-label="{attr(t["gallery_label"])}">\n'
            f'{slides}\n'
            f'          </figure>')


def render_home(lang, photos, cover):
    t = T[lang]
    folder = HOME_DIR[lang]
    p = asset_prefix(folder)
    ids = t["ids"]
    r1, r2 = t["room1"], t["room2"]
    parking_href = rel(folder, PARK_DIR[lang])
    guide_href = rel(folder, GUIDE_DIR[lang])
    cover_url = abs_url(cover["rel"]) if cover else None
    facts = "\n".join(
        f"        <div><dt>{escape(label, quote=False)}</dt><dd>{escape(value, quote=False)}</dd></div>"
        for label, value in t["facts"])

    badges = "\n".join(f"        <li>✓ {b}</li>" for b in t["badges"])
    intro = "\n".join(f"      <p>{para}</p>" for para in t["intro_p"])
    r1_amen = "\n".join(f"              <li>{a}</li>" for a in r1["amenities"])
    r2_amen = "\n".join(f"              <li>{a}</li>" for a in r2["amenities"])
    amenities = "\n".join(
        f'        <li><span class="amenity-icon">{icon}</span><strong>{title}</strong><span>{text}</span></li>'
        for icon, title, text in t["amenities"])
    distances = "\n".join(
        f"          <li><strong>{place}</strong><span>{time}</span></li>"
        for place, time in t["distances"])
    arrival_items = [(icon, title, text.replace("{parking}", parking_href))
                     for icon, title, text in t["arrival"]]
    arrival = "\n".join(
        f"""        <li>
          <span class="arrival-icon">{icon}</span>
          <div>
            <strong class="arrival-title">{title}</strong>
            {text}
          </div>
        </li>""" for icon, title, text in arrival_items)
    faq = "\n".join(
        f"""      <details class="faq-item">
        <summary>{escape(q)}</summary>
        <p>{linkify(escape(a))}</p>
      </details>""" for q, a in t["faq"])

    whatsapp = f"https://wa.me/{WHATSAPP}?text={quote(t['whatsapp_text'])}"
    mailto = f"mailto:{EMAIL}?subject={quote(t['mail_subject'])}"

    return head(lang, folder, HOME_DIR, t["title"], t["description"], t["og_description"],
                home_structured_data(lang, photos, cover_url), cover) \
        + site_header(lang, folder, "home") + f"""
<main>

  <!-- HERO -->
  <section class="hero">
    <div class="container hero-inner">
      <h1><span class="hero-eyebrow">{t["hero_eyebrow"]}</span> {t["h1"]}</h1>
      <a class="checkin-cta" {checkin_attrs(lang, folder)}>
        <span class="checkin-icon" aria-hidden="true">🗝️</span>
        <span class="checkin-text">
          <strong>{t["checkin_title"]}</strong>
          <small>{t["checkin_sub"]}</small>
        </span>
        <span class="checkin-arrow" aria-hidden="true">→</span>
      </a>
      <p class="hero-sub">{t["hero_sub"]}</p>
      <div class="hero-actions">
        <a href="#{ids["contact"]}" class="btn btn-primary">{t["cta_primary"]}</a>
        <a href="#{ids["rooms"]}" class="btn btn-ghost">{t["cta_secondary"]}</a>
      </div>
      <ul class="hero-badges" aria-label="{attr(t["highlights_label"])}">
{badges}
      </ul>
    </div>
    <figure class="hero-media" aria-hidden="true">
      <img src="{p}assets/img/hero.svg" alt="" width="1600" height="900" loading="eager">
    </figure>
  </section>

  <!-- INTRO -->
  <section class="intro section">
    <div class="container narrow">
      <p class="eyebrow">{t["intro_eyebrow"]}</p>
      <h2>{t["intro_h2"]}</h2>
{intro}
      <h3 class="facts-title">{t["facts_title"]}</h3>
      <dl class="facts-grid">
{facts}
      </dl>
    </div>
  </section>

  <!-- CAMERE -->
  <section id="{ids["rooms"]}" class="rooms section section-alt">
    <div class="container">
      <p class="eyebrow">{t["rooms_eyebrow"]}</p>
      <h2>{t["rooms_h2"]}</h2>
      <div class="rooms-grid">

        <article class="room-card">
{gallery_html(lang, folder, photos)}
          <div class="room-body">
            <h3>{r1["name"]}</h3>
            <p class="room-tagline">{r1["tagline"]}</p>
            <p>{r1["text"]}</p>
            <ul class="room-amenities">
{r1_amen}
            </ul>
            <a href="#{ids["contact"]}" class="btn btn-outline">{r1["button"]}</a>
          </div>
        </article>

        <article class="room-card room-card--full">
          <figure class="room-media">
            <img src="{p}assets/img/room-unavailable.svg" alt="{attr(r2["alt"])}" width="800" height="600" loading="lazy">
            <span class="room-badge">{r2["badge"]}</span>
          </figure>
          <div class="room-body">
            <h3>{r2["name"]}</h3>
            <p class="room-tagline">{r2["tagline"]}</p>
            <p>{r2["text"]}</p>
            <ul class="room-amenities">
{r2_amen}
            </ul>
            <p class="room-unavailable">{r2["unavailable"]}</p>
          </div>
        </article>

      </div>
    </div>
  </section>

  <!-- SERVIZI -->
  <section id="{ids["amenities"]}" class="amenities section">
    <div class="container">
      <p class="eyebrow">{t["amen_eyebrow"]}</p>
      <h2>{t["amen_h2"]}</h2>
      <ul class="amenities-grid">
{amenities}
      </ul>
    </div>
  </section>

  <!-- POSIZIONE -->
  <section id="{ids["location"]}" class="location section section-alt">
    <div class="container location-grid">
      <div>
        <p class="eyebrow">{t["loc_eyebrow"]}</p>
        <h2>{t["loc_h2"]}</h2>
        <p>{t["loc_p"]}</p>
        <ul class="distances">
{distances}
        </ul>
        <p class="guide-link"><a class="text-link" href="{guide_href}">{t["guide_link"]}</a></p>
        <a class="btn btn-primary" href="{MAPS_URL}" target="_blank" rel="noopener">{t["maps_button"]}</a>
      </div>
      <figure class="location-media" aria-hidden="true">
        <img src="{p}assets/img/map.svg" alt="" width="800" height="800" loading="lazy">
      </figure>
    </div>
  </section>

  <!-- COME ARRIVARE -->
  <section id="{ids["arrival"]}" class="arrival section">
    <div class="container narrow">
      <p class="eyebrow">{t["arr_eyebrow"]}</p>
      <h2>{t["arr_h2"]}</h2>
      <p>{t["arr_intro"]}</p>
      <ul class="arrival-list">
{arrival}
      </ul>
      <p class="arrival-note">{t["arr_note"]}</p>
    </div>
  </section>

  <!-- FAQ -->
  <section id="{ids["faq"]}" class="faq section section-alt">
    <div class="container narrow">
      <p class="eyebrow">{t["faq_eyebrow"]}</p>
      <h2>{t["faq_h2"]}</h2>

{faq}
    </div>
  </section>

  <!-- CONTATTI -->
  <section id="{ids["contact"]}" class="contact section section-dark">
    <div class="container narrow center">
      <p class="eyebrow">{t["contact_eyebrow"]}</p>
      <h2>{t["contact_h2"]}</h2>
      <p class="discount-pill">{t["discount"]}</p>
      <p>{t["contact_p"]}</p>
      <div class="contact-actions">
        <a class="btn btn-primary btn-lg" href="tel:{TEL}">📞 {t["phone_label"]}</a>
        <a class="btn btn-ghost btn-lg" href="{attr(whatsapp)}" target="_blank" rel="noopener">💬 WhatsApp</a>
        <a class="btn btn-ghost btn-lg" href="{attr(mailto)}">✉️ {EMAIL}</a>
      </div>
      <p class="contact-note">{t["address_line"]}</p>
    </div>
  </section>

</main>
""" + site_footer(lang, folder, "home")


# ------------------------------------------------- pagina parcheggi --

def render_parking(lang, photos, cover):
    t, pt = T[lang], P[lang]
    folder = PARK_DIR[lang]
    home = rel(folder, HOME_DIR[lang])
    btn = pt["buttons"]
    first = "buoncammino"
    whatsapp = f"https://wa.me/{WHATSAPP}?text={quote(t['whatsapp_text'])}"

    quick = "\n".join(
        f"""        <li><a class="quick-pick" href="#spot-{key}" data-spot="{key}">
          <span class="quick-icon" aria-hidden="true">{icon}</span>
          <strong>{title}</strong>
          <span>{text}</span>
        </a></li>""" for icon, title, text, key in pt["quick"])

    def card(key):
        name, badge, facts, text = pt["spots"][key]
        s = SPOTS[key]
        facts_html = "\n".join(
            f"              <div><dt>{label}</dt><dd>{value}</dd></div>" for label, value in facts)
        actions = ""
        if s["map"]:
            actions = f"""
            <div class="park-actions">
              <button type="button" class="btn btn-outline btn-sm" data-map-src="{attr(maps_embed(s["map"]))}" data-map-name="{attr(name)}">📍 {btn["show"]}</button>
              <a class="btn btn-ghost btn-sm" href="{attr(maps_search(s["map"]))}" target="_blank" rel="noopener">🗺️ {btn["open"]}</a>
              <a class="btn btn-primary btn-sm" href="{attr(maps_walk(s["from"]))}" target="_blank" rel="noopener">🚶 {btn["walk"]}</a>
            </div>"""
        return f"""          <article class="park-card park-card--{s["tab"]}" id="spot-{key}">
            <div class="park-head">
              <h3>{name}</h3>
              <span class="park-badge">{badge}</span>
            </div>
            <dl class="park-facts">
{facts_html}
            </dl>
            <p>{text}</p>{actions}
          </article>"""

    def panel(tab):
        if tab == "tips":
            body = "\n".join(
                f"""          <li><span class="tip-icon" aria-hidden="true">{icon}</span><div><strong>{title}</strong><p>{text}</p></div></li>"""
                for icon, title, text in pt["tips"])
            body = f'          <ul class="tip-list">\n{body}\n          </ul>'
        else:
            body = "\n".join(card(k) for k, s in SPOTS.items() if s["tab"] == tab)
        return f"""        <div class="tab-panel" id="{tab}" role="tabpanel" aria-labelledby="tab-{tab}">
          <h2 class="panel-title">{pt["tabs"][tab]}</h2>
          <p class="tab-intro">{pt["tab_intro"][tab]}</p>
{body}
        </div>"""

    tabs = "\n".join(
        f'        <button type="button" role="tab" id="tab-{tab}" aria-controls="{tab}" aria-selected="{"true" if i == 0 else "false"}">{pt["tabs"][tab]}</button>'
        for i, tab in enumerate(TABS))
    panels = "\n".join(panel(tab) for tab in TABS)
    sources = " · ".join(
        f'<a href="{attr(url)}" target="_blank" rel="noopener">{escape(label)}</a>' for label, url in SOURCES)

    return head(lang, folder, PARK_DIR, pt["title"], pt["description"], pt["og_description"],
                parking_structured_data(lang, pt, photos), cover) \
        + site_header(lang, folder, "parking") + f"""
<main class="parking-page">

  <section class="page-hero">
    <div class="container narrow">
      <a class="back-link" href="{home}">← {pt["back"]}</a>
      <p class="hero-eyebrow">{pt["eyebrow"]}</p>
      <h1>{pt["h1"]}</h1>
      <p class="hero-sub">{pt["intro"]}</p>
      <div class="satnav-tip">
        <span class="satnav-icon" aria-hidden="true">🧭</span>
        <div>
          <strong>{pt["satnav_title"]}</strong>
          <p>{pt["satnav_text"]}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section quick-section">
    <div class="container">
      <h2>{pt["quick_title"]}</h2>
      <ul class="quick-picks">
{quick}
      </ul>
    </div>
  </section>

  <section class="section section-alt parking-guide">
    <div class="container">
      <div class="tabs" role="tablist" aria-label="{attr(pt["tabs_label"])}" hidden>
{tabs}
      </div>
      <div class="parking-layout">
        <aside class="parking-map" aria-label="{attr(pt["map_title"])}">
          <div class="map-sticky">
            <iframe id="park-map" title="{attr(pt["map_title"])}" src="{attr(maps_embed(SPOTS[first]["map"]))}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
            <p class="map-caption">📍 <span id="park-map-name">{pt["spots"][first][0]}</span></p>
          </div>
        </aside>
        <div class="parking-panels">
{panels}
        </div>
      </div>
    </div>
  </section>

  <section class="section parking-sources">
    <div class="container narrow">
      <p class="parking-updated">{pt["updated"]}</p>
      <p class="parking-source-list">{pt["sources_label"]}: {sources}</p>
    </div>
  </section>

  <section class="contact section section-dark">
    <div class="container narrow center">
      <h2>{pt["help_title"]}</h2>
      <p>{pt["help_text"]}</p>
      <div class="contact-actions">
        <a class="btn btn-primary btn-lg" href="{attr(whatsapp)}" target="_blank" rel="noopener">💬 WhatsApp</a>
        <a class="btn btn-ghost btn-lg" href="tel:{TEL}">📞 {t["phone_label"]}</a>
        <a class="btn btn-ghost btn-lg" href="{home}">← {pt["back"]}</a>
      </div>
    </div>
  </section>

</main>
""" + site_footer(lang, folder, "parking")


# ---------------------------------------- pagina "cosa vedere" --

MODE_ICON = {"walking": "🚶", "transit": "🚌", "driving": "🚗"}


def render_guide(lang, photos, cover):
    t, gt = T[lang], G[lang]
    folder = GUIDE_DIR[lang]
    home = rel(folder, HOME_DIR[lang])
    parking_href = rel(folder, PARK_DIR[lang])
    btn = gt["buttons"]
    whatsapp = f"https://wa.me/{WHATSAPP}?text={quote(t['whatsapp_text'])}"
    cover_url = abs_url(cover["rel"]) if cover else None

    def card(key, badge):
        name, time, text = gt["stops"][key]
        s = STOPS[key]
        return f"""        <li class="stop-card" id="{key.replace("_", "-")}">
          <span class="stop-badge" aria-hidden="true">{badge}</span>
          <div class="stop-body">
            <div class="stop-head">
              <h3>{name}</h3>
              <span class="stop-time">{time}</span>
            </div>
            <p>{text}</p>
            <div class="park-actions">
              <a class="btn btn-outline btn-sm" href="{attr(maps_from_bnb(s["map"], s["mode"]))}" target="_blank" rel="noopener">{MODE_ICON[s["mode"]]} {btn["route"]}</a>
              <a class="btn btn-ghost btn-sm" href="{attr(maps_search(s["map"]))}" target="_blank" rel="noopener">🗺️ {btn["open"]}</a>
            </div>
          </div>
        </li>"""

    route_keys = [k for k, s in STOPS.items() if s["group"] == "castello"]
    route = "\n".join(card(k, i + 1) for i, k in enumerate(route_keys))
    beyond = "\n".join(card(k, STOPS[k]["icon"]) for k, s in STOPS.items() if s["group"] == "beyond")
    tips = "\n".join(
        f"""        <li><span class="tip-icon" aria-hidden="true">{icon}</span><div><strong>{title}</strong><p>{text.replace("{parking}", parking_href)}</p></div></li>"""
        for icon, title, text in gt["tips"])

    return head(lang, folder, GUIDE_DIR, gt["title"], gt["description"], gt["og_description"],
                guide_structured_data(lang, gt, photos, cover_url), cover, og_type="article") \
        + site_header(lang, folder, "guide") + f"""
<main class="guide-page">

  <section class="page-hero">
    <div class="container narrow">
      <a class="back-link" href="{home}">← {P[lang]["back"]}</a>
      <p class="hero-eyebrow">{gt["eyebrow"]}</p>
      <h1>{gt["h1"]}</h1>
      <p class="hero-sub">{gt["intro"]}</p>
      <div class="satnav-tip">
        <span class="satnav-icon" aria-hidden="true">👟</span>
        <div>
          <strong>{gt["before_title"]}</strong>
          <p>{gt["before_text"]}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container narrow">
      <h2>{gt["route_title"]}</h2>
      <p class="tab-intro">{gt["route_intro"]}</p>
      <ol class="stop-list">
{route}
      </ol>
    </div>
  </section>

  <section class="section">
    <div class="container narrow">
      <h2>{gt["beyond_title"]}</h2>
      <p class="tab-intro">{gt["beyond_intro"]}</p>
      <ul class="stop-list">
{beyond}
      </ul>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container narrow">
      <h2>{gt["tips_title"]}</h2>
      <ul class="tip-list">
{tips}
      </ul>
      <p class="parking-updated guide-updated">{gt["updated"]}</p>
    </div>
  </section>

  <section class="contact section section-dark">
    <div class="container narrow center">
      <h2>{gt["help_title"]}</h2>
      <p>{gt["help_text"]}</p>
      <div class="contact-actions">
        <a class="btn btn-primary btn-lg" href="{attr(whatsapp)}" target="_blank" rel="noopener">💬 WhatsApp</a>
        <a class="btn btn-ghost btn-lg" href="tel:{TEL}">📞 {t["phone_label"]}</a>
        <a class="btn btn-ghost btn-lg" href="{home}">← {P[lang]["back"]}</a>
      </div>
    </div>
  </section>

</main>
""" + site_footer(lang, folder, "guide")


# ------------------------------------------------ pagina check-in --
#
# Campi pensati per la registrazione su Alloggiati Web: ospite principale con
# documento, accompagnatori con i soli dati anagrafici. I nomi dei campi
# (guests[0][first_name], ...) sono quelli che il gestionale riceve: vedi
# docs/checkin-gestionale.md.

C = {
    # ===================================================== ITALIANO =====
    "it": {
        "title": "Check-in online — B&B Merì",
        "description": "Check-in online per gli ospiti del B&B Merì a Cagliari.",
        "eyebrow": "Check-in online",
        "h1": "Benvenuti da Merì",
        "intro": "Compila il modulo prima dell'arrivo: bastano pochi minuti. I dati ci servono per la registrazione degli ospiti, obbligatoria per legge. Alla fine vedrai le istruzioni per arrivare ed entrare, e le riceverai anche via email.",
        "required_note": "I campi con * sono obbligatori.",
        "s_stay": "Il tuo soggiorno",
        "arrival": "Data di arrivo", "departure": "Data di partenza",
        "guests_count": "Numero di ospiti",
        "arrival_time": "Orario di arrivo previsto", "arrival_time_hint": "Il check-in è dalle 15:00 alle 20:00.",
        "booking_ref": "Numero di prenotazione", "booking_ref_hint": "Lo trovi nella conferma di Booking.",
        "s_contact": "Contatti",
        "email": "Email", "email_hint": "Qui ti mandiamo la conferma e le istruzioni.",
        "phone": "Telefono (WhatsApp)",
        "s_main": "Ospite principale", "s_main_hint": "Inserisci i dati del documento con cui viaggi.",
        "s_guest": "Ospite {n}", "s_guest_hint": "Per gli accompagnatori bastano i dati anagrafici.",
        "first_name": "Nome", "last_name": "Cognome",
        "sex": "Sesso", "sex_m": "Maschio", "sex_f": "Femmina",
        "birth_date": "Data di nascita", "birth_country": "Stato di nascita",
        "birth_place": "Comune o città di nascita", "birth_province": "Provincia (solo se nato in Italia)",
        "citizenship": "Cittadinanza",
        "doc_type": "Tipo di documento", "doc_id": "Carta d'identità", "doc_passport": "Passaporto", "doc_license": "Patente di guida",
        "doc_number": "Numero del documento", "doc_place": "Rilasciato da (comune o Stato)",
        "doc_front": "Foto del documento (fronte)", "doc_back": "Foto del documento (retro)",
        "doc_photo": "Foto del documento",
        "doc_hint": "Foto nitida con tutti i dati leggibili. JPG, PNG o PDF, massimo 10 MB.",
        "s_other": "Altro", "notes": "Note o richieste", "notes_hint": "Per esempio: arrivo in auto, richiesta di transfer.",
        "privacy_title": "Privacy",
        "privacy_text": f"I tuoi dati sono trattati da B&amp;B Merì solo per la registrazione degli ospiti prevista dalla legge (art. 109 TULPS, comunicazione alla Questura tramite il portale Alloggiati Web) e per la gestione del soggiorno. Non vengono ceduti a terzi. Le foto dei documenti vengono cancellate dopo la registrazione. Puoi chiedere l'accesso, la correzione o la cancellazione dei tuoi dati scrivendo a {EMAIL}.",
        "consent": "Ho letto l'informativa e acconsento al trattamento dei dati per la registrazione.",
        "submit": "Invia il check-in", "sending": "Invio in corso…",
        "ok_title": "Check-in completato, grazie!",
        "ok_email": "Ti abbiamo inviato una copia di queste istruzioni all'indirizzo email indicato.",
        "err_title": "Non siamo riusciti a inviare il modulo.",
        "err_text": "Riprova tra poco oppure scrivici su WhatsApp: ti aiutiamo subito.",
        "err_file": "Il file «{name}» supera i 10 MB: scegli una foto più leggera.",
        "err_dates": "La data di partenza deve essere successiva a quella di arrivo.",
    },

    # ====================================================== ENGLISH =====
    "en": {
        "title": "Online check-in — B&B Merì",
        "description": "Online check-in for guests of B&B Merì in Cagliari.",
        "eyebrow": "Online check-in",
        "h1": "Welcome to Merì",
        "intro": "Please fill in this form before you arrive: it only takes a few minutes. We need these details to register our guests, as required by Italian law. At the end you will see how to get here and get in, and you will also receive the instructions by email.",
        "required_note": "Fields marked * are required.",
        "s_stay": "Your stay",
        "arrival": "Arrival date", "departure": "Departure date",
        "guests_count": "Number of guests",
        "arrival_time": "Expected arrival time", "arrival_time_hint": "Check-in is from 3:00 PM to 8:00 PM.",
        "booking_ref": "Booking number", "booking_ref_hint": "You will find it in your Booking.com confirmation.",
        "s_contact": "Contact details",
        "email": "Email", "email_hint": "We will send the confirmation and instructions here.",
        "phone": "Phone (WhatsApp)",
        "s_main": "Main guest", "s_main_hint": "Please enter the details of the ID document you are travelling with.",
        "s_guest": "Guest {n}", "s_guest_hint": "For other guests, personal details are enough.",
        "first_name": "First name", "last_name": "Surname",
        "sex": "Sex", "sex_m": "Male", "sex_f": "Female",
        "birth_date": "Date of birth", "birth_country": "Country of birth",
        "birth_place": "Place of birth (town or city)", "birth_province": "Province (only if born in Italy)",
        "citizenship": "Citizenship",
        "doc_type": "Document type", "doc_id": "ID card", "doc_passport": "Passport", "doc_license": "Driving licence",
        "doc_number": "Document number", "doc_place": "Issued by (town or country)",
        "doc_front": "Photo of the document (front)", "doc_back": "Photo of the document (back)",
        "doc_photo": "Photo of the document",
        "doc_hint": "A sharp photo with all details readable. JPG, PNG or PDF, 10 MB maximum.",
        "s_other": "Other", "notes": "Notes or requests", "notes_hint": "For example: arriving by car, transfer request.",
        "privacy_title": "Privacy",
        "privacy_text": f"Your data is processed by B&amp;B Merì only to register guests as required by Italian law (art. 109 TULPS, reported to the police through the Alloggiati Web portal) and to manage your stay. It is not shared with third parties. Photos of documents are deleted after registration. You can ask to access, correct or delete your data by writing to {EMAIL}.",
        "consent": "I have read the privacy notice and agree to the processing of my data for registration.",
        "submit": "Send check-in", "sending": "Sending…",
        "ok_title": "Check-in complete, thank you!",
        "ok_email": "We have sent a copy of these instructions to the email address you entered.",
        "err_title": "We could not send the form.",
        "err_text": "Please try again shortly or message us on WhatsApp: we will help you straight away.",
        "err_file": "The file «{name}» is larger than 10 MB: please choose a smaller photo.",
        "err_dates": "The departure date must be after the arrival date.",
    },

    # ===================================================== FRANÇAIS =====
    "fr": {
        "title": "Check-in en ligne — B&B Merì",
        "description": "Check-in en ligne pour les hôtes du B&B Merì à Cagliari.",
        "eyebrow": "Check-in en ligne",
        "h1": "Bienvenue chez Merì",
        "intro": "Remplissez ce formulaire avant votre arrivée : cela ne prend que quelques minutes. Ces informations nous servent à enregistrer nos hôtes, comme l'exige la loi italienne. À la fin, vous verrez comment venir et entrer, et vous recevrez aussi les instructions par e-mail.",
        "required_note": "Les champs marqués * sont obligatoires.",
        "s_stay": "Votre séjour",
        "arrival": "Date d'arrivée", "departure": "Date de départ",
        "guests_count": "Nombre de personnes",
        "arrival_time": "Heure d'arrivée prévue", "arrival_time_hint": "L'arrivée se fait de 15 h à 20 h.",
        "booking_ref": "Numéro de réservation", "booking_ref_hint": "Vous le trouverez dans la confirmation Booking.com.",
        "s_contact": "Coordonnées",
        "email": "E-mail", "email_hint": "Nous vous enverrons ici la confirmation et les instructions.",
        "phone": "Téléphone (WhatsApp)",
        "s_main": "Hôte principal", "s_main_hint": "Indiquez les données de la pièce d'identité avec laquelle vous voyagez.",
        "s_guest": "Personne {n}", "s_guest_hint": "Pour les accompagnants, l'état civil suffit.",
        "first_name": "Prénom", "last_name": "Nom",
        "sex": "Sexe", "sex_m": "Homme", "sex_f": "Femme",
        "birth_date": "Date de naissance", "birth_country": "Pays de naissance",
        "birth_place": "Lieu de naissance (commune ou ville)", "birth_province": "Province (seulement si né en Italie)",
        "citizenship": "Nationalité",
        "doc_type": "Type de document", "doc_id": "Carte d'identité", "doc_passport": "Passeport", "doc_license": "Permis de conduire",
        "doc_number": "Numéro du document", "doc_place": "Délivré par (commune ou pays)",
        "doc_front": "Photo du document (recto)", "doc_back": "Photo du document (verso)",
        "doc_photo": "Photo du document",
        "doc_hint": "Photo nette, toutes les informations lisibles. JPG, PNG ou PDF, 10 Mo maximum.",
        "s_other": "Autre", "notes": "Remarques ou demandes", "notes_hint": "Par exemple : arrivée en voiture, demande de transfert.",
        "privacy_title": "Confidentialité",
        "privacy_text": f"Vos données sont traitées par B&amp;B Merì uniquement pour l'enregistrement des hôtes prévu par la loi italienne (art. 109 TULPS, déclaration à la police via le portail Alloggiati Web) et pour la gestion du séjour. Elles ne sont pas transmises à des tiers. Les photos des documents sont supprimées après l'enregistrement. Vous pouvez demander l'accès, la rectification ou la suppression de vos données en écrivant à {EMAIL}.",
        "consent": "J'ai lu l'information sur la confidentialité et j'accepte le traitement de mes données pour l'enregistrement.",
        "submit": "Envoyer le check-in", "sending": "Envoi en cours…",
        "ok_title": "Check-in terminé, merci !",
        "ok_email": "Nous avons envoyé une copie de ces instructions à l'adresse e-mail indiquée.",
        "err_title": "Nous n'avons pas pu envoyer le formulaire.",
        "err_text": "Réessayez dans un instant ou écrivez-nous sur WhatsApp : nous vous aidons tout de suite.",
        "err_file": "Le fichier « {name} » dépasse 10 Mo : choisissez une photo plus légère.",
        "err_dates": "La date de départ doit être postérieure à la date d'arrivée.",
    },

    # ====================================================== ESPAÑOL =====
    "es": {
        "title": "Check-in online — B&B Merì",
        "description": "Check-in online para los huéspedes del B&B Merì en Cagliari.",
        "eyebrow": "Check-in online",
        "h1": "Bienvenidos a Merì",
        "intro": "Rellena este formulario antes de llegar: solo tardarás unos minutos. Necesitamos estos datos para registrar a los huéspedes, como exige la ley italiana. Al final verás cómo llegar y entrar, y también recibirás las instrucciones por e-mail.",
        "required_note": "Los campos con * son obligatorios.",
        "s_stay": "Tu estancia",
        "arrival": "Fecha de llegada", "departure": "Fecha de salida",
        "guests_count": "Número de huéspedes",
        "arrival_time": "Hora prevista de llegada", "arrival_time_hint": "El check-in es de 15:00 a 20:00.",
        "booking_ref": "Número de reserva", "booking_ref_hint": "Lo encontrarás en la confirmación de Booking.com.",
        "s_contact": "Contacto",
        "email": "E-mail", "email_hint": "Aquí te enviaremos la confirmación y las instrucciones.",
        "phone": "Teléfono (WhatsApp)",
        "s_main": "Huésped principal", "s_main_hint": "Introduce los datos del documento con el que viajas.",
        "s_guest": "Huésped {n}", "s_guest_hint": "Para los acompañantes bastan los datos personales.",
        "first_name": "Nombre", "last_name": "Apellidos",
        "sex": "Sexo", "sex_m": "Hombre", "sex_f": "Mujer",
        "birth_date": "Fecha de nacimiento", "birth_country": "País de nacimiento",
        "birth_place": "Lugar de nacimiento (municipio o ciudad)", "birth_province": "Provincia (solo si naciste en Italia)",
        "citizenship": "Nacionalidad",
        "doc_type": "Tipo de documento", "doc_id": "Documento de identidad", "doc_passport": "Pasaporte", "doc_license": "Permiso de conducir",
        "doc_number": "Número del documento", "doc_place": "Expedido en (municipio o país)",
        "doc_front": "Foto del documento (anverso)", "doc_back": "Foto del documento (reverso)",
        "doc_photo": "Foto del documento",
        "doc_hint": "Foto nítida con todos los datos legibles. JPG, PNG o PDF, máximo 10 MB.",
        "s_other": "Otros", "notes": "Notas o peticiones", "notes_hint": "Por ejemplo: llegada en coche, petición de traslado.",
        "privacy_title": "Privacidad",
        "privacy_text": f"B&amp;B Merì trata tus datos solo para el registro de huéspedes exigido por la ley italiana (art. 109 TULPS, comunicación a la policía a través del portal Alloggiati Web) y para gestionar tu estancia. No se ceden a terceros. Las fotos de los documentos se borran tras el registro. Puedes pedir el acceso, la rectificación o la supresión de tus datos escribiendo a {EMAIL}.",
        "consent": "He leído la información de privacidad y acepto el tratamiento de mis datos para el registro.",
        "submit": "Enviar el check-in", "sending": "Enviando…",
        "ok_title": "¡Check-in completado, gracias!",
        "ok_email": "Te hemos enviado una copia de estas instrucciones al e-mail indicado.",
        "err_title": "No hemos podido enviar el formulario.",
        "err_text": "Vuelve a intentarlo en un momento o escríbenos por WhatsApp: te ayudamos enseguida.",
        "err_file": "El archivo «{name}» supera los 10 MB: elige una foto más ligera.",
        "err_dates": "La fecha de salida debe ser posterior a la de llegada.",
    },
}

MAX_GUESTS = 4


def field(label, name, kind="text", required=True, hint=None, options=None,
          extra="", full=False, default=None):
    """Un campo del modulo con etichetta, eventuale suggerimento e controllo."""
    fid = name.replace("][", "-").replace("[", "-").replace("]", "")
    star = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    req = " required" if required else ""
    described = f' aria-describedby="{fid}-hint"' if hint else ""
    hint_html = f'<small id="{fid}-hint">{hint}</small>' if hint else ""
    if kind == "select":
        blank = "" if default is not None else '<option value="" selected disabled></option>'
        opts = "".join(
            f'<option value="{attr(v)}"{" selected" if v == default else ""}>{escape(text)}</option>'
            for v, text in options)
        control = f'<select id="{fid}" name="{name}"{req}{described}{extra}>{blank}{opts}</select>'
    elif kind == "textarea":
        control = f'<textarea id="{fid}" name="{name}" rows="3"{req}{described}{extra}></textarea>'
    else:
        control = f'<input id="{fid}" name="{name}" type="{kind}"{req}{described}{extra}>'
    css = "field field--full" if full else "field"
    return f'<div class="{css}"><label for="{fid}">{label}{star}</label>{control}{hint_html}</div>'


def guest_fields(c, i, main):
    """Campi di un ospite: `i` e' il numero (0 = principale) o "__i__" nel modello."""
    g = f"guests[{i}]"
    files = 'accept="image/*,.pdf"'
    rows = [
        field(c["first_name"], f"{g}[first_name]", extra=' autocomplete="given-name"' if main else ""),
        field(c["last_name"], f"{g}[last_name]", extra=' autocomplete="family-name"' if main else ""),
        field(c["sex"], f"{g}[sex]", "select", options=[("M", c["sex_m"]), ("F", c["sex_f"])]),
        field(c["birth_date"], f"{g}[birth_date]", "date"),
        field(c["birth_country"], f"{g}[birth_country]"),
        field(c["birth_place"], f"{g}[birth_place]"),
        field(c["birth_province"], f"{g}[birth_province]", required=False, extra=' maxlength="2"'),
        field(c["citizenship"], f"{g}[citizenship]"),
    ]
    if main:
        rows += [
            field(c["doc_type"], f"{g}[doc_type]", "select",
                  options=[("IDENT", c["doc_id"]), ("PASOR", c["doc_passport"]), ("PATEN", c["doc_license"])]),
            field(c["doc_number"], f"{g}[doc_number]"),
            field(c["doc_place"], f"{g}[doc_place]", full=True),
            field(c["doc_front"], f"{g}[doc_front]", "file", hint=c["doc_hint"], extra=" " + files),
            field(c["doc_back"], f"{g}[doc_back]", "file", required=False, extra=" " + files),
        ]
    else:
        rows.append(field(c["doc_photo"], f"{g}[doc_photo]", "file", required=False,
                          hint=c["doc_hint"], extra=" " + files, full=True))
    return "\n            ".join(rows)


def render_checkin(lang, cover):
    t, c = T[lang], C[lang]
    folder = CHECKIN_DIR[lang]
    home = rel(folder, HOME_DIR[lang])
    whatsapp = f"https://wa.me/{WHATSAPP}?text={quote(t['whatsapp_text'])}"
    guest_options = [(str(n), str(n)) for n in range(1, MAX_GUESTS + 1)]

    stay = "\n            ".join([
        field(c["arrival"], "arrival", "date"),
        field(c["departure"], "departure", "date"),
        field(c["guests_count"], "guests_count", "select", options=guest_options, default="2"),
        field(c["arrival_time"], "arrival_time", "time", hint=c["arrival_time_hint"]),
        field(c["booking_ref"], "booking_ref", required=False, hint=c["booking_ref_hint"], full=True),
    ])
    contact = "\n            ".join([
        field(c["email"], "email", "email", hint=c["email_hint"], extra=' autocomplete="email"'),
        field(c["phone"], "phone", "tel", extra=' autocomplete="tel"'),
    ])
    # Messaggi usati dallo script (errori, invio in corso, titolo ospiti aggiuntivi)
    messages = json.dumps({k: c[k] for k in ("sending", "err_file", "err_dates", "s_guest")},
                          ensure_ascii=False)

    return head(lang, folder, CHECKIN_DIR, c["title"], c["description"], c["description"], [],
                cover, robots="noindex") \
        + site_header(lang, folder, "checkin") + f"""
<main class="checkin-page">

  <section class="page-hero">
    <div class="container narrow">
      <a class="back-link" href="{home}">← {P[lang]["back"]}</a>
      <p class="hero-eyebrow">{c["eyebrow"]}</p>
      <h1>{c["h1"]}</h1>
      <p class="hero-sub">{c["intro"]}</p>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container narrow">
      <form id="checkin-form" class="checkin-form" data-endpoint="{CHECKIN_API}" data-messages="{attr(messages)}" enctype="multipart/form-data" novalidate>
        <input type="hidden" name="lang" value="{lang}">
        <div class="hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
        <p class="form-note">{c["required_note"]}</p>

        <fieldset>
          <legend>{c["s_stay"]}</legend>
          <div class="field-grid">
            {stay}
          </div>
        </fieldset>

        <fieldset>
          <legend>{c["s_contact"]}</legend>
          <div class="field-grid">
            {contact}
          </div>
        </fieldset>

        <fieldset>
          <legend>{c["s_main"]}</legend>
          <p class="fieldset-hint">{c["s_main_hint"]}</p>
          <div class="field-grid">
            {guest_fields(c, 0, True)}
          </div>
        </fieldset>

        <div id="extra-guests"></div>

        <fieldset>
          <legend>{c["s_other"]}</legend>
          <div class="field-grid">
            {field(c["notes"], "notes", "textarea", required=False, hint=c["notes_hint"], full=True)}
          </div>
        </fieldset>

        <fieldset class="privacy-box">
          <legend>{c["privacy_title"]}</legend>
          <p>{c["privacy_text"]}</p>
          <label class="consent"><input type="checkbox" name="privacy_consent" value="yes" required> <span>{c["consent"]} <span class="req" aria-hidden="true">*</span></span></label>
        </fieldset>

        <p class="form-error" id="checkin-error" role="alert" hidden></p>
        <button type="submit" class="btn btn-primary btn-lg">{c["submit"]}</button>
      </form>

      <template id="guest-template">
        <fieldset class="extra-guest">
          <legend></legend>
          <p class="fieldset-hint">{c["s_guest_hint"]}</p>
          <div class="field-grid">
            {guest_fields(c, "__i__", False)}
          </div>
        </fieldset>
      </template>

      <div id="checkin-result" class="checkin-result" hidden tabindex="-1">
        <p class="result-icon" aria-hidden="true">✓</p>
        <h2>{c["ok_title"]}</h2>
        <div class="checkin-instructions"></div>
        <p class="result-email">{c["ok_email"]}</p>
      </div>

      <div id="checkin-failure" class="checkin-failure" hidden tabindex="-1">
        <h2>{c["err_title"]}</h2>
        <p>{c["err_text"]}</p>
        <a class="btn btn-primary" href="{attr(whatsapp)}" target="_blank" rel="noopener">WhatsApp {PHONE_INTL}</a>
      </div>
    </div>
  </section>

</main>
""" + site_footer(lang, folder, "checkin")


# ------------------------------------------ date di ultima modifica --
#
# tools/lastmod.json ricorda, per ogni pagina, l'impronta del contenuto e la
# data in cui e' cambiato l'ultima volta. Cosi' la sitemap e i dati strutturati
# dicono a Google e Bing la data vera, e solo quando qualcosa cambia davvero.

LASTMOD_FILE = ROOT / "tools" / "lastmod.json"
VERSION_RE = re.compile(r"\?v=[0-9a-f]{8}")


def stamp_lastmod(url, html, store):
    digest = hashlib.sha1(VERSION_RE.sub("", html).encode("utf-8")).hexdigest()
    record = store.get(url)
    if not record or record.get("sha1") != digest:
        record = {"date": today(), "sha1": digest}
        store[url] = record
    return html.replace(LASTMOD_TOKEN, record["date"]), record["date"]


# --------------------------------------------------------------- sitemap --

def sitemap(dates, photos):
    images = "".join(
        f"\n    <image:image><image:loc>{escape(abs_url(ph['rel']))}</image:loc></image:image>"
        for ph in photos)

    def entry(dirs, lang, extra=""):
        url = url_of(dirs[lang])
        alternates = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{url_of(dirs[l])}"/>' for l in LANGS)
        alternates += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url_of(dirs["it"])}"/>'
        return f"""
  <url>
    <loc>{url}</loc>
    <lastmod>{dates[url]}</lastmod>{alternates}{extra}
  </url>"""

    urls = "".join(entry(HOME_DIR, l, images) for l in LANGS)
    urls += "".join(entry(PARK_DIR, l) for l in LANGS)
    urls += "".join(entry(GUIDE_DIR, l) for l in LANGS)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{urls}
</urlset>
"""


# -------------------------------------------------------------- llms.txt --
#
# Riassunto in testo semplice per gli assistenti AI (ChatGPT, Claude,
# Perplexity, Gemini...). E' generato dagli stessi dati delle pagine, cosi'
# non resta mai indietro rispetto al sito.

def llms_txt(photos, dates):
    it, en = T["it"], T["en"]
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    year, month = PARKING_CHECKED.split("-")
    checked = f"{months[int(month) - 1]} {year}"

    def lines(rows):
        return "\n".join(rows)

    def faq(t):
        return lines(f"- **{q}** {a}" for q, a in t["faq"])

    def facts(t):
        return lines(f"- {label}: {value}" for label, value in t["facts"])

    parking = []
    for key in SPOTS:
        name, badge, spot_facts, text = P["en"]["spots"][key]
        details = "; ".join(f"{plain(label)}: {plain(value)}" for label, value in spot_facts)
        parking.append(f"- **{plain(name)}** ({plain(badge)}): {details}. {plain(text)}")
    arrival = [f"- **{plain(title)}**: {plain(text.replace('{parking}', url_of(PARK_DIR['en'])))}"
               for _, title, text in en["arrival"]]
    distances = [f"- {place}: {time}" for place, time in en["distances"]]
    stops = [f"- **{name}** ({time}): {plain(text)}" for name, time, text in G["en"]["stops"].values()]
    photo_rows = [f"- [{photo_alt(ph, 'en', i)}]({abs_url(ph['rel'])})" for i, ph in enumerate(photos)]

    pages = []
    for l in LANGS:
        pages.append(f"- [Home — {T[l]['lang_name']}]({url_of(HOME_DIR[l])}): {T[l]['description']}")
    for l in LANGS:
        pages.append(f"- [{plain(P[l]['h1'].replace('<br>', ' '))} — {T[l]['lang_name']}]({url_of(PARK_DIR[l])}): {P[l]['description']}")
    for l in LANGS:
        pages.append(f"- [{plain(G[l]['h1'].replace('<br>', ' '))} — {T[l]['lang_name']}]({url_of(GUIDE_DIR[l])}): {G[l]['description']}")
    checkin = url_of(CHECKIN_DIR["it"]) if CHECKIN_FORM_LIVE else CHECKIN_URL
    pages.append(f"- [Check-in online]({checkin}): modulo per gli ospiti che hanno già prenotato / form for guests who have already booked")
    if SAME_AS:
        pages += [f"- [{u}]({u})" for u in SAME_AS]

    return f"""# B&B Merì

> {it["ld_description"]}
> {en["ld_description"]}

Sito ufficiale / Official website: {SITE} (italiano, English, français, español).
Aggiornato il / Last updated: {max(dates.values())}.

## In breve (italiano)

{facts(it)}

## At a glance (English)

{facts(en)}

## Domande frequenti (italiano)

{faq(it)}

## Frequently asked questions (English)

{faq(en)}

## Getting here (English)

{lines(arrival)}

## Location: walking times from the B&B (English)

{lines(distances)}

## Parking near Castello (checked {checked}; prices may change)

{lines(parking)}

## Things to see on foot from the B&B (English)

{lines(stops)}

## Foto della Camera Matrimoniale / Photos of the Double Room

{lines(photo_rows)}

## Pagine / Pages

{lines(pages)}
"""


def write_page(folder, html):
    path = ROOT / folder / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print("scritto", path.relative_to(ROOT))


def main():
    with_checkin = CHECKIN_FORM_LIVE or os.environ.get("MERI_PREVIEW") == "1"
    photos = gallery_photos()
    cover = optimize_photos(photos)
    store = json.loads(LASTMOD_FILE.read_text(encoding="utf-8")) if LASTMOD_FILE.exists() else {}
    dates = {}
    for lang in LANGS:
        pages = [(HOME_DIR[lang], render_home(lang, photos, cover)),
                 (PARK_DIR[lang], render_parking(lang, photos, cover)),
                 (GUIDE_DIR[lang], render_guide(lang, photos, cover))]
        for folder, html in pages:
            html, dates[url_of(folder)] = stamp_lastmod(url_of(folder), html, store)
            write_page(folder, html)
        if with_checkin:
            write_page(CHECKIN_DIR[lang], render_checkin(lang, cover))

    store = {url: store[url] for url in sorted(dates)}
    LASTMOD_FILE.write_text(json.dumps(store, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(dates, photos), encoding="utf-8")
    print("scritto sitemap.xml")
    (ROOT / "llms.txt").write_text(llms_txt(photos, dates), encoding="utf-8")
    print("scritto llms.txt")
    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")


if __name__ == "__main__":
    main()
