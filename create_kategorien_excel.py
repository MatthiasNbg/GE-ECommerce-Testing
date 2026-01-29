# -*- coding: utf-8 -*-
"""
Erstellt eine Excel-Datei mit Produktkategorisierung und Artikelnummern
"""

import csv
import re
from collections import defaultdict
import pandas as pd

# =============================================================================
# KATEGORIE-DEFINITIONEN
# =============================================================================

KATEGORIEN = {
    # SCHLAFEN
    ('Schlafen', 'Betten', 'Massivholzbetten'): [
        (r'Ryokan', 'Ryokan-Bett'),
        (r'Elfenbett', 'Elfenbett'),
        (r'Tana\b', 'Tana-Bett'),
        (r'Elena', 'Elena-Bett'),
        (r'La Barca', 'La Barca-Bett'),
        (r'Almeno', 'Almeno-Bett'),
        (r'Arne\b', 'Arne-Bett'),
    ],
    ('Schlafen', 'Betten', 'Design-Betten'): [
        (r'G\.Mahler', 'G.Mahler-Bett'),
        (r'Tartini', 'Tartini-Bett'),
        (r'Akumi', 'Akumi-Bett'),
        (r'Calvino', 'Calvino-Bett'),
        (r'Asanoha', 'Asanoha-Bett'),
        (r'Madrassa', 'Madrassa-Bett'),
        (r'Madras\b', 'Madras-Bett'),
    ],
    ('Schlafen', 'Betten', 'Vintage-Betten'): [
        (r'1924', '1924-Bett'),
        (r'Alpina', 'Alpina-Bett'),
    ],
    ('Schlafen', 'Betten', 'Polsterbetten'): [
        (r'Polsterbett', 'Polsterbett'),
    ],
    ('Schlafen', 'Betten', 'Kinderbetten'): [
        (r'Kinderbett', 'Kinderbett'),
        (r'Gitterbett', 'Gitterbett'),
        (r'Hochbett', 'Hochbett'),
        (r'Babybett', 'Babybett'),
        (r'Etagenbett', 'Etagenbett'),
    ],
    ('Schlafen', 'Betten', 'Betten allgemein'): [
        (r'\bBett\b', 'Bett'),
    ],
    ('Schlafen', 'Matratzen & Lattenroste', 'Matratzen'): [
        (r'Wolke', 'Wolke-Matratze'),
        (r'Matratze', 'Matratze'),
    ],
    ('Schlafen', 'Matratzen & Lattenroste', 'Lattenroste'): [
        (r'Lattenrost', 'Lattenrost'),
        (r'Unterlagsrahmen', 'Unterlagsrahmen'),
    ],
    ('Schlafen', 'Matratzen & Lattenroste', 'Schlafsysteme'): [
        (r'Schlafsystem', 'Schlafsystem'),
        (r'Federelement', 'Federelement'),
    ],
    ('Schlafen', 'Matratzen & Lattenroste', 'Topper'): [
        (r'Topper', 'Topper'),
    ],
    ('Schlafen', 'Bettausstattung', 'Unterbetten'): [
        (r'Unterbett', 'Unterbett'),
        (r'Flanellauflage', 'Flanellauflage'),
        (r'Wabenpolster', 'Wabenpolster'),
    ],
    ('Schlafen', 'Bettausstattung', 'Betthäupter'): [
        (r'Polsterbetthaupt', 'Polsterbetthaupt'),
        (r'Polsterkopfhaupt', 'Polsterkopfhaupt'),
        (r'Sprossenbetthaupt', 'Sprossenbetthaupt'),
        (r'Betthaupt', 'Betthaupt'),
        (r'Kopfhaupt', 'Kopfhaupt'),
        (r'Fu.haupt', 'Fußhaupt'),
    ],
    ('Schlafen', 'Bettausstattung', 'Bett-Zubehör'): [
        (r'Bettkasten', 'Bettkasten'),
        (r'Bettk.stchen', 'Bettkästchen'),
        (r'Mittelsteg', 'Mittelsteg'),
        (r'Mittelfu', 'Mittelfuß'),
    ],
    ('Schlafen', 'Decken', 'Ganzjahresdecken'): [
        (r'Ganzjahresdecke', 'Ganzjahresdecke'),
        (r'Kombidecke', 'Kombidecke'),
    ],
    ('Schlafen', 'Decken', 'Sommerdecken'): [
        (r'Sommerdecke', 'Sommerdecke'),
    ],
    ('Schlafen', 'Decken', 'Winterdecken'): [
        (r'Winterdecke', 'Winterdecke'),
        (r'Daunendecke', 'Daunendecke'),
    ],
    ('Schlafen', 'Decken', 'Wohndecken'): [
        (r'Wohndecke', 'Wohndecke'),
        (r'Kuscheldecke', 'Kuscheldecke'),
    ],
    ('Schlafen', 'Decken', 'Decken allgemein'): [
        (r'\bDecke\b', 'Decke'),
    ],
    ('Schlafen', 'Kissen', 'Schlafkissen'): [
        (r'Schlafkissen', 'Schlafkissen'),
        (r'Komfortkissen', 'Komfortkissen'),
        (r'Schlummerkissen', 'Schlummerkissen'),
        (r'Kopfkissen', 'Kopfkissen'),
    ],
    ('Schlafen', 'Kissen', 'Nackenrollen'): [
        (r'Nackenrolle', 'Nackenrolle'),
    ],
    ('Schlafen', 'Kissen', 'Duftkissen'): [
        (r'Lavendelkissen', 'Lavendelkissen'),
        (r'Duftkissen', 'Duftkissen'),
        (r'Kaminkissen', 'Kaminkissen'),
    ],
    ('Schlafen', 'Kissen', 'Zierkissen'): [
        (r'Zierkissen', 'Zierkissen'),
        (r'Mondkissen', 'Mondkissen'),
    ],
    ('Schlafen', 'Kissen', 'Sofakissen'): [
        (r'Sofakissen', 'Sofakissen'),
    ],
    ('Schlafen', 'Kissen', 'Sitzkissen'): [
        (r'Sitzkissen', 'Sitzkissen'),
    ],
    ('Schlafen', 'Kissen', 'Kissen allgemein'): [
        (r'\bKissen\b', 'Kissen'),
    ],
    ('Schlafen', 'Bettwäsche', 'Kissenüberzüge'): [
        (r'Schlummerkissen.berzug', 'Schlummerkissenüberzug'),
        (r'Sofakissen.berzug', 'Sofakissenüberzug'),
        (r'Zierkissen.berzug', 'Zierkissenüberzug'),
        (r'Kissen.berzug', 'Kissenüberzug'),
        (r'Kissenbezug', 'Kissenbezug'),
    ],
    ('Schlafen', 'Bettwäsche', 'Deckenüberzüge'): [
        (r'Kuscheldecken.berzug', 'Kuscheldeckenüberzug'),
        (r'Decken.berzug', 'Deckenüberzug'),
        (r'Deckenbezug', 'Deckenbezug'),
    ],
    ('Schlafen', 'Bettwäsche', 'Spannleintücher'): [
        (r'Spannleintuch', 'Spannleintuch'),
        (r'Leintuch', 'Leintuch'),
    ],
    ('Schlafen', 'Bettwäsche', 'Laken'): [
        (r'\bLaken\b', 'Laken'),
    ],
    ('Schlafen', 'Bettwäsche', 'Überzüge allgemein'): [
        (r'Schonbezug', 'Schonbezug'),
        (r'.berzug', 'Überzug'),
        (r'Bezug', 'Bezug'),
    ],

    # WOHNEN
    ('Wohnen', 'Sofas & Sessel', 'Sofas'): [
        (r'Mollino', 'Mollino-Sofa'),
        (r'Somerset', 'Somerset-Sofa'),
        (r'Buddy', 'Buddy-Sofa'),
        (r'Lounge.Sofa', 'Lounge-Sofa'),
        (r'Polstersofa', 'Polstersofa'),
        (r'Ecksofa', 'Ecksofa'),
        (r'Schlafsofa', 'Schlafsofa'),
        (r'\bSofa\b', 'Sofa'),
    ],
    ('Wohnen', 'Sofas & Sessel', 'Sessel'): [
        (r'Alani', 'Alani-Sessel'),
        (r'Fauteuil', 'Fauteuil'),
        (r'Sessel', 'Sessel'),
    ],
    ('Wohnen', 'Sofas & Sessel', 'Hocker'): [
        (r'Sitzhocker', 'Sitzhocker'),
        (r'\bHocker\b', 'Hocker'),
    ],
    ('Wohnen', 'Sofas & Sessel', 'Liegen'): [
        (r'Tagesliege', 'Tagesliege'),
        (r'Lorea', 'Lorea-Liege'),
        (r'\bLiege\b', 'Liege'),
    ],
    ('Wohnen', 'Tische', 'Couchtische'): [
        (r'Alwy', 'Alwy-Tisch'),
        (r'Sofatisch', 'Sofatisch'),
        (r'Couchtisch', 'Couchtisch'),
    ],
    ('Wohnen', 'Tische', 'Beistelltische'): [
        (r'Tanaro', 'Tanaro-Tisch'),
        (r'Beistelltisch', 'Beistelltisch'),
    ],
    ('Wohnen', 'Tische', 'Esstische'): [
        (r'Sereno', 'Sereno-Tisch'),
        (r'Esstisch', 'Esstisch'),
    ],
    ('Wohnen', 'Tische', 'Schreibtische'): [
        (r'Schreibtisch', 'Schreibtisch'),
    ],
    ('Wohnen', 'Tische', 'Nachttische'): [
        (r'Nachttisch', 'Nachttisch'),
    ],
    ('Wohnen', 'Tische', 'Tische allgemein'): [
        (r'\bTisch\b', 'Tisch'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Kleiderschränke'): [
        (r'Tonda', 'Tonda-Schrank'),
        (r'Piave', 'Piave-Schrank'),
        (r'Kleiderschrank', 'Kleiderschrank'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Wohnschränke'): [
        (r'Ettore', 'Ettore-Schrank'),
        (r'Prospero', 'Prospero-Schrank'),
        (r'Wohnschrank', 'Wohnschrank'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Schränke allgemein'): [
        (r'\bSchrank\b', 'Schrank'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Regale'): [
        (r'Mirato', 'Mirato-Regal'),
        (r'Cube', 'Cube-Regal'),
        (r'\bRegal\b', 'Regal'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Sideboards'): [
        (r'Sideboard', 'Sideboard'),
        (r'Highboard', 'Highboard'),
        (r'Lowboard', 'Lowboard'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Vitrinen'): [
        (r'Vitrine', 'Vitrine'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Garderoben'): [
        (r'Garderobe', 'Garderobe'),
    ],
    ('Wohnen', 'Schränke & Aufbewahrung', 'Kommoden & Truhen'): [
        (r'Kommode', 'Kommode'),
        (r'Truhe', 'Truhe'),
    ],
    ('Wohnen', 'Sitzmöbel', 'Stühle'): [
        (r'Stuhl', 'Stuhl'),
    ],
    ('Wohnen', 'Sitzmöbel', 'Bänke'): [
        (r'Polsterbank', 'Polsterbank'),
        (r'Sitzbank', 'Sitzbank'),
        (r'\bBank\b', 'Bank'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Schrank-Zubehör'): [
        (r'Fachbrett', 'Fachbrett'),
        (r'T.rf.llung', 'Türfüllung'),
        (r'Schublade', 'Schublade'),
        (r'Fachtr.ger', 'Fachträger'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Beschläge'): [
        (r'Beschlag', 'Beschlag'),
        (r'St.lper', 'Stülper'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Korpusse & Module'): [
        (r'Korpus', 'Korpus'),
        (r'Modul', 'Modul'),
        (r'Ablageboard', 'Ablageboard'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Polsterungen'): [
        (r'Polsterung', 'Polsterung'),
        (r'Stoffhusse', 'Stoffhusse'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Sonstiges Zubehör'): [
        (r'Seitenwangen', 'Seitenwangen'),
        (r'R.ckenlehne', 'Rückenlehne'),
        (r'Holzteil', 'Holzteil'),
        (r'Rolle\b', 'Rolle'),
        (r'Lade\b', 'Lade'),
        (r'F..e\b', 'Füße'),
        (r'Gestell', 'Gestell'),
        (r'Sockel', 'Sockel'),
        (r'Platte\b', 'Platte'),
    ],
    ('Wohnen', 'Spiegel', 'Spiegel'): [
        (r'Spiegel', 'Spiegel'),
    ],

    # HEIMTEXTILIEN
    ('Heimtextilien', 'Teppiche', 'Wollteppiche'): [
        (r'Wollteppich', 'Wollteppich'),
    ],
    ('Heimtextilien', 'Teppiche', 'Naturteppiche'): [
        (r'Maturo', 'Maturo-Teppich'),
        (r'Naturteppich', 'Naturteppich'),
    ],
    ('Heimtextilien', 'Teppiche', 'Teppiche allgemein'): [
        (r'\bTeppich\b', 'Teppich'),
    ],
    ('Heimtextilien', 'Vorhänge & Rollos', 'Vorhänge'): [
        (r'Vorhangbahn', 'Vorhangbahn'),
        (r'Vorhang', 'Vorhang'),
    ],
    ('Heimtextilien', 'Vorhänge & Rollos', 'Faltrollos'): [
        (r'Faltrollo', 'Faltrollo'),
        (r'Rollo', 'Rollo'),
    ],
    ('Heimtextilien', 'Vorhänge & Rollos', 'Gardinen'): [
        (r'Gardine', 'Gardine'),
    ],
    ('Heimtextilien', 'Plaids', 'Plaids'): [
        (r'\bPlaid\b', 'Plaid'),
    ],
    ('Heimtextilien', 'Tischwäsche', 'Tischdecken'): [
        (r'Tischdecke', 'Tischdecke'),
        (r'Tischw.sche', 'Tischwäsche'),
    ],
    ('Heimtextilien', 'Tischwäsche', 'Servietten'): [
        (r'Serviette', 'Serviette'),
    ],
    ('Heimtextilien', 'Tischwäsche', 'Untersetzer'): [
        (r'Untersetzer', 'Untersetzer'),
    ],

    # STOFFE & MUSTER
    ('Stoffe & Muster', 'Wollstoffe', 'Elverum'): [
        (r'Elverum', 'Wollstoff Elverum'),
    ],
    ('Stoffe & Muster', 'Wollstoffe', 'Kaland'): [
        (r'Kaland', 'Wollstoff Kaland'),
    ],
    ('Stoffe & Muster', 'Wollstoffe', 'Stavang'): [
        (r'Stavang', 'Wollstoff Stavang'),
    ],
    ('Stoffe & Muster', 'Wollstoffe', 'Cheviot'): [
        (r'Cheviot', 'Wollstoff Cheviot'),
    ],
    ('Stoffe & Muster', 'Wollstoffe', 'Sletta'): [
        (r'Sletta', 'Wollstoff Sletta'),
    ],
    ('Stoffe & Muster', 'Wollstoffe', 'Wollstoffe allgemein'): [
        (r'Wollstoff', 'Wollstoff'),
    ],
    ('Stoffe & Muster', 'Meterware', 'Meterware'): [
        (r'Meterware', 'Meterware'),
        (r'Voile', 'Voile-Stoff'),
        (r'Satin\b', 'Satin-Stoff'),
        (r'Reinleinen', 'Reinleinen'),
        (r'Halbleinen', 'Halbleinen'),
    ],
    ('Stoffe & Muster', 'Musterservice', 'Stoffmuster'): [
        (r'Stoffmuster', 'Stoffmuster'),
    ],
    ('Stoffe & Muster', 'Musterservice', 'Teppichmuster'): [
        (r'Teppichmuster', 'Teppichmuster'),
    ],
    ('Stoffe & Muster', 'Musterservice', 'Vorhangstoff'): [
        (r'Vorhangstoff', 'Vorhangstoff'),
    ],

    # KLEIDUNG
    ('Kleidung', 'Oberteile', 'Shirts'): [
        (r'Langarmshirt', 'Langarmshirt'),
        (r'Shirt.Langarm', 'Langarmshirt'),
        (r'\bShirt\b', 'Shirt'),
        (r'T.Shirt', 'T-Shirt'),
    ],
    ('Kleidung', 'Oberteile', 'Pullover'): [
        (r'Pullunder', 'Pullunder'),
        (r'Pullover', 'Pullover'),
    ],
    ('Kleidung', 'Oberteile', 'Strickjacken'): [
        (r'Strickjacke', 'Strickjacke'),
        (r'Cardigan', 'Cardigan'),
    ],
    ('Kleidung', 'Oberteile', 'Blusen'): [
        (r'Bluse', 'Bluse'),
    ],
    ('Kleidung', 'Oberteile', 'Tops'): [
        (r'\bTop\b', 'Top'),
    ],
    ('Kleidung', 'Oberteile', 'Ponchos'): [
        (r'Poncho', 'Poncho'),
    ],
    ('Kleidung', 'Oberteile', 'Blazer'): [
        (r'Blazer', 'Blazer'),
    ],
    ('Kleidung', 'Oberteile', 'Strickwaren'): [
        (r'\bStrick\b', 'Strickware'),
    ],
    ('Kleidung', 'Unterteile', 'Hosen'): [
        (r'Jazzpants', 'Jazzpants'),
        (r'\bHose\b', 'Hose'),
    ],
    ('Kleidung', 'Unterteile', 'Leggings'): [
        (r'Leggings', 'Leggings'),
    ],
    ('Kleidung', 'Unterteile', 'Jeans'): [
        (r'Jeans', 'Jeans'),
    ],
    ('Kleidung', 'Unterteile', 'Röcke'): [
        (r'\bRock\b', 'Rock'),
    ],
    ('Kleidung', 'Kleider', 'Kleider'): [
        (r'\bKleid\b', 'Kleid'),
    ],
    ('Kleidung', 'Oberbekleidung', 'Jacken'): [
        (r'Jacke', 'Jacke'),
    ],
    ('Kleidung', 'Oberbekleidung', 'Mäntel'): [
        (r'Mantel', 'Mantel'),
    ],
    ('Kleidung', 'Oberbekleidung', 'Westen'): [
        (r'Weste', 'Weste'),
    ],
    ('Kleidung', 'Nachtwäsche', 'Schlafhosen'): [
        (r'Schlafhose', 'Schlafhose'),
    ],
    ('Kleidung', 'Nachtwäsche', 'Schlafshirts'): [
        (r'Schlafshirt', 'Schlafshirt'),
    ],
    ('Kleidung', 'Nachtwäsche', 'Nachthemden'): [
        (r'Nachthemd', 'Nachthemd'),
    ],
    ('Kleidung', 'Nachtwäsche', 'Pyjamas'): [
        (r'Pyjama', 'Pyjama'),
        (r'Schlafanzug', 'Schlafanzug'),
    ],
    ('Kleidung', 'Accessoires', 'Schals'): [
        (r'\bSchal\b', 'Schal'),
        (r'\bTuch\b', 'Tuch'),
    ],
    ('Kleidung', 'Accessoires', 'Mützen'): [
        (r'M.tze', 'Mütze'),
    ],
    ('Kleidung', 'Accessoires', 'Handschuhe'): [
        (r'Handschuhe', 'Handschuhe'),
    ],
    ('Kleidung', 'Accessoires', 'Gürtel'): [
        (r'G.rtel', 'Gürtel'),
    ],
    ('Kleidung', 'Accessoires', 'Socken'): [
        (r'Socken', 'Socken'),
    ],
    ('Kleidung', 'Schuhe', 'Hausschuhe'): [
        (r'Hausschuhe', 'Hausschuhe'),
        (r'Hausschuh\b', 'Hausschuh'),
    ],
    ('Kleidung', 'Schuhe', 'Stiefel'): [
        (r'Stiefelette', 'Stiefelette'),
        (r'Stiefel', 'Stiefel'),
    ],
    ('Kleidung', 'Schuhe', 'Sneaker'): [
        (r'Sneaker', 'Sneaker'),
    ],
    ('Kleidung', 'Schuhe', 'Ballerinas'): [
        (r'Ballerina', 'Ballerina'),
    ],
    ('Kleidung', 'Schuhe', 'Leinenschuhe'): [
        (r'Leinenschuhe', 'Leinenschuhe'),
    ],
    ('Kleidung', 'Schuhe', 'Schuhzubehör'): [
        (r'Schuheinlagen', 'Schuheinlagen'),
    ],

    # BADEZIMMER
    ('Badezimmer', 'Badtextilien', 'Handtücher'): [
        (r'Handtuch', 'Handtuch'),
        (r'Badetuch', 'Badetuch'),
        (r'Gl.sertuch', 'Gläsertuch'),
    ],
    ('Badezimmer', 'Badtextilien', 'Bademäntel'): [
        (r'Bademantel', 'Bademantel'),
    ],
    ('Badezimmer', 'Badtextilien', 'Waschhandschuhe'): [
        (r'Waschhandschuh', 'Waschhandschuh'),
    ],
    ('Badezimmer', 'Badtextilien', 'Badematten'): [
        (r'Badematte', 'Badematte'),
        (r'Badtextilien', 'Badtextilien'),
    ],

    # KÜCHE & HAUSHALT
    ('Küche & Haushalt', 'Geschirr', 'Teller'): [
        (r'Teller', 'Teller'),
    ],
    ('Küche & Haushalt', 'Geschirr', 'Schalen & Schüsseln'): [
        (r'Sch.ssel', 'Schüssel'),
        (r'Schale', 'Schale'),
    ],
    ('Küche & Haushalt', 'Geschirr', 'Tassen & Becher'): [
        (r'Tasse', 'Tasse'),
        (r'\bBecher\b', 'Becher'),
    ],
    ('Küche & Haushalt', 'Gläser', 'Trinkgläser'): [
        (r'\bGlas\b', 'Glas'),
        (r'Gl.ser\b', 'Gläser'),
    ],
    ('Küche & Haushalt', 'Gläser', 'Karaffen'): [
        (r'Karaffe', 'Karaffe'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Tabletts'): [
        (r'Tablett', 'Tablett'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Schneidebretter'): [
        (r'Schneidebrett', 'Schneidebrett'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Küchenhelfer'): [
        (r'K.chenhelfer', 'Küchenhelfer'),
        (r'Nussknacker', 'Nussknacker'),
        (r'Butterdose', 'Butterdose'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Küchentextilien'): [
        (r'K.chent.cher', 'Küchentücher'),
        (r'Kochsch.rze', 'Kochschürze'),
        (r'Topflappen', 'Topflappen'),
    ],
    ('Küche & Haushalt', 'Aufbewahrung', 'Körbe'): [
        (r'Weidenkorb', 'Weidenkorb'),
        (r'\bKorb\b', 'Korb'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Reinigungsmittel'): [
        (r'Reiniger', 'Reiniger'),
        (r'Klarsp.ler', 'Klarspüler'),
        (r'Scheuermilch', 'Scheuermilch'),
        (r'Anti.Kalk', 'Anti-Kalk'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Waschmittel'): [
        (r'Waschmittel', 'Waschmittel'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Seifen'): [
        (r'Gallseife', 'Gallseife'),
        (r'Seife', 'Seife'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Haushaltstücher'): [
        (r'Haushalts', 'Haushaltstücher'),
    ],

    # WELLNESS & DUFT
    ('Wellness & Duft', 'Räucherwerk', 'Räucherkegel'): [
        (r'R.ucherkegel', 'Räucherkegel'),
    ],
    ('Wellness & Duft', 'Räucherwerk', 'Räucherstäbchen'): [
        (r'R.ucherst.bchen', 'Räucherstäbchen'),
        (r'R.ucherst.ngel', 'Räucherstängel'),
    ],
    ('Wellness & Duft', 'Räucherwerk', 'Räuchermischungen'): [
        (r'R.uchermischung', 'Räuchermischung'),
        (r'R.ucherstoff', 'Räucherstoff'),
        (r'R.ucherb.ndel', 'Räucherbündel'),
    ],
    ('Wellness & Duft', 'Räucherwerk', 'Räucherzubehör'): [
        (r'R.ucherst.vchen', 'Räucherstövchen'),
        (r'R.uchersand', 'Räuchersand'),
        (r'R.ucher', 'Räucherwerk'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Ätherische Öle'): [
        (r'.therisch', 'Ätherisches Öl'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Aromaöle'): [
        (r'Aroma.l', 'Aromaöl'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Raumdüfte'): [
        (r'Raumduft', 'Raumduft'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Duftsäckchen'): [
        (r'Dufts.ckchen', 'Duftsäckchen'),
        (r'Kr.utersack', 'Kräutersack'),
    ],
    ('Wellness & Duft', 'Zirbenprodukte', 'Zirbenprodukte'): [
        (r'Zirben', 'Zirbenprodukt'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Wärmekissen'): [
        (r'W.rmekissen', 'Wärmekissen'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Wärmflaschen'): [
        (r'W.rmflasche', 'Wärmflasche'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Schlafmasken'): [
        (r'Schlafmaske', 'Schlafmaske'),
    ],
    ('Wellness & Duft', 'Badezusätze', 'Badekonfekt'): [
        (r'Badekonfekt', 'Badekonfekt'),
    ],

    # KOSMETIK & PFLEGE
    ('Kosmetik & Pflege', 'Körperpflege', 'Duschpflege'): [
        (r'Duschcreme', 'Duschcreme'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Handpflege'): [
        (r'Handcreme', 'Handcreme'),
        (r'Hand.+Creme', 'Handcreme'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Lippenpflege'): [
        (r'Lippenpflege', 'Lippenpflege'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Kosmetik allgemein'): [
        (r'Kosmetik', 'Kosmetik'),
        (r'Creme\b', 'Creme'),
    ],
    ('Kosmetik & Pflege', 'Möbelpflege', 'Holzpflege'): [
        (r'Kr.uterlein.l', 'Kräuterleinöl'),
        (r'Gleitessenz', 'Gleitessenz'),
        (r'Pflegemittel', 'Pflegemittel'),
        (r'Pflegeset', 'Pflegeset'),
    ],

    # YOGA & MEDITATION
    ('Yoga & Meditation', 'Yoga', 'Yogamatten'): [
        (r'Yogamatte', 'Yogamatte'),
    ],
    ('Yoga & Meditation', 'Yoga', 'Yogablöcke'): [
        (r'Yogablock', 'Yogablock'),
    ],
    ('Yoga & Meditation', 'Yoga', 'Yoga-Zubehör'): [
        (r'\bYoga\b', 'Yoga-Zubehör'),
    ],
    ('Yoga & Meditation', 'Meditation', 'Meditationskissen'): [
        (r'ZAFU', 'ZAFU-Kissen'),
        (r'Meditationskissen', 'Meditationskissen'),
    ],
    ('Yoga & Meditation', 'Meditation', 'Meditationszubehör'): [
        (r'Meditation', 'Meditationszubehör'),
    ],

    # BABY & KINDER
    ('Baby & Kinder', 'Baby-Schlafen', 'Schlafsäcke'): [
        (r'Schlafsack', 'Schlafsack'),
        (r'Strampelsack', 'Strampelsack'),
    ],
    ('Baby & Kinder', 'Baby-Schlafen', 'Stillkissen'): [
        (r'Stillkissen', 'Stillkissen'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Tragetücher'): [
        (r'Tragetuch', 'Tragetuch'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Windeln'): [
        (r'Windel', 'Windel'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Erstausstattung'): [
        (r'Erstausstattung', 'Erstausstattung'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Baby-Artikel'): [
        (r'\bBaby\b', 'Baby-Artikel'),
    ],
    ('Baby & Kinder', 'Kinder', 'Kinder-Artikel'): [
        (r'\bKinder\b', 'Kinder-Artikel'),
    ],

    # DEKORATION
    ('Dekoration', 'Vasen & Gefäße', 'Vasen'): [
        (r'\bVase\b', 'Vase'),
    ],
    ('Dekoration', 'Vasen & Gefäße', 'Gefäße'): [
        (r'Gef..', 'Gefäß'),
    ],
    ('Dekoration', 'Anhänger', 'Holzanhänger'): [
        (r'Holzanh.nger', 'Holzanhänger'),
        (r'Astholz', 'Astholzanhänger'),
        (r'Papieranh.nger', 'Papieranhänger'),
        (r'Anh.nger', 'Anhänger'),
    ],
    ('Dekoration', 'Filzprodukte', 'Filzprodukte'): [
        (r'Filztier', 'Filztier'),
        (r'aus Filz', 'Filzprodukt'),
        (r'Filz', 'Filzprodukt'),
    ],
    ('Dekoration', 'Saisonal', 'Weihnachtsdeko'): [
        (r'Adventkalender', 'Adventkalender'),
        (r'Schneemann', 'Schneemann'),
        (r'Engel', 'Engel'),
        (r'Stern\b', 'Stern'),
        (r'Weihnacht', 'Weihnachtsartikel'),
    ],
    ('Dekoration', 'Saisonal', 'Osterdeko'): [
        (r'Osterei', 'Osterei'),
        (r'Hase\b', 'Osterhase'),
        (r'Ostern', 'Osterartikel'),
    ],
    ('Dekoration', 'Bilderrahmen', 'Bilderrahmen'): [
        (r'Bilderrahmen', 'Bilderrahmen'),
    ],
    ('Dekoration', 'Baldachine', 'Baldachine'): [
        (r'Baldachin', 'Baldachin'),
    ],
    ('Dekoration', 'Kerzen', 'Kerzen'): [
        (r'Bienenwachs', 'Bienenwachskerze'),
        (r'Figurkerze', 'Figurkerze'),
        (r'Sternenkerze', 'Sternenkerze'),
        (r'Stumpenkerze', 'Stumpenkerze'),
        (r'Teelicht', 'Teelicht'),
        (r'\bKerze\b', 'Kerze'),
    ],

    # BELEUCHTUNG
    ('Beleuchtung', 'Leuchten', 'Hängeleuchten'): [
        (r'H.ngeleuchte', 'Hängeleuchte'),
        (r'Pendelleuchte', 'Pendelleuchte'),
    ],
    ('Beleuchtung', 'Leuchten', 'Tischleuchten'): [
        (r'Tischleuchte', 'Tischleuchte'),
    ],
    ('Beleuchtung', 'Leuchten', 'Stehleuchten'): [
        (r'Stehleuchte', 'Stehleuchte'),
    ],
    ('Beleuchtung', 'Leuchten', 'Wandleuchten'): [
        (r'Wandleuchte', 'Wandleuchte'),
    ],
    ('Beleuchtung', 'Leuchten', 'Leuchten allgemein'): [
        (r'Leuchte', 'Leuchte'),
        (r'Lampe', 'Lampe'),
    ],
    ('Beleuchtung', 'Leuchtmittel', 'LED-Leuchtmittel'): [
        (r'Leuchtmittel', 'Leuchtmittel'),
        (r'\bLED\b', 'LED'),
    ],

    # LEBENSMITTEL
    ('Lebensmittel', 'Getränke', 'Kaffee & Espresso'): [
        (r'Espresso', 'Espresso'),
        (r'Kaffee', 'Kaffee'),
    ],
    ('Lebensmittel', 'Getränke', 'Tee'): [
        (r'\bTee\b', 'Tee'),
    ],
    ('Lebensmittel', 'Getränke', 'Sirupe'): [
        (r'Sirup', 'Sirup'),
    ],
    ('Lebensmittel', 'Getränke', 'Säfte'): [
        (r'Saft', 'Saft'),
        (r'Direktsaft', 'Direktsaft'),
    ],
    ('Lebensmittel', 'Aufstriche', 'Fruchtaufstriche'): [
        (r'Fruchtaufstrich', 'Fruchtaufstrich'),
        (r'Marmelade', 'Marmelade'),
    ],
    ('Lebensmittel', 'Aufstriche', 'Honig'): [
        (r'Honig', 'Honig'),
    ],
    ('Lebensmittel', 'Süßes', 'Schokolade'): [
        (r'Schokolade', 'Schokolade'),
    ],
    ('Lebensmittel', 'Öle', 'Speiseöle'): [
        (r'Oliven.l', 'Olivenöl'),
        (r'Distel.l', 'Distelöl'),
        (r'Walnuss.l', 'Walnussöl'),
        (r'Lein.l', 'Leinöl'),
    ],
    ('Lebensmittel', 'Snacks', 'Gebäck'): [
        (r'Kr.cker', 'Kräcker'),
        (r'\bBrot\b', 'Brot'),
    ],

    # BÜCHER & MEDIEN
    ('Bücher & Medien', 'Bücher', 'Bücher'): [
        (r'\bBuch\b', 'Buch'),
        (r'Buch:', 'Buch'),
    ],
    ('Bücher & Medien', 'Musik', 'CDs'): [
        (r'\bCD\b', 'CD'),
    ],
    ('Bücher & Medien', 'Karten', 'Postkarten'): [
        (r'Postkarte', 'Postkarte'),
        (r'Karte\b', 'Karte'),
    ],

    # GESCHENKE & GUTSCHEINE
    ('Geschenke & Gutscheine', 'Gutscheine', 'Gutscheine'): [
        (r'Gutschein', 'Gutschein'),
    ],
    ('Geschenke & Gutscheine', 'Verpackung', 'Geschenkverpackung'): [
        (r'Geschenkverpackung', 'Geschenkverpackung'),
        (r'Geschenkspapier', 'Geschenkspapier'),
    ],
    ('Geschenke & Gutscheine', 'Sets', 'Sets'): [
        (r'SET:', 'Set'),
        (r'Set:', 'Set'),
    ],
    ('Geschenke & Gutscheine', 'Geschenke', 'Geschenke'): [
        (r'Geschenk', 'Geschenk'),
    ],

    # TASCHEN & BEUTEL
    ('Taschen & Beutel', 'Taschen', 'Taschen'): [
        (r'Tasche', 'Tasche'),
    ],
    ('Taschen & Beutel', 'Beutel', 'Beutel'): [
        (r'Beutel', 'Beutel'),
    ],
    ('Taschen & Beutel', 'Füllsäcke', 'Füllsäcke'): [
        (r'F.llsack', 'Füllsack'),
    ],

    # INTERN
    ('Intern', 'Verpackung', 'Kartons'): [
        (r'Karton', 'Karton'),
    ],
    ('Intern', 'Etiketten', 'Etiketten'): [
        (r'Produkthangtag', 'Produkthangtag'),
        (r'Hangtag', 'Hangtag'),
        (r'Gr..enetikett', 'Größenetikett'),
        (r'Pflegeetikett', 'Pflegeetikett'),
        (r'Etikett', 'Etikett'),
        (r'Aufkleber', 'Aufkleber'),
        (r'Banderole', 'Banderole'),
        (r'Stofffahne', 'Stofffahne'),
    ],
    ('Intern', 'Marketing', 'Kataloge'): [
        (r'Katalog', 'Katalog'),
        (r'Produktbegleiter', 'Produktbegleiter'),
        (r'Folder', 'Folder'),
        (r'Preisliste', 'Preisliste'),
    ],
    ('Intern', 'Aktionen', 'Gratis'): [
        (r'Gratis', 'Gratis'),
    ],
    ('Intern', 'Aktionen', 'Outlet'): [
        (r'OUTLET', 'Outlet'),
        (r'Outlet', 'Outlet'),
    ],
    ('Intern', 'Aktionen', 'Rabatte'): [
        (r'Rabatt', 'Rabatt'),
        (r'Aktion\b', 'Aktion'),
    ],
    ('Intern', 'Versand', 'Versand'): [
        (r'Versandkost', 'Versandkosten'),
        (r'Spedition', 'Spedition'),
    ],
    ('Intern', 'Sonstiges', 'Sonstiges'): [
        (r'Gutschrift', 'Gutschrift'),
        (r'SHOP', 'Shop-Artikel'),
        (r'Shop\b', 'Shop-Artikel'),
        (r'Laden\b', 'Laden-Artikel'),
        (r'NUR\b', 'NUR-Artikel'),
        (r'FREI\b', 'Frei-Artikel'),
        (r'UNIQUE', 'UNIQUE'),
        (r'Sonderanfertigung', 'Sonderanfertigung'),
        (r'Ma.anfertigung', 'Maßanfertigung'),
        (r'Probe\b', 'Probe'),
    ],
}


def main():
    print("Lade Produkte...")

    # Lese alle Hauptprodukte
    with open('produkte.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        products = []
        for row in reader:
            if not row.get('parent_id', '').strip():
                products.append(row)

    print(f"Gefunden: {len(products)} Hauptprodukte")

    # Kategorisiere Produkte
    results = []
    kategorisiert = set()

    for (hauptkat, unterkat, typ), patterns in KATEGORIEN.items():
        artikelnummern = []
        produktnamen = []
        count = 0

        for p in products:
            if p['id'] in kategorisiert:
                continue

            name = p.get('name', '').strip()
            artikelnr = p.get('product_number', '').strip()

            for pattern, produkttyp in patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    artikelnummern.append(artikelnr)
                    produktnamen.append(name[:50])
                    kategorisiert.add(p['id'])
                    count += 1
                    break

        if count > 0:
            results.append({
                'Hauptkategorie': hauptkat,
                'Unterkategorie': unterkat,
                'Produkttyp': typ,
                'Anzahl': count,
                'Artikelnummern': ', '.join(artikelnummern),
                'Beispiel-Produkte': ' | '.join(produktnamen[:5])
            })

    # Unkategorisierte
    unkategorisiert_nummern = []
    unkategorisiert_namen = []
    for p in products:
        if p['id'] not in kategorisiert:
            unkategorisiert_nummern.append(p.get('product_number', ''))
            unkategorisiert_namen.append(p.get('name', '')[:50])

    if unkategorisiert_nummern:
        results.append({
            'Hauptkategorie': 'UNKATEGORISIERT',
            'Unterkategorie': '-',
            'Produkttyp': '-',
            'Anzahl': len(unkategorisiert_nummern),
            'Artikelnummern': ', '.join(unkategorisiert_nummern),
            'Beispiel-Produkte': ' | '.join(unkategorisiert_namen[:5])
        })

    # Erstelle DataFrame
    df = pd.DataFrame(results)

    # Sortiere
    df = df.sort_values(['Hauptkategorie', 'Unterkategorie', 'Produkttyp'])

    # Speichere als Excel
    output_file = 'produktkategorien.xlsx'

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Kategorien', index=False)

        # Spaltenbreiten anpassen
        worksheet = writer.sheets['Kategorien']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 25
        worksheet.column_dimensions['C'].width = 25
        worksheet.column_dimensions['D'].width = 10
        worksheet.column_dimensions['E'].width = 100
        worksheet.column_dimensions['F'].width = 80

    print(f"\nExcel-Datei erstellt: {output_file}")
    print(f"Kategorisiert: {len(kategorisiert)} von {len(products)} Produkten")
    print(f"Unkategorisiert: {len(products) - len(kategorisiert)}")

    # Zusammenfassung nach Hauptkategorie
    print("\n=== ZUSAMMENFASSUNG ===")
    summary = df.groupby('Hauptkategorie')['Anzahl'].sum().sort_values(ascending=False)
    for kat, anzahl in summary.items():
        print(f"{kat}: {anzahl}")


if __name__ == '__main__':
    main()
