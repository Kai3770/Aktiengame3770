from db import get_db


def get_spieler(spieler_id):
    """Liefert {'id', 'name', 'guthaben'} oder None."""
    with get_db() as conn:
        return conn.execute(
            "SELECT id, name, guthaben FROM spieler WHERE id = %s",
            (spieler_id,),
        ).fetchone()
