#!/usr/bin/env python3
"""
PDF Generator für Projektsteckbrief
Konvertiert Markdown zu professionell formatiertem PDF
"""

import markdown2
from weasyprint import HTML, CSS
from pathlib import Path

# CSS für professionelles Layout
CSS_STYLE = """
@page {
    size: A4;
    margin: 2.5cm 2cm 2cm 2cm;

    @top-right {
        content: "Seite " counter(page) " von " counter(pages);
        font-size: 9pt;
        color: #666;
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    @bottom-center {
        content: "Matthias Sax GmbH | m.sax@matthias-sax.de | (+49) 151 20 792 782";
        font-size: 8pt;
        color: #999;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
}

body {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 24pt;
    font-weight: 600;
    color: #1a1a1a;
    margin-top: 0;
    margin-bottom: 0.5cm;
    padding-bottom: 0.3cm;
    border-bottom: 3px solid #0066cc;
}

h2 {
    font-size: 16pt;
    font-weight: 600;
    color: #0066cc;
    margin-top: 0.8cm;
    margin-bottom: 0.4cm;
    padding-bottom: 0.15cm;
    border-bottom: 1px solid #ccc;
    page-break-after: avoid;
}

h3 {
    font-size: 13pt;
    font-weight: 600;
    color: #333;
    margin-top: 0.6cm;
    margin-bottom: 0.3cm;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #0066cc;
    margin-top: 0.4cm;
    margin-bottom: 0.2cm;
}

h5 {
    font-size: 10pt;
    font-weight: 600;
    color: #333;
    margin-top: 0.3cm;
    margin-bottom: 0.15cm;
}

p {
    margin-bottom: 0.3cm;
    text-align: justify;
}

ul, ol {
    margin-left: 0.5cm;
    margin-bottom: 0.3cm;
}

li {
    margin-bottom: 0.15cm;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.4cm 0;
    font-size: 9.5pt;
}

th {
    background-color: #0066cc;
    color: white;
    font-weight: 600;
    padding: 0.3cm;
    text-align: left;
    border: 1px solid #0066cc;
}

td {
    padding: 0.25cm;
    border: 1px solid #ddd;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 0.5cm 0;
}

strong {
    font-weight: 600;
    color: #1a1a1a;
}

code {
    background-color: #f4f4f4;
    padding: 0.1cm 0.15cm;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    color: #d63384;
}

.contact-info {
    font-size: 9pt;
    color: #666;
    margin-bottom: 0.5cm;
}

.highlight {
    background-color: #fffacd;
    padding: 0.05cm 0.1cm;
}

/* Verhindere Seitenumbrüche in kritischen Bereichen */
h2, h3, h4, h5, h6 {
    page-break-after: avoid;
}

table, figure {
    page-break-inside: avoid;
}

/* Erste Seite spezielle Formatierung */
body > h1:first-child {
    margin-top: 0;
}
"""

def markdown_to_html(markdown_file: Path) -> str:
    """Konvertiert Markdown zu HTML"""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Konvertiere Markdown zu HTML mit Extras
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            'tables',
            'fenced-code-blocks',
            'break-on-newline',
            'header-ids'
        ]
    )

    # Wickle in HTML-Dokument
    full_html = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Projektsteckbrief - Grüne Erde GmbH</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    return full_html

def generate_pdf(markdown_file: Path, output_file: Path):
    """Generiert PDF aus Markdown"""
    print(f"📄 Lese Markdown-Datei: {markdown_file}")
    html_content = markdown_to_html(markdown_file)

    print(f"🎨 Wende professionelles Styling an...")
    html = HTML(string=html_content)
    css = CSS(string=CSS_STYLE)

    print(f"📝 Generiere PDF: {output_file}")
    html.write_pdf(output_file, stylesheets=[css])

    print(f"✅ PDF erfolgreich erstellt: {output_file}")
    print(f"📊 Dateigröße: {output_file.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    # Pfade
    base_dir = Path(__file__).parent
    markdown_file = base_dir / "projektsteckbrief.md"
    output_file = base_dir / "Projektsteckbrief_Gruene_Erde_Matthias_Sax.pdf"

    # Prüfe ob Markdown-Datei existiert
    if not markdown_file.exists():
        print(f"❌ Fehler: Markdown-Datei nicht gefunden: {markdown_file}")
        exit(1)

    # Generiere PDF
    generate_pdf(markdown_file, output_file)
    print(f"\n🎉 Fertig! PDF wurde erstellt.")
    print(f"📁 Speicherort: {output_file.absolute()}")
