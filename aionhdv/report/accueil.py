"""Onglet 🏠 Aujourd'hui."""
from datetime import datetime, timedelta, timezone

from ..collect import paris
from .base import METIERS, _md, _num_td, _th, esc, fmt
from .tables import position_advice


def todo_html(con, my):
    """« A faire maintenant » : les actions du jour, par ordre d'importance. Plan de recolte et mise en vente sont
    completes dans le navigateur (Planning safe : temps de jeu, recolte/heure, niveaux)."""
    items = []
    for l in my.get("listings") or []:                       # 1. mes annonces
        if not l["item_id"] or l["plancher"] is None:
            continue
        if l.get("chute"):
            items.append(("bad", f"📉 <b>{esc(l['nom'])}</b> : le prix chute ({fmt(l['plancher'])}). Si tu veux vendre, c’est maintenant."))
        if l.get("sous_seuil"):
            items.append(("bad", f"⛔ <b>{esc(l['nom'])}</b> : le plus bas ({fmt(l['plancher'])}) est sous ton seuil "
                                 f"({fmt(l['seuil'])}). Ne baisse pas ; garde ou coupe la perte."))
        elif l.get("conseil"):
            items.append(("warn", f"⚔️ <b>{esc(l['nom'])}</b> : tu es battu. Repasse devant à <b>{fmt(l['conseil'])}</b>."))
        if (l.get("ecoulement_h") or 0) > 24:
            items.append(("warn", f"🐢 <b>{esc(l['nom'])}</b> : ~{l['ecoulement_h']:.0f} h pour écouler ton stock : "
                                  "mets moins d’annonces à la fois."))
    # 2. achats surs (vert) : plusieurs candidats, la page masque ceux que mes niveaux de metier ne permettent pas
    # de fabriquer (niveaux enregistres dans le navigateur) et n'en garde que 2
    seen = set()
    for e in (my.get("buy_trans") or []) + (my.get("buy_direct") or []):
        s_ = e.get("surete") or {}
        if s_.get("feu") == "vert" and e["net_u"] > 0 and not e["flags"] and e["item_id"] not in seen:
            seen.add(e["item_id"])
            how = "via Od transmuté" if any("transmuté" in x for x in e["ingredients"]) else "à l’HDV"
            metier = METIERS.get(e.get("metier"), e.get("metier") or "?")
            items.append(("ok buy", f'<span data-item="{e["item_id"]}">🟢 Achat → craft <b>{esc(e["objet"])}</b> '
                                    f'<span class="badge b-mut">🛠️ {esc(metier)}<span class="td-rate"></span></span> ({how}) : '
                                    f'+{fmt(e["net_u"])}/u, max ~{fmt(s_["qte_max"])} u, '
                                    f'ne vends pas sous {fmt(s_["prix_plancher"])}.</span>'))
        if len(seen) >= 8:
            break
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()[:19]
    for n in con.execute("SELECT * FROM news WHERE key LIKE 'update%' AND posted >= ? ORDER BY posted DESC LIMIT 2", (since,)):
        items.append(("mut", f"🛠️ Nouvelle note de version : <a href=\"{esc(n['url'])}\" target=\"_blank\" rel=\"noopener\" "
                             f"style=\"color:var(--acc)\">{esc(n['title'])}</a>"))
    order = {"bad": 0, "warn": 1, "ok": 2, "ok buy": 2, "mut": 3}
    rows = "".join(f'<li class="td-{k}">{t}</li>' for k, t in sorted(items, key=lambda x: order[x[0]]))
    return ('<div class="card todo"><b>✅ À faire maintenant</b><ol id="todo">' + rows
            + '<li id="todo-plan" class="td-plan">Plan du jour : calcul en cours…</li></ol></div>')


def hours_html(h):
    """Barres des ventes par heure, fenetre de 3 h la plus active en surbrillance."""
    if not h:
        return ('<p class="mut">Heures de vente : pas encore assez d’historique horaire, '
                'il se remplit à chaque passage quotidien.</p>')
    top = max(h["share"])
    bars = "".join(
        f'<div class="hb{" on" if (i - h["best"]) % 24 < 3 else ""}" title="{i}h : {v:.1%} des ventes">'
        f'<i style="height:{v / top * 100:.0f}%"></i><span>{i if i % 3 == 0 else ""}</span></div>'
        for i, v in enumerate(h["share"]))
    return (f'<div class="card"><div class="row"><span>Meilleur moment pour poster : '
            f'<b>{h["best"]}h – {(h["best"] + 3) % 24}h</b> · creux : {h["low"]}h – {(h["low"] + 3) % 24}h</span>'
            f'<span>{fmt(h["sold"])} annonces vendues sur {h["days"]} j · heure de {h["tz"]}</span></div>'
            f'<div class="hours">{bars}</div></div>')


