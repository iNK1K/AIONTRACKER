"""Tableaux partages entre onglets : crafts, cibles de recolte, pics, flips, Unique, plan, stock."""
import json

from ..collect import paris
from .base import BRUT_BADGE, METIERS, _cls, _num_td, _th, craft_attrs, esc, fmt, is_good, kfmt, lots_txt, niveau, status, surete_html, toolbar, use_name


def cmp_class(compare, e):
    c = (compare or {}).get(e["item_id"])
    return "" if not c else ("better" if c[0] else "worse")


def cmp_badge(compare, e):
    c = (compare or {}).get(e["item_id"])
    if not c:
        return ""
    better, diff, other = c
    return (f'<span class="badge b-ok">✔ mieux que {esc(other)} (+{fmt(diff)}/u)</span>' if better
            else f'<span class="badge b-bad">✖ moins bien que {esc(other)} (−{fmt(diff)}/u)</span>')


def compare_ways(a, b, label_b):
    """Pour chaque craft present dans les deux listes : meilleur ou moins bien que l'autre facon (net par unite)."""
    other = {e["item_id"]: e for e in b}
    out = {}
    for e in a:
        o = other.get(e["item_id"])
        if o and o["net_u"] != e["net_u"]:
            out[e["item_id"]] = (e["net_u"] > o["net_u"], abs(e["net_u"] - o["net_u"]), label_b)
    return out


def table_crafts(ctx, rows, tid, harvest, compare=None):
    """compare : {item_id: (meilleur?, ecart net/u, nom de l'autre facon)} pour colorer vert/rouge face a l'autre categorie."""
    head = ("<tr>" + _th("#") + _th("Craft") +
            (_th("Ressources / unité") if harvest else _th("Ingrédients achetés")) +
            ("" if harvest else _th("Coût/u", "Coût des ingrédients au prix réaliste", True)) +
            _th("Réussite", "Chance de réussite selon tes niveaux (onglet Mes métiers) ; 🔒 = niveau insuffisant", True) +
            _th("Vendre à", "Prix de vente conseillé (réaliste)", True) +
            _th("Net/u", "Bénéfice par unité après la taxe de l’HDV (10 %) et les frais d’enregistrement (2 %) (et échecs, selon tes niveaux)", True) +
            (_th("Net/ressource", "Bénéfice par ressource récoltée utilisée", True) +
             _th("vs brut/u", "Net/u − ce que les mêmes ressources rapporteraient vendues brutes (prix réaliste, après "
                 "taxe et frais ; échecs compris selon tes niveaux) : négatif = vends plutôt le brut", True) if harvest
             else _th("Marge", "Bénéfice / coût", True)) +
            _th("Ventes/j", "Ta part du marché des ventes sur ton serveur, en unités : annonces disparues sur 24 h × taille "
                "estimée des annonces (type d’objet, config lots)", True) +
            _th("Profit/j", "Ventes/j × Net/u", True) +
            _th("Annonces vendues/j", "Annonces disparues sur 24 h sur ton serveur (achats ; une annonce retirée compte aussi)",
                True, True) +
            _th("Prix affiché", "Prix le plus bas actuellement en vente", True, True) +
            _th("Prix habituel", "Prix des ventes observées sur ton serveur (médiane 48 h) ; à défaut, prix plancher médian sur 7 j", True, True) +
            _th("Net pess./u", "Bénéfice si on vend au prix le plus bas", True, True) +
            _th("Profit pess./j", None, True, True) +
            ("" if harvest else _th("Capital/j", "Kinah à avancer par jour", True, True)) +
            _th("Statut") + "</tr>")
    good = [e for e in rows if is_good(e)]
    bad = [e for e in rows if not is_good(e)]
    ncol = 17 if not harvest else 16
    body = []
    for i, e in enumerate(good + bad, 1):
        if i == len(good) + 1 and bad:
            body.append(f'<tr class="grp"><td colspan="{ncol}">À vérifier, à perte{" ou moins bien que le brut" if harvest else ""} '
                        f'({len(bad)})</td></tr>')
        if harvest:
            res = '<div class="chips">' + "".join(
                f'<span class="chip">{ctx.icon(name=k)}{esc(k)} ×{v:g}'
                + (f' <span class="mut">· {fmt((e.get("prix_ressources") or {}).get(k))}</span>' if (e.get("prix_ressources") or {}).get(k) else "")
                + f'{ctx.mapbtn(k)}</span>' for k, v in e["ressources"].items()) + "</div>"
            if e["ingredients"] and any("récolte" not in x for x in e["ingredients"]):
                res += '<div class="sub">+ ' + esc("; ".join(x for x in e["ingredients"] if "récolte" not in x)) + "</div>"
        else:
            res = '<div class="ing">' + "".join(f"<div>{esc(x)}</div>" for x in e["ingredients"]) + "</div>"
        cols = (_num_td(e["net_par_ressource"]) + _num_td(e.get("vs_brut_u"), "cvb") if harvest else
                f'<td class="n {_cls(e["marge"])}" data-v="{e["marge"] or 0}">{(e["marge"] or 0):+.0%}</td>')
        body.append(
            f"<tr class='{'' if is_good(e) else 'dim'} {cmp_class(compare, e)}' {craft_attrs(e)}><td class='n rank'>{i}</td>"
            f"<td>{ctx.label(e['item_id'], sub='vente du brut' if e.get('brut') else f'{METIERS.get(e['metier'], e['metier'])} {niveau(e['maitrise'])} · lot ×{e['lot']:g}')}</td>"
            f"<td>{res}</td>"
            + ("" if harvest else _num_td(e["achats_u"], color=False))
            + '<td class="n csr">–</td>'
            + _num_td(e["prix_real"], color=False) + _num_td(e["net_u"], "cnet") + cols
            + _num_td(e["ma_part_j"], color=False)
            + _num_td(e["profit_j"], "big cprof", k=True)
            + _num_td(e.get("annonces_vendues_j"), color=False, x=True)
            + _num_td(e["prix_affiche"], color=False, x=True)
            + _num_td(e["prix_ref"], color=False, x=True) + _num_td(e["net_pess_u"], x=True)
            + _num_td(e["profit_pess_j"], k=True, x=True)
            + ("" if harvest else _num_td(e["capital_j"], color=False, k=True, x=True))
            + f"<td>{cmp_badge(compare, e)}{status(e)}{surete_html(e)}</td></tr>")
    return toolbar(tid) + f'<div class="wrap"><table id="{tid}"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>'


