import os

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from Buy import kaufe_aktie
from Depot import depot_summe, get_depot, get_transaktionen
from Sell import verkaufe_aktie
from Stock import get_stock_price
from Wallet import get_spieler

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-nur-zum-testen")

SPIELER_ID = 1
STARTKAPITAL = 10000  # nur für die Gesamtbilanz-Anzeige


@app.template_filter("eur")
def eur(wert):
    """12345.6 -> '12.345,60'"""
    if wert is None:
        return "–"
    text = f"{wert:,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        symbol = request.form.get("symbol", "").upper().strip()

        try:
            anzahl = int(request.form.get("anzahl", "0"))
        except ValueError:
            anzahl = 0

        if not symbol or anzahl <= 0:
            flash("Bitte ein Symbol und eine Anzahl größer als 0 eingeben.", "fehler")
            return redirect(url_for("home"))

        kurs = get_stock_price(symbol)

        if "buy" in request.form:
            ok, meldung = kaufe_aktie(SPIELER_ID, symbol, anzahl, kurs)
        elif "sell" in request.form:
            ok, meldung = verkaufe_aktie(SPIELER_ID, symbol, anzahl, kurs)
        else:
            return redirect(url_for("home"))

        flash(meldung, "ok" if ok else "fehler")
        # Redirect nach POST: Seite neu laden kauft nicht nochmal!
        return redirect(url_for("home"))

    spieler = get_spieler(SPIELER_ID)
    depot = get_depot(SPIELER_ID)
    depot_wert, depot_gewinn = depot_summe(depot)
    gesamt = spieler["guthaben"] + depot_wert

    return render_template(
        "index.html",
        spieler=spieler,
        depot=depot,
        depot_wert=depot_wert,
        depot_gewinn=depot_gewinn,
        gesamt=gesamt,
        bilanz=gesamt - STARTKAPITAL,
        transaktionen=get_transaktionen(SPIELER_ID),
    )


@app.route("/api/kurs/<symbol>")
def api_kurs(symbol):
    """Wird von der Kursvorschau im Formular genutzt."""
    kurs = get_stock_price(symbol)
    if kurs is None:
        return jsonify({"ok": False}), 404
    return jsonify({"ok": True, "symbol": symbol.upper(), "kurs": float(kurs)})


if __name__ == "__main__":
    app.run(debug=True)
