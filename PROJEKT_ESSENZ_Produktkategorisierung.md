# Projekt-Essenz: Produktkategorisierung Shopware 6.x

## Projektziel
Aus Shopware 6.x CSV-Exporten (produkte.csv, properties.csv) alle Produkttypen identifizieren für Filter-/Sortierfunktionen im Shop. Mehrfachzuordnung möglich (z.B. ein Bett kann gleichzeitig Polsterbett, Einzelbett, Kinderbett sein).

## Quelldaten
- **produkte.csv** (~52 MB): 25.433 Hauptprodukte (Zeilen ohne parent_id)
  - Spalten: id, parent_id, product_number, active, stock, name, description, price, etc.
- **properties.csv** (~8.8 MB): Property-Werte mit group_name (Holzart, Farbe, Größe, etc.)

## Erstellte Skripte

### 1. create_kategorien_excel_v2.py
- Einfache Kategorisierung (1 Produkt = 1 Kategorie)
- Ergebnis: 90.6% kategorisiert
- Output: `produktkategorien_v2.xlsx`

### 2. create_kategorien_excel_v3.py (AKTUELL)
- **Mehrfachzuordnung**: 1 Produkt kann mehreren Typen zugeordnet werden
- Zusätzliche Eigenschaften: Bettgrößen, Materialien, Zielgruppen, Saison
- Ergebnis: 90.5% kategorisiert, 49.2% mit Mehrfachzuordnung
- Output: `produktkategorien_v3_mehrfach.xlsx` (3 Sheets)

### 3. Hilfs-Skripte
- `analyze_produkttypen.py` - Erste Analyse
- `analyze_produkttypen_semantic.py` - Semantische Analyse
- `analyze_unkategorisiert.py` - Analyse der unkategorisierten Produkte
- `show_unkategorisiert.py` - Zeigt aktuelle unkategorisierte Produkte

## Kategorisierungsstruktur

### Hauptkategorien (20)
1. Schlafen (8.797 Produkte)
2. Kleidung (3.992)
3. Wohnen (3.739)
4. Intern (4.812)
5. Stoffe & Muster (3.421)
6. Heimtextilien (1.519)
7. Dekoration (1.271)
8. Geschenke & Gutscheine (1.264)
9. Küche & Haushalt (1.059)
10. Kosmetik & Pflege (582)
11. Wellness & Duft (572)
12. Lebensmittel (557)
13. Bücher & Medien (485)
14. Baby & Kinder (382)
15. Yoga & Meditation (332)
16. Beleuchtung (299)
17. Taschen & Beutel (214)
18. Badezimmer (166)
19. Garten (18)
20. UNKATEGORISIERT (2.406)

### Kategorie-Definition (Beispiel)
```python
KATEGORIEN = {
    ('Schlafen', 'Betten', 'Polsterbetten'): [
        (r'Polsterbett', 'Polsterbett'),
    ],
    ('Schlafen', 'Betten', 'Kinderbetten'): [
        (r'Kinderbett', 'Kinderbett'),
        (r'Gitterbett', 'Gitterbett'),
        (r'Babybett', 'Babybett'),
    ],
    # ... weitere Kategorien
}
```

### Produktlinien-Mapping
```python
# Bett-Serien
'Ryokan', 'Elfenbett', 'Tana', 'Elena', 'La Barca', 'Almeno', 'Arne' → Massivholzbetten
'G.Mahler', 'Tartini', 'Akumi', 'Calvino', 'Asanoha' → Design-Betten
'1924', 'Alpina' → Vintage-Betten

# Sofa-Serien
'Mollino', 'Somerset', 'Buddy' → Sofas

# Schrank-Serien
'Tonda', 'Piave' → Kleiderschränke
'Ettore', 'Prospero' → Wohnschränke

# Weitere Serien
'Wolke' → Matratzen
'Maturo' → Teppiche
'Elverum', 'Kaland', 'Stavang', 'Cheviot', 'Sletta' → Wollstoffe
```

### Zusätzliche Eigenschaften (für Mehrfachzuordnung)
```python
BETTGROESSEN = [
    (r'Einzelbett|90\s*x\s*200|100\s*x\s*200', 'Einzelbett'),
    (r'Doppelbett|140\s*x\s*200|180\s*x\s*200', 'Doppelbett'),
    # ...
]

MATERIALIEN = [
    (r'Massivholz|Buche|Eiche|Zirbe', 'Massivholz'),
    (r'Bio.Baumwolle|kbA', 'Bio-Baumwolle'),
    (r'Schurwolle|Merinowolle', 'Schurwolle'),
    # ...
]

ZIELGRUPPEN = [
    (r'Kinder|Kind', 'Kinder'),
    (r'Damen|Frauen', 'Damen'),
    # ...
]
```

