"""Onglets 🎯 Opportunites et 📅 Planning."""
import json

from .base import _num_td, _th, esc, is_good


def precision_html(prec):
    """Bilan des alertes passees (alerts.precision) : est-ce que les opportunites annoncees ont vraiment rapporte ?"""
    if not prec["kinds"]:
        return (f"<h3>Précision des alertes</h3><p class='mut'>Pas encore d’alerte jugée : chaque opportunité alertée est "
                f"vérifiée 48 h après (6 h pour un pic). {prec['attente']} en attente.</p>")
    rows = "".join(
        f"<tr><td>{esc(k['label'])}</td>{_num_td(k['n'], color=False)}"
        f"<td class='n'><b class='{'pos' if k['taux'] >= 0.7 else 'neg' if k['taux'] < 0.5 else ''}'>{k['taux']:.0%}</b></td>"
        f"{_num_td(round(k['reel'] / k['n']))}"
        f"<td class='n'>{format(k['vs_prevu'], '.0%') if k['vs_prevu'] is not None else '–'}</td></tr>"
        for k in prec["kinds"])
    return (f"<h3>Précision des alertes ({prec['jours']} derniers jours)</h3><p class='lead'>Chaque opportunité alertée est "
            "notée puis jugée une fois sa fenêtre de vente passée (48 h, 6 h pour un pic) : prix réel = médiane du prix le "
            "plus bas en vente sur cette fenêtre. <b>Tenue</b> = elle aurait rapporté après la taxe. "
            f"{prec['attente']} alerte(s) en attente de jugement.</p>"
            f'<div class="wrap"><table><thead><tr>{_th("Type")}{_th("Alertes", "Opportunités jugées", True)}'
            f'{_th("Tenues", "Net réel > 0 après la taxe de 10 %", True)}{_th("Net réel /u", "Moyenne par alerte", True)}'
            f'{_th("Réel / prévu", "Net réel total rapporté au net annoncé", True)}</tr></thead><tbody>{rows}</tbody></table></div>')


def opportunities_tab(cfg, my, prec=None):
    """🎯 Opportunites : recolte (ressources blanches), achat -> craft et flip dans une seule liste. Chaque objet occupe
    une annonce (relistee a chaque vente) : le navigateur garde les meilleures selon les annonces libres (limite du jeu
    moins mes annonces en cours), les kinah disponibles et le temps de recolte (calcul dans site.js, oppRender)."""
    m = my["market"]
    share = m.share
    rows = []

    def row(e, t, **kw):
        """ql : ma part des annonces vendues par jour ; lot : taille estimee (modifiable dans la page) ; dh : annonces
        vendues par heure sur le marche, nl : annonces en vente (delai de vente) ; s, f : surete."""
        sl, s = m.sales(e["item_id"]) or {}, e.get("surete") or {}
        dh = (sl.get("listings") or 0) / 24
        rows.append(dict(t=t, o=e["objet"], i=e["item_id"], n=e["net_u"], ql=round((sl.get("listings") or 0) * share, 2),
                         lot=e.get("lot_vente") or 1, dh=round(dh, 3), nl=m.listings.get(e["item_id"], 0),
                         s=s.get("score"), f=s.get("feu"), **kw))
    for e in my["harvest"] + (my.get("raw") or []):
        if e.get("rang") or not is_good(e) or not e["ma_part_j"]:
            continue                                   # procs non planifies ; usages douteux, a perte ou sans ventes
        row(e, "r", k=0, b=1 if e.get("brut") else 0, res={k: round(v, 3) for k, v in e["ressources"].items()},
            p=e["prix_real"])
    for e in my["buy"]:
        if is_good(e) and e["ma_part_j"]:
            row(e, "c", k=e["achats_u"], p=e["prix_real"], ing=e["ingredients"][:4])
    for f in my["flips"]:
        if f["ma_part_j"]:
            row(f, "f", k=f["achat_cible"], p=f["revente_cible"], now=1 if f["acheter"] else 0)
    data = json.dumps(dict(rows=rows, slots=cfg.get("max_listings", 10)), ensure_ascii=False, separators=(",", ":"))
    inp = ('style="width:{w}px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;background:var(--bg2);'
           'color:var(--txt);font:inherit"')
    return ("<h2>Opportunités du jour</h2><p class='lead'>Récolte, achat → craft et flip dans une seule liste. Une "
            "opportunité occupe <b>une annonce</b>, relistée à chaque vente : la page garde les meilleures selon tes "
            "annonces libres (limite du jeu moins tes annonces en cours du journal 💰), tes kinah disponibles et ton temps "
            "de récolte. Ventes/j = ta part des annonces vendues × <b>taille d’annonce</b> (estimée par type d’objet : "
            "corrige-la dans la colonne Lot si tu vois autre chose en jeu, c’est gardé dans ce navigateur). Délai de vente : "
            "<b>devant</b> = tu postes au prix le plus bas, ton annonce part avec la prochaine vente ; <b>à la file</b> = "
            "toutes les annonces déjà en vente partent avant la tienne. La réussite des crafts suit tes niveaux "
            "(🛠️ Mes métiers).</p>"
            '<div class="toolbar">'
            f'<label class="tg">Kinah disponibles : <input type="number" id="obudget" min="0" step="100000" placeholder="illimité" '
            f'{inp.format(w=130)} oninput="oppRender(true)"></label>'
            f'<label class="tg">Temps de récolte : <input type="number" id="ohours" min="0" step="0.5" value="3" '
            f'{inp.format(w=64)} oninput="oppRender(true)"> h</label>'
            '<label class="tg">Annonces libres : <b id="oslots">–</b></label></div>'
            '<div id="obox"></div>'
            f"<script>window.OPPDATA={data};</script>" + (precision_html(prec) if prec else ""))


