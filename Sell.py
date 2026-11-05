from decimal import Decimal

from db import get_db


def verkaufe_aktie(spieler_id, symbol, anzahl, kurs):
    """Verkauft Aktien. Gibt (erfolg, meldung) zurück."""
    if kurs is None:
        return False, "Kurs nicht verfügbar – Symbol prüfen."

    erloes = (Decimal(kurs) * anzahl).quantize(Decimal("0.01"))

    try:
        with get_db() as conn:
            # FOR UPDATE sperrt die Zeile, damit nicht zwei Verkäufe
            # gleichzeitig dieselben Aktien verkaufen können.
            position = conn.execute(
                """
                SELECT id, anzahl, kaufkurs
                FROM depot
                WHERE spieler_id = %s AND symbol = %s
                FOR UPDATE
                """,
                (spieler_id, symbol),
            ).fetchone()

            if not position or position["anzahl"] < anzahl:
                return False, "Nicht genug Aktien vorhanden."

            if position["anzahl"] == anzahl:
                conn.execute("DELETE FROM depot WHERE id = %s", (position["id"],))
            else:
                conn.execute(
                    "UPDATE depot SET anzahl = anzahl - %s WHERE id = %s",
                    (anzahl, position["id"]),
                )

            conn.execute(
                "UPDATE spieler SET guthaben = guthaben + %s WHERE id = %s",
                (erloes, spieler_id),
            )

            conn.execute(
                """
                INSERT INTO transaktionen
                    (spieler_id, symbol, anzahl, preis, aktion)
                VALUES (%s, %s, %s, %s, 'VERKAUF')
                """,
                (spieler_id, symbol, anzahl, kurs),
            )

        gewinn = erloes - (position["kaufkurs"] * anzahl).quantize(Decimal("0.01"))
        vorzeichen = "+" if gewinn >= 0 else ""
        return True, (
            f"{anzahl}x {symbol} für {erloes:.2f} € verkauft "
            f"({vorzeichen}{gewinn:.2f} € Gewinn/Verlust)."
        )

    except Exception as e:
        print("Fehler beim Verkauf:", e)
        return False, "Verkauf fehlgeschlagen (Datenbankfehler)."