## Aktuelle Ergebnisse (v3)

| Metrik | Wert |
|--------|------|
| Kategorisiert | 23.027 / 25.433 (90.5%) |
| Mit Mehrfachzuordnung | 12.507 (49.2%) |
| Max. Typen pro Produkt | 8 |
| Unkategorisiert | 2.406 (9.5%) |

### Verteilung Mehrfachzuordnung
- 1 Typ: 10.520 Produkte
- 2 Typen: 6.785 Produkte
- 3 Typen: 3.595 Produkte
- 4+ Typen: 2.127 Produkte

## Excel-Output (produktkategorien_v3_mehrfach.xlsx)

### Sheet 1: Kategorien
| Hauptkategorie | Unterkategorie | Produkttyp | Anzahl | Artikelnummern | Beispiel-Produkte |

### Sheet 2: Produkte-Mehrfach
| Artikelnummer | Produktname | Hauptkategorien | Produkttypen | Anzahl Typen | Eigenschaften |

### Sheet 3: Nur-Mehrfach
Nur Produkte mit 2+ Typen

## Offene Punkte / Nächste Schritte

### 1. Unkategorisierte Produkte (2.406)
Häufige Wörter in unkategorisierten Produkten:
- Buche (163x) - oft Möbelteile ohne klare Kategorie
- Baumwolle (82x) - meist in Beschreibungen
- Bettwäscheset (28x) - könnte als eigene Kategorie hinzugefügt werden
- Schlafdecke (17x) - könnte Decken zugeordnet werden

### 2. Mögliche Erweiterungen
- [ ] Bettwäscheset als Kategorie hinzufügen
- [ ] Schlafdecke → Decken zuordnen
- [ ] Mehr Möbel-Serien erkennen (Galanto, Scribble, etc.)
- [ ] Interne Artikel besser kategorisieren

### 3. Properties.csv nutzen
Die properties.csv enthält zusätzliche Attribute (Farbe, Größe, Material), die für erweiterte Filterung genutzt werden könnten.

## Wichtige Code-Patterns

### Regex für deutsche Umlaute
```python
r'Sch.ssel'     # Schüssel
r'M.tze'        # Mütze
r'F.llsack'     # Füllsack
r'.berzug'      # Überzug
r'Gr..enetikett' # Größenetikett
```

### Mehrfachzuordnung aktivieren
```python
# In create_kategorien_excel_v3.py:
# Produkt wird gegen ALLE Patterns geprüft (nicht nur bis zum ersten Match)
for (hauptkat, unterkat, typ), patterns in KATEGORIEN.items():
    for p in products:
        name = p.get('name', '').strip()
        for pattern, produkttyp in patterns:
            if re.search(pattern, name, re.IGNORECASE):
                produkt_kategorien[p['id']].append((hauptkat, unterkat, typ, produkttyp))
                break  # Nur einmal pro Kategorie-Typ, aber weiter mit nächster Kategorie
```

## Ausführung

```bash
# Version 2 (Einfach)
python create_kategorien_excel_v2.py

# Version 3 (Mehrfachzuordnung)
python create_kategorien_excel_v3.py

# Unkategorisierte analysieren
python show_unkategorisiert.py
```

## Datei-Übersicht

```
C:\Projekte\GE-ECommerce-Testing\
├── produkte.csv                          # Quelldaten (52 MB)
├── properties.csv                        # Quelldaten (8.8 MB)
├── create_kategorien_excel_v2.py         # Einfache Kategorisierung
├── create_kategorien_excel_v3.py         # Mehrfachzuordnung (AKTUELL)
├── produktkategorien_v2.xlsx             # Output v2
├── produktkategorien_v3_mehrfach.xlsx    # Output v3 (AKTUELL)
├── show_unkategorisiert.py               # Zeigt unkategorisierte Produkte
├── analyze_unkategorisiert.py            # Analysiert fehlende Patterns
└── PROJEKT_ESSENZ_Produktkategorisierung.md  # Diese Datei
```

---
Erstellt: 2026-01-28
Stand: 90.5% kategorisiert, 49.2% mit Mehrfachzuordnung
