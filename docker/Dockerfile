# E2E Test Runner mit Playwright
FROM python:3.11-slim

# Playwright-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Python-Dependencies zuerst (für Cache-Optimierung)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Browser installieren
RUN playwright install chromium

# Anwendungscode
COPY . .

# Reports-Verzeichnis
RUN mkdir -p /app/reports/traces /app/reports/html /app/reports/screenshots

# Pytest als Entrypoint
ENTRYPOINT ["pytest"]
CMD ["playwright_tests/", "-v", "--html=/app/reports/html/report.html", "--self-contained-html"]
