# 📈 Börsenspiel

## Einrichten

1. Pakete installieren: `pip install -r requirements.txt`
2. Datenbank anpassen: `schema.sql` einmal ausführen (legt Zeitstempel an, legt doppelte Depot-Zeilen zusammen, fügt Schutzregeln hinzu).
3. Finnhub-Key als Umgebungsvariable setzen:
   - Windows (PowerShell): `$env:FINNHUB_API_KEY="dein_neuer_key"`
   - Linux/Mac: `export FINNHUB_API_KEY="dein_neuer_key"`
4. Starten: `python app.py` und `http://127.0.0.1:5000` öffnen.

Optional: `SECRET_KEY`, `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

## Wichtig

Dein alter Finnhub-Key stand im Klartext im Code. Erzeuge im Finnhub-Dashboard einen neuen und lösche den alten.
