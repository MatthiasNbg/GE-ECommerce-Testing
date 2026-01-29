# -*- coding: utf-8 -*-
"""
Semantische Produkttypen-Analyse fuer Shopware 6.x
Erkennt Produkttypen auch aus Kontext, Produktlinien und zusammengesetzten Begriffen
"""

import csv
import re
from collections import Counter, defaultdict

# =============================================================================
# PRODUKTLINIEN / SERIEN (Eigenname -> Produkttyp)
# =============================================================================
PRODUKTLINIEN = {
    # BETTEN
    'Akumi': 'Bett',
    'Calvino': 'Bett',
    'G.Mahler': 'Bett',
    'Ryokan': 'Bett',
    'Elfenbett': 'Bett',
    'Tartini': 'Bett',
    'Tana': 'Bett',
    'Arne': 'Bett',
    'La Barca': 'Bett',
    'Elena': 'Bett',
    'Madrassa': 'Bett',
    'Madras': 'Bett',
    'Asanoha': 'Bett',
    'Almeno': 'Bett',
    'Alpina': 'Bett',
    '1924': 'Bett',

    # SOFAS
    'Somerset': 'Sofa',
    'Lounge-Sofa': 'Sofa',
    'Mollino': 'Sofa',
    'Buddy': 'Sofa',

    # SESSEL
    'Alani': 'Sessel',

    # SCHRAENKE
    'Piave': 'Schrank',
    'Tonda': 'Schrank',
    'Ettore': 'Schrank',
    'Prospero': 'Schrank',

    # TISCHE
    'Alwy': 'Tisch',
    'Tanaro': 'Tisch',
    'Sereno': 'Tisch',

    # REGALE
    'Cube': 'Regal',
    'Mirato': 'Regal',

    # STOFFE
    'Elverum': 'Wollstoff',
    'Kaland': 'Wollstoff',
    'Stavang': 'Wollstoff',
    'Sletta': 'Wollstoff',
    'Cheviot': 'Wollstoff',

    # MATRATZEN
    'Wolke': 'Matratze',

    # TEPPICHE
    'Maturo': 'Teppich',
}

