"""Onglet 🛠️ Mes metiers."""
import json

from .base import METIERS, _th, esc, is_good, niveau


def metiers_tab(con, my):
    """Onglet Mes metiers : niveaux enregistres dans le navigateur, + tables de reussite du jeu."""
    curves = {r["id"]: json.loads(r["rates"]) for r in con.execute("SELECT * FROM rate_curves")}
    items, good = {}, []
    for e in my["harvest"] + my["buy"] + (my.get("spikes") or []):
        items[e["item_id"]] = [list(a) for a in e.get("alts") or []]
        if is_good(e) and e["profit_j"] > 0:
            good.append(dict(o=e["objet"], a=items[e["item_id"]], j=e["profit_j"]))
    gaps = (0, 5, 10, 20, 30, 50)
    rows = []
    for k, c in sorted(curves.items(), key=lambda kv: kv[0]):
        # qui utilise cette courbe : metiers, niveaux requis, exemples (recettes visibles, objets echangeables)
        used = con.execute("SELECT DISTINCT r.profession, r.mastery, i.base_name FROM recipes r JOIN items i ON i.id = r.item_id "
                           "WHERE r.rate_curve = ? AND r.visible = 1 AND r.combo_result = 0 AND r.method = 'craft'", (k,)).fetchall()
        if not used:
            continue
        profs = ", ".join(METIERS.get(p, p) for p in sorted({u["profession"] for u in used}))
        levels = sorted({u["mastery"] or 0 for u in used})
        examples = ", ".join(list(dict.fromkeys(u["base_name"] for u in used))[:3])
        rows.append(f"<tr><td><b>{esc(examples)}</b>…<div class='sub'>{esc(profs)} · {niveau(levels[0])} à {niveau(levels[-1])}</div></td>"
                    + "".join(f"<td class='n'>{c[min(g, len(c) - 1)] / 1e6:.1f} %</td>".replace(".", ",") for g in gaps) + "</tr>")
    rows = "".join(rows)
    table = (f'<div class="wrap" style="max-height:none"><table><thead><tr>{_th("Recettes concernées (exemples)")}'
             + "".join(_th(f"Écart {g}" + ("+" if g == gaps[-1] else ""), None, True) for g in gaps)
             + f'</tr></thead><tbody>{rows}</tbody></table></div>') if curves else '<p class="mut">Tables pas encore chargées.</p>'
    data = json.dumps(dict(curves={str(k): v for k, v in curves.items()}, items=items, good=good), separators=(",", ":"))
    return ("<h2>Mes métiers</h2><p class='lead'>Renseigne le niveau de tes métiers : les crafts que tu ne peux pas faire "
            "sont grisés partout sur le site, et le profit tient compte de ta chance de réussite. Tes niveaux restent "
            "enregistrés dans ce navigateur ; clique sur <b>+1</b> quand tu montes.</p>"
            '<div class="cards" id="metiers"></div>'
            '<div class="toolbar" style="margin-top:12px"><label class="tg"><input type="checkbox" id="mlose" '
            'onchange="setOpt(\'lose\',this.checked)"> En cas d’échec, les ingrédients sont perdus</label>'
            '<label class="tg"><input type="checkbox" id="mhide" onchange="setOpt(\'hide\',this.checked)"> '
            'Masquer les crafts que je ne peux pas faire</label>'
            '<button class="mapbtn" onclick="shareLevels()">🔗 Copier le lien de mes niveaux (autre appareil)</button></div>'
            "<h3>Bientôt débloqué (10 prochains niveaux)</h3><div id='soon'></div>"
            "<h3>Chances de réussite du jeu selon l’écart de niveau</h3><p class='lead'>Écart = ton niveau − niveau requis "
            "par la recette. Valeurs du jeu (identiques à la fenêtre « Chances de fabrication »). Les recettes de niveau 0 "
            "sans table réussissent toujours. Niveaux : Débutant 1 à 50, puis Spécialiste 1 à 50.</p>" + table
            + f"<script>window.CRAFTDATA={data};</script>")
