-- Einmalig ausführen (z. B. in pgAdmin oder: psql -U postgres -f schema.sql)
-- Passt deine bestehenden Tabellen an, ohne Daten zu löschen.

BEGIN;

-- 1) Zeitstempel für den Transaktionsverlauf
ALTER TABLE transaktionen
    ADD COLUMN IF NOT EXISTS zeitpunkt TIMESTAMPTZ NOT NULL DEFAULT now();

-- 2) Doppelte Depot-Zeilen (gleiche Aktie mehrfach gekauft) zusammenlegen
CREATE TEMP TABLE depot_merged AS
SELECT spieler_id,
       symbol,
       SUM(anzahl)::int AS anzahl,
       ROUND(SUM(anzahl * kaufkurs) / SUM(anzahl), 4) AS kaufkurs
FROM depot
GROUP BY spieler_id, symbol;

DELETE FROM depot;

INSERT INTO depot (spieler_id, symbol, anzahl, kaufkurs)
SELECT spieler_id, symbol, anzahl, kaufkurs FROM depot_merged;

-- 3) Pro Spieler und Aktie nur noch eine Zeile erlaubt
ALTER TABLE depot
    ADD CONSTRAINT depot_spieler_symbol_uniq UNIQUE (spieler_id, symbol);

-- 4) Schutz vor negativem Guthaben und ungültigen Mengen
ALTER TABLE spieler ADD CONSTRAINT guthaben_nicht_negativ CHECK (guthaben >= 0);
ALTER TABLE depot   ADD CONSTRAINT anzahl_positiv CHECK (anzahl > 0);

COMMIT;
