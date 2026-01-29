# -*- coding: utf-8 -*-
import csv
import re
from collections import Counter, defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Produktlinien
PRODUKTLINIEN = {
    'Akumi': 'Bett', 'Calvino': 'Bett', 'G.Mahler': 'Bett', 'Ryokan': 'Bett',
    'Elfenbett': 'Bett', 'Tartini': 'Bett', 'Tana': 'Bett', 'Arne': 'Bett',
    'La Barca': 'Bett', 'Elena': 'Bett', 'Madrassa': 'Bett', 'Madras': 'Bett',
    'Asanoha': 'Bett', 'Almeno': 'Bett', 'Alpina': 'Bett', '1924': 'Bett',
    'Somerset': 'Sofa', 'Mollino': 'Sofa', 'Buddy': 'Sofa', 'Lana': 'Sofa',
    'Alani': 'Sessel', 'Piave': 'Schrank', 'Tonda': 'Schrank', 'Ettore': 'Schrank',
    'Prospero': 'Schrank', 'Alwy': 'Tisch', 'Tanaro': 'Tisch', 'Sereno': 'Tisch',
    'Cube': 'Regal', 'Mirato': 'Regal', 'Elverum': 'Wollstoff', 'Kaland': 'Wollstoff',
    'Stavang': 'Wollstoff', 'Sletta': 'Wollstoff', 'Cheviot': 'Wollstoff',
    'Wolke': 'Matratze', 'Maturo': 'Teppich',
}

PATTERNS = [
    r'Bett', r'Matratze', r'Lattenrost', r'Schlafsystem', r'Topper',
    r'Sofa', r'Sessel', r'Hocker', r'Stuhl', r'Bank',
    r'Tisch', r'Schrank', r'Regal', r'Sideboard', r'Kommode', r'Vitrine', r'Garderobe', r'Truhe',
    r'Teppich', r'Vorhang', r'Gardine', r'Rollo', r'Plaid',
    r'Decke', r'Kissen', r'bezug', r'Laken', r'Leintuch', r'Unterbett',
    r'Leuchte', r'Lampe', r'LED',
    r'Handtuch', r'Bademantel', r'Waschhandschuh',
    r'Shirt', r'Pullover', r'Bluse', r'Top', r'Jacke', r'Mantel', r'Strickjacke', r'Cardigan',
    r'Hose', r'Rock', r'Kleid', r'Leggings', r'Jeans',
    r'Pyjama', r'Nachthemd', r'Schlafanzug', r'Schlafhose', r'Schlafshirt',
    r'Schal', r'Socken', r'Hausschuhe', r'Handschuhe',
    r'Yoga', r'Meditation', r'ZAFU',
    r'Kerze', r'Bienenwachs', r'Raumduft', r'Zirben',
    r'Geschirr', r'Teller', r'Schale', r'Tasse', r'Becher', r'Glas', r'Vase', r'Korb', r'Besteck',
    r'Spiegel', r'Baldachin', r'Weihnacht',
    r'Reiniger', r'Waschmittel', r'Seife', r'Pflege',
    r'Espresso', r'Kaffee', r'Tee', r'Brot', r'Schokolade',
    r'Buch', r'Katalog', r'Postkarte', r'Karte',
    r'Tasche', r'Beutel',
    r'Karton', r'Hangtag', r'Etikett', r'Aufkleber', r'Banderole', r'Stofffahne', r'Produktbegleiter',
    r'Gratis', r'OUTLET', r'Outlet', r'Rabatt', r'Gutschein', r'Gutschrift', r'Angebot',
    r'Shop', r'Laden', r'SHOP', r'NUR', r'FREI',
    r'Sonderanfertigung', r'SET:', r'Set:',
    r'Betthaupt', r'Kopfhaupt', r'Bettkasten', r'Mittelfu', r'Mittelsteg',
    r'Seitenwangen', r'Schublade', r'Fachbrett', r'Beschlag',
    r'Holzteil', r'Rolle', r'Lade',
    r'Meterware', r'Stoffmuster', r'Teppichmuster', r'Wollstoff', r'Vorhangstoff',
    r'Filz', r'Karaffe', r'Ostern', r'Osterei', r'Weidenkorb',
    r'Gestell', r'Sockel', r'Fach', r'Box',
    r'Baby', r'Kinder', r'Schlafsack', r'Strampelsack', r'Stillkissen', r'Tragetuch', r'Windel',
    r'Polsterbank', r'Polstersofa', r'Polsterauflage', r'Wabenpolster', r'Flanellauflage',
    r'Stoffhusse', r'Schonbezug',
]

