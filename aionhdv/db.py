import sqlite3

from .config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
    id TEXT PRIMARY KEY,           -- id a2-tracker (ex. 2310)
    name TEXT, region TEXT, faction TEXT, env TEXT,
    ax_id INTEGER                  -- id aion2.exchange (ex. 12310)
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT, item_key TEXT, grade TEXT, category TEXT, sub_category TEXT,
    is_gather INTEGER DEFAULT 0,
    bound INTEGER DEFAULT 0,
    base_name TEXT,                -- nom sans "(lie)"
    name_en TEXT,
    auction_category TEXT,
    level INTEGER,
    icon_url TEXT,                 -- image distante (a2-tracker)
    icon_file TEXT,                -- image locale (data/icons/...)
    on_market INTEGER DEFAULT 0,   -- deja vu en vente sur un serveur suivi
    name_check TEXT                -- ok / non traduit / provisoire / different questlog
);
CREATE INDEX IF NOT EXISTS ix_items_base ON items(base_name);
CREATE TABLE IF NOT EXISTS map_worlds (
    id TEXT PRIMARY KEY, name TEXT, grp TEXT, map_key TEXT,
    x0 REAL, y0 REAL, nx INTEGER, ny INTEGER, size REAL, layer TEXT, url TEXT
);
CREATE TABLE IF NOT EXISTS gather_nodes (
    id TEXT PRIMARY KEY, name TEXT, item_id INTEGER, world_id TEXT, category TEXT,
    gx REAL, gy REAL, px REAL, py REAL, icon TEXT, db_id TEXT
);
CREATE INDEX IF NOT EXISTS ix_nodes_name ON gather_nodes(name);
CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    item_id INTEGER, method TEXT, profession TEXT, mastery INTEGER, faction TEXT,
    output_qty REAL, visible INTEGER, combo_result INTEGER, unresolved INTEGER,
    combo_item_id INTEGER, combo_prob_raw INTEGER
);
CREATE INDEX IF NOT EXISTS ix_recipes_item ON recipes(item_id);
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id TEXT, slot INTEGER, item_id INTEGER, qty REAL, is_alternative INTEGER
);
CREATE INDEX IF NOT EXISTS ix_ri_recipe ON recipe_ingredients(recipe_id);
CREATE TABLE IF NOT EXISTS quotes (           -- prix plancher horaires (a2-tracker)
    server TEXT, item_id INTEGER, ts TEXT, price REAL, listings INTEGER,
    PRIMARY KEY (server, item_id, ts)
);
CREATE INDEX IF NOT EXISTS ix_quotes_item ON quotes(server, item_id, ts);
CREATE TABLE IF NOT EXISTS activity (         -- mouvements d'annonces sur 24 h (a2-tracker)
    server TEXT, item_id INTEGER, ts TEXT, hours REAL,
    drops_h REAL, adds_h REAL, floor_up_drops_h REAL, points INTEGER, recorded INTEGER,
    PRIMARY KEY (server, item_id, ts)
);
CREATE TABLE IF NOT EXISTS ref_volume (       -- unites vendues publiees par le jeu (aion2.exchange)
    ax_server INTEGER, item_id INTEGER, registered TEXT,
    units_sold REAL, units_delta REAL, days_since_previous REAL,
    avg_price REAL, min_price REAL, max_price REAL, window_from TEXT,
    PRIMARY KEY (ax_server, item_id, registered)
);
CREATE TABLE IF NOT EXISTS ax_prices (        -- historique de prix agrege (aion2.exchange)
    ax_server INTEGER, item_id INTEGER, ts TEXT, bucket TEXT,
    low REAL, high REAL, avg REAL, close REAL, listings REAL, listings_min REAL, listings_max REAL,
    PRIMARY KEY (ax_server, item_id, ts, bucket)
);
CREATE TABLE IF NOT EXISTS analyses (
    run_ts TEXT, server TEXT, kind TEXT, item_id INTEGER, recipe_id TEXT,
    score REAL, data TEXT
);
CREATE INDEX IF NOT EXISTS ix_analyses ON analyses(run_ts, server, kind);
CREATE TABLE IF NOT EXISTS alerts_sent (
    key TEXT PRIMARY KEY, ts TEXT, message TEXT
);
CREATE TABLE IF NOT EXISTS news (            -- annonces officielles vues (site officiel, Reddit)
    key TEXT PRIMARY KEY, label TEXT, title TEXT, url TEXT, posted TEXT
);
CREATE TABLE IF NOT EXISTS patch_watch (     -- items cites dans une note de version, surveilles 48 h
    item_id INTEGER, news_key TEXT, title TEXT, url TEXT, since TEXT, base_price REAL,
    PRIMARY KEY (item_id, news_key)
);
CREATE TABLE IF NOT EXISTS rate_curves (     -- taux de reussite (en millioniemes de %) selon l'ecart de maitrise
    id INTEGER PRIMARY KEY, rates TEXT
);
CREATE TABLE IF NOT EXISTS runs (
    ts TEXT, job TEXT, status TEXT, detail TEXT
);
"""


def connect():
    DATA_DIR.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=60)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    # colonnes ajoutees apres coup aux bases existantes
    cols = {r["name"] for r in con.execute("PRAGMA table_info(recipes)")}
    for col, typ in (("rate_curve", "INTEGER"), ("fail_gauge", "INTEGER")):
        if col not in cols:
            con.execute(f"ALTER TABLE recipes ADD COLUMN {col} {typ}")
    return con