def home(con, cfg, ctx, my, sname):
    """Page d'accueil : uniquement ce qui sert a faire du profit aujourd'hui."""
    kpis = (f'<div class="kpis">'
            '<div class="kpi"><div class="l">Gain du jour</div><div class="v pos" id="kopp">–</div>'
            '<div class="s" id="kopps">selon 🎯 Opportunités</div></div>'
            '<div class="kpi"><div class="l">Annonces libres</div><div class="v" id="kslots">–</div>'
            '<div class="s">limite du jeu moins tes annonces en cours</div></div>'
            f'<div class="kpi"><div class="l">Ventes mesurées sur {esc(sname)}</div>'
            f'<div class="v">{sum(1 for e in my["harvest"] if e.get("vol_source") == "serveur")} / {len(my["harvest"])}</div>'
            f'<div class="s">crafts comparés (annonces disparues sur 24 h)</div></div></div>')

    # 1. opportunites du jour : meme calcul que l'onglet 🎯 (site.js, oppRender), 5 premieres
    opp_html = ('<div id="hopps"></div><p class="mut" style="margin-top:8px">Liste complète, budget et temps de récolte : '
                '<a href="#" onclick="show(\'opps\');return false" style="color:var(--acc)">onglet 🎯 Opportunités</a>.</p>')
    spikes = my.get("spikes") or []
    if spikes:
        opp_html += (f'<div class="card" style="margin-top:10px;border-color:var(--warn)"><span>⚡ <b>{len(spikes)} pic(s) de prix</b> '
                     f'en cours ({esc(", ".join(e["objet"] for e in spikes[:3]))}) : rentable seulement en vendant vite. '
                     f'<a href="#" onclick="show(\'buy\');return false" style="color:var(--acc)">Voir l’onglet Achat → craft</a></span></div>')

    # 4. alertes du jour
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat(timespec="seconds")
    al = con.execute("SELECT ts, message FROM alerts_sent WHERE ts >= ? ORDER BY ts DESC LIMIT 12", (since,)).fetchall()
    alert_html = ('<div class="uses">' + "".join(
        f'<div class="card" style="padding:10px 14px"><span><span class="mut">{esc(paris(a["ts"], "%H:%M"))}</span> · {_md(a["message"])}</span></div>'
        for a in al) + "</div>") if al else '<p class="mut">Aucune alerte aujourd’hui.</p>'

    # 5. mes annonces
    costs = {e["objet"]: e["achats_u"] for e in my["buy"] if e.get("achats_u")}   # cout estime : achat des ingredients
    mine = my.get("listings") or []
    if mine:
        rows = "".join(
            f"<tr><td>{ctx.label(l['item_id']) if l['item_id'] else esc(l['nom']) + ' <span class=\"badge b-warn\">nom introuvable</span>'}</td>"
            f"{_num_td(l['mon_prix'], color=False)}{_num_td(l['plancher'], color=False)}"
            f"<td>{'<span class=\"badge b-bad\">Battu de ' + fmt(l['ecart']) + '</span>' if l['battu'] else ('<span class=\"badge b-ok\">Le moins cher</span>' if l['plancher'] is not None else '<span class=\"badge b-mut\">Pas en vente</span>')}"
            f"{'<span class=\"badge b-bad\">⛔ sous ton seuil</span>' if l.get('sous_seuil') else ''}"
            f"{'<span class=\"badge b-bad\">📉 chute</span>' if l.get('chute') else ''}</td>"
            f"{_num_td(l.get('seuil'), color=False)}{_num_td(l.get('marge_u'))}"
            f"<td class='sub'>{position_advice(l)}</td></tr>"
            for l in mine)
        mine_html = (f'<div class="wrap"><table><thead><tr>{_th("Mon annonce")}{_th("Mon prix", None, True)}'
                     f'{_th("Prix le plus bas", None, True)}{_th("Statut")}'
                     f'{_th("Seuil de rentabilité", "Coût de revient + taxe (10 %) et frais d’enregistrement (2 %) : ne vends pas en dessous", True)}'
                     f'{_th("Gain/u au plus bas", None, True)}{_th("Conseil")}</tr></thead><tbody>{rows}</tbody></table></div>')
    else:
        mine_html = ('<p class="mut">Aucune annonce en cours dans ton journal : note-les dans l’onglet 💰 Mes ventes pour être '
                     'alerté quand quelqu’un vend moins cher que toi ou sous ton seuil.</p>')

    mine_html += ('<p class="sub" style="margin-top:8px">Pour noter une annonce postée, vendue, relistée ou retirée : '
                  '<a href="#" onclick="show(\'gains\');return false" style="color:var(--acc)">onglet 💰 Mes ventes</a>.</p>')
    ctx.data.update(COSTS=costs, MARKET_ICONS=ctx.market_icons())

    # 6. annonces officielles
    news = con.execute("SELECT * FROM news WHERE key NOT LIKE 'reddit|%' ORDER BY posted DESC LIMIT 6").fetchall()
    news_html = ('<div class="uses">' + "".join(
        f'<div class="card" style="padding:10px 14px"><span><span class="mut">{esc(paris(n["posted"], "%d/%m %H:%M"))}</span> · '
        f'{_md(n["label"])} : <a href="{esc(n["url"])}" target="_blank" rel="noopener" style="color:var(--acc)">'
        f'{esc(n["title"])}</a></span></div>' for n in news) + "</div>") if news else \
        '<p class="mut">Les annonces officielles apparaîtront ici après le prochain passage.</p>'

    return (f"<h2>Aujourd’hui sur {esc(sname)}</h2><p class='lead'>Ce qu’il faut faire aujourd’hui pour gagner un maximum de kinah. "
            "Les tableaux complets sont dans les autres onglets.</p>" + kpis + todo_html(con, my)
            + "<h3>① Opportunités du jour</h3>" + hours_html(my.get("hours")) + "<br>" + opp_html
            + "<h3>② Mes annonces</h3>" + mine_html
            + "<h3>③ Alertes du jour</h3>" + alert_html
            + "<h3>④ Annonces officielles</h3>" + news_html)
