"""Onglet 💰 Mes ventes : journal et ventes face aux estimations."""
import json

from ..analysis import CALIB_MIN_ITEMS
from ..collect import paris
from .base import _num_td, _th, esc, fmt, kfmt


def journal_html(ctx, cfg, my):
    """Journal des ventes : annonces en cours avec leurs actions (vendu, relister, retirer), ajout, captures, bilan.
    Tout est calcule et affiche dans le navigateur (site.js, j*) a partir de journal.json."""
    m = my["market"]
    j = cfg.get("journal") or {"lots": []}
    # par objet du journal : prix le plus bas, annonces en vente, prix habituel, annonces vendues par heure, taille d'annonce
    floor = {}
    for lot in j.get("lots") or []:
        iid = m.by_base.get(lot["objet"])
        if iid in m.price:
            sp, sl = m.sell_price(iid), m.sales(iid)
            floor[lot["objet"]] = [m.price[iid], m.listings.get(iid, 0), sp and sp["ref"] and round(sp["ref"]),
                                   sl and round(sl["listings"] / 24, 3), m.lot_size(iid)]
    names = "".join(f'<option value="{esc(n["n"])}">' for n in sorted(ctx.market_icons(), key=lambda x: x["n"]))
    inp = lambda i, ph, w, t="number", extra="": (f'<input id="{i}" class="search" type="{t}" placeholder="{ph}" '
                                                 f'style="width:{w}px;display:inline-block" {extra}>')
    return (
        '<p class="lead">Note ici ce que deviennent tes annonces : un clic quand tu postes, vends, relistes ou retires. '
        f'Le site calcule ce que tu gagnes vraiment. La taxe de {cfg["fees"]:.0%} est payée à chaque mise en vente : elle est '
        'déduite de la vente si l’annonce part, et <b>perdue si tu la relistes ou la retires</b> (relister = retirer puis '
        'remettre en vente, donc repayer).</p>'
        '<span id="jsync" class="sub"></span>'
        '<h3>Mes annonces en cours</h3><div class="wrap"><table><thead><tr>'
        f'{_th("Objet")}{_th("Reste", None, True)}{_th("Prix /u", None, True)}{_th("Coût /u", "Coût de revient (clique « Coût » pour le changer)", True)}'
        f'{_th("Gain /u", "Prix − taxe − coût", True)}'
        f'{_th("Conseil", "Garder, relister moins cher (la taxe de l’annonce retirée est perdue) ou retirer pour libérer l’annonce")}'
        f'{_th("Posté le")}{_th("Relistes", None, True)}'
        f'{_th("Taxe perdue", "Taxe des annonces retirées pour relister", True)}{_th("Actions")}'
        '</tr></thead><tbody id="jopen"></tbody></table></div>'
        '<div class="card" style="margin-top:10px"><b>📦 J’ai posté</b><div class="toolbar" style="margin:0;flex-wrap:wrap;gap:6px">'
        + '<select id="js" class="search" style="width:auto;display:inline-block" onchange="jCostFill()">'
        '<option value="recolte">🌲 Récolte → craft</option><option value="brut">💰 Récolte vendue brute</option>'
        '<option value="achat">🛒 Achat → craft</option><option value="ravit">📦 Ravitaillement</option>'
        '<option value="flip">🔁 Flip</option></select>'
        + inp("jo", "Objet (nom exact)", 260, "text", 'list="jnames" onchange="jCostFill(1)"') + f'<datalist id="jnames">{names}</datalist>'
        + inp("jq", "Quantité", 90) + inp("jp", "Prix /u", 110) + inp("jc", "Coût /u (facultatif)", 150)
        + inp("jn", "Nb d’annonces", 120, extra='value="1" min="1"')
        + '<button class="mapbtn" onclick="jPost()">Ajouter</button></div>'
        '<span class="sub">Origine : proposée selon l’objet (craft de ta récolte ou non), à changer si besoin. Coût /u proposé : '
        '0 pour ta récolte (craftée ou vendue brute), l’estimation du site (ingrédients achetés) pour l’achat → craft, le total du craft de l’onglet Ravitaillement pour le ravitaillement, ton prix d’achat à saisir pour '
        'un flip. Nb d’annonces : pour poster plusieurs lots identiques d’un coup (ex. 5 annonces de 30).</span></div>'
        '<div class="card" style="margin-top:10px" ondragover="event.preventDefault()" '
        'ondrop="event.preventDefault();jScan(event.dataTransfer.files[0])"><b>📷 Ou colle une capture (Ctrl + V sur cet onglet)</b>'
        '<span class="mut">Fenêtre de <b>tes annonces en vente</b> : les nouvelles annonces sont ajoutées (celles déjà notées sont '
        'reconnues). <b>Historique des ventes</b> : chaque vente est rattachée à ton annonce (même objet, même prix), avec sa vraie '
        'date et le montant reçu ; les ventes déjà notées ne sont pas doublées. Ou <label style="color:var(--acc);cursor:pointer;'
        'text-decoration:underline">choisis un fichier<input type="file" accept="image/*" hidden onchange="jScan(this.files[0])">'
        '</label>.</span><span id="jmsg" class="mut"></span></div>'
        '<h3>Bilan</h3><div class="toolbar" style="margin:0 0 8px"><select id="jper" class="search" style="width:auto" '
        'onchange="jRender()"><option value="1">Dernières 24 h</option><option value="7" selected>7 derniers jours</option>'
        '<option value="30">30 derniers jours</option><option value="0">Depuis le début</option></select>'
        '<select id="jsrc" class="search" style="width:auto" onchange="jRender()"><option value="">Toutes les activités</option>'
        '<option value="recolte">🌲 Récolte → craft</option><option value="brut">💰 Récolte vendue brute</option>'
        '<option value="achat">🛒 Achat → craft</option><option value="ravit">📦 Ravitaillement</option>'
        '<option value="flip">🔁 Flip</option></select></div>'
        '<div class="wrap" style="margin-bottom:10px"><table><thead><tr>'
        f'{_th("Activité")}{_th("Ventes", None, True)}{_th("Unités", None, True)}{_th("Reçu", "Après taxe", True)}'
        f'{_th("Coût", None, True)}{_th("Taxe perdue", "Relistes et retraits", True)}{_th("Bénéfice", None, True)}'
        f'{_th("Marge", "Bénéfice / reçu", True)}</tr></thead><tbody id="jact"></tbody></table></div>'
        '<div class="kpis" id="jkpi"></div><div class="wrap"><table><thead><tr>'
        f'{_th("Objet")}{_th("Unités vendues", None, True)}{_th("Prix moyen /u", None, True)}{_th("Reçu", "Après taxe", True)}'
        f'{_th("Coût", None, True)}{_th("Taxe perdue", "Relistes et retraits", True)}{_th("Relistes / retraits", None, True)}'
        f'{_th("Bénéfice", "Reçu − coût − taxe perdue (* : une partie sans coût connu)", True)}'
        '</tr></thead><tbody id="jitems"></tbody></table></div>'
        '<h3>Derniers mouvements</h3><div class="wrap"><table><thead><tr>'
        f'{_th("Date")}{_th("Action")}{_th("Objet")}{_th("Qté", None, True)}{_th("Prix /u", None, True)}{_th("Kinah", None, True)}{_th("")}'
        '</tr></thead><tbody id="jlog"></tbody></table></div>'
        '<details class="card" style="margin-top:14px"><summary><b>🔗 Enregistrement sur GitHub (à faire une fois par appareil)</b></summary>'
        '<span class="mut">Pour que le journal soit gardé dans ton dépôt (et serve aux alertes Discord), le site a besoin d’un jeton '
        'GitHub qui ne peut écrire <b>que</b> dans ce dépôt. Il reste dans ce navigateur, il n’est jamais publié.<br>'
        '1. <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener" style="color:var(--acc)">'
        'Créer un jeton « fine-grained »</a> : nom « journal HDV », expiration au choix ; <b>Repository access</b> → '
        f'<i>Only select repositories</i> → <b>{esc((cfg.get("_github_repo") or "ton dépôt").split("/")[-1])}</b> ; '
        '<b>Permissions</b> → Repository permissions → <b>Contents : Read and write</b>. « Generate token ».<br>'
        '2. Colle-le ici :</span><div class="toolbar" style="margin:0">'
        + inp("jtoken", "github_pat_…", 320, "password")
        + '<button class="mapbtn" onclick="jSetToken()">Enregistrer</button>'
        '<button class="mapbtn" onclick="jForget()">Oublier le jeton</button></div>'
        '<span class="sub">Sans jeton, le journal est gardé dans ce navigateur seulement.</span></details>'
        f'<script>window.JOURNAL={json.dumps(j, ensure_ascii=False)};'
        f'window.JCFG={json.dumps(dict(tax=cfg["fees"], repo=cfg.get("_github_repo")))};'
        f'window.JFLOOR={json.dumps(floor, ensure_ascii=False)};'
        f'window.HARVEST_ITEMS={json.dumps(sorted({e["objet"] for e in my["harvest"]}), ensure_ascii=False)};'
        f'window.RAW_ITEMS={json.dumps(m.gather_names(), ensure_ascii=False)};</script>')


