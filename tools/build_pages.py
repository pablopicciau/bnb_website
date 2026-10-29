#!/usr/bin/env python3
"""Genera la home del sito B&B Merì in quattro lingue (IT, EN, FR, ES).

Tutti i testi stanno nel dizionario T qui sotto, una sezione per lingua.
Per cambiare qualcosa: modifica i testi e rilancia

    python3 tools/build_pages.py

Lo script riscrive la home (index.html, en/, fr/, es/), la guida ai
parcheggi (parcheggi/, en/parking/, fr/stationnement/, es/aparcamiento/)
e sitemap.xml, cosi' le quattro lingue restano sempre allineate.
"""
import hashlib
import os
import json
import posixpath
import re
from html import escape, unescape
from pathlib import Path
from urllib.parse import quote, quote_plus

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
LASTMOD = "2026-10-29"

LANGS = ["it", "en", "fr", "es"]


# ---------------------------------------------------------------- testi --

T = {
    # ===================================================== ITALIANO =====
    "it": {
        "lang_name": "Italiano",
        "og_locale": "it_IT",
        "region": "Sardegna",
        "title": "B&B Merì — Bed & Breakfast nel centro storico di Cagliari",
        "description": "B&B Merì: camera matrimoniale con bagno privato nel cuore di Castello, il centro storico di Cagliari. Wi-Fi, aria condizionata, acqua potabile dal rubinetto e transfer su richiesta. A pochi passi dal Bastione di Saint Remy.",
        "keywords": "b&b cagliari centro, bed and breakfast cagliari, camera con bagno privato cagliari, dormire a cagliari castello, alloggio centro storico cagliari, b&b merì cagliari",
        "og_description": "Camere con bagno privato nel quartiere Castello, centro storico di Cagliari. A pochi passi dal Bastione di Saint Remy.",
        "ids": {"rooms": "stanze", "amenities": "servizi", "location": "posizione",
                "arrival": "come-arrivare", "faq": "faq", "contact": "contatti"},
        "nav": {"rooms": "Le Stanze", "amenities": "Servizi", "location": "Posizione", "parking": "Parcheggi",
                "arrival": "Come arrivare", "faq": "FAQ", "book": "Prenota"},
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
            ("Il transfer è disponibile?", "Sì, su richiesta: scriveteci in anticipo per organizzarlo."),
            ("L'acqua del rubinetto è potabile?", "Sì, l'acqua del rubinetto è potabile: fresca e buona da bere."),
            ("A che ora sono il check-in e il check-out?", "Il check-in è dalle 15:00 alle 20:00; per orari diversi basta avvisarci. Il check-out è entro le 10:30. Potete fare il check-in online in anticipo dal pulsante in cima alla pagina."),
            ("Le camere hanno il bagno privato?", "Sì, ogni camera ha il bagno privato con doccia, asciugacapelli e set di cortesia."),
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
            ("Camera con Cucina", "Camera matrimoniale con angolo cottura e bagno privato, nel quartiere Castello.", ["Bagno privato", "Angolo cottura"]),
        ],
    },

    # ====================================================== ENGLISH =====
    "en": {
        "lang_name": "English",
        "og_locale": "en_GB",
        "region": "Sardinia",
        "title": "B&B Merì — Bed & Breakfast in the historic centre of Cagliari",
        "description": "B&B Merì: double room with private bathroom in the heart of Castello, Cagliari's historic centre. Free Wi-Fi, air conditioning, drinkable tap water and transfer on request. Steps from the Bastione di Saint Remy.",
        "keywords": "b&b cagliari centre, bed and breakfast cagliari, room with private bathroom cagliari, where to stay cagliari castello, accommodation cagliari old town, b&b merì cagliari",
        "og_description": "Rooms with private bathroom in the Castello district, Cagliari's historic centre. Steps from the Bastione di Saint Remy.",
        "ids": {"rooms": "rooms", "amenities": "amenities", "location": "location",
                "arrival": "getting-here", "faq": "faq", "contact": "contact"},
        "nav": {"rooms": "Rooms", "amenities": "Amenities", "location": "Location", "parking": "Parking",
                "arrival": "Getting here", "faq": "FAQ", "book": "Book"},
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
            ("Is a transfer available?", "Yes, on request: write to us in advance to arrange it."),
            ("Is the tap water drinkable?", "Yes, the tap water is drinkable: fresh and good to drink."),
            ("What are the check-in and check-out times?", "Check-in is from 3:00 PM to 8:00 PM; just let us know if you need a different time. Check-out is by 10:30 AM. You can complete online check-in in advance using the button at the top of the page."),
            ("Do the rooms have a private bathroom?", "Yes, every room has a private bathroom with shower, hairdryer and toiletries."),
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
            ("Room with Kitchenette", "Double room with kitchenette and private bathroom, in the Castello district.", ["Private bathroom", "Kitchenette"]),
        ],
    },

    # ===================================================== FRANÇAIS =====
    "fr": {
        "lang_name": "Français",
        "og_locale": "fr_FR",
        "region": "Sardaigne",
        "title": "B&B Merì — Chambres d'hôtes dans le centre historique de Cagliari",
        "description": "B&B Merì : chambre double avec salle de bains privative au cœur de Castello, le centre historique de Cagliari. Wi-Fi gratuit, climatisation, eau du robinet potable et transfert sur demande. À deux pas du Bastion de Saint-Remy.",
        "keywords": "b&b cagliari centre, chambre d'hôtes cagliari, chambre avec salle de bains privative cagliari, où dormir à cagliari castello, logement centre historique cagliari, b&b merì cagliari",
        "og_description": "Chambres avec salle de bains privative dans le quartier de Castello, centre historique de Cagliari. À deux pas du Bastion de Saint-Remy.",
        "ids": {"rooms": "chambres", "amenities": "services", "location": "emplacement",
                "arrival": "acces", "faq": "faq", "contact": "contact"},
        "nav": {"rooms": "Chambres", "amenities": "Services", "location": "Emplacement", "parking": "Parkings",
                "arrival": "Accès", "faq": "FAQ", "book": "Réserver"},
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
            ("Un transfert est-il possible ?", "Oui, sur demande : écrivez-nous à l'avance pour l'organiser."),
            ("L'eau du robinet est-elle potable ?", "Oui, l'eau du robinet est potable : fraîche et bonne à boire."),
            ("Quels sont les horaires d'arrivée et de départ ?", "L'arrivée se fait de 15 h à 20 h ; pour un autre horaire, prévenez-nous. Le départ se fait avant 10 h 30. Vous pouvez faire le check-in en ligne à l'avance grâce au bouton en haut de la page."),
            ("Les chambres ont-elles une salle de bains privative ?", "Oui, chaque chambre dispose d'une salle de bains privative avec douche, sèche-cheveux et produits d'accueil."),
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
            ("Chambre avec kitchenette", "Chambre double avec kitchenette et salle de bains privative, dans le quartier de Castello.", ["Salle de bains privative", "Kitchenette"]),
        ],
    },

    # ====================================================== ESPAÑOL =====
    "es": {
        "lang_name": "Español",
        "og_locale": "es_ES",
        "region": "Cerdeña",
        "title": "B&B Merì — Bed & Breakfast en el centro histórico de Cagliari",
        "description": "B&B Merì: habitación doble con baño privado en el corazón de Castello, el centro histórico de Cagliari. Wi-Fi gratis, aire acondicionado, agua potable del grifo y traslado bajo petición. A pocos pasos del Bastión de Saint Remy.",
        "keywords": "b&b cagliari centro, bed and breakfast cagliari, habitación con baño privado cagliari, dónde dormir en cagliari castello, alojamiento centro histórico cagliari, b&b merì cagliari",
        "og_description": "Habitaciones con baño privado en el barrio de Castello, centro histórico de Cagliari. A pocos pasos del Bastión de Saint Remy.",
        "ids": {"rooms": "habitaciones", "amenities": "servicios", "location": "ubicacion",
                "arrival": "como-llegar", "faq": "faq", "contact": "contacto"},
        "nav": {"rooms": "Habitaciones", "amenities": "Servicios", "location": "Ubicación", "parking": "Aparcar",
                "arrival": "Cómo llegar", "faq": "FAQ", "book": "Reservar"},
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
            ("¿Hay servicio de traslado?", "Sí, bajo petición: escríbenos con antelación para organizarlo."),
            ("¿El agua del grifo es potable?", "Sí, el agua del grifo es potable: fresca y buena para beber."),
            ("¿A qué hora son el check-in y el check-out?", "El check-in es de 15:00 a 20:00; si necesitas otro horario, avísanos. El check-out es antes de las 10:30. Puedes hacer el check-in online con antelación desde el botón de arriba de la página."),
            ("¿Las habitaciones tienen baño privado?", "Sí, cada habitación tiene baño privado con ducha, secador de pelo y artículos de aseo."),
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
            ("Habitación con cocina", "Habitación doble con cocina equipada y baño privado, en el barrio de Castello.", ["Baño privado", "Cocina"]),
        ],
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
CHECKIN_DIR = {"it": "checkin", "en": "en/check-in", "fr": "fr/check-in", "es": "es/check-in"}
PAGE_DIRS = {"home": HOME_DIR, "parking": PARK_DIR, "checkin": CHECKIN_DIR}

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
        "description": "Guida ai parcheggi vicino al quartiere Castello di Cagliari: parcheggio gratuito in Viale Buoncammino, aree a pagamento e multipiano in Viale Regina Elena, ascensori pubblici, ZTL, tariffe e mappe.",
        "keywords": "parcheggio castello cagliari, dove parcheggiare cagliari, parcheggio gratuito cagliari centro, viale buoncammino parcheggio, parcheggio regina elena cagliari, ztl castello cagliari",
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
        "description": "Parking guide for Cagliari's Castello district: free parking on Viale Buoncammino, paid street areas and the multi-storey car park on Viale Regina Elena, public lifts, ZTL rules, prices and maps.",
        "keywords": "parking castello cagliari, where to park cagliari, free parking cagliari centre, viale buoncammino parking, regina elena car park cagliari, ztl castello cagliari",
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
        "description": "Guide du stationnement dans le quartier de Castello à Cagliari : parking gratuit sur le Viale Buoncammino, zones payantes et parking à étages du Viale Regina Elena, ascenseurs publics, ZTL, tarifs et cartes.",
        "keywords": "parking castello cagliari, où se garer cagliari, parking gratuit cagliari centre, viale buoncammino parking, parking regina elena cagliari, ztl castello cagliari",
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
        "description": "Guía de aparcamiento para el barrio de Castello en Cagliari: aparcamiento gratuito en el Viale Buoncammino, zonas de pago y aparcamiento de varias plantas en el Viale Regina Elena, ascensores públicos, ZTL, tarifas y mapas.",
        "keywords": "aparcamiento castello cagliari, dónde aparcar en cagliari, aparcamiento gratis cagliari centro, viale buoncammino aparcamiento, parking regina elena cagliari, ztl castello cagliari",
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


