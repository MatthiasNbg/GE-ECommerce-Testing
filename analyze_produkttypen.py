# -*- coding: utf-8 -*-
import csv
from collections import Counter
import re

# Lese alle Hauptprodukte
with open('produkte.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    products = []
    for row in reader:
        if not row.get('parent_id', '').strip():
            products.append(row)

# Umfassende Produkttypen-Patterns (Prioritaet: spezifisch vor allgemein)
produkttypen_patterns = [
    # MOEBEL - Betten (spezifisch)
    (r'Elfenbett', 'Elfenbett'),
    (r'Ryokan.?Bett', 'Ryokan-Bett'),
    (r'Familienbett', 'Familienbett'),
    (r'Balkenbett', 'Balkenbett'),
    (r'Polsterbett', 'Polsterbett'),
    (r'Boxspringbett', 'Boxspringbett'),
    (r'Etagenbett', 'Etagenbett'),
    (r'Hochbett', 'Hochbett'),
    (r'Gitterbett', 'Gitterbett'),
    (r'Kinderbett', 'Kinderbett'),
    (r'Massivholzbett', 'Massivholzbett'),
    (r'\bBett\b', 'Bett (allgemein)'),

    # MOEBEL - Schlafen
    (r'Naturlatexmatratze', 'Naturlatexmatratze'),
    (r'Matratze', 'Matratze'),
    (r'Lattenrost', 'Lattenrost'),
    (r'Schlafsystem', 'Schlafsystem'),
    (r'Topper', 'Topper'),

    # MOEBEL - Polster
    (r'Ecksofa', 'Ecksofa'),
    (r'Schlafsofa', 'Schlafsofa'),
    (r'\bSofa\b', 'Sofa'),
    (r'Sessel', 'Sessel'),
    (r'Ottomane', 'Ottomane'),
    (r'Recamiere', 'Recamiere'),

    # MOEBEL - Sitzen
    (r'Esszimmerstuhl', 'Esszimmerstuhl'),
    (r'\bStuhl\b', 'Stuhl'),
    (r'Sitzbank', 'Sitzbank'),
    (r'Sitzkissen', 'Sitzkissen'),
    (r'Sofakissen', 'Sofakissen'),
    (r'\bBank\b', 'Bank'),
    (r'Barhocker', 'Barhocker'),
    (r'\bHocker\b', 'Hocker'),

    # MOEBEL - Tische
    (r'Esstisch', 'Esstisch'),
    (r'Couchtisch', 'Couchtisch'),
    (r'Nachttisch', 'Nachttisch'),
    (r'Beistelltisch', 'Beistelltisch'),
    (r'Schreibtisch', 'Schreibtisch'),
    (r'Konsolentisch', 'Konsolentisch'),
    (r'Sofatisch', 'Sofatisch'),
    (r'\bTisch\b', 'Tisch (allgemein)'),

    # MOEBEL - Aufbewahrung
    (r'Kleiderschrank', 'Kleiderschrank'),
    (r'Wohnschrank', 'Wohnschrank'),
    (r'\bSchrank\b', 'Schrank (allgemein)'),
    (r'Kommode', 'Kommode'),
    (r'Sideboard', 'Sideboard'),
    (r'Highboard', 'Highboard'),
    (r'Lowboard', 'Lowboard'),
    (r'\bRegal\b', 'Regal'),
    (r'Vitrine', 'Vitrine'),
    (r'Garderobe', 'Garderobe'),
    (r'Truhe', 'Truhe'),

    # HEIMTEXTILIEN - Teppiche
    (r'Naturteppich', 'Naturteppich'),
    (r'Wollteppich', 'Wollteppich'),
    (r'\bTeppich\b', 'Teppich'),

    # HEIMTEXTILIEN - Vorhaenge & Deko
    (r'Vorhang', 'Vorhang'),
    (r'Gardine', 'Gardine'),
    (r'\bPlaid\b', 'Plaid'),

    # HEIMTEXTILIEN - Tisch
    (r'Tischdecke', 'Tischdecke'),
    (r'Tischw', 'Tischdecke'),
    (r'Untersetzer', 'Untersetzer'),

    # STOFFE & MUSTER
    (r'Meterware', 'Meterware/Stoffe'),
    (r'Stoffmuster', 'Stoffmuster'),
    (r'Teppichmuster', 'Teppichmuster'),
    (r'Vorhangstoff', 'Vorhangstoff'),
    (r'Wollstoff', 'Wollstoff/Stoffmuster'),

    # BETTWAREN - Bezuege
    (r'Kissenbezug', 'Kissenbezug'),
    (r'Deckenbezug', 'Deckenbezug'),
    (r'Bettwaesche', 'Bettwaesche'),
    (r'Bettbezug', 'Bettbezug'),
    (r'Deckenueberzug', 'Deckenueberzug'),
    (r'Deckenüberzug', 'Deckenueberzug'),
    (r'Kissenueberzug', 'Kissenueberzug'),
    (r'Kissenüberzug', 'Kissenueberzug'),
    (r'Überzug', 'Ueberzug'),
    (r'ueberzug', 'Ueberzug'),

    # BETTWAREN - Decken & Kissen
    (r'Bettdecke', 'Bettdecke'),
    (r'Kopfkissen', 'Kopfkissen'),
    (r'Daunendecke', 'Daunendecke'),
    (r'Lavendelkissen', 'Lavendelkissen'),
    (r'Zierkissen', 'Zierkissen'),
    (r'Mondkissen', 'Mondkissen'),
    (r'\bDecke\b', 'Decke'),
    (r'\bKissen\b', 'Kissen'),
    (r'Spannbetttuch', 'Spannbetttuch'),
    (r'\bLaken\b', 'Laken'),
    (r'Schlafsack', 'Schlafsack'),
    (r'Strampelsack', 'Strampelsack'),

    # BELEUCHTUNG
    (r'Pendelleuchte', 'Pendelleuchte'),
    (r'Stehleuchte', 'Stehleuchte'),
    (r'Tischleuchte', 'Tischleuchte'),
    (r'Wandleuchte', 'Wandleuchte'),
    (r'Leuchte', 'Leuchte'),
    (r'Lampe', 'Lampe'),

    # BADEZIMMER
    (r'Handtuch', 'Handtuch'),
    (r'Bademantel', 'Bademantel'),
    (r'Waschhandschuh', 'Waschhandschuh'),
    (r'Badetuch', 'Badetuch'),

    # KLEIDUNG - Oberteile
    (r'Pullover', 'Pullover'),
    (r'\bShirt\b', 'Shirt'),
    (r'T-Shirt', 'T-Shirt'),
    (r'Bluse', 'Bluse'),
    (r'Cardigan', 'Cardigan'),
    (r'Strickjacke', 'Strickjacke'),
    (r'\bTop\b', 'Top'),
    (r'Weste', 'Weste'),

    # KLEIDUNG - Unterteile & Kleider
    (r'\bHose\b', 'Hose'),
    (r'\bRock\b', 'Rock'),
    (r'\bKleid\b', 'Kleid'),

    # KLEIDUNG - Oberbekleidung
    (r'Jacke', 'Jacke'),
    (r'Mantel', 'Mantel'),

    # KLEIDUNG - Nachtwaesche
    (r'Pyjama', 'Pyjama'),
    (r'Nachthemd', 'Nachthemd'),
    (r'Schlafanzug', 'Schlafanzug'),

    # KLEIDUNG - Accessoires
    (r'Socken', 'Socken'),
    (r'Hausschuhe', 'Hausschuhe'),
    (r'\bSchal\b', 'Schal'),
    (r'Handschuhe', 'Handschuhe'),
    (r'Tragetuch', 'Tragetuch'),

    # DEKORATION
    (r'Spiegel', 'Spiegel'),
    (r'Baldachin', 'Baldachin'),
    (r'Bettkasten', 'Bettkasten'),
    (r'\bVase\b', 'Vase'),

    # MOEBEL-ZUBEHOER
    (r'Mittelfuss', 'Moebel-Zubehoer'),
    (r'Mittelfuß', 'Moebel-Zubehoer'),
    (r'Fachbrett', 'Moebel-Zubehoer'),
    (r'Seitenwangen', 'Moebel-Zubehoer'),
    (r'Tuerfuellung', 'Moebel-Zubehoer'),
    (r'Türfüllung', 'Moebel-Zubehoer'),
    (r'Schublade', 'Moebel-Zubehoer'),
    (r'Rueckenlehne', 'Moebel-Zubehoer'),
    (r'Rückenlehne', 'Moebel-Zubehoer'),
    (r'Beschlag', 'Moebel-Zubehoer'),
    (r'Mittelsteg', 'Moebel-Zubehoer'),
    (r'Montageleiste', 'Moebel-Zubehoer'),
    (r'\bPlatte\b', 'Moebel-Zubehoer'),

    # WELLNESS & DUFT
    (r'Waermekissen', 'Waermekissen'),
    (r'Wärmekissen', 'Waermekissen'),
    (r'Waermflasche', 'Waermflasche'),
    (r'Wärmflasche', 'Waermflasche'),
    (r'Kuehlkissen', 'Kuehlkissen'),
    (r'Kühlkissen', 'Kuehlkissen'),
    (r'\bKerze\b', 'Kerze'),
    (r'Raumduft', 'Raumduft'),
    (r'Raeuch', 'Raeucherware'),
    (r'Räuch', 'Raeucherware'),
    (r'Aetherisch', 'Aetherisches Oel'),
    (r'Ätherisch', 'Aetherisches Oel'),
    (r'Zirben', 'Zirbenprodukt'),

    # YOGA & WELLNESS
    (r'Yoga', 'Yoga-Zubehoer'),
    (r'Meditation', 'Meditationszubehoer'),
    (r'ZAFU', 'Meditationszubehoer'),

    # KUECHE & HAUSHALT
    (r'Geschirr', 'Geschirr'),
    (r'Besteck', 'Besteck'),
    (r'Tasse', 'Tasse'),
    (r'\bBecher\b', 'Becher'),
    (r'Reiniger', 'Reinigungsmittel'),
    (r'Waschmittel', 'Waschmittel'),

    # INTERN / VERPACKUNG
    (r'Karton', 'Verpackung/Karton'),
    (r'Produkthangtag', 'Produkthangtag/Etikett'),
    (r'Gratis', 'Gratis/Werbeaktion'),
    (r'Tasche', 'Tasche'),

    # OUTDOOR
    (r'Liege', 'Liege'),

    # DIVERSES
    (r'Set:', 'Set/Kombi-Produkt'),
    (r'Sonderanfertigung', 'Sonderanfertigung'),
    (r'Massanfertigung', 'Massanfertigung'),
    (r'Maßanfertigung', 'Massanfertigung'),
    (r'Gleitessenz', 'Pflegemittel'),
    (r'\bBuch\b', 'Buch'),

    # ZUSAETZLICHE TYPEN
    (r'Spannleintuch', 'Spannleintuch'),
    (r'Leintuch', 'Leintuch'),
    (r'Pflegeset', 'Pflegemittel'),
    (r'Korb', 'Korb'),
    (r'Fauteuil', 'Sessel'),
    (r'Glas\b', 'Glas/Trinkglas'),
    (r'Espresso', 'Lebensmittel'),
    (r'Brot\b', 'Lebensmittel'),
    (r'Kaffee', 'Lebensmittel'),
    (r'Tee\b', 'Lebensmittel'),
    (r'Oliven', 'Lebensmittel'),
    (r'Beutel', 'Beutel/Verpackung'),
    (r'Sitzauflage', 'Sitzauflage'),
    (r'Sockel', 'Moebel-Zubehoer'),
    (r'Fachtraeger', 'Moebel-Zubehoer'),
    (r'Fachträger', 'Moebel-Zubehoer'),
    (r'\bFach\b', 'Moebel-Zubehoer'),
    (r'Tabs\b', 'Reinigungsmittel'),
    (r'Wunschliste', 'Wunschliste'),
    (r'Anti-Kalk', 'Reinigungsmittel'),

    # Weihnachten & Deko
    (r'Weihnachtsschmuck', 'Weihnachtsschmuck'),
    (r'Weihnacht', 'Weihnachtsartikel'),

    # Wohndecken
    (r'Wohndecke', 'Wohndecke'),
    (r'Puckdecke', 'Baby-Textilien'),
    (r'Wickeldecke', 'Baby-Textilien'),
    (r'Stillkissen', 'Stillkissen'),

    # Baby
    (r'Baby', 'Baby-Artikel'),

    # Keramik
    (r'Keramik', 'Keramik'),
    (r'Teller\b', 'Teller'),

    # Bienenwachs
    (r'Bienenwachs', 'Bienenwachsprodukt'),
    (r'Figurkerze', 'Kerze'),
    (r'Sternenkerze', 'Kerze'),

    # Polsterung
    (r'Polsterung', 'Polsterung/Bezug'),
    (r'Weisspolsterung', 'Polsterung/Bezug'),

    # Duftsack
    (r'Duftsack', 'Duftsack'),
    (r'Duftkissen', 'Duftkissen'),
    (r'Kraeutersack', 'Kraeutersack'),
    (r'Kräutersack', 'Kraeutersack'),

    # Holz-Deko
    (r'Sternschale', 'Holz-Deko'),
    (r'Schale\b', 'Schale'),
]

# Kategorisiere Produkte
produkttypen_count = Counter()
unkategorisiert = []

for product in products:
    name = product.get('name', '').strip()
    kategorisiert = False

    for pattern, typ in produkttypen_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            produkttypen_count[typ] += 1
            kategorisiert = True
            break

    if not kategorisiert:
        unkategorisiert.append(name)

print('=== FINALE PRODUKTTYPEN-UEBERSICHT ===')
print()
print(f'Gesamt Hauptprodukte: {len(products)}')
print(f'Kategorisiert: {len(products) - len(unkategorisiert)}')
print(f'Unkategorisiert: {len(unkategorisiert)}')
print()
print('| Produkttyp                              | Anzahl |')
print('|-----------------------------------------|--------|')
for typ, count in sorted(produkttypen_count.items(), key=lambda x: -x[1]):
    print(f'| {typ:39} | {count:>6} |')

print()
print(f'Summe kategorisiert: {sum(produkttypen_count.values())}')
print()
print('=== BEISPIELE UNKATEGORISIERT (erste 30) ===')
for name in unkategorisiert[:30]:
    print(f'- {name[:80]}')