# =============================================================================
# SEMANTISCHE PRODUKTTYPEN-PATTERNS
# =============================================================================
PRODUKTTYPEN_PATTERNS = [
    # =========================================================================
    # BETTEN - Spezifische Typen
    # =========================================================================
    (r'Elfenbett', 'Elfenbett', 'Betten'),
    (r'Ryokan.?Bett', 'Ryokan-Bett', 'Betten'),
    (r'Polsterbett', 'Polsterbett', 'Betten'),
    (r'Familienbett', 'Familienbett', 'Betten'),
    (r'Boxspringbett', 'Boxspringbett', 'Betten'),
    (r'Etagenbett', 'Etagenbett', 'Betten'),
    (r'Hochbett', 'Hochbett', 'Betten'),
    (r'Gitterbett', 'Gitterbett', 'Betten'),
    (r'Kinderbett', 'Kinderbett', 'Betten'),
    (r'Babybett', 'Babybett', 'Betten'),
    (r'Balkenbett', 'Balkenbett', 'Betten'),
    (r'Massivholzbett', 'Massivholzbett', 'Betten'),
    (r'\bBett\b', 'Bett', 'Betten'),

    # Bett-Zubehoer
    (r'Betthaupt', 'Betthaupt', 'Bett-Zubehoer'),
    (r'Kopfhaupt', 'Kopfhaupt', 'Bett-Zubehoer'),
    (r'Fusshaupt', 'Fusshaupt', 'Bett-Zubehoer'),
    (r'Fu.haupt', 'Fusshaupt', 'Bett-Zubehoer'),
    (r'Bettkasten', 'Bettkasten', 'Bett-Zubehoer'),
    (r'Bettk.stchen', 'Bettkaestchen', 'Bett-Zubehoer'),
    (r'Sprossenbetthaupt', 'Sprossenbetthaupt', 'Bett-Zubehoer'),
    (r'Polsterbetthaupt', 'Polsterbetthaupt', 'Bett-Zubehoer'),
    (r'Polsterkopfhaupt', 'Polsterkopfhaupt', 'Bett-Zubehoer'),

    # =========================================================================
    # MATRATZEN & SCHLAFSYSTEME
    # =========================================================================
    (r'Naturlatexmatratze', 'Naturlatexmatratze', 'Matratzen'),
    (r'Naturlatex.Matratze', 'Naturlatexmatratze', 'Matratzen'),
    (r'Matratze', 'Matratze', 'Matratzen'),
    (r'Matratzen.Querschnitt', 'Matratzen-Muster', 'Muster'),
    (r'Lattenrost', 'Lattenrost', 'Lattenroste'),
    (r'Unterlagsrahmen', 'Unterlagsrahmen', 'Lattenroste'),
    (r'Schlafsystem', 'Schlafsystem', 'Schlafsysteme'),
    (r'Topper', 'Topper', 'Topper'),
    (r'Federelement', 'Federelement', 'Schlafsystem-Zubehoer'),

    # =========================================================================
    # BETTWAREN - Decken
    # =========================================================================
    (r'Kuscheldecken.berzug', 'Kuscheldecken-Ueberzug', 'Decken-Ueberzuege'),
    (r'Kuscheldecke', 'Kuscheldecke', 'Decken'),
    (r'Wohndecke', 'Wohndecke', 'Decken'),
    (r'Ganzjahresdecke', 'Ganzjahresdecke', 'Decken'),
    (r'Sommerdecke', 'Sommerdecke', 'Decken'),
    (r'Winterdecke', 'Winterdecke', 'Decken'),
    (r'Kombidecke', 'Kombidecke', 'Decken'),
    (r'Daunendecke', 'Daunendecke', 'Decken'),
    (r'Bettdecke', 'Bettdecke', 'Decken'),
    (r'\bDecke\b', 'Decke', 'Decken'),

    # =========================================================================
    # BETTWAREN - Kissen
    # =========================================================================
    (r'Schlafkissen', 'Schlafkissen', 'Kissen'),
    (r'Komfortkissen', 'Komfortkissen', 'Kissen'),
    (r'Kopfkissen', 'Kopfkissen', 'Kissen'),
    (r'Schlummerkissen', 'Schlummerkissen', 'Kissen'),
    (r'Lavendelkissen', 'Lavendelkissen', 'Duftkissen'),
    (r'Duftkissen', 'Duftkissen', 'Duftkissen'),
    (r'Kaminkissen', 'Kaminkissen', 'Duftkissen'),
    (r'Zierkissen', 'Zierkissen', 'Zierkissen'),
    (r'Sofakissen', 'Sofakissen', 'Sofakissen'),
    (r'Sitzkissen', 'Sitzkissen', 'Sitzkissen'),
    (r'Mondkissen', 'Mondkissen', 'Kissen'),
    (r'Stillkissen', 'Stillkissen', 'Baby-Kissen'),
    (r'Nackenrolle', 'Nackenrolle', 'Nackenrollen'),
    (r'\bKissen\b', 'Kissen', 'Kissen'),

    # =========================================================================
    # BETTWAREN - Ueberzuege & Bezuege
    # =========================================================================
    (r'Schlummerkissen.berzug', 'Schlummerkissen-Ueberzug', 'Kissen-Ueberzuege'),
    (r'Sofakissen.berzug', 'Sofakissen-Ueberzug', 'Kissen-Ueberzuege'),
    (r'Sofakissen..berzug', 'Sofakissen-Ueberzug', 'Kissen-Ueberzuege'),
    (r'Zierkissen.berzug', 'Zierkissen-Ueberzug', 'Kissen-Ueberzuege'),
    (r'Zierkissen..berzug', 'Zierkissen-Ueberzug', 'Kissen-Ueberzuege'),
    (r'Kissen.berzug', 'Kissen-Ueberzug', 'Kissen-Ueberzuege'),
    (r'Decken.berzug', 'Decken-Ueberzug', 'Decken-Ueberzuege'),
    (r'Kissenbezug', 'Kissenbezug', 'Kissen-Ueberzuege'),
    (r'Deckenbezug', 'Deckenbezug', 'Decken-Ueberzuege'),
    (r'Schonbezug', 'Schonbezug', 'Schonbezuege'),
    (r'.berzug', 'Ueberzug', 'Ueberzuege'),
    (r'Bezug', 'Bezug', 'Bezuege'),

    # =========================================================================
    # BETTWAREN - Unterbetten & Auflagen
    # =========================================================================
    (r'Unterbett', 'Unterbett', 'Unterbetten'),
    (r'Flanellauflage', 'Flanellauflage', 'Bettauflagen'),
    (r'Polsterauflage', 'Polsterauflage', 'Polsterauflagen'),
    (r'Wabenpolster', 'Wabenpolster', 'Bettauflagen'),

    # =========================================================================
    # BETTWAREN - Leintuecher
    # =========================================================================
    (r'Spannleintuch', 'Spannleintuch', 'Spannleintuecher'),
    (r'Leintuch', 'Leintuch', 'Leintuecher'),
    (r'\bLaken\b', 'Laken', 'Laken'),

    # =========================================================================
    # POLSTERMOEBEL
    # =========================================================================
    (r'Lounge.Sofa', 'Lounge-Sofa', 'Sofas'),
    (r'Ecksofa', 'Ecksofa', 'Sofas'),
    (r'Schlafsofa', 'Schlafsofa', 'Sofas'),
    (r'\bSofa\b', 'Sofa', 'Sofas'),
    (r'Sessel', 'Sessel', 'Sessel'),
    (r'Fauteuil', 'Fauteuil', 'Sessel'),
    (r'Ottomane', 'Ottomane', 'Sofas'),
    (r'Recamiere', 'Recamiere', 'Sofas'),
    (r'Polsterbank', 'Polsterbank', 'Baenke'),
    (r'Sitzhocker', 'Sitzhocker', 'Hocker'),
    (r'\bHocker\b', 'Hocker', 'Hocker'),
    (r'Stoffhusse', 'Stoffhusse', 'Husse'),

    # =========================================================================
    # SITZMOEBEL
    # =========================================================================
    (r'Stuhl', 'Stuhl', 'Stuehle'),
    (r'Sitzbank', 'Sitzbank', 'Baenke'),
    (r'\bBank\b', 'Bank', 'Baenke'),
    (r'Barhocker', 'Barhocker', 'Hocker'),

    # =========================================================================
    # TISCHE
    # =========================================================================
    (r'Sofatisch', 'Sofatisch', 'Tische'),
    (r'Beistelltisch', 'Beistelltisch', 'Tische'),
    (r'Couchtisch', 'Couchtisch', 'Tische'),
    (r'Esstisch', 'Esstisch', 'Tische'),
    (r'Schreibtisch', 'Schreibtisch', 'Tische'),
    (r'Nachttisch', 'Nachttisch', 'Tische'),
    (r'Konsolentisch', 'Konsolentisch', 'Tische'),
    (r'\bTisch\b', 'Tisch', 'Tische'),

    # =========================================================================
    # SCHRAENKE & AUFBEWAHRUNG
    # =========================================================================
    (r'Kleiderschrank', 'Kleiderschrank', 'Schraenke'),
    (r'Wohnschrank', 'Wohnschrank', 'Schraenke'),
    (r'\bSchrank\b', 'Schrank', 'Schraenke'),
    (r'Sideboard', 'Sideboard', 'Sideboards'),
    (r'Highboard', 'Highboard', 'Boards'),
    (r'Lowboard', 'Lowboard', 'Boards'),
    (r'\bRegal\b', 'Regal', 'Regale'),
    (r'Vitrine', 'Vitrine', 'Vitrinen'),
    (r'Garderobe', 'Garderobe', 'Garderoben'),
    (r'Kommode', 'Kommode', 'Kommoden'),
    (r'Truhe', 'Truhe', 'Truhen'),

    # =========================================================================
    # HEIMTEXTILIEN - Teppiche
    # =========================================================================
    (r'Wollteppich', 'Wollteppich', 'Teppiche'),
    (r'Naturteppich', 'Naturteppich', 'Teppiche'),
    (r'Teppichmuster', 'Teppichmuster', 'Muster'),
    (r'\bTeppich\b', 'Teppich', 'Teppiche'),

    # =========================================================================
    # HEIMTEXTILIEN - Vorhaenge & Rollos
    # =========================================================================
    (r'Faltrollo', 'Faltrollo', 'Rollos'),
    (r'Rollo', 'Rollo', 'Rollos'),
    (r'Vorhangstoff', 'Vorhangstoff', 'Stoffe'),
    (r'Vorhangbahn', 'Vorhangbahn', 'Vorhaenge'),
    (r'Vorhang', 'Vorhang', 'Vorhaenge'),
    (r'Gardine', 'Gardine', 'Gardinen'),
    (r'\bPlaid\b', 'Plaid', 'Plaids'),

    # =========================================================================
    # HEIMTEXTILIEN - Tischwaesche
    # =========================================================================
    (r'Tischdecke', 'Tischdecke', 'Tischwaesche'),
    (r'Tischw.sche', 'Tischwaesche', 'Tischwaesche'),
    (r'Untersetzer', 'Untersetzer', 'Tischwaesche'),

    # =========================================================================
    # STOFFE & MUSTER
    # =========================================================================
    (r'Wollstoff', 'Wollstoff', 'Stoffe'),
    (r'Stoffmuster', 'Stoffmuster', 'Muster'),
    (r'Meterware', 'Meterware', 'Meterware'),
    (r'Stofffahne', 'Stofffahne', 'Intern'),

    # =========================================================================
    # BELEUCHTUNG
    # =========================================================================
    (r'H.ngeleuchte', 'Haengeleuchte', 'Leuchten'),
    (r'Pendelleuchte', 'Pendelleuchte', 'Leuchten'),
    (r'Stehleuchte', 'Stehleuchte', 'Leuchten'),
    (r'Tischleuchte', 'Tischleuchte', 'Leuchten'),
    (r'Wandleuchte', 'Wandleuchte', 'Leuchten'),
    (r'Leuchte', 'Leuchte', 'Leuchten'),
    (r'Lampe', 'Lampe', 'Leuchten'),

    # =========================================================================
    # BADEZIMMER
    # =========================================================================
    (r'Handtuch', 'Handtuch', 'Handtuecher'),
    (r'Badetuch', 'Badetuch', 'Handtuecher'),
    (r'Bademantel', 'Bademantel', 'Bademaentel'),
    (r'Waschhandschuh', 'Waschhandschuh', 'Waschhandschuhe'),

    # =========================================================================
    # KLEIDUNG - Oberteile
    # =========================================================================
    (r'Langarmshirt', 'Langarmshirt', 'Shirts'),
    (r'Schlafshirt', 'Schlafshirt', 'Nachtwaesche'),
    (r'Shirt.Langarm', 'Langarmshirt', 'Shirts'),
    (r'\bShirt\b', 'Shirt', 'Shirts'),
    (r'T.Shirt', 'T-Shirt', 'Shirts'),
    (r'Pullover', 'Pullover', 'Pullover'),
    (r'Strickjacke', 'Strickjacke', 'Strickjacken'),
    (r'Cardigan', 'Cardigan', 'Strickjacken'),
    (r'Bluse', 'Bluse', 'Blusen'),
    (r'\bTop\b', 'Top', 'Tops'),
    (r'Weste', 'Weste', 'Westen'),
    (r'\bStrick\b', 'Strickware', 'Strickwaren'),

    # =========================================================================
    # KLEIDUNG - Unterteile & Kleider
    # =========================================================================
    (r'Schlafhose', 'Schlafhose', 'Nachtwaesche'),
    (r'Leggings', 'Leggings', 'Hosen'),
    (r'Jeans', 'Jeans', 'Hosen'),
    (r'\bHose\b', 'Hose', 'Hosen'),
    (r'\bRock\b', 'Rock', 'Roecke'),
    (r'\bKleid\b', 'Kleid', 'Kleider'),

    # =========================================================================
    # KLEIDUNG - Oberbekleidung
    # =========================================================================
    (r'Jacke', 'Jacke', 'Jacken'),
    (r'Mantel', 'Mantel', 'Maentel'),

    # =========================================================================
    # KLEIDUNG - Nachtwaesche
    # =========================================================================
    (r'Pyjama', 'Pyjama', 'Nachtwaesche'),
    (r'Nachthemd', 'Nachthemd', 'Nachtwaesche'),
    (r'Schlafanzug', 'Schlafanzug', 'Nachtwaesche'),

    # =========================================================================
    # KLEIDUNG - Accessoires
    # =========================================================================
    (r'\bSchal\b', 'Schal', 'Schals'),
    (r'M.tze', 'Muetze', 'Muetzen'),
    (r'Handschuhe', 'Handschuhe', 'Handschuhe'),
    (r'Socken', 'Socken', 'Socken'),
    (r'Hausschuhe', 'Hausschuhe', 'Hausschuhe'),

    # =========================================================================
    # BABY & KINDER
    # =========================================================================
    (r'Schlafsack', 'Schlafsack', 'Baby-Schlafsaecke'),
    (r'Strampelsack', 'Strampelsack', 'Baby-Schlafsaecke'),
    (r'Puckdecke', 'Puckdecke', 'Baby-Textilien'),
    (r'Wickeldecke', 'Wickeldecke', 'Baby-Textilien'),
    (r'Tragetuch', 'Tragetuch', 'Baby-Zubehoer'),
    (r'\bBaby\b', 'Baby-Artikel', 'Baby'),
    (r'\bKinder\b', 'Kinder-Artikel', 'Kinder'),

    # =========================================================================
    # WELLNESS & DUFT
    # =========================================================================
    (r'Duftendes', 'Duftprodukt', 'Duftprodukte'),
    (r'R.ucherwerk', 'Raeucherwerk', 'Raeucherwerk'),
    (r'R.ucherkegel', 'Raeucherkegel', 'Raeucherwerk'),
    (r'R.ucherst.bchen', 'Raeucher-Staebchen', 'Raeucherwerk'),
    (r'.therisch', 'Aetherisches Oel', 'Aetherische Oele'),
    (r'Raumduft', 'Raumduft', 'Raumduefte'),
    (r'Zirben', 'Zirbenprodukt', 'Zirbenprodukte'),
    (r'W.rmekissen', 'Waermekissen', 'Waermekissen'),
    (r'W.rmflasche', 'Waermflasche', 'Waermflaschen'),
    (r'K.hlkissen', 'Kuehlkissen', 'Kuehlkissen'),

    # =========================================================================
    # YOGA & MEDITATION
    # =========================================================================
    (r'Yogamatte', 'Yogamatte', 'Yoga'),
    (r'Yogablock', 'Yogablock', 'Yoga'),
    (r'Yogakissen', 'Yogakissen', 'Yoga'),
    (r'\bYoga\b', 'Yoga-Zubehoer', 'Yoga'),
    (r'Meditation', 'Meditations-Zubehoer', 'Meditation'),
    (r'ZAFU', 'Meditationskissen', 'Meditation'),

    # =========================================================================
    # KERZEN - Semantisch abgeleitet
    # =========================================================================
    (r'Bienenwachskerze', 'Bienenwachskerze', 'Kerzen'),
    (r'Rapswachskerze', 'Rapswachskerze', 'Kerzen'),
    (r'Figurkerze', 'Figurkerze', 'Kerzen'),
    (r'Sternenkerze', 'Sternenkerze', 'Kerzen'),
    (r'Stumpenkerze', 'Stumpenkerze', 'Kerzen'),
    (r'Teelicht', 'Teelicht', 'Kerzen'),
    (r'\bKerze\b', 'Kerze', 'Kerzen'),
    (r'Bienenwachs', 'Bienenwachsprodukt', 'Bienenwachs'),

    # =========================================================================
    # KUECHE & HAUSHALT
    # =========================================================================
    (r'Geschirr', 'Geschirr', 'Geschirr'),
    (r'Teller', 'Teller', 'Geschirr'),
    (r'Schale', 'Schale', 'Geschirr'),
    (r'Tasse', 'Tasse', 'Geschirr'),
    (r'\bBecher\b', 'Becher', 'Geschirr'),
    (r'\bGlas\b', 'Glas', 'Glaeser'),
    (r'Besteck', 'Besteck', 'Besteck'),
    (r'\bVase\b', 'Vase', 'Vasen'),
    (r'\bKorb\b', 'Korb', 'Koerbe'),

    # =========================================================================
    # DEKORATION
    # =========================================================================
    (r'Spiegel', 'Spiegel', 'Spiegel'),
    (r'Baldachin', 'Baldachin', 'Baldachine'),
    (r'Weihnachtsschmuck', 'Weihnachtsschmuck', 'Weihnachten'),
    (r'Weihnacht', 'Weihnachtsartikel', 'Weihnachten'),

    # =========================================================================
    # REINIGUNG & PFLEGE
    # =========================================================================
    (r'Reiniger', 'Reiniger', 'Reinigungsmittel'),
    (r'Waschmittel', 'Waschmittel', 'Waschmittel'),
    (r'Pflegeset', 'Pflegeset', 'Pflegemittel'),
    (r'Pflegemittel', 'Pflegemittel', 'Pflegemittel'),

    # =========================================================================
    # LEBENSMITTEL
    # =========================================================================
    (r'Espresso', 'Espresso', 'Lebensmittel'),
    (r'Kaffee', 'Kaffee', 'Lebensmittel'),
    (r'\bTee\b', 'Tee', 'Lebensmittel'),
    (r'Oliven.l', 'Olivenoel', 'Lebensmittel'),
    (r'\bBrot\b', 'Brot', 'Lebensmittel'),
    (r'Schokolade', 'Schokolade', 'Lebensmittel'),

    # =========================================================================
    # BUECHER & MEDIEN
    # =========================================================================
    (r'\bBuch\b', 'Buch', 'Buecher'),
    (r'Buch:', 'Buch', 'Buecher'),
    (r'Katalog', 'Katalog', 'Kataloge'),
    (r'Postkarte', 'Postkarte', 'Postkarten'),
    (r'Karte', 'Karte', 'Karten'),

    # =========================================================================
    # TASCHEN & BEUTEL
    # =========================================================================
    (r'Tasche', 'Tasche', 'Taschen'),
    (r'Beutel', 'Beutel', 'Beutel'),

    # =========================================================================
    # MOEBEL-ZUBEHOER
    # =========================================================================
    (r'R.ckenlehne', 'Rueckenlehne', 'Moebel-Zubehoer'),
    (r'Fachtr.ger', 'Fachtraeger', 'Moebel-Zubehoer'),
    (r'Mittelfu.', 'Mittelfuss', 'Moebel-Zubehoer'),
    (r'Mittelfuss', 'Mittelfuss', 'Moebel-Zubehoer'),
    (r'Mittelsteg', 'Mittelsteg', 'Moebel-Zubehoer'),
    (r'Seitenwangen', 'Seitenwangen', 'Moebel-Zubehoer'),
    (r'T.rf.llung', 'Tuerfuellung', 'Moebel-Zubehoer'),
    (r'Schublade', 'Schublade', 'Moebel-Zubehoer'),
    (r'Fachbrett', 'Fachbrett', 'Moebel-Zubehoer'),
    (r'Beschlag', 'Beschlag', 'Moebel-Zubehoer'),
    (r'Montageleiste', 'Montageleiste', 'Moebel-Zubehoer'),
    (r'St.lper', 'Stuelper', 'Moebel-Zubehoer'),
    (r'Holzteil', 'Holzteil', 'Moebel-Zubehoer'),
    (r'Rolle\b', 'Rolle', 'Moebel-Zubehoer'),
    (r'Lade\b', 'Lade', 'Moebel-Zubehoer'),
    (r'F..e', 'Fuesse', 'Moebel-Zubehoer'),

    # =========================================================================
    # OUTDOOR & GARTEN
    # =========================================================================
    (r'Liege', 'Liege', 'Gartenmoebel'),
    (r'Gartenm.bel', 'Gartenmoebel', 'Gartenmoebel'),
    (r'Sonnenschirm', 'Sonnenschirm', 'Gartenmoebel'),

    # =========================================================================
    # GESCHENKE & AKTIONEN
    # =========================================================================
    (r'Geschenk', 'Geschenk', 'Geschenke'),
    (r'Gutschein', 'Gutschein', 'Gutscheine'),
    (r'Gutschrift', 'Gutschrift', 'Intern'),
    (r'Kennenlerngutschein', 'Kennenlerngutschein', 'Gutscheine'),

    # =========================================================================
    # INTERN / NICHT FUER SHOP
    # =========================================================================
    (r'Karton', 'Karton', 'Intern'),
    (r'Produkthangtag', 'Produkthangtag', 'Intern'),
    (r'Hangtag', 'Hangtag', 'Intern'),
    (r'Etikett', 'Etikett', 'Intern'),
    (r'Gr..enetikett', 'Groessenetikett', 'Intern'),
    (r'Pflegeetikett', 'Pflegeetikett', 'Intern'),
    (r'Aufkleber', 'Aufkleber', 'Intern'),
    (r'Banderole', 'Banderole', 'Intern'),
    (r'Produktbegleiter', 'Produktbegleiter', 'Intern'),
    (r'Folder', 'Folder', 'Intern'),
    (r'Probe', 'Probe', 'Intern'),
    (r'Gratis', 'Gratis-Artikel', 'Aktionen'),
    (r'OUTLET', 'Outlet-Artikel', 'Aktionen'),
    (r'Outlet', 'Outlet-Artikel', 'Aktionen'),
    (r'Rabatt', 'Rabatt', 'Aktionen'),
    (r'Pr.mie', 'Praemie', 'Aktionen'),
    (r'Angebot', 'Angebot', 'Aktionen'),
    (r'Versandkostenfrei', 'Versandkostenfrei', 'Aktionen'),
    (r'SHOP', 'Shop-Artikel', 'Intern'),
    (r'Shop', 'Shop-Artikel', 'Intern'),
    (r'Laden', 'Laden-Artikel', 'Intern'),
    (r'Mindestkaufbetrag', 'Mindestkaufbetrag', 'Intern'),
    (r'Einkauf', 'Einkauf', 'Intern'),
    (r'NUR', 'NUR-Artikel', 'Intern'),
    (r'FREI', 'Frei-Artikel', 'Intern'),
    (r'frei', 'Frei-Artikel', 'Intern'),
    (r'P.rchen', 'Paerchen-Artikel', 'Aktionen'),
    (r'Ihr\b', 'Ihr-Artikel', 'Intern'),
    (r'Ihre\b', 'Ihre-Artikel', 'Intern'),

    # =========================================================================
    # SONDERANFERTIGUNGEN
    # =========================================================================
    (r'Sonderanfertigung', 'Sonderanfertigung', 'Sonderanfertigungen'),
    (r'Ma.anfertigung', 'Massanfertigung', 'Massanfertigungen'),
    (r'SET:', 'Set', 'Sets'),
    (r'Set:', 'Set', 'Sets'),

    # =========================================================================
    # ZUSAETZLICHE SEMANTISCHE TYPEN
    # =========================================================================
    # Leuchtmittel
    (r'Leuchtmittel', 'Leuchtmittel', 'Leuchtmittel'),
    (r'\bLED\b', 'LED-Leuchtmittel', 'Leuchtmittel'),
    (r'Gl.hbirne', 'Gluehbirne', 'Leuchtmittel'),

    # Filzprodukte
    (r'aus Filz', 'Filzprodukt', 'Filzprodukte'),
    (r'Filzauflage', 'Filzauflage', 'Filzprodukte'),
    (r'Filztier', 'Filztier', 'Filzprodukte'),

    # Glaswaren
    (r'Glaskaraffe', 'Karaffe', 'Glaswaren'),
    (r'Karaffe', 'Karaffe', 'Glaswaren'),

    # Seifen
    (r'Seife', 'Seife', 'Seifen'),
    (r'Gallseife', 'Gallseife', 'Seifen'),

    # Ostern
    (r'Osterei', 'Osterei', 'Ostern'),
    (r'Ostern', 'Osterartikel', 'Ostern'),

    # Kraeutersack
    (r'Kr.utersack', 'Kraeutersack', 'Kraeutersaecke'),
    (r'R.ucherb.ndel', 'Raeucher-Buendel', 'Raeucherwerk'),

    # Weidenkorb
    (r'Weidenkorb', 'Weidenkorb', 'Koerbe'),

    # Moebel-Serien als Sofa
    (r'Polstersofa', 'Polstersofa', 'Sofas'),
    (r'Lana\s', 'Lana-Moebel', 'Moebel'),

    # Gestell / Zubehoer
    (r'Gestell\b', 'Gestell', 'Moebel-Zubehoer'),
    (r'Gestrick', 'Gestrick', 'Moebel-Zubehoer'),

    # Deckel
    (r'\bDeckel\b', 'Deckel', 'Zubehoer'),

    # Diverses
    (r'Nussknacker', 'Nussknacker', 'Kuechenzubehoer'),
    (r'Windel', 'Windel', 'Baby'),
    (r'V.gelchen', 'Deko-Voegel', 'Dekoration'),
    (r'Tropfen\b', 'Glas-Tropfen', 'Glaswaren'),
    (r'Gleitessenz', 'Gleitessenz', 'Pflegemittel'),
    (r'Sitzauflage', 'Sitzauflage', 'Auflagen'),
    (r'Sockel', 'Sockel', 'Moebel-Zubehoer'),
    (r'\bFach\b', 'Fach', 'Moebel-Zubehoer'),
    (r'Aufbewahrungsbox', 'Aufbewahrungsbox', 'Aufbewahrung'),
    (r'\bBox\b', 'Box', 'Aufbewahrung'),
    (r'Gef..', 'Gefaess', 'Gefaesse'),
]