def structured_data(lang, t):
    def feature(name):
        return {"@type": "LocationFeatureSpecification", "name": name, "value": True}

    bnb = {
        "@context": "https://schema.org",
        "@type": "BedAndBreakfast",
        "name": "B&B Merì",
        "description": t["ld_description"],
        "url": url_of(HOME_DIR[lang]),
        "image": SITE + "assets/img/og-cover.svg",
        "logo": SITE + "assets/img/logo.svg",
        "email": EMAIL,
        "telephone": PHONE_INTL,
        "priceRange": "€€",
        "currenciesAccepted": "EUR",
        "checkinTime": "15:00",
        "checkoutTime": "10:30",
        "numberOfRooms": 2,
        "petsAllowed": False,
        "smokingAllowed": False,
        "availableLanguage": ["Italian", "English", "French", "Spanish"],
        "identifier": {"@type": "PropertyValue", "propertyID": "CIN", "value": CIN},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": STREET,
            "addressLocality": "Cagliari",
            "addressRegion": t["region"],
            "postalCode": "09124",
            "addressCountry": "IT",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 39.2183, "longitude": 9.1164},
        "amenityFeature": [feature(n) for n in t["ld_amenities"]],
        "containsPlace": [
            {
                "@type": "HotelRoom",
                "name": name,
                "description": desc,
                "occupancy": {"@type": "QuantitativeValue", "maxValue": 2},
                "amenityFeature": [feature(n) for n in feats],
            }
            for name, desc, feats in t["ld_rooms"]
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in t["faq"]
        ],
    }
    return [("BedAndBreakfast", json_ld(bnb)), ("FAQ", json_ld(faq))]


