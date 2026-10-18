import json
import time
import urllib.error
import urllib.request

from .config import load_config

_last_call = 0.0


def get_json(url, retries=3):
    """GET poli : pause entre appels, quelques tentatives, None si introuvable."""
    global _last_call
    cfg = load_config()["http"]
    for attempt in range(retries):
        wait = cfg["delay_seconds"] - (time.time() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()
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
    cfg = load_config()["http"]
    req = urllib.request.Request(url, headers={"User-Agent": cfg["user_agent"]})
    with urllib.request.urlopen(req, timeout=cfg["timeout_seconds"]) as resp:
        return resp.read().decode("utf-8")
