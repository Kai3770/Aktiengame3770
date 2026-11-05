import os
import time
from decimal import Decimal

import requests

# Den Key NICHT mehr im Code speichern, sondern als Umgebungsvariable setzen:
#   Windows (PowerShell):  $env:FINNHUB_API_KEY="dein_key"
#   Linux/Mac:             export FINNHUB_API_KEY="dein_key"
API_KEY = os.getenv("FINNHUB_API_KEY", "")

CACHE_SEKUNDEN = 30
_cache = {}  # symbol -> (zeitstempel, preis)


def get_stock_price(symbol):
    """Aktueller Kurs als Decimal oder None, wenn das Symbol unbekannt ist."""
    symbol = symbol.upper().strip()

    eintrag = _cache.get(symbol)
    if eintrag and time.time() - eintrag[0] < CACHE_SEKUNDEN:
        return eintrag[1]

    if not API_KEY:
        print("FINNHUB_API_KEY ist nicht gesetzt")
        return eintrag[1] if eintrag else None

    try:
        antwort = requests.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": API_KEY},
            timeout=5,
        )
        antwort.raise_for_status()
        preis = antwort.json().get("c")
    except (requests.RequestException, ValueError) as e:
        print("Kursabfrage fehlgeschlagen:", e)
        # Bei Netzwerkproblemen lieber den alten Kurs nehmen als gar keinen
        return eintrag[1] if eintrag else None

    # Finnhub liefert 0 zurück, wenn das Symbol nicht existiert
    if not preis or preis <= 0:
        return None

    preis = Decimal(str(preis))
    _cache[symbol] = (time.time(), preis)
    return preis