def parking_structured_data(lang, pt):
    page = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": pt["title"],
        "description": pt["description"],
        "url": url_of(PARK_DIR[lang]),
        "inLanguage": lang,
        "about": {"@type": "BedAndBreakfast", "name": "B&B Merì", "url": url_of(HOME_DIR[lang])},
        "mainEntity": {
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
        },
    }
    return [("WebPage", json_ld(page))]


# ------------------------------------------------- parti in comune --

def head(lang, folder, alt_dirs, title, description, keywords, og_description, ld_blocks, extra_meta=""):
    p = asset_prefix(folder)
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{l}" href="{url_of(alt_dirs[l])}">' for l in LANGS)
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
  <meta name="keywords" content="{attr(keywords)}">{extra_meta}
  <link rel="canonical" href="{url_of(folder)}">
{alternates}
  <link rel="alternate" hreflang="x-default" href="{url_of(alt_dirs["it"])}">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{attr(title)}">
  <meta property="og:description" content="{attr(og_description)}">
  <meta property="og:url" content="{url_of(folder)}">
  <meta property="og:image" content="{SITE}assets/img/og-cover.svg">
  <meta property="og:locale" content="{T[lang]["og_locale"]}">
  <meta property="og:site_name" content="B&amp;B Merì">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}css/style.css?v={asset_version("css/style.css")}">

