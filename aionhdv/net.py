import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .config import load_config

_last_call = 0.0
_lock = threading.Lock()
_http = load_config()["http"]


def _pace(delay):
    """Au moins `delay` secondes entre deux departs de requete, meme avec plusieurs requetes en cours."""
    global _last_call
    with _lock:
        wait = delay - (time.time() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()


def fetch_all(fn, keys, workers=3):
    """Telecharge fn(cle) pour chaque cle, `workers` requetes a la fois (les sites restent menages : _pace).
    Renvoie {cle: resultat} ; les ecritures en base se font ensuite, en serie."""
    keys = list(keys)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(zip(keys, ex.map(fn, keys)))


def get_json(url, retries=3):
    """GET poli : pause entre appels, quelques tentatives, None si introuvable."""
    cfg = _http
    for attempt in range(retries):
        _pace(cfg["delay_seconds"])
        req = urllib.request.Request(url, headers={"User-Agent": cfg["user_agent"], "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=cfg["timeout_seconds"]) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (404, 422):
                return None
            if e.code == 429 or e.code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(3 * (attempt + 1))
    return None


def get_text(url):
    cfg = _http
    _pace(cfg["delay_seconds"])
    req = urllib.request.Request(url, headers={"User-Agent": cfg["user_agent"]})
    with urllib.request.urlopen(req, timeout=cfg["timeout_seconds"]) as resp:
        return resp.read().decode("utf-8")
