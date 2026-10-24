"""Pont local de l'assistant : le chat du site passe par Claude Code sur ce PC (ton abonnement Claude), sans clé API.

py scripts\\assistant_local.py      (laisser la fenêtre ouverte ; Ctrl + C pour arrêter)
Puis sur le site, onglet 💬 Assistant : bouton « Abonnement Claude (ce PC) » en bas du chat.

- Nécessite Claude Code installé et connecté sur ce PC (commande `claude`) : chacun utilise son propre abonnement.
- N'écoute que 127.0.0.1 et ne répond qu'aux pages du site (en-tête Origin) : un autre site ne peut pas s'en servir.
- Claude Code tourne en lecture seule (recherche web, lecture de pages, recherche dans le catalogue), dans .runtime/assistant/.
- Le catalogue du tracker (prix, recettes, récolte) vient du site publié (assist.js), relu toutes les 30 min.
"""
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / ".runtime" / "assistant"
PORT = 8787
_owner, _repo = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))["github_repo"].split("/")
SITE = f"https://{_owner.lower()}.github.io/{_repo}/"
ORIGINS = {f"https://{_owner.lower()}.github.io"}
LOCAL_ORIGIN = re.compile(r"^http://(localhost|127\.0\.0\.1)(:\d+)?$")       # site ouvert en local (reports/)
CLAUDE = shutil.which("claude")
TOOLS = ["WebSearch", "WebFetch", "Read", "Grep", "Glob"]

SYSTEM = """You are the Aion 2 assistant inside AION HDV, a private tool used by two friends who play Aion 2 (NCSOFT's MMORPG) \
on the server {server}, with a French game client. They ask anything about the game: loot and drops, dungeons, bosses, classes \
and builds, gear progression, crafting, gathering, quests, the auction house (HDV), events and patches. You are a chat assistant: \
never create or edit files.

Your built-in knowledge of Aion 2 is thin and easily confused with the original Aion (2008). Do not answer game facts from memory: \
search the web first and base the answer on what you find. Prefer recent, specific sources (official site and patch notes, game \
databases and wikis, guides, Reddit, Korean or Taiwanese community sites when the global version lacks coverage), fetch a page when \
search snippets are not enough, and say so when sources disagree, are old, or only cover the Korean version.

For item prices, crafting recipes and costs, profit, ingredients or gathering locations, Grep tracker-data.md in the working \
directory first (case-insensitive, French or English item name): one line per item with rarity, type, level, current lowest price, \
usual selling price and listings on their server (kinah), recipes with ingredients, what it is used to craft, and gathering zones. \
Prices were taken at {asof} UTC; the auction house keeps a 10% tax on sales. Item names there are French; give French names as they appear in game, with the English name in \
brackets when it helps.

Answer in the language of the question. Lead with the direct answer, then the details that matter: short sections, lists, and a \
table when comparing options. Bold key item names and numbers. Be concrete (names, numbers, where, how many), skip filler. \
End with the main sources as Markdown links."""


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def tracker_markdown(data):
    """Une ligne par objet (tout ce qu'il faut sur l'objet sort d'un seul Grep)."""
    by = {r[0]: r for r in data["items"]}
    name = lambda i: (by.get(i) or [0, f"#{i}"])[1]
    num = lambda n: f"{n:,}".replace(",", " ")
    uses = {}
    for iid, rs in data["recipes"].items():
        for r in rs:
            for i, _ in r[3]:
                uses.setdefault(i, set()).add(name(int(iid)))
    out = [f"# Catalogue du tracker AION HDV, serveur {data['server']} (prix en kinah relevés le {data['asof']} UTC)", ""]
    for r in sorted(data["items"], key=lambda r: r[1] or ""):
        if not r[1]:
            continue
        iid, parts = r[0], [f"{r[1]}" + (f" ({r[2]})" if r[2] else ""), " ".join(str(x) for x in (r[3], r[4]) if x)
                            + (f" niv. {r[5]}" if r[5] else "")]
        if r[6]:
            parts.append(f"prix le plus bas {num(r[6])}" + (f", prix habituel {num(r[8])}" if r[8] else "")
                         + (f", {r[7]} annonces" if r[7] is not None else ""))
        for prof, mastery, qty, ings in data["recipes"].get(str(iid), []):
            parts.append(f"recette {prof} (maîtrise {mastery}, donne {qty:g}) : "
                         + ", ".join(f"{q:g} x {name(i)}" + (f" [{num(by[i][6])}]" if i in by and by[i][6] else "")
                                     for i, q in ings))
        if iid in uses:
            parts.append("sert à crafter : " + ", ".join(sorted(uses[iid])[:15]))
        nodes = data["nodes"].get(str(iid))
        if nodes:
            parts.append("récolte : " + ", ".join(f"{z} ({n} points)" for z, n in nodes.items()))
        out.append(" | ".join(parts))
    return "\n".join(out) + "\n"


