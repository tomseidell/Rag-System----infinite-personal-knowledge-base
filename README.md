# FastAPI Project

Ein einfaches FastAPI-Projekt mit grundlegender Konfiguration.

## Einrichtung

1. Erstellen Sie eine virtuelle Umgebung (empfohlen):
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

2. Installieren Sie die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

## Starten der Anwendung

Starten Sie den Server mit:
```bash
python main.py
```
oder
```bash
uvicorn main:app --reload
```

Der Server läuft dann unter http://localhost:8000

## API-Dokumentation

- Swagger UI (OpenAPI): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Verfügbare Endpunkte

- `GET /`: Willkommensnachricht
- `GET /health`: Gesundheitscheck der API

## Entwicklung

Das Projekt verwendet:
- FastAPI für das API-Framework
- Uvicorn als ASGI-Server
- Pydantic für Datenvalidierung
- python-dotenv für Umgebungsvariablen