{ld}
</head>
<body>
"""


def site_header(lang, folder, page):
    """Intestazione con menu. `page` e' "home" oppure "parking"."""
    t = T[lang]
    ids, nav = t["ids"], t["nav"]
    p = asset_prefix(folder)
    home = "" if page == "home" else rel(folder, HOME_DIR[lang])
    dirs = PAGE_DIRS[page]
    parking_href = "#top" if page == "parking" else rel(folder, PARK_DIR[lang])
    current = ' aria-current="page"' if page == "parking" else ""
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
        <li><a href="{parking_href}"{current}>{nav["parking"]}</a></li>
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
    parking_href = "#top" if page == "parking" else rel(folder, PARK_DIR[lang])
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
      <a href="{parking_href}">{nav["parking"]}</a>
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

def render_home(lang):
    t = T[lang]
    folder = HOME_DIR[lang]
    p = asset_prefix(folder)
    ids = t["ids"]
    r1, r2 = t["room1"], t["room2"]
    parking_href = rel(folder, PARK_DIR[lang])

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

    return head(lang, folder, HOME_DIR, t["title"], t["description"], t["keywords"],
                t["og_description"], structured_data(lang, t)) \
        + site_header(lang, folder, "home") + f"""
<main>

  <!-- HERO -->
  <section class="hero">
    <div class="container hero-inner">
      <p class="hero-eyebrow">{t["hero_eyebrow"]}</p>
      <h1>{t["h1"]}</h1>
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
    </div>
  </section>

  <!-- CAMERE -->
  <section id="{ids["rooms"]}" class="rooms section section-alt">
    <div class="container">
      <p class="eyebrow">{t["rooms_eyebrow"]}</p>
      <h2>{t["rooms_h2"]}</h2>
      <div class="rooms-grid">

        <article class="room-card">
          <figure class="room-media room-gallery" data-gallery="assets/img/camera-matrimoniale" data-gallery-base="{p}assets/img/camera-matrimoniale/">
            <img src="{p}assets/img/room-castello.svg" alt="{attr(r1["alt"])}" width="800" height="600" loading="lazy">
          </figure>
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

def render_parking(lang):
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

    return head(lang, folder, PARK_DIR, pt["title"], pt["description"], pt["keywords"],
                pt["og_description"], parking_structured_data(lang, pt)) \
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


def render_checkin(lang):
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

    return head(lang, folder, CHECKIN_DIR, c["title"], c["description"], "", c["description"], [],
                extra_meta='\n  <meta name="robots" content="noindex">') \
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


# --------------------------------------------------------------- sitemap --

def sitemap():
    def entry(dirs, lang, priority):
        alternates = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{url_of(dirs[l])}"/>' for l in LANGS)
        alternates += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url_of(dirs["it"])}"/>'
        return f"""
  <url>
    <loc>{url_of(dirs[lang])}</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{priority}</priority>{alternates}
  </url>"""
    urls = "".join(entry(HOME_DIR, l, "1.0" if l == "it" else "0.9") for l in LANGS)
    urls += "".join(entry(PARK_DIR, l, "0.8") for l in LANGS)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}
</urlset>
"""


def main():
    with_checkin = CHECKIN_FORM_LIVE or os.environ.get("MERI_PREVIEW") == "1"
    for lang in LANGS:
        pages = [(HOME_DIR[lang], render_home(lang)), (PARK_DIR[lang], render_parking(lang))]
        if with_checkin:
            pages.append((CHECKIN_DIR[lang], render_checkin(lang)))
        for folder, html in pages:
            path = ROOT / folder / "index.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
            print("scritto", path.relative_to(ROOT))
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    print("scritto sitemap.xml")


if __name__ == "__main__":
    main()
