"""Onglet ⚖️ Acheter ou crafter : chaines d'amelioration (blanc -> ... -> base unique -> equipement du Roi dragon)."""
from ..chains import HIST_DAYS, load_history


def chains_tab(ctx, con, cfg, my):
    """Donnees des chaines (prix du passage) et historique du cout de chaque option ; tout le calcul avec mes niveaux
    est fait dans le navigateur (site.js, partie « chaines »)."""
    ctx.data["CHAINS"] = my.get("chains") or []
    ctx.data["CHAINS_HIST"] = load_history(con, my["server"])
    ctx.data["CHAIN_CFG"] = dict(fees=cfg["fees"], days=HIST_DAYS)
    return ("<h2>⚖️ Acheter ou crafter</h2><p class='lead'>Pour chaque équipement unique qui se fabrique en chaîne "
            "(objet blanc → éclatant → expert → maître → <b>base unique</b> → équipement du Roi dragon) : combien coûte la base "
            "selon le palier où tu commences. Tu peux <b>tout crafter</b> depuis l’objet blanc, <b>acheter un objet éclatant</b> "
            "intermédiaire et crafter la suite, ou <b>acheter directement la base</b>. Chaque palier ne donne l’objet éclatant "
            "qu’au <b>combo</b> (25 %) : les objets normaux obtenus entre-temps sont revendus. Taux de réussite selon tes niveaux "
            "(🛠️ Mes métiers). Prix : sites de suivi, prix d’achat réaliste ; vente après taxe et frais d’enregistrement "
            f"({cfg['fees']:.0%}).</p>"
            '<div class="toolbar"><input class="search" id="chq" placeholder="Filtrer (arc, épée, gants…)" oninput="chRender()" style="max-width:260px">'
            '<label class="tg" title="Coché : une ressource que tu récoltes coûte ce qu’elle rapporterait vendue brute (ou l’Od '
            'à transmuter, si c’est moins). Décoché : tout s’achète à l’HDV."><input type="checkbox" id="chown" checked '
            'onchange="chOpt(\'own\',this.checked)"> J’utilise ma récolte</label>'
            '<label class="tg">Mon budget <input class="search" id="chbud" type="number" min="0" step="1000000" placeholder="ex. 20000000" '
            'style="width:140px;display:inline-block" onchange="chOpt(\'bud\',+this.value||0)"> kinah</label></div>'
            '<div id="chbox"></div>')
