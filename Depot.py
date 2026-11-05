from decimal import Decimal

from db import get_db
from Stock import get_stock_price

NULL = Decimal("0")


def get_depot(spieler_id):
    """Depot mit Live-Kursen, Wert und Gewinn/Verlust pro Position."""
    with get_db() as conn:
        zeilen = conn.execute(
            """
            SELECT symbol, anzahl, kaufkurs
            FROM depot
            WHERE spieler_id = %s
            ORDER BY symbol
            """,
            (spieler_id,),
        ).fetchall()

    positionen = []
    for z in zeilen:
        aktuell = get_stock_price(z["symbol"])
        einsatz = z["kaufkurs"] * z["anzahl"]

        if aktuell is None:
            wert = None
            gewinn = None
            prozent = None
        else:
            wert = aktuell * z["anzahl"]
            gewinn = wert - einsatz
            prozent = (gewinn / einsatz * 100) if einsatz else NULL

        positionen.append(
            {
                "symbol": z["symbol"],
                "anzahl": z["anzahl"],
                "kaufkurs": z["kaufkurs"],
                "kurs": aktuell,
                "wert": wert,
                "gewinn": gewinn,
                "prozent": prozent,
            }
        )
    return positionen


def depot_summe(positionen):
    """Gesamtwert und Gesamtgewinn aller Positionen."""
    wert = sum((p["wert"] for p in positionen if p["wert"] is not None), NULL)
    gewinn = sum((p["gewinn"] for p in positionen if p["gewinn"] is not None), NULL)
    return wert, gewinn


def get_transaktionen(spieler_id, limit=10):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT symbol, anzahl, preis, aktion, zeitpunkt
            FROM transaktionen
            WHERE spieler_id = %s
            ORDER BY zeitpunkt DESC, id DESC
            LIMIT %s
            """,
            (spieler_id, limit),
        ).fetchall()