def planning_tab(cfg, my):
    """Onglet Planning : plan « safe » (recolte -> crafts qui se vendent) et plan « gamble » (chaines d'amelioration
    avec combo). Calcul dans le navigateur : niveaux de metier, recolte par heure et stock du joueur."""
    targets = []
    for t in my["targets"]:
        if t.get("rang"):
            continue                                   # procs (vert, bleu, eclatant) : pas planifies
        uses = [dict(o=u["objet"], i=u["item_id"], n=u["net_par_ressource"], cap=u["ressources_j"], per=round(u["per_u"], 4),
                     v=1 if u.get("via") else 0, b=1 if u.get("brut") else 0,
                     lot=u.get("lot")) for u in t["usages"] if u["fiable"] and u["ressources_j"]]
        if uses:
            avg = sum(u["n"] * u["cap"] for u in uses) / sum(u["cap"] for u in uses)
            targets.append(dict(r=t["ressource"], u=uses, avg=round(avg)))
    hours = my.get("hours")
    best = f"{hours['best']}h – {(hours['best'] + 3) % 24}h" if hours else "21h – 0h"
    data = json.dumps(dict(targets=targets, best=best), ensure_ascii=False,
                      separators=(",", ":"))
    return ("<h2>Planning de la journée</h2><p class='lead'>Quoi récolter et qu’en faire (le transformer, ou le vendre "
            "brut quand le brut rapporte plus), sur les ressources blanches des points de récolte : les procs (vert, bleu, "
            "éclatant) sont trop rares pour être planifiés, ils sont dans 🌲 Récolte. "
            "Les calculs utilisent tes niveaux de métier (🛠️ Mes métiers), ta récolte par heure (🌲 Récolte, "
            "100 par défaut) et ton stock (🧮 Mon stock).</p>"
            "<h3>🛡️ Planning safe : récolter ce qui rapporte et se vend</h3>"
            '<div class="toolbar"><label class="tg">Temps de jeu aujourd’hui : <input type="number" id="phours" min="0.5" '
            'step="0.5" value="3" style="width:70px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;'
            'background:var(--bg2);color:var(--txt);font:inherit" oninput="planSafe(true)"> h</label></div>'
            '<div id="psafe"></div>'
            f"<script>window.PLANDATA={data};</script>")