def gains_tab(ctx, cfg, my):
    """💰 Mes ventes : journal des annonces (journal.json) et mes ventes face aux estimations de l'outil."""
    g = my.get("gains")
    head = ("<h2>Mes ventes</h2>" + journal_html(ctx, cfg, my)
            + "<h3>Mes ventes face aux estimations de l’outil</h3><p class='lead'>Tes ventes du journal comparées à ce que "
            "l’outil prévoit, pour vérifier ses estimations : combien tu vends par jour, à quel prix, et ta vraie part du "
            "marché. Une vente = un achat (un acheteur peut ne prendre qu’une partie d’une annonce). Mis à jour à chaque "
            "passage horaire.</p>")
    if g:
        pct = lambda v: f"{v:.0%}" if v is not None else "–"
        kpis = (f'<div class="kpis">'
                f'<div class="kpi"><div class="l">Kinah reçus</div><div class="v pos">{kfmt(g["recu"])}</div>'
                f'<div class="s">{g["ventes"]} ventes du {esc(paris(g["debut"].isoformat(), "%d/%m %H:%M"))} au '
                f'{esc(paris(g["fin"].isoformat(), "%d/%m %H:%M"))}</div></div>'
                f'<div class="kpi"><div class="l">Par jour</div><div class="v pos">{kfmt(g["recu_j"])}</div>'
                f'<div class="s">après la taxe de 10 %, sur {g["jours"]:.1f} j</div></div>'
                f'<div class="kpi"><div class="l">Ma part réelle du marché</div><div class="v">{pct(g["part"])}</div>'
                f'<div class="s">l’outil suppose {pct(g["part_supposee"])}</div></div>'
                f'<div class="kpi"><div class="l">Ventes réelles / prévues</div>'
                f'<div class="v">{"×" + format(g["ratio"], ".2f").replace(".", ",") if g["ratio"] else "–"}</div>'
                f'<div class="s">unités par jour, objets vendus 3 fois ou plus</div></div></div>')
        notes = []
        if g["n_cal"]:
            n = g["n_cal"]
            if g["ratio"]:
                notes.append(f"Tu vends <b>{g['ratio']:.2f}".replace(".", ",") + "×</b> ce que l’outil prévoit (ta part de "
                             f"{pct(g['part_supposee'])} des ventes mesurées), ce qui fait une part réelle de <b>{pct(g['part'])}</b>.")
            if g["prix_ratio"]:
                notes.append(f"Prix obtenu = <b>{g['prix_ratio']:.2f}".replace(".", ",") + "×</b> le prix des ventes "
                             "observées sur le marché pendant la même période.")
            sh = my["market"]._share
            notes.append(f"Calcul sur {n} objet{'s' if n > 1 else ''} vendu{'s' if n > 1 else ''} au moins 3 fois : "
                         + (f"<b>l’outil utilise maintenant ta part réelle ({pct(sh['value'])})</b> pour tous les profits par "
                            f"jour, au lieu des {pct(sh['supposee'])} supposés (bornée entre 2 et 50 %)." if sh["source"] == "journal"
                            else f"il en faut {CALIB_MIN_ITEMS} pour que l’outil remplace la part supposée "
                                 f"({pct(sh['supposee'])}) par ta part réelle."))
        else:
            notes.append("Pas encore d’objet vendu au moins 3 fois : ajoute des captures pour comparer aux estimations. "
                         f"À partir de {CALIB_MIN_ITEMS} objets, l’outil remplace la part supposée par ta part réelle.")
        loss = [x for x in g["items"] if x["marge_u"] is not None and x["marge_u"] < 0]
        for x in loss:
            notes.append(f"<b class='neg'>⚠ {esc(x['objet'])} : vendu à perte</b> (reçu {fmt(round(x['recu_u']))} /u après "
                         f"taxe, coût {fmt(x['cout'])} /u dans le journal, soit {fmt(round(x['marge_u']))} /u).")
        rows = "".join(
            f"<tr><td>{ctx.label(x['item_id'], x['objet'])}</td>"
            f"{_num_td(x['lots'], color=False)}{_num_td(x['unites'], color=False)}{_num_td(x['recu'], color=False, k=True)}"
            f"{_num_td(round(x['prix_u']), color=False)}{_num_td(round(x['prix_marche']) if x['prix_marche'] else None, color=False)}"
            f"{_num_td(round(x['marge_u']) if x['marge_u'] is not None else None)}"
            f"{_num_td(round(x['unites_j'], 1) if x['unites_j'] else None, color=False)}"
            f"{_num_td(round(x['estime_unites_j'], 1) if x['estime_unites_j'] else None, color=False)}"
            f"<td class='n'>{pct(x['part']) if x['part'] else '–'}</td>"
            f"{_num_td(round(x['achat_moyen'], 1), color=False)}"
            f"{_num_td(my['market'].lot_size(x['item_id']) if x['item_id'] else None, color=False)}</tr>"
            for x in g["items"])
        table = (f'<div class="wrap"><table><thead><tr>{_th("Objet")}{_th("Ventes", "Achats (lignes de l’historique)", True)}'
                 f'{_th("Unités", None, True)}{_th("Reçu", "Après la taxe de 10 %", True)}'
                 f'{_th("Prix obtenu /u", "Prix de vente moyen par unité", True)}'
                 f'{_th("Prix du marché /u", "Médiane des ventes observées sur le marché pendant la même période", True)}'
                 f'{_th("Marge /u", "Reçu par unité − coût de revient noté dans le journal", True)}'
                 f'{_th("Unités /j réel", "À partir de 3 ventes : (n − 1) achats entre le premier et le dernier", True)}'
                 f'{_th("Unités /j prévu", "Annonces vendues par jour sur le serveur × taille estimée des annonces × ta part supposée", True)}'
                 f'{_th("Part réelle", "Mes unités vendues / unités vendues sur le marché", True)}'
                 f'{_th("Achat moyen", "Unités par achat", True)}'
                 f'{_th("Annonce estimée", "Taille estimée d’une annonce vendue sur le marché (Kaisinel ou règle par type), à comparer à l’achat moyen", True)}'
                 f'</tr></thead><tbody>{rows}</tbody></table></div>')
        body = kpis + "<div class='card' style='margin:12px 0'>" + "".join(f"<div>{n}</div>" for n in notes) + "</div>" + table
    else:
        body = "<p class='mut'>Pas encore de vente dans le journal.</p>"
    return head + body