def table_targets(ctx, targets, tid="targets", rates=True, crafts="th"):
    """rates : colonnes Recolte / heure, Kinah / heure, Heures / jour (ressources recoltees sur les points)."""
    body = []
    for t in targets:
        # gain moyen par ressource quand la recolte du jour est repartie sur les crafts fiables, selon ce que chacun absorbe
        ok = [u for u in t["usages"] if u["fiable"] and u["ressources_j"]]
        avg = round(sum(u["net_par_ressource"] * u["ressources_j"] for u in ok) / sum(u["ressources_j"] for u in ok)) if ok else 0
        uses = '<div class="uses">' + "".join(
            f"<div>{esc(use_name(u))} : <b class='{_cls(u['net_par_ressource'])}'>{fmt(u['net_par_ressource'])}</b> / ressource"
            + (f" <span class='mut'>· ~{fmt(u['ressources_j'])} ressources/j</span>" if u["fiable"] else "")
            + ("" if u["fiable"] else f" <span class='badge b-warn'>⚠ {esc('; '.join(u['flags']) or 'à perte')}</span>")
            + "</div>" for u in t["usages"]) + "</div>"
        body.append(f"<tr class='{'' if t['meilleur'] else 'dim'}' data-res=\"{esc(t['ressource'])}\" "
                    f"data-best='{avg}' data-abs='{t['absorbable_j'] or 0}'><td>{ctx.label(name=t['ressource'])}"
                    f"<button class='mapbtn' style='margin-top:4px' onclick=\"resCrafts(this.closest('tr').dataset.res,'{crafts}')\">crafts</button></td>"
                    + (f"<td class='n'><input type='number' min='0' step='10' class='rate' placeholder='100' "
                       f"style='width:74px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;background:var(--bg2);"
                       f"color:var(--txt);font:inherit;text-align:right' oninput='rateCalc(this)'></td>"
                       f"<td class='n big pos kh' data-v='0'>–</td><td class='n hj' data-v='0'>–</td>" if rates else "")
                    + f"{_num_td(t['meilleur'], 'big')}<td>{uses}</td>{_num_td(t['absorbable_j'], color=False)}"
                    f"{_num_td(t['prix_brut'], color=False, x=True)}</tr>")
    head = ("<tr>" + _th("Ressource")
            + (_th("Récolte / heure", "Ce que tu récoltes en une heure (100 par défaut) : modifiable, enregistré dans ce navigateur")
               + _th("Kinah / heure", "Récolte par heure × gain moyen par ressource, la récolte étant répartie sur les usages "
                     "fiables (crafts et vente du brut) selon ce que chacun absorbe (après frais)", True)
               + _th("Heures / jour", "Heures de récolte avant de saturer ce que le marché absorbe par jour", True) if rates else "")
            + _th("Meilleur net / ressource", "Ce que te rapporte chaque ressource récoltée dans son meilleur usage fiable "
                  "(craft ou vente du brut)", True)
            + _th("Qu’en faire") + _th("Utilisable/j", "Ressources que le marché absorbe par jour (crafts fiables et vente "
                                        "du brut)", True)
            + _th("Prix brut HDV", "Prix le plus bas du brut en vente", True, True)
            + "</tr>")
    return (toolbar(tid) + f'<div class="wrap"><table id="{tid}"><thead>{head}</thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def stock_calc(ctx, cfg, harvest, names, transmute=None):
    """Je saisis mes ressources, la page calcule quoi fabriquer et combien ca rapporte (calcul dans le navigateur).
    Les crafts fiables passent d'abord ; les douteux (drapeaux) seulement si on coche l'option."""
    crafts = [e for e in harvest if e["net_u"] > 0 and e["ressources_u"]]
    crafts.sort(key=lambda e: (bool(e["flags"]), -(e["net_u"] / e["ressources_u"])))
    data = [dict(o=e["objet"], i=e["item_id"], s=e.get("vente_net_u"), a=e["achats_u"],
                 n=e["net_u"], p=e["prix_real"], c=e["ma_part_j"], l=e.get("lot_vente"), b=1 if e.get("brut") else 0,
                 f="; ".join(e["flags"]), r={k: round(v, 4) for k, v in e["ressources"].items()}) for e in crafts]
    names = sorted(set(names) | {k for e in crafts for k in e["ressources"]})
    preset = cfg.get("harvest_per_day") or {}
    inputs = "".join(f'<label class="sk">{ctx.icon(name=n)}<span>{esc(n)}</span><input type="number" min="0" step="1" '
                     f'inputmode="numeric" data-r="{esc(n)}" value="{esc(preset.get(n, ""))}" oninput="calc()"></label>'
                     for n in names)
    head = (f'<tr>{_th("Craft ou vente du brut")}{_th("Quantité", None, True)}{_th("Vendre à", None, True)}{_th("Net/u", None, True)}'
            f'{_th("Kinah", None, True)}{_th("Mettre en vente", "Taille habituelle des lots vendus sur le marché")}'
            f'{_th("Ressources utilisées")}</tr>')
    return ('<p class="lead">Entre les ressources que tu possèdes : la page choisit, pour chaque ressource, le craft ou la '
            'vente du brut qui rapporte le plus et calcule le gain. Tes quantités restent enregistrées dans ce navigateur.</p>'
            '<div class="toolbar"><label class="tg"><input type="checkbox" id="cap" checked onchange="calc()"> '
            'Ne pas dépasser ce que le marché absorbe en un jour</label>'
            '<label class="tg"><input type="checkbox" id="risky" onchange="calc()"> '
            'Inclure les usages douteux (volume inconnu, prix suspect)</label>'
            '<button class="mapbtn" onclick="clearStock()">Tout effacer</button></div>'
            '<div class="card" id="sdrop" style="margin:0 0 12px" ondragover="event.preventDefault()" '
            'ondrop="event.preventDefault();scanFile(event.dataTransfer.files[0])"><b>📷 Lire une capture de ta réserve</b>'
            '<span class="mut">Fais une capture de ta réserve (Win + Maj + S), recadrée au plus près de la grille, puis colle-la '
            'ici avec <b>Ctrl + V</b>, glisse le fichier sur ce cadre, ou <label style="color:var(--acc);cursor:pointer;'
            'text-decoration:underline">choisis un fichier<input type="file" accept="image/*" hidden '
            'onchange="scanFile(this.files[0])"></label>. La capture reste dans ton navigateur.</span>'
            '<span id="smsg" class="mut"></span><div class="chips" id="sthumbs"></div></div>'
            f'<script>window.GATHER={json.dumps([dict(n=n, s=ctx.icon_src(n)) for n in names if ctx.icon_src(n)], ensure_ascii=False)};</script>'
            '<details class="card" id="pdet" style="margin:0 0 12px"><summary style="cursor:pointer"><b>📋 Coller une liste</b> '
            '<span class="mut">— une ligne par ressource : « Bois d\'Asvata 300 » ou « Saphir brut : 96 ». '
            'Rempli automatiquement par la lecture de capture ci-dessus, modifiable avant de cliquer sur Remplir.</span></summary>'
            '<textarea id="paste" placeholder="Bois d\'Asvata 300&#10;Saphir brut : 96&#10;Rubis brut d\'une grande pureté x169"></textarea>'
            '<div class="toolbar" style="margin:0"><select id="pmode" class="search" style="width:auto">'
            '<option value="replace">Remplacer tout le stock</option><option value="add">Ajouter au stock</option></select>'
            '<button class="mapbtn" onclick="importStock()">Remplir</button><span class="mut" id="pmsg"></span></div></details>'
            f'<div class="stock" id="stock">{inputs}</div>'
            '<div class="kpis"><div class="kpi"><div class="l">Total estimé</div><div class="v pos" id="stot">–</div>'
            '<div class="s">kinah une fois tout vendu</div></div></div>'
            f'<div class="wrap"><table id="splan"><thead>{head}</thead><tbody></tbody></table></div>'
            '<p class="mut" id="sleft"></p>'
            f'<script>window.CRAFTS={json.dumps(data, ensure_ascii=False).replace("</", "<\\/")};'
            f'window.TRANSMUTE={json.dumps(transmute, ensure_ascii=False)};</script>')


def position_advice(l):
    """Conseil pour une de mes annonces."""
    if not l["item_id"] or l["plancher"] is None:
        return ""
    tips = []
    if l["conseil"]:
        tips.append(f"Repasse devant à {fmt(l['conseil'])}")
    elif l["battu"] and l.get("seuil"):
        tips.append("Ne baisse pas : le plus bas est sous ton seuil")
    if l.get("chute"):
        tips.append("le prix chute : vends maintenant ou garde")
    if l.get("ecoulement_h"):
        tips.append(f"écoulement ~{l['ecoulement_h']:.0f} h")
    return esc(" · ".join(tips))


def table_spikes(ctx, spikes):
    """Pics de prix : rentable au prix affiche seulement."""
    if not spikes:
        return ""
    rows = "".join(
        f"<tr {craft_attrs(e)}><td>{ctx.label(e['item_id'])}</td>{_num_td(e['prix_affiche'], 'big', color=False)}"
        f"{_num_td(e['prix_ref'], color=False)}<td class='n' data-v='{e['ratio']}'><span class='badge b-warn'>×{e['ratio']}</span></td>"
        f"<td class='sub'>{esc(paris(e['depuis'], '%d/%m %H:%M') if e['depuis'] else '–')}</td>"
        f"{_num_td(e['achats_u'], color=False)}{_num_td(e['net_affiche_u'])}{_num_td(e['net_habituel_u'])}"
        f"{_num_td(e['annonces'], 'mut', color=False)}<td data-v='{(e.get('surete') or {}).get('score', 0)}'>{surete_html(e)}</td>"
        f"<td class='ing'>{'<br>'.join(esc(x) for x in e['ingredients'])}</td></tr>"
        for e in spikes)
    head = ("<tr>" + _th("Craft") + _th("Prix affiché", None, True) + _th("Prix habituel", "Médiane 3 j sur ton serveur", True)
            + _th("Pic", None, True) + _th("Depuis") + _th("Coût/u", None, True)
            + _th("Net/u si vendu au prix affiché", None, True) + _th("Net/u si le prix redescend", None, True)
            + _th("Annonces", None, True)
            + _th("Sûreté", "Peut-on revendre ? Pression de l'offre, temps d'écoulement, perte si le prix redescend (détail au survol)")
            + _th("Acheter") + "</tr>")
    return ("<h3>⚡ Pics de prix : rentable seulement tant que le prix reste haut</h3>"
            "<p class='lead'>Le prix affiché est bien au-dessus du prix habituel depuis peu. Fabriquer et vendre maintenant "
            "rapporte, mais si le prix redescend avant la vente, c’est à perte. Petite quantité, à vendre vite, et "
            "regarde la courbe 📈 avant de te lancer. 🔴 = d’autres vendeurs arrivent déjà : à éviter.</p>"
            f'<div class="wrap"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div><h3>Toujours rentables</h3>')


def table_flips(ctx, flips, cfg):
    a = cfg["alerts"]
    body = []
    for f in flips:
        st = ('<span class="badge b-ok">Acheter maintenant</span>' if f["acheter"]
              else '<span class="badge b-mut">Attendre</span>') + surete_html(f)
        body.append(f"<tr><td>{ctx.label(f['item_id'])}</td><td data-v='{0 if f['acheter'] else 1}'>{st}</td>"
                    f"{_num_td(f['prix'], color=False)}{_num_td(f['achat_cible'], 'big', color=False)}"
                    f"{_num_td(f['revente_cible'], color=False)}{_num_td(f['net_u'])}"
                    f"<td class='n' data-v='{f['marge']}'>{f['marge']:.0%}</td>{_num_td(f['ma_part_j'], color=False)}"
                    f"{_num_td(f['profit_j'], 'big', k=True)}<td>{lots_txt(f)}</td>"
                    f"{_num_td(f['capital_j'], 'x', color=False, k=True)}{_num_td(f['annonces'], 'mut x', color=False)}"
                    f"{_num_td(f['releves'], 'mut x', color=False)}</tr>")
        if f["releves"] < 48:
            body[-1] = body[-1].replace("</td><td data-v=", "<div><span class='badge b-mut' title='Moins de 48 prix relevés : "
                                        "fourchette encore peu fiable'>historique court</span></div></td><td data-v=", 1)
    head = ("<tr>" + _th("Item") + _th("Statut") + _th("Prix actuel", "Prix le plus bas en vente", True)
            + _th("Acheter à ≤", "Prix d'achat cible : bas de la fourchette habituelle (1er quartile sur 3 j)", True)
            + _th("Revendre à", "Prix plancher médian des 3 derniers jours", True)
            + _th("Net/u", "Après la taxe de l’HDV (10 %) et les frais d’enregistrement (2 %)", True) + _th("Marge", None, True)
            + _th("Ventes/j", "Ta part du marché (voir les hypothèses en haut de l’onglet)", True) + _th("Profit/j", None, True)
            + _th("Mettre en vente", "Taille habituelle des lots vendus")
            + _th("Capital/j", "Kinah à immobiliser par jour", True, True) + _th("Annonces", None, True, True)
            + _th("Relevés", "Prix relevés sur 3 j", True, True) + "</tr>")
    lead = ("<p class='lead'>Acheter un item quand il passe en bas de sa fourchette de prix habituelle, le revendre "
            "au prix médian, sans rien fabriquer. Calcul sur les 3 derniers jours ; les items dont le prix monte ou "
            "baisse durablement, les items sans volume de vente connu et les prix aberrants (prix actuel hors de "
            f"{1 - a.get('flip_max_ecart', 0.5):.0%} à {1 / (1 - a.get('flip_max_ecart', 0.5)):.0%} de la médiane : erreur de "
            "saisie d’un vendeur ou relevé faux ; ou fourchette trop large) sont écartés. Le brut est compris, sur ses prix "
            f"depuis le {esc(cfg.get('brut_vendable_depuis') or '?')} (avant, il n’était pas vendable). "
            "🛡️ Sûreté : 🟢 marché fluide, 🟠 prudence, 🔴 stock qui s’accumule (détail au survol). "
            f"Alerte Discord quand un item passe sous son prix d’achat cible (marge ≥ {a['flip_min_margin']:.0%}, "
            f"profit ≥ {fmt(a['flip_min_profit_day'])}/j).</p>")
    if not flips:
        return lead + ('<div class="card"><span class="mut">Rien pour l’instant : il faut au moins '
                       f'{a["flip_min_samples"]} prix relevés par item, l’historique se remplit à chaque passage.</span></div>')
    return lead + toolbar("flips") + (f'<div class="wrap"><table id="flips"><thead>{head}</thead>'
                                      f'<tbody>{"".join(body)}</tbody></table></div>')


def table_uniques(ctx, uniques, cfg):
    a = cfg["alerts"]
    body = []
    for u in uniques:
        deal = u["ratio"] <= a["unique_ratio"] and u["releves"] >= a["unique_min_samples"]
        badge = (f'<span class="badge {"b-ok" if deal else "b-mut"}">{u["ratio"]:.0%}</span>')
        body.append(f"<tr><td>{ctx.label(u['item_id'])}</td><td class='sub'>{esc(u['categorie'])}</td>"
                    f"{_num_td(u['prix'], 'big', color=False)}{_num_td(u['mediane'], color=False)}"
                    f"<td class='n' data-v='{u['ratio']}'>{badge}</td>{_num_td(u['plus_bas'], color=False)}"
                    f"{_num_td(u['annonces'], 'mut', color=False)}{_num_td(u['releves'], 'mut', color=False)}</tr>")
    head = ("<tr>" + _th("Équipement Unique") + _th("Type", "L'harmonisation consomme une pièce de même rang et de même type") + _th("Prix actuel", None, True)
            + _th("Médiane 7 j", "Prix plancher médian des 7 derniers jours", True)
            + _th("Prix / médiane", "Plus c'est bas, plus c'est une affaire", True)
            + _th("Plus bas vu", "Prix plancher le plus bas des 7 derniers jours", True)
            + _th("Annonces", None, True) + _th("Relevés", "Nombre de prix relevés sur 7 j (fiabilité de la médiane)", True)
            + "</tr>")
    lead = (f"<p class='lead'>Équipements Unique en vente (armes, armures, accessoires), utilisables pour l’harmonisation "
            f"(une pièce de même rang et de même type). Les moins chers par rapport à leur prix habituel d’abord ; "
            f"tape un type (ex. « Épée ») dans la recherche pour ne voir que celui-là. "
            f"Alerte Discord quand un Unique passe sous <b>{a['unique_ratio']:.0%}</b> de sa médiane 7 j "
            f"(médiane d’au moins {fmt(a['unique_min_median'])} kinah, au moins {a['unique_min_samples']} relevés).</p>")
    return (lead + toolbar("uniques", f'<span class="mut">{len(uniques)} équipements Unique en vente</span>')
            + f'<div class="wrap"><table id="uniques"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>')


def table_plan(plan):
    if not plan:
        return ('<div class="card"><b>Pas encore de plan.</b><span class="mut">Renseigne <code>harvest_per_day</code> dans '
                '<code>config.json</code>, par exemple <code>{"Bois d\'Asvata": 300, "Azpha": 150}</code>, '
                'pour obtenir ton plan de production du jour.</span></div>')
    body = "".join(f"<tr><td>{esc(p['objet'])}{BRUT_BADGE if p.get('brut') else ''}</td>{_num_td(p['quantite_j'], color=False)}{_num_td(p['prix_conseille'], color=False)}"
                   f"{_num_td(p['net_u'])}{_num_td(p['kinah_j'], 'big', k=True)}<td>{lots_txt(p)}</td><td class='sub'>"
                   f"{esc(', '.join(f'{k} ×{v}' for k, v in p['ressources'].items()))}</td></tr>" for p in plan)
    total = sum(p["kinah_j"] for p in plan)
    return (f'<div class="kpis"><div class="kpi"><div class="l">Total estimé</div><div class="v pos">{kfmt(total)}</div>'
            f'<div class="s">kinah par jour</div></div></div><div class="wrap"><table><thead><tr>{_th("Craft")}'
            f'{_th("Quantité/j", None, True)}{_th("Vendre à", None, True)}{_th("Net/u", None, True)}'
            f'{_th("Kinah/j", None, True)}{_th("Mettre en vente", "Taille habituelle des lots vendus sur le marché")}'
            f'{_th("Ressources utilisées")}</tr></thead><tbody>{body}</tbody></table></div>')