def analyze_products():
    """Hauptanalyse-Funktion"""

    # Lese alle Hauptprodukte
    with open('produkte.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        products = []
        for row in reader:
            if not row.get('parent_id', '').strip():
                products.append(row)

    # Zaehler
    produkttypen_count = Counter()
    kategorien_count = Counter()
    unkategorisiert = []

    # Analyse jedes Produkts
    for product in products:
        name = product.get('name', '').strip()
        kategorisiert = False

        # 1. Pruefe Produktlinien zuerst
        for serie, typ in PRODUKTLINIEN.items():
            if serie in name:
                produkttypen_count[f"{typ} ({serie})"] += 1
                kategorien_count[typ] += 1
                kategorisiert = True
                break

        if kategorisiert:
            continue

        # 2. Pruefe Pattern-basierte Typen
        for pattern, typ, kategorie in PRODUKTTYPEN_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                produkttypen_count[typ] += 1
                kategorien_count[kategorie] += 1
                kategorisiert = True
                break

        if not kategorisiert:
            unkategorisiert.append(name)

    # Ausgabe
    print('=' * 80)
    print('SEMANTISCHE PRODUKTTYPEN-ANALYSE')
    print('=' * 80)
    print()
    print(f'Gesamt Hauptprodukte: {len(products):,}')
    print(f'Kategorisiert: {len(products) - len(unkategorisiert):,} ({100*(len(products) - len(unkategorisiert))/len(products):.1f}%)')
    print(f'Unkategorisiert: {len(unkategorisiert):,} ({100*len(unkategorisiert)/len(products):.1f}%)')
    print()

    print('=' * 80)
    print('PRODUKTTYPEN (Top 80, nach Anzahl)')
    print('=' * 80)
    print()
    print(f'{"Produkttyp":<45} | {"Anzahl":>7} |')
    print('-' * 57)
    for typ, count in produkttypen_count.most_common(80):
        print(f'{typ:<45} | {count:>7} |')

    print()
    print('=' * 80)
    print('HAUPTKATEGORIEN (fuer Filter-Gruppen)')
    print('=' * 80)
    print()
    print(f'{"Kategorie":<35} | {"Anzahl":>7} |')
    print('-' * 47)
    for kat, count in sorted(kategorien_count.items(), key=lambda x: -x[1]):
        print(f'{kat:<35} | {count:>7} |')

    print()
    print('=' * 80)
    print('UNKATEGORISIERT (erste 50 Beispiele)')
    print('=' * 80)
    for name in unkategorisiert[:50]:
        print(f'  - {name[:75]}')

    return produkttypen_count, kategorien_count, unkategorisiert


if __name__ == '__main__':
    analyze_products()
