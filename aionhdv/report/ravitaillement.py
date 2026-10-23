"""Onglet 📦 Ravitaillement."""
import json

from ..collect import paris
from ..config import DATA_DIR
from .base import esc


def supply_tab(ctx, cfg, my):
    """📦 Ravitaillement : capture de la fenetre des ravitaillements (objets demandes chaque jour, donc recherches a
    l'HDV) -> pour chaque objet, de quoi calculer dans le navigateur le gain a le crafter pour le revendre : ingredients
    au prix d'achat realiste, ingredient eclatant crafte par sa chaine ou achete, combo, plus bas prix en vente, prix
    de vente realiste (plafond du prix propose) et mediane 3 j."""
    m, fees, items = my["market"], cfg["fees"], []
    rnd = lambda v: round(v) if v is not None else None
    combo_cfg = cfg.get("combo_rate")
    # objet eclatant -> recette qui le donne en combo : un ingredient eclatant peut se crafter (option A) ou s'acheter (B)
    combo_of = {}
    for rs in m.recipes_by_item.values():
        for r in rs:
            if r["combo_item_id"] and not r["unresolved"]:
                combo_of.setdefault(r["combo_item_id"], r)

    def meds(iid):
        """Medianes 3 j et 7 j du prix plancher : de quoi signaler un prix trop haut (site.js, sHigh)."""
        return [rnd(st and st["median"]) for st in (m.price_stats(iid, 3), m.price_stats(iid, 7))]

    def part(p):
        """Ligne de detail d'une recette, avec les medianes des ingredients achetes a l'HDV."""
        return dict(p, p=rnd(p["p"]), md=meds(p["i"]) if p.get("i") else None, sub=[part(x) for x in p.get("sub") or []])

    def value(iid):
        """Prix de revente d'un objet : mediane 3 j du prix plancher, sinon prix habituel (avant taxe)."""
        st = m.price_stats(iid, 3)
        u = m.usual_price(iid)
        return rnd(st["median"] if st else u["price"] if u else None)

    def combo(r):
        """Chance de combo d'une recette et objet obtenu (nom, valeur). Valeur prudente : le plus bas entre le prix
        realiste et le prix habituel (objets chers, peu d'annonces et de ventes)."""
        cid = r["combo_item_id"]
        if not cid or cid not in m.items:
            return None
        sp = m.sell_price(cid)
        return dict(c=combo_cfg if combo_cfg is not None else (r["combo_prob_raw"] or 0) / 10000,
                    n=m.items[cid]["name"], v=rnd(sp["pess"]) if sp else value(cid), md=meds(cid))

    def plain(r):
        """Revente de l'objet de base d'une recette a combo, plafonnee a la valeur prudente de sa version eclatante :
        l'objet normal ne vaut jamais plus (une annonce aberrante seule en vente fausse sa mediane et son prix habituel)."""
        v, cv = value(r["item_id"]), (combo(r) or {}).get("v")
        return min(v, cv) if v is not None and cv is not None else v

    def needs(r, seen):
        """Ingredients eclatants d'une recette, avec la chaine pour les crafter (toute la chaine) et le prix HDV."""
        out = []
        for opts in m.ingredients.get(r["id"], {}).values():
            o = next((o for o in opts if o["item_id"] in combo_of), None)
            if o and o["item_id"] not in seen and len(seen) < 6:
                bp = m.buy_price(o["item_id"])
                out.append(dict(i=o["item_id"], n=m.items[o["item_id"]]["name"], q=o["qty"],
                                buy=rnd(bp and bp["real"]), med=value(o["item_id"]), md=meds(o["item_id"]), l=bp["listings"] if bp else 0,
                                chain=step(combo_of[o["item_id"]], seen | {o["item_id"]})))
        return out

    def step(r, seen):
        """Une etape de chaine : la recette de l'objet de base, dont le combo donne l'ingredient eclatant voulu."""
        sub = needs(r, seen)
        c = m.recipe_cost(r, "buy", skip={x["i"] for x in sub})
        return dict(i=r["item_id"], n=m.items[r["item_id"]]["name"], prof=r["profession"], m=r["mastery"] or 0, cv=r.get("rate_curve"),
                    c=combo(r)["c"], k=rnd(c["cost_r"]) if c["ok"] else None, plain=plain(r),
                    pmd=meds(r["item_id"]), parts=[part(p) for p in c["parts"]],
                    need=sub)

    def rest_cost(r, need):
        """Cout des autres ingredients (hors eclatants), communs aux deux options."""
        c = m.recipe_cost(r, "buy", skip={x["i"] for x in need})
        return rnd(c["cost_r"]) if c["ok"] else None

    def craft_info(iid, recs):
        """Recette la moins chere d'un objet (ingredients au prix d'achat realiste) : de quoi calculer son craft."""
        best = None
        for r in recs:
            c = m.recipe_cost(r, "buy")
            q = r["output_qty"] or 1
            cu = c["cost_r"] / q if c["ok"] else None
            if best is None or (cu is not None and (best[0] is None or cu < best[0])):
                best = (cu, c, q, r)
        r = best[3]
        need = needs(r, {iid, r["combo_item_id"]})
        return dict(c=rnd(best[0]), q=best[2], cv=r.get("rate_curve"), combo=combo(r), need=need,
                    rest=rest_cost(r, need) if need else None,
                    parts=[part(p) for p in best[1]["parts"]],
                    prof=r["profession"], m=r["mastery"] or 0)

    def sale(iid, it):
        st, sp = m.price_stats(iid, 3), m.sell_price(iid)
        return dict(i=iid, n=it["name"], s=f"../data/{it['icon_file']}", sell=value(iid), l=m.listings.get(iid, 0),
                    med=rnd(st and st["median"]), ask=rnd(m.price.get(iid)), real=rnd(sp and sp["real"]), md=meds(iid))

    def shown(it):
        return it.get("category") == "Equip" and not it.get("bound") and it.get("icon_file") \
            and (DATA_DIR / it["icon_file"]).exists()

    # objet normal : obtenu par sa recette quand le craft ne fait pas combo
    for iid, recs in m.recipes_by_item.items():
        it = m.items.get(iid) or {}
        if shown(it):
            items.append(dict(sale(iid, it), **craft_info(iid, recs)))
    # objet eclatant : obtenu seulement par le combo de la recette de l'objet de base (via) ; meme icone que l'objet
    # normal sur un fond d'une autre qualite, ce qui permet a la lecture de la capture de les departager
    for cid, r in combo_of.items():
        it = m.items.get(cid) or {}
        if shown(it):
            bi = r["item_id"]
            items.append(dict(sale(cid, it), via=dict(craft_info(bi, [r]), i=bi, n=m.items[bi]["name"], plain=plain(r), pmd=meds(bi)),
                              prof=r["profession"], m=r["mastery"] or 0))
    ctx.data["SUPPLY"] = items
    return ("<h2>Ravitaillement</h2><p class='lead'>Les objets demandés du jour sont recherchés à l’HDV : colle une capture "
            "de ta fenêtre de ravitaillement (<b>Ctrl + V</b> sur cet onglet) pour voir lesquels rapportent à crafter puis "
            f"revendre. Gain par craft = vente après taxe ({fees:.0%}) − coût des ingrédients (prix d’achat réaliste, dernier relevé "
            f"{esc(paris(m.as_of, '%d/%m %H:%M')) if m.as_of else '?'}), échecs compris selon tes niveaux (🛠️ Mes métiers). "
            "La capture distingue l’objet normal de sa version <b>éclatante</b> (même icône, fond de "
            "qualité différent) : l’objet normal s’obtient quand le craft ne fait pas combo (le combo est montré à part, c’est "
            "un pari) ; l’éclatant seulement par combo, d’où plusieurs crafts par objet, objets normaux revendus. Un "
            "ingrédient éclatant est crafté par sa chaîne <b>(A)</b> ou acheté <b>(B)</b>, au moins cher.</p>"
            '<div class="card" ondragover="event.preventDefault()" ondrop="event.preventDefault();supplyScan(event.dataTransfer.files[0])">'
            '<b>📷 Capture de la fenêtre de ravitaillement</b><span class="mut">Ctrl + V sur cet onglet, glisse le fichier, ou '
            '<label style="color:var(--acc);cursor:pointer;text-decoration:underline">choisis un fichier<input type="file" '
            'accept="image/*" hidden onchange="supplyScan(this.files[0])"></label>. La dernière lecture est gardée dans ce '
            'navigateur et recalculée avec les prix de chaque passage.</span><span id="smsg" class="mut"></span></div>'
            '<div id="sbox"></div>'
            f'<script>window.SUPPLY_CFG={json.dumps(dict(tax=fees, warn=cfg["alerts"].get("price_vs_median", 0.5)))};</script>')
