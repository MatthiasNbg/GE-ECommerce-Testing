# -*- coding: utf-8 -*-
"""
Zeigt unkategorisierte Produkte
"""
import csv
import re
import sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

# Importiere KATEGORIEN aus dem Hauptskript
from create_kategorien_excel_v2 import KATEGORIEN

# Lese Produkte
with open('produkte.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    products = [row for row in reader if not row.get('parent_id', '').strip()]

# Kategorisiere
kategorisiert = set()
for (hauptkat, unterkat, typ), patterns in KATEGORIEN.items():
    for p in products:
        if p['id'] in kategorisiert:
            continue
        name = p.get('name', '').strip()
        for pattern, produkttyp in patterns:
            if re.search(pattern, name, re.IGNORECASE):
                kategorisiert.add(p['id'])
                break

# Zeige unkategorisierte
print('UNKATEGORISIERTE PRODUKTE (erste 100):')
print('='*70)
count = 0
words = Counter()
for p in products:
    if p['id'] not in kategorisiert:
        count += 1
        name = p.get('name', '')
        if count <= 100:
            print(f'{count:3}. {name[:70]}')
        for word in re.findall(r'[A-ZÄÖÜ][a-zäöüß]+', name):
            if len(word) > 4:
                words[word] += 1

print(f'\nTotal unkategorisiert: {count}')
print('\nHÄUFIGE WÖRTER:')
for word, cnt in words.most_common(50):
    print(f'  {word}: {cnt}')
