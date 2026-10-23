"""Onglet 🌲 Recolte."""
import json

from .base import esc
from .tables import table_crafts, table_targets

GRADE_TABS = (("⚪ Blancs", "récoltés sur les points"), ("🟢 Verts", "« d’une grande pureté »"), ("🔵 Bleus", "« pur »"),
              ("🟠 Éclatants", "« éclatant »"))


def harvest_tab(ctx, my, hyp):
    """🌲 Recolte, une section par grade : seul le blanc se recolte sur les points (recolte/heure, kinah/heure) ; vert,
    bleu et eclatant sont des procs, trop rares pour etre planifies : on dit seulement quoi en faire."""
    rows = my["harvest"] + (my.get("raw") or [])
    rows.sort(key=lambda e: -e["profit_j"])
    seg, panels = [], []
    for g, (title, what) in enumerate(GRADE_TABS):
        targets = [t for t in my["targets"] if t.get("rang", 0) == g]
        crafts = [e for e in rows if e.get("rang", 0) == g]
        if not targets and not crafts:
            continue
        pid, tid = f"hg{g}", f"th{g}"
        seg.append(f'<button{" class=on" if not seg else ""} onclick="segShow(this,\'{pid}\')">{title} '
                   f'<span class="mut">({len(crafts)})</span></button>')
        lead = ("Indique ce que tu récoltes par heure pour chaque ressource (100 par défaut) : <b>Kinah / heure</b> dit où "
                "passer ton temps, <b>Heures / jour</b> combien de temps de récolte le marché absorbe avant que les prix "
                "baissent." if g == 0 else
                f"Ressources {what} : elles tombent en proc pendant la récolte, trop rarement pour planifier leur récolte. "
                "Voici quoi en faire quand tu en as.")
        panels.append(f"<div id='{pid}' class='segp'{'' if not panels else ' style=display:none'}>"
                      f"<h3>Ressources</h3><p class='lead'>{lead} Les usages douteux ou à perte sont indiqués en orange.</p>"
                      + table_targets(ctx, targets, "targets" if g == 0 else f"targets{g}", rates=g == 0, crafts=tid)
                      + f"<h3>Crafts et vente du brut, par profit</h3><p class='lead'>{hyp} Prix le plus bas de chaque "
                      "ressource à côté de son nom.</p>" + table_crafts(ctx, crafts, tid, True) + "</div>")
    return ("<h2>Récolte → craft ou vente du brut</h2><p class='lead'>Ta récolte ne coûte rien, mais chaque ressource vaut "
            "au moins ce qu’elle rapporte vendue brute : un craft n’est intéressant que s’il fait mieux (colonne "
            "« vs brut/u »). Une section par grade de ressource.</p>"
            f'<div class="seg">{"".join(seg)}</div>' + "".join(panels) + procs_html(my))


def procs_html(my):
    """Mesure de mes procs : je note mes sessions de recolte (blancs recoltes, verts, bleus, eclatants obtenus) ; le
    navigateur en tire mes taux et ce qu'ils rapportent en plus par ressource blanche (site.js, procRender)."""
    m = my["market"]
    best = {t["ressource"]: t["meilleur"] for t in my["targets"] if t["meilleur"]}
    names = m.gather_names()
    procs = {}
    for c in names:
        if m.grade(c):
            continue
        for p in names:
            g = m.grade(p)
            if g and p.startswith(c + " "):
                v = best.get(p) or m.raw_net(p)
                procs.setdefault(c, []).append([g, p, round(v) if v else 0])
    data = json.dumps({c: sorted(v) for c, v in procs.items()}, ensure_ascii=False, separators=(",", ":"))
    opts = "".join(f"<option>{esc(c)}</option>" for c in sorted(procs))
    inp = ('type="number" min="0" style="width:84px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;'
           'background:var(--bg2);color:var(--txt);font:inherit"')
    return ("<h3>📊 Mes procs de récolte</h3><p class='lead'>Note tes sessions de récolte : combien de ressources blanches "
            "récoltées et combien de vertes, bleues, éclatantes obtenues. Le site en tire tes taux de proc et ce qu’ils "
            "rapportent en plus par ressource blanche (meilleur usage de chaque proc). Gardé dans ce navigateur.</p>"
            f'<div class="toolbar"><select id="pres" style="padding:5px 7px;border:1px solid var(--line);border-radius:7px;'
            f'background:var(--bg2);color:var(--txt);font:inherit">{opts}</select>'
            f'<label class="tg">Blancs <input id="pn" {inp}></label><label class="tg">🟢 <input id="pg1" {inp}></label>'
            f'<label class="tg">🔵 <input id="pg2" {inp}></label><label class="tg">🟠 <input id="pg3" {inp}></label>'
            '<button class="mapbtn" onclick="procAdd()">Ajouter la session</button></div><div id="pbox"></div>'
            f"<script>window.PROCS={data};</script>")
