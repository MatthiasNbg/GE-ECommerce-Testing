# -*- coding: utf-8 -*-
"""
Erstellt eine Excel-Datei mit Produktkategorisierung und Artikelnummern
Version 2 - Erweitert um fehlende Produkttypen
"""

import csv
import re
from collections import defaultdict
import pandas as pd

# =============================================================================
# KATEGORIE-DEFINITIONEN (ERWEITERT)
# =============================================================================

KATEGORIEN = {
    # =========================================================================
    # SCHLAFEN
    # =========================================================================
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
    ('Schlafen', 'Decken', 'Tagesdecken'): [
        (r'Tagesdecke', 'Tagesdecke'),
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
    ('Schlafen', 'Decken', 'Premiumdecken'): [
        (r'Premiumdecke', 'Premiumdecke'),
        (r'.bergangsdecke', 'Übergangsdecke'),
        (r'Schlafdecke', 'Schlafdecke'),
    ],
    ('Schlafen', 'Decken', 'Auflagen'): [
        (r'Auflage\b', 'Auflage'),
        (r'Auflagenset', 'Auflagenset'),
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
        (r'Nackenkissen', 'Nackenkissen'),
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
    ('Schlafen', 'Kissen', 'Nackenstützkissen'): [
        (r'Nackenst.tzkissen', 'Nackenstützkissen'),
    ],
    ('Schlafen', 'Kissen', 'Armlehnenkissen'): [
        (r'Armlehnenkissen', 'Armlehnenkissen'),
    ],
    ('Schlafen', 'Kissen', 'Stützkissen'): [
        (r'St.tzkissen', 'Stützkissen'),
        (r'Schulterkissen', 'Schulterkissen'),
    ],
    ('Schlafen', 'Kissen', 'Dinkelkissen'): [
        (r'Dinkelkissen', 'Dinkelkissen'),
        (r'Dinkelspelzen', 'Dinkelspelzen'),
    ],
    ('Schlafen', 'Kissen', 'Kissen allgemein'): [
        (r'\bKissen\b', 'Kissen'),
    ],
    ('Schlafen', 'Bettwäsche', 'Kissenüberzüge'): [
        (r'Kissen.berz.ge', 'Kissenüberzüge'),
        (r'Schlummerkissen.berzug', 'Schlummerkissenüberzug'),
        (r'Sofakissen.berzug', 'Sofakissenüberzug'),
        (r'Zierkissen.berzug', 'Zierkissenüberzug'),
        (r'Kissen.berzug', 'Kissenüberzug'),
        (r'Kissenbezug', 'Kissenbezug'),
    ],
    ('Schlafen', 'Bettwäsche', 'Deckenüberzüge'): [
        (r'Decken.berz.ge', 'Deckenüberzüge'),
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
    ('Schlafen', 'Bettwäsche', 'Betttücher'): [
        (r'Betttuch', 'Betttuch'),
    ],
    ('Schlafen', 'Bettwäsche', 'Überzüge allgemein'): [
        (r'Schonbezug', 'Schonbezug'),
        (r'.berzug', 'Überzug'),
        (r'Bezug', 'Bezug'),
    ],

    # =========================================================================
    # WOHNEN
    # =========================================================================
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
        (r'Hochlehner', 'Hochlehner'),
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
        (r'Ausziehtisch', 'Ausziehtisch'),
        (r'\bTisch\b', 'Tisch'),
    ],
    ('Wohnen', 'Bretter', 'Schlüsselboards'): [
        (r'Schl.sselboard', 'Schlüsselboard'),
    ],
    ('Wohnen', 'Bretter', 'Boards'): [
        (r'\bBoard\b', 'Board'),
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
        (r'H.ngeregal', 'Hängeregal'),
        (r'Wandregal', 'Wandregal'),
        (r'Badezimmerregal', 'Badezimmerregal'),
        (r'Regalsystem', 'Regalsystem'),
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
        (r'Kleiderst.nder', 'Kleiderständer'),
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
        (r'Weidenbank', 'Weidenbank'),
        (r'\bBank\b', 'Bank'),
    ],
    ('Wohnen', 'Tische', 'Konsolentische'): [
        (r'Konsolentisch', 'Konsolentisch'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Kleiderbügel'): [
        (r'Kleiderb.gel', 'Kleiderbügel'),
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
        (r'Wei.polsterung', 'Weißpolsterung'),
        (r'Stoffhusse', 'Stoffhusse'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Armlehnen'): [
        (r'Armlehne', 'Armlehne'),
    ],
    ('Wohnen', 'Möbel-Zubehör', 'Befestigungen'): [
        (r'Befestigungsring', 'Befestigungsring'),
        (r'H.henverstellungsset', 'Höhenverstellungsset'),
        (r'Verbindungsbl.ttchen', 'Verbindungsblättchen'),
        (r'Kippschalter', 'Kippschalter'),
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
        (r'Montageleiste', 'Montageleiste'),
        (r'\bFach\b', 'Fach'),
        (r'Bodenblende', 'Bodenblende'),
        (r'Fu.haupt', 'Fußhaupt'),
        (r'Tenso', 'Tenso-Zubehör'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Akato'): [
        (r'Akato', 'Akato'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Jukai'): [
        (r'Jukai', 'Jukai'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Linera'): [
        (r'Linera', 'Linera'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Esempio'): [
        (r'Esempio', 'Esempio'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Kurami'): [
        (r'Kurami', 'Kurami'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Kyushu'): [
        (r'Kyushu', 'Kyushu'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Tesoro'): [
        (r'Tesoro', 'Tesoro'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Kristian'): [
        (r'Kristian', 'Kristian'),
    ],
    ('Wohnen', 'Möbel-Serien', 'Kador'): [
        (r'Kador', 'Kador'),
    ],
    ('Wohnen', 'Spiegel', 'Spiegel'): [
        (r'Spiegel', 'Spiegel'),
    ],

    # =========================================================================
    # HEIMTEXTILIEN
    # =========================================================================
    ('Heimtextilien', 'Teppiche', 'Wollteppiche'): [
        (r'Wollteppich', 'Wollteppich'),
    ],
    ('Heimtextilien', 'Teppiche', 'Naturteppiche'): [
        (r'Maturo', 'Maturo-Teppich'),
        (r'Naturteppich', 'Naturteppich'),
    ],
    ('Heimtextilien', 'Teppiche', 'Leinenteppiche'): [
        (r'Leinenteppich', 'Leinenteppich'),
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
    ('Heimtextilien', 'Tischwäsche', 'Tischläufer'): [
        (r'Tischl.ufer', 'Tischläufer'),
    ],
    ('Heimtextilien', 'Tischwäsche', 'Tischsets'): [
        (r'Tischset', 'Tischset'),
    ],
    ('Heimtextilien', 'Tischwäsche', 'Servietten'): [
        (r'Serviette', 'Serviette'),
    ],
    ('Heimtextilien', 'Tischwäsche', 'Untersetzer'): [
        (r'Untersetzer', 'Untersetzer'),
    ],

    # =========================================================================
    # STOFFE & MUSTER
    # =========================================================================
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
        (r'Fischgrat', 'Fischgrat-Stoff'),
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
    ('Stoffe & Muster', 'Musterservice', 'Holzmuster'): [
        (r'Holzmuster', 'Holzmuster'),
    ],
    ('Stoffe & Muster', 'Rohwolle', 'Rohwolle'): [
        (r'Rohwolle', 'Rohwolle'),
        (r'gebleicht.*Rohwolle', 'Rohwolle gebleicht'),
        (r'Alpaka Wolle', 'Alpaka Wolle'),
        (r'Nesselflocken', 'Nesselflocken'),
    ],
    ('Stoffe & Muster', 'Meterware', 'Stoffrollen'): [
        (r'Stoff.*gerollt', 'Stoff gerollt'),
    ],
    ('Stoffe & Muster', 'Meterware', 'Baumwollstoffe'): [
        (r'BW.Stoff', 'BW-Stoff'),
        (r'BW.*Rips', 'BW-Rips'),
        (r'Leinen.*Utenos', 'Leinenstoff'),
    ],

    # =========================================================================
    # KLEIDUNG
    # =========================================================================
    ('Kleidung', 'Oberteile', 'Shirts'): [
        (r'Rollkragenshirt', 'Rollkragenshirt'),
        (r'Schlaftop', 'Schlaftop'),
        (r'Sweatshirt', 'Sweatshirt'),
        (r'Kurzarmshirt', 'Kurzarmshirt'),
        (r'Langarmshirt', 'Langarmshirt'),
        (r'Shirt.Langarm', 'Langarmshirt'),
        (r'\bShirt\b', 'Shirt'),
        (r'T.Shirt', 'T-Shirt'),
    ],
    ('Kleidung', 'Oberteile', 'Sweater'): [
        (r'Sweathoody', 'Sweathoody'),
        (r'Kapuzenshirt', 'Kapuzenshirt'),
        (r'Hoodie', 'Hoodie'),
        (r'Sweater', 'Sweater'),
        (r'\bSweat\b', 'Sweat'),
    ],
    ('Kleidung', 'Oberteile', 'Tops erweitert'): [
        (r'Longtop', 'Longtop'),
        (r'Yogatop', 'Yogatop'),
        (r'Sporttop', 'Sporttop'),
        (r'Spitzentop', 'Spitzentop'),
        (r'Wickeltop', 'Wickeltop'),
        (r'Halbarmshirt', 'Halbarmshirt'),
        (r'Fledermausshirt', 'Fledermausshirt'),
        (r'Ringelshirt', 'Ringelshirt'),
        (r'Samtshirt', 'Samtshirt'),
        (r'Wendeshirt', 'Wendeshirt'),
    ],
    ('Kleidung', 'Oberteile', 'Boleros'): [
        (r'Bolero', 'Bolero'),
    ],
    ('Kleidung', 'Oberteile', 'Poloshirts'): [
        (r'Poloshirt', 'Poloshirt'),
    ],
    ('Kleidung', 'Oberteile', 'Polo'): [
        (r'\bPolo\b', 'Polo'),
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
        (r'Strickshirt', 'Strickshirt'),
        (r'Stricktop', 'Stricktop'),
        (r'Wickelshirt', 'Wickelshirt'),
        (r'\bStrick\b', 'Strickware'),
    ],
    ('Kleidung', 'Oberteile', 'Tops'): [
        (r'Spaghettitop', 'Spaghettitop'),
        (r'\bTop\b', 'Top'),
    ],
    ('Kleidung', 'Oberteile', 'Tuniken'): [
        (r'Tunika', 'Tunika'),
    ],
    ('Kleidung', 'Unterteile', 'Hosen'): [
        (r'Sweatpants', 'Sweatpants'),
        (r'Jogginghose', 'Jogginghose'),
        (r'Strickhose', 'Strickhose'),
        (r'Jazzpants', 'Jazzpants'),
        (r'Hipster', 'Hipster'),
        (r'\bHose\b', 'Hose'),
    ],
    ('Kleidung', 'Unterteile', 'Leggings'): [
        (r'Legging\b', 'Legging'),
        (r'Leggings', 'Leggings'),
    ],
    ('Kleidung', 'Unterteile', 'Culottes'): [
        (r'Culotte', 'Culotte'),
    ],
    ('Kleidung', 'Unterteile', 'Bermudas'): [
        (r'Bermuda', 'Bermuda'),
    ],
    ('Kleidung', 'Unterteile', 'Jerseyhosen'): [
        (r'Jerseyhose', 'Jerseyhose'),
        (r'Joggpants', 'Joggpants'),
    ],
    ('Kleidung', 'Unterteile', 'Jeans'): [
        (r'Jeans', 'Jeans'),
    ],
    ('Kleidung', 'Unterteile', 'Röcke'): [
        (r'Strickrock', 'Strickrock'),
        (r'Hosenrock', 'Hosenrock'),
        (r'\bRock\b', 'Rock'),
    ],
    ('Kleidung', 'Unterteile', 'Shorts'): [
        (r'Sweatshort', 'Sweatshort'),
        (r'\bShorts\b', 'Shorts'),
        (r'\bShort\b', 'Short'),
        (r'\bChino\b', 'Chino'),
    ],
    ('Kleidung', 'Unterteile', 'Marlenehosen'): [
        (r'Marlenehose', 'Marlenehose'),
    ],
    ('Kleidung', 'Unterteile', 'Sweathosen'): [
        (r'Sweathose', 'Sweathose'),
    ],
    ('Kleidung', 'Unterteile', 'Overalls'): [
        (r'Latzhose', 'Latzhose'),
        (r'Overall', 'Overall'),
    ],
    ('Kleidung', 'Unterteile', 'Cordhosen'): [
        (r'Cordhose', 'Cordhose'),
    ],
    ('Kleidung', 'Kleider', 'Kleider'): [
        (r'Sweatkleid', 'Sweatkleid'),
        (r'Leinenkleid', 'Leinenkleid'),
        (r'Strickkleid', 'Strickkleid'),
        (r'Tr.gerkleid', 'Trägerkleid'),
        (r'\bKleid\b', 'Kleid'),
    ],
    ('Kleidung', 'Oberbekleidung', 'Jacken'): [
        (r'Jacke', 'Jacke'),
    ],
    ('Kleidung', 'Oberbekleidung', 'Mäntel'): [
        (r'Trenchcoat', 'Trenchcoat'),
        (r'Mantel', 'Mantel'),
    ],
    ('Kleidung', 'Oberbekleidung', 'Westen'): [
        (r'Weste', 'Weste'),
    ],
    ('Kleidung', 'Nachtwäsche', 'Schlafhosen'): [
        (r'Schlafhose', 'Schlafhose'),
    ],
    ('Kleidung', 'Nachtwäsche', 'Schlafshorts'): [
        (r'Schlafshort', 'Schlafshort'),
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
        (r'Strickschal', 'Strickschal'),
        (r'Dreieckstuch', 'Dreieckstuch'),
        (r'\bSchal\b', 'Schal'),
        (r'\bTuch\b', 'Tuch'),
    ],
    ('Kleidung', 'Accessoires', 'Mützen'): [
        (r'Beanie', 'Beanie'),
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
    ('Kleidung', 'Accessoires', 'Stulpen'): [
        (r'Strickstulpen', 'Strickstulpen'),
        (r'Stulpen', 'Stulpen'),
    ],
    ('Kleidung', 'Accessoires', 'Stirnbänder'): [
        (r'Stirnband', 'Stirnband'),
    ],
    ('Kleidung', 'Accessoires', 'Fäustlinge'): [
        (r'F.ustlinge', 'Fäustlinge'),
    ],
    ('Kleidung', 'Unterwäsche', 'BHs'): [
        (r'B.gel BH', 'Bügel-BH'),
        (r'Leichter BH', 'Leichter BH'),
        (r'\bBH\b', 'BH'),
    ],
    ('Kleidung', 'Unterwäsche', 'Slips'): [
        (r'Minislip', 'Minislip'),
        (r'H.ftslip', 'Hüftslip'),
        (r'\bSlip\b', 'Slip'),
    ],
    ('Kleidung', 'Unterwäsche', 'Bralettes'): [
        (r'Bralette', 'Bralette'),
    ],
    ('Kleidung', 'Unterwäsche', 'Hemdchen'): [
        (r'Hemdchen', 'Hemdchen'),
    ],
    ('Kleidung', 'Unterwäsche', 'Bustiers'): [
        (r'Bustier', 'Bustier'),
    ],
    ('Kleidung', 'Unterwäsche', 'Pantys'): [
        (r'Panty', 'Panty'),
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
    ('Kleidung', 'Schuhe', 'Sandalen'): [
        (r'Sandale', 'Sandale'),
        (r'R.mersandale', 'Römersandale'),
    ],
    ('Kleidung', 'Schuhe', 'Schuhzubehör'): [
        (r'Schuheinlagen', 'Schuheinlagen'),
    ],
    ('Kleidung', 'Schuhe', 'Schnürschuhe'): [
        (r'Schn.rschuh', 'Schnürschuh'),
        (r'Schn.rer', 'Schnürer'),
    ],
    ('Kleidung', 'Schuhe', 'Pantoffeln'): [
        (r'Pantoffel', 'Pantoffel'),
        (r'Pantolette', 'Pantolette'),
    ],
    ('Kleidung', 'Schuhe', 'Badeschuhe'): [
        (r'Badeschuhe', 'Badeschuhe'),
    ],
    ('Kleidung', 'Schuhe', 'Chelsea Boots'): [
        (r'Chelsea', 'Chelsea Boots'),
    ],
    ('Kleidung', 'Schuhe', 'Budapester'): [
        (r'Budapester', 'Budapester'),
    ],
    ('Kleidung', 'Schuhe', 'Halbschuhe'): [
        (r'Halbschuh', 'Halbschuh'),
        (r'Lederschuh', 'Lederschuh'),
    ],

    # =========================================================================
    # BADEZIMMER
    # =========================================================================
    ('Badezimmer', 'Badtextilien', 'Handtücher'): [
        (r'Handtuch', 'Handtuch'),
        (r'Badetuch', 'Badetuch'),
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

    # =========================================================================
    # KÜCHE & HAUSHALT
    # =========================================================================
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
        (r'Teeglas', 'Teeglas'),
        (r'\bGlas\b', 'Glas'),
        (r'Gl.ser\b', 'Gläser'),
    ],
    ('Küche & Haushalt', 'Gläser', 'Karaffen'): [
        (r'Karaffe', 'Karaffe'),
    ],
    ('Küche & Haushalt', 'Gläser', 'Kännchen'): [
        (r'K.nnchen', 'Kännchen'),
    ],
    ('Küche & Haushalt', 'Tee & Kaffee', 'Teekannen'): [
        (r'Teekanne', 'Teekanne'),
        (r'Teesieb', 'Teesieb'),
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
        (r'Jausenbrett', 'Jausenbrett'),
        (r'Brotsack', 'Brotsack'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Küchentextilien'): [
        (r'Geschirrtuch', 'Geschirrtuch'),
        (r'Geschirrt.cher', 'Geschirrtücher'),
        (r'Gl.sertuch', 'Gläsertuch'),
        (r'K.chent.cher', 'Küchentücher'),
        (r'Kochsch.rze', 'Kochschürze'),
        (r'Topflappen', 'Topflappen'),
    ],
    ('Küche & Haushalt', 'Aufbewahrung', 'Körbe'): [
        (r'Weidenkorb', 'Weidenkorb'),
        (r'H.kelkorb', 'Häkelkorb'),
        (r'Badezimmerkorb', 'Badezimmerkorb'),
        (r'Mehrzweckkorb', 'Mehrzweckkorb'),
        (r'\bKorb\b', 'Korb'),
    ],
    ('Küche & Haushalt', 'Aufbewahrung', 'Kisten & Boxen'): [
        (r'Aufbewahrungsbox', 'Aufbewahrungsbox'),
        (r'Kiste', 'Kiste'),
        (r'\bBox\b', 'Box'),
    ],
    ('Küche & Haushalt', 'Aufbewahrung', 'Dosen'): [
        (r'Runddose', 'Runddose'),
        (r'\bDeckel\b', 'Deckel'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Trinkhalme'): [
        (r'Trinkhalm', 'Trinkhalm'),
        (r'Biotrinkhalm', 'Biotrinkhalm'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Keramik-Geschirr'): [
        (r'Keramik.*Geschirr', 'Keramik-Geschirr'),
        (r'Geschirr.*Keramik', 'Keramik-Geschirr'),
        (r'Keramik', 'Keramik'),
        (r'Steingut', 'Steingut'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Spülmittel'): [
        (r'Handsp.lmittel', 'Handspülmittel'),
        (r'Geschirrsp.l', 'Geschirrspülmittel'),
        (r'Klarsp.ler', 'Klarspüler'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Reinigungsmittel'): [
        (r'Reiniger', 'Reiniger'),
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
    ('Küche & Haushalt', 'Reinigung', 'WC-Reiniger'): [
        (r'WC.+Reinig', 'WC-Reiniger'),
        (r'WC.+Tabs', 'WC-Tabs'),
    ],
    ('Küche & Haushalt', 'Reinigung', 'Reinigungstabs'): [
        (r'Reinigungstabs', 'Reinigungstabs'),
        (r'Antikalk.*Tabs', 'Antikalk-Tabs'),
    ],
    ('Küche & Haushalt', 'Wäschepflege', 'Bügelwasser'): [
        (r'B.gelwasser', 'Bügelwasser'),
    ],
    ('Küche & Haushalt', 'Backzubehör', 'Backpapier'): [
        (r'Backpapier', 'Backpapier'),
        (r'Backschanze', 'Backschanze'),
    ],

    # =========================================================================
    # WELLNESS & DUFT
    # =========================================================================
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
        (r'Nachf.llpackung R.ucher', 'Räucher-Nachfüllpackung'),
        (r'R.ucher', 'Räucherwerk'),
    ],
    ('Wellness & Duft', 'Kräuter', 'Kräuterprodukte'): [
        (r'Wildkr.uter', 'Wildkräuter'),
        (r'Kr.utermischung', 'Kräutermischung'),
        (r'7.Elemente', 'Kräutermischung'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Ätherische Öle'): [
        (r'.therisch', 'Ätherisches Öl'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Aromaöle'): [
        (r'Aroma.l', 'Aromaöl'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Raumdüfte'): [
        (r'Raumduft', 'Raumduft'),
        (r'Bl.tenduft', 'Blütenduft'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Duftsäckchen'): [
        (r'Dufts.ckchen', 'Duftsäckchen'),
        (r'Kr.utersack', 'Kräutersack'),
        (r'Duft\b', 'Duftprodukt'),
    ],
    ('Wellness & Duft', 'Zirbenprodukte', 'Zirbenprodukte'): [
        (r'Zirben', 'Zirbenprodukt'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Wärmekissen'): [
        (r'W.rme.+K.hlkissen', 'Wärme-Kühlkissen'),
        (r'W.rmekissen', 'Wärmekissen'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Wärmflaschen'): [
        (r'W.rmflasche', 'Wärmflasche'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Schlafmasken'): [
        (r'Schlafmaske', 'Schlafmaske'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Entspannungskissen'): [
        (r'Augen.Entspannungskissen', 'Augen-Entspannungskissen'),
        (r'Lagerungskissen', 'Lagerungskissen'),
        (r'Begrenzungskissen', 'Begrenzungskissen'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Aromasprays'): [
        (r'Aromaspray', 'Aromaspray'),
    ],
    ('Wellness & Duft', 'Wellness-Sets', 'Wellness-Sets'): [
        (r'Aromatherapie.*Set', 'Aromatherapie Set'),
        (r'Set.Angebot', 'Set-Angebot'),
    ],
    ('Wellness & Duft', 'Badezusätze', 'Badekonfekt'): [
        (r'Badekonfekt', 'Badekonfekt'),
    ],
    ('Wellness & Duft', 'Badezusätze', 'Badekugeln'): [
        (r'Badekugel', 'Badekugel'),
    ],
    ('Wellness & Duft', 'Massage', 'Massagezubehör'): [
        (r'Flachs.Massage', 'Flachs-Massageprodukt'),
        (r'Massagegurt', 'Massagegurt'),
        (r'Massagehandschuh', 'Massagehandschuh'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Raumsprays'): [
        (r'Raum.*Kissenspray', 'Raum- & Kissenspray'),
        (r'Raumspray', 'Raumspray'),
    ],
    ('Wellness & Duft', 'Düfte & Öle', 'Duftmischungen'): [
        (r'Duftmischung', 'Duftmischung'),
        (r'Duftstreifen', 'Duftstreifen'),
        (r'Ahornholzst.bchen', 'Ahornholzstäbchen'),
        (r'Ahorn.*st.bchen.*Raumduft', 'Raumduftstäbchen'),
        (r'alkoholischer Auszug', 'Auszug'),
    ],
    ('Wellness & Duft', 'Wärme & Entspannung', 'Menthol'): [
        (r'Menthol.Kristalle', 'Menthol-Kristalle'),
    ],
    ('Wellness & Duft', 'Körperpflege', 'Kräuterbalsam'): [
        (r'Kr.uterbalsam', 'Kräuterbalsam'),
    ],

    # =========================================================================
    # KOSMETIK & PFLEGE
    # =========================================================================
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
    ('Kosmetik & Pflege', 'Körperpflege', 'Mundpflege'): [
        (r'Mundsp.l', 'Mundspülung'),
        (r'Propolis', 'Propolisprodukt'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Kosmetik allgemein'): [
        (r'Kosmetik', 'Kosmetik'),
        (r'Creme\b', 'Creme'),
    ],
    ('Kosmetik & Pflege', 'Haarpflege', 'Shampoo'): [
        (r'Shampoo', 'Shampoo'),
    ],
    ('Kosmetik & Pflege', 'Haarpflege', 'Haarpflege'): [
        (r'Haarpflege.l', 'Haarpflegeöl'),
        (r'Haarbalsam', 'Haarbalsam'),
        (r'Haarsp.lung', 'Haarspülung'),
        (r'Haarspray', 'Haarspray'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Duschgel'): [
        (r'Duschgel', 'Duschgel'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Körperlotion'): [
        (r'K.rperlotion', 'Körperlotion'),
        (r'K.rperbutter', 'Körperbutter'),
    ],
    ('Kosmetik & Pflege', 'Gesichtspflege', 'Gesichtspflege'): [
        (r'Gesichtspflege', 'Gesichtspflege'),
        (r'Gesichts.Serum', 'Gesichts-Serum'),
        (r'Gesichts.l', 'Gesichtsöl'),
        (r'Gesichtstonikum', 'Gesichtstonikum'),
        (r'Augenpflege', 'Augenpflege'),
        (r'Tagespflege', 'Tagespflege'),
        (r'Nachtpflege', 'Nachtpflege'),
        (r'Aufbaumaske', 'Aufbaumaske'),
        (r'Reinigungsgel', 'Reinigungsgel'),
        (r'Reinigungsschaum', 'Reinigungsschaum'),
        (r'Reinigungsmilch', 'Reinigungsmilch'),
        (r'Reinigungspeeling', 'Reinigungspeeling'),
        (r'Reinigungspuder', 'Reinigungspuder'),
        (r'Make.up Entferner', 'Make-up Entferner'),
        (r'Pickel.Gel', 'Pickel-Gel'),
        (r'Gelmaske', 'Gelmaske'),
        (r'Feuchtigkeitsgel', 'Feuchtigkeitsgel'),
        (r'Hydrobutter', 'Hydrobutter'),
        (r'Waschschaum', 'Waschschaum'),
    ],
    ('Kosmetik & Pflege', 'Gesichtspflege', 'Abschminkprodukte'): [
        (r'Abschminkpads', 'Abschminkpads'),
        (r'Abschminkschw.mmchen', 'Abschminkschwämmchen'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Öle'): [
        (r'Pfege.l', 'Pflegeöl'),
        (r'Pflege.l', 'Pflegeöl'),
        (r'Mandel.l', 'Mandelöl'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Ölbad'): [
        (r'.lbad', 'Ölbad'),
        (r'Entspannungsbad', 'Entspannungsbad'),
    ],
    ('Kosmetik & Pflege', 'Werkzeuge', 'Pinsel'): [
        (r'F.cherpinsel', 'Fächerpinsel'),
        (r'Masken.Pinsel', 'Masken-Pinsel'),
    ],
    ('Kosmetik & Pflege', 'Werkzeuge', 'Bimsstein'): [
        (r'Bimsstein', 'Bimsstein'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Basisöle'): [
        (r'Basis.l', 'Basisöl'),
        (r'Pfege.l', 'Pflegeöl'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Fußpflege'): [
        (r'Fu.pflege', 'Fußpflege'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Handpflege'): [
        (r'Handpflege', 'Handpflege'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Nagelpflege'): [
        (r'Nagel.l', 'Nagelöl'),
    ],
    ('Kosmetik & Pflege', 'Körperpflege', 'Tonerde'): [
        (r'Tonerde', 'Tonerde'),
    ],
    ('Kosmetik & Pflege', 'Massage', 'Massageöl'): [
        (r'Massage.l', 'Massageöl'),
    ],
    ('Kosmetik & Pflege', 'Sauna', 'Saunaöl'): [
        (r'Sauna.l', 'Saunaöl'),
        (r'Saunatuch', 'Saunatuch'),
    ],
    ('Kosmetik & Pflege', 'Bürsten', 'Haarbürsten'): [
        (r'Haarb.rste', 'Haarbürste'),
        (r'B.rste', 'Bürste'),
        (r'Kamm\b', 'Kamm'),
    ],
    ('Kosmetik & Pflege', 'Bürsten', 'Körperbürsten'): [
        (r'Anti.Cellulite', 'Anti-Cellulite Produkt'),
    ],
    ('Kosmetik & Pflege', 'Schwämme', 'Badeschwämme'): [
        (r'Schwamm', 'Schwamm'),
    ],
    ('Kosmetik & Pflege', 'Möbelpflege', 'Holzpflege'): [
        (r'Kr.uterlein.l', 'Kräuterleinöl'),
        (r'Gleitessenz', 'Gleitessenz'),
        (r'Pflegemittel', 'Pflegemittel'),
        (r'Pflegeset', 'Pflegeset'),
    ],

    # =========================================================================
    # YOGA & MEDITATION
    # =========================================================================
    ('Yoga & Meditation', 'Yoga', 'Yogamatten'): [
        (r'Yogamatte', 'Yogamatte'),
    ],
    ('Yoga & Meditation', 'Yoga', 'Yogablöcke'): [
        (r'Yogablock', 'Yogablock'),
    ],
    ('Yoga & Meditation', 'Yoga', 'Yogahosen'): [
        (r'Yogahose', 'Yogahose'),
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

    # =========================================================================
    # BABY & KINDER
    # =========================================================================
    ('Baby & Kinder', 'Baby-Schlafen', 'Schlafsäcke'): [
        (r'Schlafsack', 'Schlafsack'),
        (r'Strampelsack', 'Strampelsack'),
    ],
    ('Baby & Kinder', 'Baby-Schlafen', 'Stillkissen'): [
        (r'Stillkissen', 'Stillkissen'),
    ],
    ('Baby & Kinder', 'Baby-Schlafen', 'Puckdecken'): [
        (r'Puckdecke', 'Puckdecke'),
        (r'Wickel.+decke', 'Wickeldecke'),
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
    ('Baby & Kinder', 'Baby-Zubehör', 'Stillsets'): [
        (r'Stillset', 'Stillset'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Schnullerhalter'): [
        (r'Schnullerhalter', 'Schnullerhalter'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Still- und Seitenschläferkissen'): [
        (r'Still.*Seitenschl.fer', 'Still- und Seitenschläferkissen'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Babylätzchen'): [
        (r'Babyl.tzchen', 'Babylätzchen'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Babypatschen'): [
        (r'Babypatschen', 'Babypatschen'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Babyfuton'): [
        (r'Babyfuton', 'Babyfuton'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Babydecken'): [
        (r'Babydecke', 'Babydecke'),
    ],
    ('Baby & Kinder', 'Baby-Zubehör', 'Baby-Artikel'): [
        (r'\bBaby\b', 'Baby-Artikel'),
    ],
    ('Baby & Kinder', 'Kinder', 'Kinder-Artikel'): [
        (r'\bKinder\b', 'Kinder-Artikel'),
    ],
    ('Baby & Kinder', 'Spielzeug', 'Holzspielzeug'): [
        (r'F.delspiel', 'Fädelspiel'),
        (r'Stapelturm', 'Stapelturm'),
        (r'Rolltier', 'Rolltier'),
        (r'Holzbausteine', 'Holzbausteine'),
        (r'Meilensteinkarten', 'Meilensteinkarten'),
        (r'Buntstifte', 'Buntstifte'),
    ],
    ('Baby & Kinder', 'Spielzeug', 'Spiele'): [
        (r'Memo Spiel', 'Memo Spiel'),
        (r'Kartenspiel', 'Kartenspiel'),
        (r'Spieluhr', 'Spieluhr'),
    ],
    ('Baby & Kinder', 'Spielzeug', 'Kuscheltiere'): [
        (r'Faultier', 'Faultier'),
        (r'Schmusegans', 'Schmusegans'),
        (r'Schmusetuch', 'Schmusetuch'),
        (r'Schmusewichtel', 'Schmusewichtel'),
        (r'Schlummersch.fchen', 'Schlummerschäfchen'),
        (r'Schlummerschaf', 'Schlummerschaf'),
        (r'Schlummerw.lkchen', 'Schlummerwölkchen'),
        (r'Sanftes W.lkchen', 'Sanftes Wölkchen'),
        (r'Traumhaftes W.lkchen', 'Traumhaftes Wölkchen'),
        (r'Sternenw.lkchen', 'Sternenwölkchen'),
        (r'Kuschelkissen', 'Kuschelkissen'),
        (r'Kuschelkatze', 'Kuschelkatze'),
        (r'Sonnenschein.Affe', 'Sonnenschein-Affe'),
        (r'Waldtiere', 'Waldtiere'),
    ],
    ('Baby & Kinder', 'Spielzeug', 'Rasseln'): [
        (r'Rassel', 'Rassel'),
    ],
    ('Baby & Kinder', 'Baby-Ausstattung', 'Wiegen'): [
        (r'Wiege\b', 'Wiege'),
    ],
    ('Baby & Kinder', 'Baby-Ausstattung', 'Kinderdecken'): [
        (r'Kinderdecke', 'Kinderdecke'),
    ],
    ('Baby & Kinder', 'Baby-Ausstattung', 'Kindermesslatten'): [
        (r'Kindermesslatte', 'Kindermesslatte'),
    ],
    ('Baby & Kinder', 'Baby-Ausstattung', 'Wimpelketten'): [
        (r'Wimpelkette', 'Wimpelkette'),
    ],

    # =========================================================================
    # DEKORATION
    # =========================================================================
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
        (r'Adventkranzkerzen', 'Adventkranzkerzen'),
        (r'Christbaumkugel', 'Christbaumkugel'),
        (r'Christbaumspitz', 'Christbaumspitz'),
        (r'Baumschmuck', 'Baumschmuck'),
        (r'Schneemann', 'Schneemann'),
        (r'Engel', 'Engel'),
        (r'Stern\b', 'Stern'),
        (r'Weihnacht', 'Weihnachtsartikel'),
    ],
    ('Dekoration', 'Saisonal', 'Osterdeko'): [
        (r'Osterei', 'Osterei'),
        (r'Hase\b', 'Osterhase'),
        (r'Ostern', 'Osterartikel'),
        (r'Eier\b', 'Eier-Deko'),
    ],
    ('Dekoration', 'Bilderrahmen', 'Bilderrahmen'): [
        (r'Bilderrahmen', 'Bilderrahmen'),
    ],
    ('Dekoration', 'Baldachine', 'Baldachine'): [
        (r'Baldachin', 'Baldachin'),
    ],
    ('Dekoration', 'Kerzen', 'Kerzen'): [
        (r'Rapswachskerze', 'Rapswachskerze'),
        (r'Spitzkerze', 'Spitzkerze'),
        (r'Bienenwachs', 'Bienenwachskerze'),
        (r'Figurkerze', 'Figurkerze'),
        (r'Sternenkerze', 'Sternenkerze'),
        (r'Stumpenkerze', 'Stumpenkerze'),
        (r'Teelicht', 'Teelicht'),
        (r'Kerzenbastelset', 'Kerzenbastelset'),
        (r'\bKerze\b', 'Kerze'),
    ],
    ('Dekoration', 'Kerzen', 'Kerzenhalter'): [
        (r'Kerzenhalter', 'Kerzenhalter'),
        (r'Stabkerzenst.nder', 'Stabkerzenständer'),
    ],
    ('Dekoration', 'Kerzen', 'Duftkerzen'): [
        (r'Duftkerze', 'Duftkerze'),
    ],
    ('Dekoration', 'Glas', 'Glasdeko'): [
        (r'Borosilikatglas', 'Glasdeko'),
        (r'mundgeblasen', 'Glasdeko'),
    ],
    ('Dekoration', 'Tierfiguren', 'Tierfiguren'): [
        (r'Schwalben', 'Schwalben'),
        (r'Bienen', 'Bienen'),
        (r'Pilze', 'Pilze'),
        (r'Eicheln', 'Eicheln'),
        (r'V.gelchen', 'Vögelchen'),
        (r'Kuscheltier', 'Kuscheltier'),
    ],
    ('Dekoration', 'Holzdeko', 'Holzdeko'): [
        (r'Holzkistchen', 'Holzkistchen'),
        (r'Baumschmuck', 'Baumschmuck'),
    ],

    # =========================================================================
    # BELEUCHTUNG
    # =========================================================================
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
    ('Beleuchtung', 'Zubehör', 'Lampenschirme'): [
        (r'Glasschirm', 'Glasschirm'),
        (r'Schirm\b', 'Lampenschirm'),
    ],
    ('Beleuchtung', 'Zubehör', 'Elektrozubehör'): [
        (r'Dimmschalter', 'Dimmschalter'),
    ],

    # =========================================================================
    # LEBENSMITTEL
    # =========================================================================
    ('Lebensmittel', 'Getränke', 'Kaffee & Espresso'): [
        (r'Espresso', 'Espresso'),
        (r'Kaffee', 'Kaffee'),
    ],
    ('Lebensmittel', 'Getränke', 'Tee'): [
        (r'Baldriantee', 'Baldriantee'),
        (r'\bTee\b', 'Tee'),
    ],
    ('Lebensmittel', 'Getränke', 'Sirupe'): [
        (r'Sirup', 'Sirup'),
    ],
    ('Lebensmittel', 'Getränke', 'Säfte'): [
        (r'Saft', 'Saft'),
        (r'Direktsaft', 'Direktsaft'),
    ],
    ('Lebensmittel', 'Getränke', 'Liköre'): [
        (r'Eierlik.r', 'Eierlikör'),
        (r'Lik.r', 'Likör'),
    ],
    ('Lebensmittel', 'Aufstriche', 'Fruchtaufstriche'): [
        (r'Fruchtaufstrich', 'Fruchtaufstrich'),
        (r'Marmelade', 'Marmelade'),
    ],
    ('Lebensmittel', 'Aufstriche', 'Honig'): [
        (r'Honig', 'Honig'),
    ],
    ('Lebensmittel', 'Aufstriche', 'Nussmus'): [
        (r'Haselnuss', 'Haselnussmus'),
        (r'KREM', 'Nussmus'),
    ],
    ('Lebensmittel', 'Süßes', 'Schokolade'): [
        (r'Schokolade', 'Schokolade'),
    ],
    ('Lebensmittel', 'Öle', 'Speiseöle'): [
        (r'Oliven.l', 'Olivenöl'),
        (r'Distel.l', 'Distelöl'),
        (r'Walnuss.l', 'Walnussöl'),
        (r'Lein.l', 'Leinöl'),
        (r'Hanf.l', 'Hanföl'),
    ],
    ('Lebensmittel', 'Snacks', 'Gebäck'): [
        (r'Suchtk', 'Kräcker'),
        (r'Kr.cker', 'Kräcker'),
        (r'Krustenbrot', 'Krustenbrot'),
        (r'\bBrot\b', 'Brot'),
        (r'Hanfschnitte', 'Hanfschnitte'),
    ],
    ('Lebensmittel', 'Süßes', 'Pralinen'): [
        (r'Pralinen', 'Pralinen'),
    ],
    ('Lebensmittel', 'Getränke', 'Bier'): [
        (r'Naturbursch Bier', 'Naturbursch Bier'),
        (r'\bBier\b', 'Bier'),
    ],
    ('Lebensmittel', 'Kräuter', 'Kräuter'): [
        (r'Rucola', 'Rucola'),
        (r'Kr.uter.*Provence', 'Kräuter'),
        (r'Smokey Paprika', 'Gewürz'),
        (r'Brennnesselstroh', 'Brennnesselstroh'),
        (r'Nesselfaser', 'Nesselfaser'),
        (r'Senfsaaten', 'Senfsaaten'),
        (r'Sprossen.Mix', 'Sprossen-Mix'),
        (r'Kresse', 'Kresse'),
    ],
    ('Lebensmittel', 'Aufstriche', 'Ajvar'): [
        (r'Ajvar', 'Ajvar'),
        (r'Malidano', 'Malidano'),
        (r'Pindur', 'Pindur'),
    ],
    ('Lebensmittel', 'Öle', 'Bio-Öle'): [
        (r'Bio.*l.*Kaltgepresst', 'Bio-Öl'),
        (r'Leindotter.l', 'Leindotteröl'),
        (r'B.rlauch.l', 'Bärlauchöl'),
        (r'Chili.l', 'Chiliöl'),
    ],
    ('Lebensmittel', 'Essig', 'Bio-Essig'): [
        (r'Balsam Essig', 'Balsamessig'),
        (r'Essig', 'Essig'),
    ],
    ('Lebensmittel', 'Nudeln', 'Dinkelnudeln'): [
        (r'Dinkelnudeln', 'Dinkelnudeln'),
        (r'Dinkelspitz', 'Dinkelspitz'),
    ],
    ('Lebensmittel', 'Öle', 'Olivenöle'): [
        (r'Liola', 'Olivenöl Liola'),
    ],
    ('Lebensmittel', 'Gewürze', 'Sonnentor'): [
        (r'Sonnentor', 'Sonnentor-Produkt'),
    ],
    ('Lebensmittel', 'Gewürze', 'Gewürze'): [
        (r'Gew.rz', 'Gewürz'),
    ],

    # =========================================================================
    # BÜCHER & MEDIEN
    # =========================================================================
    ('Bücher & Medien', 'Bücher', 'Bücher'): [
        (r'\bBuch\b', 'Buch'),
        (r'Buch:', 'Buch'),
    ],
    ('Bücher & Medien', 'Musik', 'CDs'): [
        (r'\bCD\b', 'CD'),
    ],
    ('Bücher & Medien', 'Film', 'DVDs'): [
        (r'\bDVD\b', 'DVD'),
    ],
    ('Bücher & Medien', 'Bücher', 'Buchserien'): [
        (r'Buchserie', 'Buchserie'),
    ],
    ('Bücher & Medien', 'Karten', 'Postkarten'): [
        (r'Postkarte', 'Postkarte'),
        (r'Karte\b', 'Karte'),
    ],
    ('Bücher & Medien', 'Spiele', 'Bastelbögen'): [
        (r'Bastelbogen', 'Bastelbogen'),
    ],

    # =========================================================================
    # GESCHENKE & GUTSCHEINE
    # =========================================================================
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

    # =========================================================================
    # TASCHEN & BEUTEL
    # =========================================================================
    ('Taschen & Beutel', 'Taschen', 'Taschen'): [
        (r'Tasche', 'Tasche'),
    ],
    ('Taschen & Beutel', 'Beutel', 'Beutel'): [
        (r'Beutel', 'Beutel'),
    ],
    ('Taschen & Beutel', 'Füllsäcke', 'Füllsäcke'): [
        (r'F.llsack', 'Füllsack'),
    ],
    ('Taschen & Beutel', 'Stoffbeutel', 'Stoffbeutel'): [
        (r'Stoffsack', 'Stoffsack'),
        (r'Stoff.Kr.utersack', 'Stoff-Kräutersack'),
    ],

    # =========================================================================
    # INTERN
    # =========================================================================
    ('Intern', 'Verpackung', 'Kartons'): [
        (r'Karton', 'Karton'),
    ],
    ('Intern', 'Verpackung', 'Papiersäcke'): [
        (r'Papiersack', 'Papiersack'),
    ],
    ('Intern', 'Verpackung', 'Seidenpapier'): [
        (r'Seidenpapier', 'Seidenpapier'),
    ],
    ('Intern', 'Verpackung', 'Klebeband'): [
        (r'Papierklebeband', 'Papierklebeband'),
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
    ('Intern', 'Aktionen', 'Pärchen-Aktionen'): [
        (r'P.rchen', 'Pärchen-Aktion'),
    ],
    ('Intern', 'Versand', 'Versand'): [
        (r'Versandkost', 'Versandkosten'),
        (r'Spedition', 'Spedition'),
    ],
    ('Intern', 'Mottenschutz', 'Mottenschutz'): [
        (r'Mottenfalle', 'Mottenfalle'),
        (r'Motten', 'Mottenschutz'),
    ],
    ('Intern', 'Beilagen', 'Produktbeileger'): [
        (r'Produktbeileger', 'Produktbeileger'),
        (r'Paketbeilage', 'Paketbeilage'),
        (r'Beileger', 'Beileger'),
    ],
    ('Intern', 'Verpackung', 'Faltschachteln'): [
        (r'Faltschachtel', 'Faltschachtel'),
    ],
    ('Intern', 'Marketing', 'Klebepunkte'): [
        (r'Klebepunkt', 'Klebepunkt'),
    ],
    ('Intern', 'Marketing', 'Abdeckkappen'): [
        (r'Abdeckkappen', 'Abdeckkappen'),
    ],
    ('Intern', 'Marketing', 'Plakate'): [
        (r'Plakat', 'Plakat'),
    ],
    ('Intern', 'Marketing', 'Display Cards'): [
        (r'Display Cards', 'Display Cards'),
    ],
    ('Intern', 'Marketing', 'Grußkarten'): [
        (r'Gru.karten', 'Grußkarten'),
    ],
    ('Intern', 'Intern', 'Stores'): [
        (r'Spatel.*Probenentnahme', 'Spatel'),
        (r'Handdesinfektion', 'Handdesinfektion'),
        (r'Halterung Listello', 'Halterung'),
        (r'B.gel Valetto', 'Bügel'),
    ],
    ('Intern', 'Intern', 'Finanzen'): [
        (r'Zinsaussch.ttung', 'Zinsausschüttung'),
        (r'Freundeskreis Bonus', 'Freundeskreis Bonus'),
        (r'Geburtstagsmailing', 'Geburtstagsmailing'),
        (r'Discount', 'Discount'),
    ],
    ('Intern', 'Muster', 'Möbelmuster'): [
        (r'Muster Badezimmerm.bel', 'Möbelmuster'),
        (r'Muster Betten', 'Möbelmuster'),
        (r'Muster B.rom.bel', 'Möbelmuster'),
        (r'Muster Kinderm.bel', 'Möbelmuster'),
        (r'Muster Kleinm.bel', 'Möbelmuster'),
        (r'Muster Polsterm.bel', 'Möbelmuster'),
        (r'Muster Schr.nke', 'Möbelmuster'),
        (r'Muster St.hle', 'Möbelmuster'),
        (r'Muster Teppiche', 'Möbelmuster'),
        (r'Muster Tische', 'Möbelmuster'),
        (r'Muster Vorh.nge', 'Möbelmuster'),
        (r'Querschnitt', 'Querschnitt'),
    ],
    ('Intern', 'Sonstiges', 'Sonstiges'): [
        (r'Gutschrift', 'Gutschrift'),
        (r'Wunschliste', 'Wunschliste'),
        (r'SHOP', 'Shop-Artikel'),
        (r'Shop\b', 'Shop-Artikel'),
        (r'Laden\b', 'Laden-Artikel'),
        (r'NUR\b', 'NUR-Artikel'),
        (r'FREI\b', 'Frei-Artikel'),
        (r'UNIQUE', 'UNIQUE'),
        (r'Sonderanfertigung', 'Sonderanfertigung'),
        (r'Ma.anfertigung', 'Maßanfertigung'),
        (r'Probe\b', 'Probe'),
        (r'copy\b', 'Kopie'),
        (r'Abf.llung', 'Abfüllung'),
        (r'Bulk', 'Bulk'),
        (r'Diverse', 'Diverses'),
        (r'Sortimentkoffer', 'Sortimentkoffer'),
        (r'Darlehensvertrag', 'Darlehensvertrag'),
        (r'F.llmaterialien', 'Füllmaterialien'),
    ],

    # =========================================================================
    # WEITERE PRODUKTE
    # =========================================================================
    ('Kleidung', 'Schuhe', 'Schuhe allgemein'): [
        (r'\bSchuh\b', 'Schuh'),
    ],
    ('Küche & Haushalt', 'Küchenzubehör', 'Sonstiges Küchenzubehör'): [
        (r'Gl.ser f.r', 'Gläser für Speisen'),
        (r'Gef..', 'Gefäß'),
    ],
    ('Heimtextilien', 'Sonstiges', 'Sitzauflagen'): [
        (r'Polsterauflage', 'Polsterauflage'),
        (r'Sitzauflage', 'Sitzauflage'),
    ],
    ('Wellness & Duft', 'Naturprodukte', 'Naturprodukte'): [
        (r'Propolis', 'Propolis'),
    ],
    ('Wellness & Duft', 'Naturprodukte', 'Lavendel'): [
        (r'Lavendel.Sack', 'Lavendel-Sack'),
        (r'Zirben.Sack', 'Zirben-Sack'),
        (r'Alpaka.Pellets', 'Alpaka-Pellets'),
    ],

    # =========================================================================
    # GARTEN
    # =========================================================================
    ('Garten', 'Samen', 'Blumenwiese'): [
        (r'Blumenwiese', 'Blumenwiese'),
        (r'Samen\b', 'Samen'),
    ],
    ('Garten', 'Pflege', 'Holzpflege'): [
        (r'Holzpflege', 'Holzpflege'),
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
    output_file = 'produktkategorien_v2.xlsx'

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
    print(f"Kategorisiert: {len(kategorisiert)} von {len(products)} Produkten ({100*len(kategorisiert)/len(products):.1f}%)")
    print(f"Unkategorisiert: {len(products) - len(kategorisiert)} ({100*(len(products) - len(kategorisiert))/len(products):.1f}%)")

    # Zusammenfassung nach Hauptkategorie
    print("\n=== ZUSAMMENFASSUNG ===")
    summary = df.groupby('Hauptkategorie')['Anzahl'].sum().sort_values(ascending=False)
    for kat, anzahl in summary.items():
        print(f"{kat}: {anzahl}")


if __name__ == '__main__':
    main()
