"""Point d'entree : python -m aionhdv <commande>

Commandes :
  init        serveurs, recettes, catalogue complet (FR/EN), carte questlog, controle des noms
  icons       telecharge les images des items vus sur le marche ou dans les recettes
  snapshot    prix de tout le marche des serveurs suivis (toutes les heures)
  activity    mouvements d'annonces sur 24 h (serveur suivi + reference)
  refvolume   unites vendues du serveur de reference (aion2.exchange, une fois par jour)
  backfill    historique de prix aion2.exchange depuis le 5 octobre
  servers     instantane de tous les serveurs launch asmodiens EU (comparaison)
  analyze     calculs + rapport HTML
  news        annonces officielles (site officiel, Reddit) -> Discord
  hourly      snapshot + analyze + alertes + annonces officielles
  daily       refvolume + activity + historique + servers + resume du jour (+ tendances le dimanche)
  report      regenere seulement le rapport HTML

Option :
  --dry-run   mode test : rien n'est envoye sur Discord (les alertes restent dans logs/alerts.log)
"""
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

from . import alerts, analysis, catalog, collect, news, report
from .config import LOG_DIR, load_config
from .db import connect


def log(msg):
    LOG_DIR.mkdir(exist_ok=True)
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "run.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ax_of(con, server):
    r = con.execute("SELECT ax_id FROM servers WHERE id = ?", (str(server),)).fetchone()
    return r["ax_id"] if r else None


def cmd_init(con, cfg):
    log(f"serveurs : {collect.sync_servers(con)}")
    log(f"recettes (items, recettes) : {collect.sync_recipes(con, cfg['locale'])}")
    log(f"catalogue (FR, EN) : {catalog.sync_catalog(con, cfg['my_server'])}")
    log(f"carte (mondes, points de recolte) : {catalog.sync_map(con)}")
    log(f"controle des noms : {catalog.check_names(con)}")


def cmd_snapshot(con, cfg):
    for s in cfg["watch_servers"]:
        log(f"marche {s} : {catalog.snapshot_market(con, s)} items cotes (a2-tracker), "
            f"complement aion2.exchange (ajoutes, nouveaux items) : {catalog.snapshot_market_ax(con, s)}")


def cmd_activity(con, cfg):
    """Annonces disparues sur 24 h pour TOUS les produits compares (et les ressources) : c'est la mesure des ventes
    sur chaque serveur. Le serveur de reference sert a mesurer la taille des annonces vendues."""
    core = collect.core_items(con, 60)
    per_server = {str(s): list(dict.fromkeys(core + collect.top_products(con, s, 1000)))
                  for s in dict.fromkeys([cfg["my_server"], *cfg["watch_servers"]])}
    items = list(dict.fromkeys(i for ids in per_server.values() for i in ids))
    # le serveur de reference est elyseen : on y suit les equivalents des produits asmodiens
    ref_items = list(dict.fromkeys(items + [e for e in (analysis.elyos_equivalent(con, i) for i in items) if e]))
    for s in dict.fromkeys([cfg["my_server"], *cfg["watch_servers"], cfg["reference_server"]]):
        ids = ref_items if str(s) == str(cfg["reference_server"]) else per_server.get(str(s), items)
        log(f"activite {s} : {collect.collect_activity(con, s, ids)} items")


def cmd_refvolume(con, cfg):
    ax = ax_of(con, cfg["reference_server"])
    log(f"volumes de reference ({ax}) : {collect.collect_ref_volume(con, ax, collect.ref_item_ids(con))} lignes")


def cmd_backfill(con, cfg, since="2026-10-05T00:00:00Z", servers=None):
    items = collect.tracked_items(con)
    for s in servers or cfg["watch_servers"]:
        ax = ax_of(con, s)
        if ax:
            log(f"historique {s} : {collect.collect_ax_prices(con, ax, items, since)} points")


def cmd_servers(con, cfg):
    rows = con.execute("SELECT id FROM servers WHERE region='eu' AND faction=(SELECT faction FROM servers WHERE id=?) "
                       "AND env=(SELECT env FROM servers WHERE id=?)", (cfg["my_server"], cfg["my_server"])).fetchall()
    for r in rows:
        log(f"marche {r['id']} : {catalog.snapshot_market(con, r['id'])} items cotes")


