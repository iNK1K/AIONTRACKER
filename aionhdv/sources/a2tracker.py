"""a2-tracker.com : catalogue des serveurs, recettes, prix plancher, historique des annonces."""
import re
from urllib.parse import quote

from ..net import get_json, get_text

BASE = "https://a2-tracker.com"


def servers():
    js = get_text(BASE + "/assets/server-catalogue.js")
    pat = re.compile(r'\{"id":"(\d+)","name":"([^"]+)","regionId":"(\w+)","regionName":"[^"]*",'
                     r'"factionId":"\d","faction":"(\w+)","environment":"([\w-]+)"')
    return [dict(id=m[0], name=m[1], region=m[2], faction=m[3], env=m[4]) for m in pat.findall(js)]


def crafting(locale="fr-FR"):
    return get_json(f"{BASE}/api.crafting.ashx?locale={quote(locale)}")


def quotes(server):
    return get_json(f"{BASE}/api.crafting.ashx?quotes=1&server={quote(str(server))}")


def history(item_id, server, days=1):
    return get_json(f"{BASE}/api.history.ashx?item={item_id}&server={quote(str(server))}&days={days}")


def database_page(server, page, limit=50, locale="fr-FR"):
    return get_json(f"{BASE}/api.database.ashx?page={page}&limit={limit}&server={server}"
                    f"&locale={locale}&sort=name&dir=asc&priced=current")
