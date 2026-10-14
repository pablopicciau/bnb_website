#!/usr/bin/env python3
"""Genera la home del sito B&B Merì in quattro lingue (IT, EN, FR, ES).

Tutti i testi stanno nel dizionario T qui sotto, una sezione per lingua.
Per cambiare qualcosa: modifica i testi e rilancia

    python3 tools/build_pages.py

Lo script riscrive index.html, en/index.html, fr/index.html, es/index.html
e sitemap.xml, cosi' le quattro versioni restano sempre allineate.
"""
import hashlib
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent

SITE = "https://www.meribnb.it/"
PHONE = "352 036 8357"
PHONE_INTL = "+39 352 036 8357"
TEL = "+393520368357"
WHATSAPP = "393520368357"
EMAIL = "meri.bnb.cagliari@gmail.com"
CHECKIN_URL = "https://form.jotform.com/262836960089066"
CIN = "IT092009C2000U6994"   # Codice Identificativo Nazionale della struttura
STREET = "Via Alberto Lamarmora 18"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=Via+Alberto+Lamarmora+18%2C+Cagliari"
LASTMOD = "2026-10-14"

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
        "nav": {"rooms": "Le Stanze", "amenities": "Servizi", "location": "Posizione",
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
        "arr_h2": "Aeroporto, auto e parcheggi",
        "arr_intro": "Castello è una <strong>zona a traffico limitato (ZTL)</strong>: in auto non si arriva fino al portone. Ecco i modi più comodi per raggiungerci.",
        "arrival": [
            ("✈️", "Dall'aeroporto in treno", "Dalla stazione Elmas Aeroporto, a pochi passi dal terminal, il treno vi porta in circa 10 minuti alla stazione di Cagliari in <strong>Piazza Matteotti</strong> (biglietto circa €1,30, una corsa ogni 20 minuti circa)."),
            ("🚌", "Poi il bus 7", "Davanti alla stazione prendete il bus CTM <strong>linea 7</strong>: sale in Castello e ferma proprio davanti a casa."),
            ("🅿️", "In auto: parcheggio gratuito", "Il più vicino è in <strong>Viale Buoncammino</strong>, sul lato panoramico con vista sulla città: le strisce bianche sono gratuite, quelle <strong>blu sono a pagamento</strong>."),
            ("🏢", "In auto: parcheggio Regina Elena", "Parcheggio coperto in <strong>Viale Regina Elena 17</strong>, aperto 24 ore su 24: circa €1,70 l'ora, massimo <strong>€10 al giorno</strong>. Da qui si sale in Castello con gli <strong>ascensori pubblici gratuiti</strong> di Viale Regina Elena: quello di <strong>Saint Remy</strong>, nei giardini sotto le mura a circa 100 m da Piazza Costituzione, che porta al Bastione di Saint Remy, e quelli dell'<strong>ex Unione Sarda</strong>, che salgono verso il quartiere."),
            ("🚐", "Transfer su richiesta", "Preferite essere accompagnati? Organizziamo il transfer da e per la struttura: chiedetecelo in anticipo."),
        ],
        "arr_note": "Tariffe e orari (anche degli ascensori, che d'estate possono fermarsi nelle ore più calde) sono indicativi: verificateli prima del viaggio.",
        "faq_eyebrow": "Domande frequenti",
        "faq_h2": "Buono a sapersi",
        "faq": [
            ("Come arrivo dall'aeroporto?", "In treno da Elmas Aeroporto alla stazione di Cagliari in Piazza Matteotti (circa 10 minuti), poi bus CTM linea 7, che ferma proprio davanti a casa."),
            ("Castello è ZTL? Dove parcheggio?", "Sì, Castello è zona a traffico limitato. Il parcheggio gratuito più vicino è in Viale Buoncammino (strisce bianche; quelle blu sono a pagamento). In alternativa c'è il parcheggio coperto di Viale Regina Elena (circa €1,70 l'ora, massimo €10 al giorno), collegato a Castello dagli ascensori pubblici gratuiti."),
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
        "nav": {"rooms": "Rooms", "amenities": "Amenities", "location": "Location",
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
        "arr_h2": "Airport, car and parking",
        "arr_intro": "Castello is a <strong>limited-traffic zone (ZTL)</strong>: you can't drive up to the front door. Here are the easiest ways to reach us.",
        "arrival": [
            ("✈️", "From the airport by train", "From Elmas Aeroporto station, a short walk from the terminal, the train takes you in about 10 minutes to Cagliari station in <strong>Piazza Matteotti</strong> (ticket about €1.30, a train roughly every 20 minutes)."),
            ("🚌", "Then bus no. 7", "In front of the station, take CTM bus <strong>line 7</strong>: it climbs up to Castello and stops right outside our door."),
            ("🅿️", "By car: free parking", "The nearest free parking is on <strong>Viale Buoncammino</strong>, on the panoramic side overlooking the city: white lines are free, <strong>blue lines are paid</strong>."),
            ("🏢", "By car: Regina Elena car park", "Covered car park at <strong>Viale Regina Elena 17</strong>, open 24/7: about €1.70 per hour, <strong>€10 per day</strong> maximum. From there, go up to Castello with the <strong>free public lifts</strong> on Viale Regina Elena: the <strong>Saint Remy</strong> lift, in the gardens below the walls about 100 m from Piazza Costituzione, which takes you to the Bastione di Saint Remy, and the <strong>former Unione Sarda</strong> lifts, which climb up to the quarter."),
            ("🚐", "Transfer on request", "Rather be picked up? We can arrange a transfer to and from the property: just ask us in advance."),
        ],
        "arr_note": "Prices and times (including the lifts, which in summer may pause during the hottest hours) are indicative: please check them before you travel.",
        "faq_eyebrow": "Frequently asked questions",
        "faq_h2": "Good to know",
        "faq": [
            ("How do I get there from the airport?", "By train from Elmas Aeroporto to Cagliari station in Piazza Matteotti (about 10 minutes), then CTM bus line 7, which stops right outside our door."),
            ("Is Castello a ZTL? Where can I park?", "Yes, Castello is a limited-traffic zone. The nearest free parking is on Viale Buoncammino (white lines; blue lines are paid). Alternatively there is the covered car park on Viale Regina Elena (about €1.70 per hour, €10 per day maximum), connected to Castello by free public lifts."),
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
        "nav": {"rooms": "Chambres", "amenities": "Services", "location": "Emplacement",
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
        "arr_h2": "Aéroport, voiture et parkings",
        "arr_intro": "Castello est une <strong>zone à trafic limité (ZTL)</strong> : impossible d'arriver en voiture jusqu'à la porte. Voici les moyens les plus simples de nous rejoindre.",
        "arrival": [
            ("✈️", "Depuis l'aéroport en train", "Depuis la gare Elmas Aeroporto, à quelques pas du terminal, le train vous amène en 10 minutes environ à la gare de Cagliari, <strong>Piazza Matteotti</strong> (billet d'environ 1,30 €, un train toutes les 20 minutes environ)."),
            ("🚌", "Puis le bus n° 7", "Devant la gare, prenez le bus CTM <strong>ligne 7</strong> : il monte à Castello et s'arrête juste devant chez nous."),
            ("🅿️", "En voiture : parking gratuit", "Le plus proche se trouve sur le <strong>Viale Buoncammino</strong>, côté panoramique avec vue sur la ville : les lignes blanches sont gratuites, les <strong>lignes bleues sont payantes</strong>."),
            ("🏢", "En voiture : parking Regina Elena", "Parking couvert au <strong>Viale Regina Elena 17</strong>, ouvert 24 h/24 : environ 1,70 € de l'heure, <strong>10 € par jour</strong> maximum. De là, on monte à Castello avec les <strong>ascenseurs publics gratuits</strong> du Viale Regina Elena : celui de <strong>Saint-Remy</strong>, dans les jardins sous les remparts à environ 100 m de la Piazza Costituzione, qui mène au Bastion de Saint-Remy, et ceux de l'<strong>ancienne Unione Sarda</strong>, qui montent vers le quartier."),
            ("🚐", "Transfert sur demande", "Vous préférez être accompagnés ? Nous organisons le transfert depuis et vers la maison : demandez-le-nous à l'avance."),
        ],
        "arr_note": "Tarifs et horaires (y compris ceux des ascenseurs, qui en été peuvent s'arrêter aux heures les plus chaudes) sont indicatifs : vérifiez-les avant votre voyage.",
        "faq_eyebrow": "Questions fréquentes",
        "faq_h2": "Bon à savoir",
        "faq": [
            ("Comment venir depuis l'aéroport ?", "En train d'Elmas Aeroporto à la gare de Cagliari, Piazza Matteotti (10 minutes environ), puis bus CTM ligne 7, qui s'arrête juste devant chez nous."),
            ("Castello est-il en ZTL ? Où se garer ?", "Oui, Castello est une zone à trafic limité. Le parking gratuit le plus proche se trouve sur le Viale Buoncammino (lignes blanches ; les bleues sont payantes). Sinon, il y a le parking couvert du Viale Regina Elena (environ 1,70 € de l'heure, 10 € par jour maximum), relié à Castello par des ascenseurs publics gratuits."),
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
        "nav": {"rooms": "Habitaciones", "amenities": "Servicios", "location": "Ubicación",
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
        "arr_h2": "Aeropuerto, coche y aparcamientos",
        "arr_intro": "Castello es una <strong>zona de tráfico limitado (ZTL)</strong>: en coche no se llega hasta la puerta. Estas son las formas más cómodas de llegar.",
        "arrival": [
            ("✈️", "Desde el aeropuerto en tren", "Desde la estación Elmas Aeroporto, a pocos pasos de la terminal, el tren te lleva en unos 10 minutos a la estación de Cagliari en <strong>Piazza Matteotti</strong> (billete de aprox. 1,30 €, un tren cada 20 minutos aprox.)."),
            ("🚌", "Después, el autobús 7", "Delante de la estación, toma el autobús CTM <strong>línea 7</strong>: sube a Castello y para justo delante de casa."),
            ("🅿️", "En coche: aparcamiento gratuito", "El más cercano está en el <strong>Viale Buoncammino</strong>, en el lado panorámico con vistas a la ciudad: las plazas de rayas blancas son gratuitas y las de <strong>rayas azules, de pago</strong>."),
            ("🏢", "En coche: aparcamiento Regina Elena", "Aparcamiento cubierto en <strong>Viale Regina Elena 17</strong>, abierto 24 horas: aprox. 1,70 € la hora, <strong>10 € al día</strong> como máximo. Desde allí se sube a Castello con los <strong>ascensores públicos gratuitos</strong> del Viale Regina Elena: el de <strong>Saint Remy</strong>, en los jardines bajo las murallas a unos 100 m de Piazza Costituzione, que lleva al Bastión de Saint Remy, y los de la <strong>antigua Unione Sarda</strong>, que suben hacia el barrio."),
            ("🚐", "Traslado bajo petición", "¿Prefieres que te acompañemos? Organizamos el traslado desde y hacia el alojamiento: pídenoslo con antelación."),
        ],
        "arr_note": "Precios y horarios (también los de los ascensores, que en verano pueden pararse en las horas de más calor) son orientativos: compruébalos antes del viaje.",
        "faq_eyebrow": "Preguntas frecuentes",
        "faq_h2": "Bueno saberlo",
        "faq": [
            ("¿Cómo llego desde el aeropuerto?", "En tren desde Elmas Aeroporto hasta la estación de Cagliari en Piazza Matteotti (unos 10 minutos) y después el autobús CTM línea 7, que para justo delante de casa."),
            ("¿Castello es ZTL? ¿Dónde aparco?", "Sí, Castello es zona de tráfico limitado. El aparcamiento gratuito más cercano está en el Viale Buoncammino (rayas blancas; las azules son de pago). Como alternativa está el aparcamiento cubierto del Viale Regina Elena (aprox. 1,70 € la hora, 10 € al día como máximo), conectado con Castello por ascensores públicos gratuitos."),
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


# ----------------------------------------------------------- utilita' --

def page_url(lang):
    return SITE if lang == "it" else f"{SITE}{lang}/"


def page_path(lang):
    return ROOT / "index.html" if lang == "it" else ROOT / lang / "index.html"


def lang_href(current, target):
    """Link relativo dalla pagina `current` alla pagina `target`."""
    prefix = "" if current == "it" else "../"
    href = prefix + ("" if target == "it" else f"{target}/")
    return href or "./"


def asset_version(rel_path):
    """Impronta del file: cambia quando il file cambia, cosi' i browser
    scaricano subito la versione nuova invece di usare quella in memoria."""
    return hashlib.sha1((ROOT / rel_path).read_bytes()).hexdigest()[:8]


def attr(text):
    return escape(text, quote=True)


def json_ld(data):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def structured_data(lang, t):
    def feature(name):
        return {"@type": "LocationFeatureSpecification", "name": name, "value": True}

    bnb = {
        "@context": "https://schema.org",
        "@type": "BedAndBreakfast",
        "name": "B&B Merì",
        "description": t["ld_description"],
        "url": page_url(lang),
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
    return json_ld(bnb), json_ld(faq)


# ------------------------------------------------------------ pagina --

def render(lang):
    t = T[lang]
    p = "" if lang == "it" else "../"   # prefisso per css/js/immagini
    ids, nav = t["ids"], t["nav"]
    r1, r2 = t["room1"], t["room2"]
    ld_bnb, ld_faq = structured_data(lang, t)

    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{l}" href="{page_url(l)}">' for l in LANGS)
    lang_switch = "".join(
        f'<a href="{lang_href(lang, l)}" hreflang="{l}" lang="{l}"'
        + (' aria-current="page"' if l == lang else "")
        + f'>{l.upper()}</a>'
        for l in LANGS)
    footer_langs = "\n      ".join(
        f'<a href="{lang_href(lang, l)}" hreflang="{l}" lang="{l}">{T[l]["lang_name"]}</a>'
        for l in LANGS if l != lang)

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
    arrival = "\n".join(
        f"""        <li>
          <span class="arrival-icon">{icon}</span>
          <div>
            <strong class="arrival-title">{title}</strong>
            {text}
          </div>
        </li>""" for icon, title, text in t["arrival"])
    faq = "\n".join(
        f"""      <details class="faq-item">
        <summary>{escape(q)}</summary>
        <p>{escape(a)}</p>
      </details>""" for q, a in t["faq"])

    whatsapp = f"https://wa.me/{WHATSAPP}?text={quote(t['whatsapp_text'])}"
    mailto = f"mailto:{EMAIL}?subject={quote(t['mail_subject'])}"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Pagina generata da tools/build_pages.py: modifica i testi li', non qui. -->
  <title>{escape(t["title"])}</title>
  <meta name="description" content="{attr(t["description"])}">
  <meta name="keywords" content="{attr(t["keywords"])}">
  <link rel="canonical" href="{page_url(lang)}">
{alternates}
  <link rel="alternate" hreflang="x-default" href="{SITE}">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{attr(t["title"])}">
  <meta property="og:description" content="{attr(t["og_description"])}">
  <meta property="og:url" content="{page_url(lang)}">
  <meta property="og:image" content="{SITE}assets/img/og-cover.svg">
  <meta property="og:locale" content="{t["og_locale"]}">
  <meta property="og:site_name" content="B&amp;B Merì">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}css/style.css?v={asset_version("css/style.css")}">

  <!-- Dati strutturati: BedAndBreakfast -->
  <script type="application/ld+json">
{ld_bnb}
  </script>

  <!-- Dati strutturati: FAQ -->
  <script type="application/ld+json">
{ld_faq}
  </script>
</head>
<body>

<header class="site-header" id="top">
  <div class="container header-inner">
    <a href="#top" class="logo" aria-label="B&amp;B Merì — home">
      <img class="logo-mark" src="{p}assets/img/logo-mark.svg" alt="" width="46" height="46">
      <span class="logo-text">Merì <em>Bed &amp; Breakfast · Cagliari</em></span>
    </a>
    <nav class="main-nav" aria-label="{attr(t["nav_label"])}">
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="{attr(t["menu_open"])}">
        <span></span><span></span><span></span>
      </button>
      <ul id="nav-menu" class="nav-menu">
        <li><a href="#{ids["rooms"]}">{nav["rooms"]}</a></li>
        <li><a href="#{ids["amenities"]}">{nav["amenities"]}</a></li>
        <li><a href="#{ids["location"]}">{nav["location"]}</a></li>
        <li><a href="#{ids["arrival"]}">{nav["arrival"]}</a></li>
        <li><a href="#{ids["faq"]}">{nav["faq"]}</a></li>
        <li><a href="#{ids["contact"]}" class="nav-cta">{nav["book"]}</a></li>
        <li class="lang-switch">{lang_switch}</li>
      </ul>
    </nav>
  </div>
</header>

<main>

  <!-- HERO -->
  <section class="hero">
    <div class="container hero-inner">
      <p class="hero-eyebrow">{t["hero_eyebrow"]}</p>
      <h1>{t["h1"]}</h1>
      <a class="checkin-cta" href="{CHECKIN_URL}" target="_blank" rel="noopener">
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
      <a href="#{ids["rooms"]}">{nav["rooms"]}</a>
      <a href="#{ids["amenities"]}">{nav["amenities"]}</a>
      <a href="#{ids["location"]}">{nav["location"]}</a>
      <a href="#{ids["arrival"]}">{nav["arrival"]}</a>
      <a href="#{ids["faq"]}">{nav["faq"]}</a>
      <a href="{CHECKIN_URL}" target="_blank" rel="noopener">{t["checkin_title"]}</a>
      {footer_langs}
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


def sitemap():
    alternates = "".join(
        f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l)}"/>' for l in LANGS)
    alternates += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}"/>'
    urls = "".join(
        f"""
  <url>
    <loc>{page_url(l)}</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{"1.0" if l == "it" else "0.9"}</priority>{alternates}
  </url>""" for l in LANGS)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}
</urlset>
"""


def main():
    for lang in LANGS:
        path = page_path(lang)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(lang), encoding="utf-8")
        print("scritto", path.relative_to(ROOT))
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    print("scritto sitemap.xml")


if __name__ == "__main__":
    main()