# Neue Patterns fuer fehlende Typen
NEUE_PATTERNS = {
    'Schuhe': [r'Stiefelette', r'Stiefel', r'Sneaker', r'Ballerina', r'Leinenschuhe', r'Schuh'],
    'Kleidung-Zusatz': [r'Jazzpants', r'Poncho', r'Pullunder', r'Blazer'],
    'Accessoires': [r'Guertel', r'Gürtel'],
    'Deko-Anhaenger': [r'Anhaenger', r'Anhänger', r'Astholz', r'Holzanhaenger'],
    'Weihnachten': [r'Stern\b', r'Engel', r'Adventkalender', r'Schneemann'],
    'Ostern-Deko': [r'Hase\b', r'Ei\b', r'Eier\b'],
    'Geschenk-Verpackung': [r'Geschenkspapier', r'Geschenkverpackung', r'Bogen'],
    'Lebensmittel': [r'Sirup', r'Fruchtaufstrich', r'Honig', r'Sonnentor', r'Marmelade'],
    'Duft-Wellness': [r'Badekonfekt', r'Bluetenduft', r'Blütenduft', r'Duftsaeckchen', r'Duftsäckchen'],
    'Kueche': [r'Schuessel', r'Schüssel', r'Tablett', r'Serviette', r'Kochschuerze', r'Topflappen'],
    'Haushalt': [r'Klarspueler', r'Klarspüler', r'Handspuelmittel', r'Haushaltstuecher'],
    'Moebel-Serien': [r'Fauteuil', r'Lorea', r'Kurami', r'Esempio', r'Kyushu', r'Tesoro', r'Kristian', r'Kador'],
    'Moebel-Zubehoer': [r'Korpus', r'Modul', r'Ablageboard', r'Platte\b', r'Kiste'],
    'Kosmetik': [r'Kosmetik', r'Lippenpflege', r'Creme\b'],
    'Textil-Stoffe': [r'Voile', r'Satin', r'Reinleinen', r'Halbleinen'],
    'Fuellmaterial': [r'Fuellsack', r'Füllsack', r'Abfuellung', r'Bulk'],
    'Aromaoel': [r'Aromaoel', r'Aromaöl'],
    'Tagesliege': [r'Tagesliege'],
    'Intern-Versand': [r'Versandkostenanteil', r'Spedition', r'Preisliste', r'UNIQUE', r'Aktion\b'],
}

# Lese Produkte
with open('produkte.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    products = [row for row in reader if not row.get('parent_id', '').strip()]

# Finde unkategorisierte
unkategorisiert = []
for p in products:
    name = p.get('name', '').strip()
    found = False
    for serie in PRODUKTLINIEN:
        if serie in name:
            found = True
            break
    if not found:
        for pattern in PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                found = True
                break
    if not found:
        unkategorisiert.append(name)

# Kategorisiere mit neuen Patterns
neue_kategorien = defaultdict(list)
immer_noch_unkategorisiert = []

for name in unkategorisiert:
    found = False
    for kategorie, patterns in NEUE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, name, re.IGNORECASE):
                neue_kategorien[kategorie].append(name)
                found = True
                break
        if found:
            break
    if not found:
        immer_noch_unkategorisiert.append(name)

print('=' * 80)
print('FEHLENDE PRODUKTTYPEN - VORSCHLAG ZUR ERGAENZUNG')
print('=' * 80)
print()
print(f'Urspruenglich unkategorisiert: {len(unkategorisiert)}')
print(f'Davon neu erkannt: {sum(len(v) for v in neue_kategorien.values())}')
print(f'Weiterhin unkategorisiert: {len(immer_noch_unkategorisiert)}')
print()

print('=' * 80)
print('NEUE PRODUKTTYPEN ZUM HINZUFUEGEN')
print('=' * 80)
print()
for kategorie, items in sorted(neue_kategorien.items(), key=lambda x: -len(x[1])):
    print(f'### {kategorie} ({len(items)} Produkte)')
    for item in items[:5]:
        print(f'    - {item[:70]}')
    if len(items) > 5:
        print(f'    ... und {len(items)-5} weitere')
    print()

print('=' * 80)
print('WEITERHIN UNKATEGORISIERT (erste 100)')
print('=' * 80)
print()
for i, name in enumerate(immer_noch_unkategorisiert[:100], 1):
    print(f'{i:3}. {name[:75]}')
