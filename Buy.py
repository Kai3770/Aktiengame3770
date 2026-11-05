from decimal import Decimal

from db import get_db


def kaufe_aktie(spieler_id, symbol, anzahl, kurs):
    """Kauft Aktien. Gibt (erfolg, meldung) zurück.

    Alles passiert in EINER Transaktion: Entweder klappt alles oder nichts.
    Das Abbuchen prüft das Guthaben direkt in der Datenbank, so kann man
    auch mit zwei gleichzeitigen Klicks nicht ins Minus rutschen.
    """
    if kurs is None:
        return False, "Kurs nicht verfügbar – Symbol prüfen."

    kosten = (Decimal(kurs) * anzahl).quantize(Decimal("0.01"))

    try:
        with get_db() as conn:
            abgebucht = conn.execute(
                """
                UPDATE spieler
                SET guthaben = guthaben - %s
                WHERE id = %s AND guthaben >= %s
                RETURNING guthaben
                """,
                (kosten, spieler_id, kosten),
            ).fetchone()

            if not abgebucht:
                return False, "Nicht genug Guthaben."

            # Gleiche Aktie nochmal gekauft -> Position zusammenlegen,
            # Kaufkurs wird als Durchschnitt neu berechnet.
            conn.execute(
                """
                INSERT INTO depot (spieler_id, symbol, anzahl, kaufkurs)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (spieler_id, symbol) DO UPDATE
                SET kaufkurs = (depot.kaufkurs * depot.anzahl
                                + EXCLUDED.kaufkurs * EXCLUDED.anzahl)
                               / (depot.anzahl + EXCLUDED.anzahl),
                    anzahl = depot.anzahl + EXCLUDED.anzahl
                """,
                (spieler_id, symbol, anzahl, kurs),
            )

            conn.execute(
                """
                INSERT INTO transaktionen
                    (spieler_id, symbol, anzahl, preis, aktion)
                VALUES (%s, %s, %s, %s, 'KAUF')
                """,
                (spieler_id, symbol, anzahl, kurs),
            )
        return True, f"{anzahl}x {symbol} für {kosten:.2f} € gekauft."

    except Exception as e:
        print("Fehler beim Kauf:", e)
        return False, "Kauf fehlgeschlagen (Datenbankfehler)."