def cmd_analyze(con, cfg, send_alerts=False, send_digest=False):
    results = []
    for s in cfg["watch_servers"]:
        res = analysis.run_all(con, cfg, s)
        results.append(res)
        log(f"analyse {s} : {len(res['harvest'])} crafts recolte, {len(res['buy'])} achat-craft, ratio {res['ratio']:.2f}")
        if send_alerts and str(s) == str(cfg["my_server"]):
            watch = analysis.watched_items(res)
            analysis.add_safety(con, res, collect.recent_activity(con, s, watch))
            log(f"activite recente : {len(watch)} items surveilles")
            msgs = alerts.detect(con, cfg, res)
            for m in msgs:
                alerts.send(cfg, m)
            uniques = alerts.detect_uniques(con, cfg, res)
            for m in uniques:
                alerts.send(cfg, m, "unique")
            flips = (alerts.detect_flips(con, cfg, res) + alerts.detect_undercuts(con, cfg, res)
                     + alerts.detect_patch_moves(con, cfg, res) + alerts.detect_spikes(con, cfg, res)
                     + alerts.detect_positions(con, cfg, res))
            for m in flips:
                alerts.send(cfg, m)
            log(f"alertes : {len(msgs)}, uniques : {len(uniques)}, flips et annonces battues : {len(flips)}")
        if send_digest and str(s) == str(cfg["my_server"]):
            alerts.send(cfg, alerts.digest(con, cfg, res))
            if datetime.now(collect.PARIS or timezone.utc).weekday() == 6:      # dimanche
                alerts.send(cfg, alerts.weekly(con, cfg, res))
    path = report.build(con, cfg, results)
    log(f"rapport : {path}")
    return results


def cmd_news(con, cfg):
    """Ne fait jamais echouer le passage : une source injoignable est seulement notee dans le journal."""
    try:
        msgs, errors = news.check(con, cfg)
    except Exception as e:
        log(f"annonces : erreur {e}")
        return
    for m in msgs:
        alerts.send(cfg, m, "news")
    log(f"annonces : {len(msgs)} nouvelle(s)" + (f", sources en erreur : {'; '.join(errors)}" if errors else ""))


def step(name, fn, errors):
    """Etape isolee : une erreur (source injoignable, requete expiree...) est notee et n'empeche pas les suivantes."""
    t = time.time()
    try:
        fn()
        log(f"etape {name} : {time.time() - t:.0f}s")
    except Exception:
        errors.append(name)
        log(f"ERREUR etape {name} (les etapes suivantes continuent)\n{traceback.format_exc()}")


def main(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cfg = load_config()
    if dry:
        for k in cfg:
            if k.startswith("discord_webhook"):
                cfg[k] = ""
        log("mode test : aucune alerte envoyée sur Discord (voir logs/alerts.log)")
    con = connect()
    cmd = argv[1]
    t0 = time.time()
    try:
        if cmd == "init":
            cmd_init(con, cfg)
        elif cmd == "icons":
            log(f"images : {catalog.download_icons(con)}")
        elif cmd == "snapshot":
            cmd_snapshot(con, cfg)
        elif cmd == "activity":
            cmd_activity(con, cfg)
        elif cmd == "refvolume":
            cmd_refvolume(con, cfg)
        elif cmd == "backfill":
            cmd_backfill(con, cfg, *(argv[2:3]))
        elif cmd == "servers":
            cmd_servers(con, cfg)
        elif cmd == "analyze":
            cmd_analyze(con, cfg)
        elif cmd == "report":
            cmd_analyze(con, cfg)
        elif cmd == "news":
            cmd_news(con, cfg)
        elif cmd in ("hourly", "daily"):
            # chaque etape est isolee : le rapport et le site sont produits meme si une source fait defaut
            errors = []
            if cmd == "hourly":
                if not con.execute("SELECT 1 FROM rate_curves LIMIT 1").fetchone():
                    step("recettes", lambda: log(f"recettes : {collect.sync_recipes(con, cfg['locale'])}"), errors)
                step("marche", lambda: cmd_snapshot(con, cfg), errors)
                step("analyse", lambda: cmd_analyze(con, cfg, send_alerts=True), errors)
                step("annonces", lambda: cmd_news(con, cfg), errors)
            else:
                # aion2.exchange est lent (5-10 s par requete) : on s'en sert le moins possible. Les volumes de
                # Kaisinel (taille des annonces vendues, qui evolue lentement) sont recharges s'ils ont plus de 3 jours ;
                # l'historique horaire n'est plus telecharge (nos releves horaires du marche le remplacent).
                last = con.execute("SELECT MAX(registered) AS r FROM ref_volume").fetchone()["r"]
                stale = not last or last < (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
                step("recettes", lambda: log(f"recettes : {collect.sync_recipes(con, cfg['locale'])}"), errors)
                if stale:
                    step("volumes de reference", lambda: cmd_refvolume(con, cfg), errors)
                step("activite", lambda: cmd_activity(con, cfg), errors)
                step("serveurs", lambda: cmd_servers(con, cfg), errors)
                step("images", lambda: catalog.download_icons(con), errors)
                step("analyse", lambda: cmd_analyze(con, cfg, send_alerts=True, send_digest=True), errors)
            if "analyse" in errors:
                raise RuntimeError("analyse impossible : rapport non produit")
            collect.log_run(con, cmd, "partiel" if errors else "ok",
                            f"{time.time() - t0:.0f}s" + (f", erreurs : {', '.join(errors)}" if errors else ""))
            return 0
        else:
            print(__doc__)
            return 2
        collect.log_run(con, cmd, "ok", f"{time.time() - t0:.0f}s")
        return 0
    except Exception:
        err = traceback.format_exc()
        log(f"ERREUR {cmd}\n{err}")
        collect.log_run(con, cmd, "error", err)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