def refresh():
    """tracker-data.md depuis le site publié (assist.js), sinon depuis reports/ ; garde l'ancien en cas d'échec."""
    path = WORK / "tracker-data.md"
    if path.exists() and time.time() - path.stat().st_mtime < 1800:
        return json.loads((WORK / "meta.json").read_text(encoding="utf-8"))
    try:
        with urllib.request.urlopen(SITE + "assist.js", timeout=20) as r:
            text = r.read().decode("utf-8")
    except Exception as e:
        local = ROOT / "reports" / "assist.js"
        if not local.exists():
            log(f"catalogue injoignable ({e})")
            return json.loads((WORK / "meta.json").read_text(encoding="utf-8")) if path.exists() else {}
        text = local.read_text(encoding="utf-8")
    data = json.loads(text[text.index("=") + 1:].strip().rstrip(";"))
    path.write_text(tracker_markdown(data), encoding="utf-8")
    meta = dict(server=data["server"], asof=data["asof"])
    (WORK / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    log(f"catalogue : {len(data['items'])} objets, prix du {data['asof']}")
    return meta


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _origin(self):
        o = self.headers.get("Origin", "")
        return o if o in ORIGINS or LOCAL_ORIGIN.match(o) else None

    def _head(self, code, origin, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST")
        self.send_header("Access-Control-Allow-Private-Network", "true")     # site public -> 127.0.0.1 (Chrome)
        self.send_header("Vary", "Origin")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_OPTIONS(self):
        o = self._origin()
        if not o:
            return self.send_error(403)
        self._head(204, o)

    def do_GET(self):
        o = self._origin()
        if self.path != "/health" or not o:
            return self.send_error(403 if self.path == "/health" else 404)
        self._head(200, o)
        self.wfile.write(json.dumps({"ok": bool(CLAUDE)}).encode())

    def do_POST(self):
        o = self._origin()
        if self.path != "/ask" or not o:
            return self.send_error(403)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self.send_error(400)
        q, session = str(body.get("q") or "").strip(), str(body.get("session") or "")
        if not q:
            return self.send_error(400)
        self._head(200, o, "application/x-ndjson")
        try:
            self.ask(q, session)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            log("question interrompue depuis la page")

    def send_ev(self, **ev):
        self.wfile.write((json.dumps(ev, ensure_ascii=False) + "\n").encode("utf-8"))
        self.wfile.flush()

    def ask(self, q, session):
        meta = refresh()
        cmd = [CLAUDE, "-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages", "--model", "opus",
               "--tools", ",".join(TOOLS), "--allowedTools", *TOOLS, "--strict-mcp-config", "--setting-sources", "local",
               "--system-prompt", SYSTEM.format(server=meta.get("server", "?"), asof=meta.get("asof", "?"))]
        if re.fullmatch(r"[0-9a-f-]{36}", session):
            cmd += ["--resume", session]                                       # suite de la conversation
        log(f"question : {q[:80]}")
        p = subprocess.Popen(cmd, cwd=WORK, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", errors="replace")
        err = []
        threading.Thread(target=lambda: err.extend(p.stderr), daemon=True).start()
        p.stdin.write(q)
        p.stdin.close()
        sources, done = [], False
        try:
            for line in p.stdout:
                try:
                    x = json.loads(line)
                except ValueError:
                    continue
                if x.get("type") == "stream_event":
                    d = x["event"].get("delta") or {}
                    if d.get("type") == "text_delta":
                        self.send_ev(t="text", v=d["text"])
                elif x.get("type") == "assistant":
                    for b in x["message"].get("content", []):
                        if b.get("type") == "tool_use":
                            inp = b.get("input") or {}
                            if b["name"] == "WebFetch" and inp.get("url"):
                                sources.append(inp["url"])
                            self.send_ev(t="tool", name=b["name"],
                                         v=inp.get("query") or inp.get("url") or inp.get("pattern") or "")
                elif x.get("type") == "result":
                    done = True
                    if x.get("is_error"):
                        self.send_ev(t="error", v=str(x.get("result") or x.get("subtype") or "erreur de Claude Code"))
                    else:
                        self.send_ev(t="done", text=x.get("result") or "", session=x.get("session_id"),
                                     sources=list(dict.fromkeys(sources)))
            p.wait()
            if not done:
                self.send_ev(t="error", v=("".join(err[-5:]).strip() or f"Claude Code s'est arrêté (code {p.returncode})"))
        finally:
            if p.poll() is None:
                p.kill()


def main():
    if not CLAUDE:
        sys.exit("Claude Code introuvable : installe-le et connecte-toi (commande `claude`), puis relance.")
    WORK.mkdir(parents=True, exist_ok=True)
    refresh()
    log(f"pont de l'assistant prêt sur http://127.0.0.1:{PORT} (site : {SITE}). Ctrl + C pour arrêter.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
