#!/usr/bin/env python3
"""
Konvertiert das Test-Konzept Markdown in ein schön formatiertes HTML-Dokument.
"""

import re
from pathlib import Path
from datetime import datetime

def markdown_to_html(md_content: str) -> str:
    """Konvertiert Markdown zu HTML mit Custom-Styling."""

    # Ersetze Progress-Bar Kommentar mit HTML (einzeilig um p-Tag-Problem zu vermeiden)
    progress_pattern = r'<!-- PROGRESS_BAR:(\d+):(\d+):(\d+) -->'
    progress_match = re.search(progress_pattern, md_content)
    if progress_match:
        impl = progress_match.group(1)
        total = progress_match.group(2)
        percent = progress_match.group(3)
        progress_html = f'<div class="progress-container"><div class="progress-header"><span class="progress-title">Gesamtfortschritt</span><span class="progress-stats"><strong>{impl}</strong> von <strong>{total}</strong> Tests implementiert</span></div><div class="progress-bar-wrapper"><div class="progress-bar" style="width: {percent}%;"></div></div><div class="progress-percent">{percent}%</div></div>'
        md_content = re.sub(progress_pattern, progress_html, md_content)

    # Ersetze Status-Symbole mit HTML-Badges
    md_content = md_content.replace('✅', '<span class="badge badge-success">✓ Abgeschlossen</span>')
    md_content = md_content.replace('⚠️', '<span class="badge badge-warning">⚠ Teilweise</span>')
    md_content = md_content.replace('❌', '<span class="badge badge-error">✗ Fehlend</span>')
    md_content = md_content.replace('⏳', '<span class="badge badge-pending">⏳ Offen</span>')

    # Ersetze Prioritäten mit Badges
    md_content = md_content.replace('🔴 P0', '<span class="badge badge-priority-p0">P0 Kritisch</span>')
    md_content = md_content.replace('🟠 P1', '<span class="badge badge-priority-p1">P1 Hoch</span>')
    md_content = md_content.replace('🟡 P2', '<span class="badge badge-priority-p2">P2 Mittel</span>')
    md_content = md_content.replace('🔴 Kritisch', '<span class="badge badge-priority-p0">Kritisch</span>')
    md_content = md_content.replace('🟠 Hoch', '<span class="badge badge-priority-p1">Hoch</span>')
    md_content = md_content.replace('🟡 Mittel', '<span class="badge badge-priority-p2">Mittel</span>')

    lines = md_content.split('\n')
    html_lines = []
    in_list = False
    in_ordered_list = False
    in_table = False
    in_code_block = False

    for i, line in enumerate(lines):
        # Code-Blöcke
        if line.strip().startswith('```'):
            if not in_code_block:
                html_lines.append('<pre><code>')
                in_code_block = True
            else:
                html_lines.append('</code></pre>')
                in_code_block = False
            continue

        if in_code_block:
            html_lines.append(line)
            continue

        # Headers mit IDs für Anker
        if line.startswith('# '):
            text = line[2:]
            anchor_id = text.lower().replace(' ', '-').replace(':', '').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
            html_lines.append(f'<h1 id="{anchor_id}">{text}</h1>')
        elif line.startswith('## '):
            text = line[3:]
            anchor_id = text.lower().replace(' ', '-').replace(':', '').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
            html_lines.append(f'<h2 id="{anchor_id}">{text}</h2>')
        elif line.startswith('### '):
            text = line[4:]
            anchor_id = text.lower().replace(' ', '-').replace(':', '').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
            html_lines.append(f'<h3 id="{anchor_id}">{text}</h3>')
        elif line.startswith('#### '):
            text = line[5:]
            anchor_id = text.lower().replace(' ', '-').replace(':', '').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
            html_lines.append(f'<h4 id="{anchor_id}">{text}</h4>')
        elif line.startswith('##### '):
            text = line[6:]
            anchor_id = text.lower().replace(' ', '-').replace(':', '').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
            html_lines.append(f'<h5 id="{anchor_id}">{text}</h5>')
        # Tabellen
        elif '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                html_lines.append('<div class="table-wrapper"><table class="test-table">')
                # Header-Zeile
                cells = [c.strip() for c in line.split('|')[1:-1]]
                html_lines.append('<thead><tr>')
                for cell in cells:
                    html_lines.append(f'<th>{cell}</th>')
                html_lines.append('</tr></thead><tbody>')
            elif '---' in line:
                # Separator-Zeile überspringen
                continue
            else:
                # Daten-Zeile
                cells = [c.strip() for c in line.split('|')[1:-1]]
                html_lines.append('<tr>')
                for cell in cells:
                    # Konvertiere Markdown-Links in HTML
                    cell = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', cell)
                    html_lines.append(f'<td>{cell}</td>')
                html_lines.append('</tr>')
        elif in_table and not line.strip().startswith('|'):
            html_lines.append('</tbody></table></div>')
            in_table = False
            # Verarbeite diese Zeile weiter
        else:
            # Schließe offene Tabelle
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False

            # Listen
            if line.strip().startswith('- '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                content = line.strip()[2:]
                # Konvertiere Markdown-Links
                content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', content)
                html_lines.append(f'<li>{content}</li>')
            elif in_list and not line.strip().startswith('- '):
                html_lines.append('</ul>')
                in_list = False
            # Geordnete Listen
            elif re.match(r'^\d+\.\s', line.strip()):
                if not in_ordered_list:
                    html_lines.append('<ol>')
                    in_ordered_list = True
                content = re.sub(r'^\d+\.\s', '', line.strip())
                # Konvertiere Markdown-Links
                content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', content)
                html_lines.append(f'<li>{content}</li>')
            elif in_ordered_list and not re.match(r'^\d+\.\s', line.strip()):
                html_lines.append('</ol>')
                in_ordered_list = False
            else:
                # Bold
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                # Inline Code
                line = re.sub(r'`([^`]+)`', r'<code>\1</code>', line)
                # Markdown-Links
                line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', line)
                # Blockquotes
                if line.strip().startswith('> '):
                    content = line.strip()[2:]
                    html_lines.append(f'<blockquote>{content}</blockquote>')
                # Horizontale Linien
                elif line.strip() == '---':
                    html_lines.append('<hr>')
                # Normale Zeilen
                elif line.strip() and not line.startswith('<'):
                    html_lines.append(f'<p>{line}</p>')
                else:
                    html_lines.append(line)

    # Schließe offene Elemente
    if in_list:
        html_lines.append('</ul>')
    if in_ordered_list:
        html_lines.append('</ol>')
    if in_table:
        html_lines.append('</tbody></table></div>')

    return '\n'.join(html_lines)


def create_html_document(md_file: Path, output_file: Path):
    """Erstellt das HTML-Dokument."""

    # Lese Markdown
    md_content = md_file.read_text(encoding='utf-8')

    # Konvertiere zu HTML
    body_html = markdown_to_html(md_content)

    # HTML-Template
    html_template = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test-Konzept: Grüne Erde E-Commerce Shop</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        :root {{
            --primary-color: #2c5f2d;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --error-color: #dc3545;
            --info-color: #17a2b8;
            --text-color: #333;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --border-color: #dee2e6;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background: var(--bg-color);
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 40px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}

        /* Back to top button */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--primary-color);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: all 0.3s;
            font-size: 24px;
        }}

        .back-to-top:hover {{
            background: #1a3a1b;
            transform: translateY(-5px);
        }}

        header {{
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        h1 {{
            color: var(--primary-color);
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        h2 {{
            color: var(--primary-color);
            font-size: 2em;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
            scroll-margin-top: 20px;
        }}

        h3 {{
            color: #495057;
            font-size: 1.5em;
            margin: 30px 0 15px 0;
            scroll-margin-top: 20px;
        }}

        h4 {{
            color: #495057;
            font-size: 1.25em;
            margin: 25px 0 10px 0;
            scroll-margin-top: 20px;
        }}

        h5 {{
            color: #6c757d;
            font-size: 1.1em;
            margin: 20px 0 10px 0;
        }}

        p {{
            margin: 10px 0;
        }}

        a {{
            color: var(--primary-color);
            text-decoration: none;
            transition: color 0.2s;
        }}

        a:hover {{
            color: #1a3a1b;
            text-decoration: underline;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0 2px;
            white-space: nowrap;
        }}

        .badge-success {{
            background: var(--success-color);
            color: white;
        }}

        .badge-warning {{
            background: var(--warning-color);
            color: #333;
        }}

        .badge-error {{
            background: var(--error-color);
            color: white;
        }}

        .badge-pending {{
            background: #6c757d;
            color: white;
        }}

        .badge-priority-p0 {{
            background: #dc3545;
            color: white;
        }}

        .badge-priority-p1 {{
            background: #fd7e14;
            color: white;
        }}

        .badge-priority-p2 {{
            background: #ffc107;
            color: #333;
        }}

        .table-wrapper {{
            overflow-x: auto;
            margin: 20px 0;
        }}

        .test-table {{
            width: 100%;
            border-collapse: collapse;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background: white;
        }}

        .test-table thead {{
            background: var(--primary-color);
            color: white;
        }}

        .test-table th,
        .test-table td {{
            padding: 12px 15px;
            text-align: left;
            border: 1px solid var(--border-color);
        }}

        .test-table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .test-table tbody tr:hover {{
            background: #e9ecef;
        }}

        ul, ol {{
            margin: 15px 0 15px 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #d63384;
        }}

        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        blockquote {{
            border-left: 4px solid var(--primary-color);
            padding: 10px 20px;
            margin: 15px 0;
            background: #f8f9fa;
            font-style: italic;
        }}

        hr {{
            border: none;
            border-top: 2px solid var(--border-color);
            margin: 30px 0;
        }}

        .metadata {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin: 15px 0;
            color: #6c757d;
        }}

        .metadata strong {{
            color: var(--text-color);
        }}

        .summary-box {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 8px;
            border-left: 5px solid var(--primary-color);
            margin: 20px 0;
        }}

        /* Progress Bar Styles */
        .progress-container {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 20px 25px;
            margin: 20px 0 25px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid var(--border-color);
        }}

        .progress-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .progress-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: var(--primary-color);
        }}

        .progress-stats {{
            color: #6c757d;
            font-size: 0.95em;
        }}

        .progress-stats strong {{
            color: var(--text-color);
        }}

        .progress-bar-wrapper {{
            background: #e9ecef;
            border-radius: 10px;
            height: 24px;
            overflow: hidden;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }}

        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color) 0%, #4a9c4b 100%);
            border-radius: 10px;
            transition: width 0.6s ease;
            position: relative;
        }}

        .progress-bar::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(255,255,255,0.2) 50%,
                rgba(255,255,255,0) 100%
            );
            animation: shimmer 2s infinite;
        }}

        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}

        .progress-percent {{
            text-align: center;
            margin-top: 10px;
            font-size: 1.5em;
            font-weight: 700;
            color: var(--primary-color);
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                padding: 20px;
            }}

            .back-to-top {{
                display: none;
            }}

            h2 {{
                page-break-before: always;
            }}

            .test-table {{
                page-break-inside: avoid;
            }}

            a {{
                color: var(--text-color);
                text-decoration: none;
            }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            h1 {{
                font-size: 2em;
            }}

            h2 {{
                font-size: 1.5em;
            }}

            .test-table {{
                font-size: 0.85em;
            }}

            .test-table th,
            .test-table td {{
                padding: 8px 10px;
            }}

            .back-to-top {{
                width: 40px;
                height: 40px;
                font-size: 20px;
            }}
        }}

        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid var(--border-color);
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}

        /* Highlight für verlinkte Sektionen */
        :target {{
            animation: highlight 2s;
        }}

        @keyframes highlight {{
            0% {{
                background-color: #fff3cd;
            }}
            100% {{
                background-color: transparent;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <main>
            {body_html}
        </main>

        <footer class="footer">
            <p>Generiert am {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}</p>
            <p>GE-ECommerce-Testing © 2026</p>
        </footer>
    </div>

    <a href="#test-konzept-gruene-erde-e-commerce-shop" class="back-to-top" title="Zurück nach oben">↑</a>
</body>
</html>
"""

    # Schreibe HTML-Datei
    output_file.write_text(html_template, encoding='utf-8')
    print(f"[OK] HTML-Dokument erstellt: {output_file}")
    print(f"[OK] Dateigroesse: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    # Pfade
    project_root = Path(__file__).parent.parent
    md_file = project_root / "docs" / "test-concept.md"
    output_file = project_root / "docs" / "test-concept.html"

    if not md_file.exists():
        print(f"[FEHLER] Markdown-Datei nicht gefunden: {md_file}")
        exit(1)

    # Erstelle HTML
    create_html_document(md_file, output_file)
    print(f"\n[INFO] Oeffnen Sie die Datei im Browser:")
    print(f"       {output_file}")
