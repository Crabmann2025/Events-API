# Python-Image
FROM python:3.13-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den Rest des Codes kopieren
COPY . .

# Den Port deiner API freigeben (meist 5000 oder 8000)
EXPOSE 5000

# Befehl zum Starten der App
CMD ["python", "app.py"]