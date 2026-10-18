"""aion2.exchange : unites vendues (publiees par le jeu, seulement certains serveurs) et historique de prix."""
from ..net import get_json

BASE = "https://aion2.exchange/api"


def servers():
    return (get_json(BASE + "/servers") or {}).get("servers", [])


def items(ax_server, offset=0, limit=200):
    return get_json(f"{BASE}/items?server={ax_server}&limit={limit}&offset={offset}")


def volume(item_id, ax_server):
    return get_json(f"{BASE}/items/{item_id}/volume?server={ax_server}")


def prices(item_id, ax_server, since_iso):
    return get_json(f"{BASE}/items/{item_id}/prices?server={ax_server}&from={since_iso}")
