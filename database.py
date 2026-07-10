"""
Persistenza SQLite — tutte le tabelle del progetto in un unico file.
"""
import sqlite3, os, time
from contextlib import contextmanager
import config

_DB = config.DATABASE_PATH

def init_db():
    os.makedirs(os.path.dirname(_DB), exist_ok=True)
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            channel_id INTEGER PRIMARY KEY,
            user_id INTEGER, staff_id INTEGER,
            panel_message_id INTEGER,
            created_at REAL, closed_at REAL,
            status TEXT DEFAULT 'open', close_reason TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL, level TEXT DEFAULT 'INFO', message TEXT
        );
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER, user_id INTEGER, username TEXT,
            categoria TEXT, status TEXT DEFAULT 'open',
            claimed_by INTEGER, opened_at REAL, closed_at REAL
        );
        CREATE TABLE IF NOT EXISTS warns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, username TEXT,
            mod_id INTEGER, mod_name TEXT,
            motivo TEXT, ts REAL
        );
        CREATE TABLE IF NOT EXISTS levels (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0, level INTEGER DEFAULT 0, messages INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS tags (
            name TEXT PRIMARY KEY,
            content TEXT, author TEXT, created_at REAL, uses INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS giveaways (
            message_id INTEGER PRIMARY KEY,
            channel_id INTEGER, premio TEXT,
            vincitori INTEGER, ends_at REAL,
            status TEXT DEFAULT 'active',
            host TEXT, winners TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS polls (
            message_id INTEGER PRIMARY KEY,
            channel_id INTEGER, domanda TEXT,
            opzioni TEXT, autore TEXT, status TEXT DEFAULT 'open'
        );
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, channel_id INTEGER,
            testo TEXT, at REAL, created_at REAL
        );
        CREATE TABLE IF NOT EXISTS reaction_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER, emoji TEXT, role_id INTEGER
        );
        CREATE TABLE IF NOT EXISTS autoroles (
            role_id INTEGER PRIMARY KEY
        );
        CREATE TABLE IF NOT EXISTS welcome_config (
            id INTEGER PRIMARY KEY DEFAULT 1,
            channel_id INTEGER DEFAULT 0,
            message TEXT DEFAULT 'Benvenuto {mention} in **{server}**! Sei il membro #{count}! 🎉'
        );
        CREATE TABLE IF NOT EXISTS goodbye_config (
            id INTEGER PRIMARY KEY DEFAULT 1,
            channel_id INTEGER DEFAULT 0,
            message TEXT DEFAULT '{name} ha lasciato **{server}**. 👋'
        );
        CREATE TABLE IF NOT EXISTS automod_config (
            id INTEGER PRIMARY KEY DEFAULT 1,
            enabled INTEGER DEFAULT 0,
            filter_links INTEGER DEFAULT 1,
            filter_spam INTEGER DEFAULT 1,
            spam_limit INTEGER DEFAULT 5,
            blacklist TEXT DEFAULT ''
        );
        INSERT OR IGNORE INTO welcome_config(id) VALUES(1);
        INSERT OR IGNORE INTO goodbye_config(id) VALUES(1);
        INSERT OR IGNORE INTO automod_config(id) VALUES(1);
        """)
        c.commit()

@contextmanager
def _conn():
    con = sqlite3.connect(_DB)
    con.row_factory = sqlite3.Row
    try: yield con
    finally: con.close()

# ── Events / Log ────────────────────────────────────────────────
def log_event(msg: str, level: str = "INFO"):
    with _conn() as c:
        c.execute("INSERT INTO events(ts,level,message) VALUES(?,?,?)", (time.time(), level, msg))
        c.commit()

def get_events(limit=100):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM events ORDER BY ts DESC LIMIT ?", (limit,))]

# ── Sessions (vocal support) ─────────────────────────────────────
def create_session(channel_id, user_id, staff_id, panel_msg_id):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO sessions(channel_id,user_id,staff_id,panel_message_id,created_at,status) VALUES(?,?,?,?,?,'open')",
                  (channel_id, user_id, staff_id, panel_msg_id, time.time()))
        c.commit()

def close_session_db(channel_id, reason=""):
    with _conn() as c:
        c.execute("UPDATE sessions SET status='closed',closed_at=?,close_reason=? WHERE channel_id=?",
                  (time.time(), reason, channel_id))
        c.commit()

def get_open_sessions():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM sessions WHERE status='open'")]

def get_all_sessions(limit=50):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,))]

# ── Tickets ──────────────────────────────────────────────────────
def create_ticket(channel_id, user_id, username, categoria):
    with _conn() as c:
        c.execute("INSERT INTO tickets(channel_id,user_id,username,categoria,opened_at) VALUES(?,?,?,?,?)",
                  (channel_id, user_id, username, categoria, time.time()))
        c.commit()
        return c.execute("SELECT last_insert_rowid()").fetchone()[0]

def close_ticket_db(channel_id):
    with _conn() as c:
        c.execute("UPDATE tickets SET status='closed',closed_at=? WHERE channel_id=?", (time.time(), channel_id))
        c.commit()

def get_tickets(status=None, limit=100):
    with _conn() as c:
        if status:
            return [dict(r) for r in c.execute("SELECT * FROM tickets WHERE status=? ORDER BY opened_at DESC LIMIT ?", (status, limit))]
        return [dict(r) for r in c.execute("SELECT * FROM tickets ORDER BY opened_at DESC LIMIT ?", (limit,))]

def claim_ticket_db(channel_id, mod_id):
    with _conn() as c:
        c.execute("UPDATE tickets SET claimed_by=? WHERE channel_id=?", (mod_id, channel_id))
        c.commit()

# ── Warns ────────────────────────────────────────────────────────
def add_warn(user_id, username, mod_id, mod_name, motivo):
    with _conn() as c:
        c.execute("INSERT INTO warns(user_id,username,mod_id,mod_name,motivo,ts) VALUES(?,?,?,?,?,?)",
                  (user_id, username, mod_id, mod_name, motivo, time.time()))
        c.commit()

def get_warns(user_id=None):
    with _conn() as c:
        if user_id:
            return [dict(r) for r in c.execute("SELECT * FROM warns WHERE user_id=? ORDER BY ts DESC", (user_id,))]
        return [dict(r) for r in c.execute("SELECT * FROM warns ORDER BY ts DESC LIMIT 200")]

def clear_warns(user_id):
    with _conn() as c:
        c.execute("DELETE FROM warns WHERE user_id=?", (user_id,))
        c.commit()

# ── Levels ───────────────────────────────────────────────────────
def get_user_level(user_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM levels WHERE user_id=?", (user_id,)).fetchone()
        return dict(r) if r else {"user_id": user_id, "xp": 0, "level": 0, "messages": 0}

def update_user_level(user_id, xp, level, messages):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO levels(user_id,xp,level,messages) VALUES(?,?,?,?)",
                  (user_id, xp, level, messages))
        c.commit()

def get_leaderboard(limit=20):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM levels ORDER BY xp DESC LIMIT ?", (limit,))]

def set_user_xp(user_id, xp, level):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO levels(user_id,xp,level,messages) VALUES(?,?,?,(SELECT COALESCE(messages,0) FROM levels WHERE user_id=?))",
                  (user_id, xp, level, user_id))
        c.commit()

# ── Tags ─────────────────────────────────────────────────────────
def create_tag(name, content, author):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO tags(name,content,author,created_at,uses) VALUES(?,?,?,?,0)",
                  (name, content, author, time.time()))
        c.commit()

def get_tag(name):
    with _conn() as c:
        r = c.execute("SELECT * FROM tags WHERE name=?", (name,)).fetchone()
        if r:
            c.execute("UPDATE tags SET uses=uses+1 WHERE name=?", (name,))
            c.commit()
        return dict(r) if r else None

def get_all_tags():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM tags ORDER BY uses DESC")]

def delete_tag(name):
    with _conn() as c:
        c.execute("DELETE FROM tags WHERE name=?", (name,))
        c.commit()

# ── Giveaways ────────────────────────────────────────────────────
def create_giveaway(message_id, channel_id, premio, vincitori, ends_at, host):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO giveaways(message_id,channel_id,premio,vincitori,ends_at,host) VALUES(?,?,?,?,?,?)",
                  (message_id, channel_id, premio, vincitori, ends_at, host))
        c.commit()

def end_giveaway(message_id, winners_str):
    with _conn() as c:
        c.execute("UPDATE giveaways SET status='ended',winners=? WHERE message_id=?", (winners_str, message_id))
        c.commit()

def get_active_giveaways():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM giveaways WHERE status='active'")]

def get_all_giveaways():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM giveaways ORDER BY ends_at DESC LIMIT 50")]

# ── Polls ────────────────────────────────────────────────────────
def create_poll(message_id, channel_id, domanda, opzioni_json, autore):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO polls(message_id,channel_id,domanda,opzioni,autore) VALUES(?,?,?,?,?)",
                  (message_id, channel_id, domanda, opzioni_json, autore))
        c.commit()

def close_poll(message_id):
    with _conn() as c:
        c.execute("UPDATE polls SET status='closed' WHERE message_id=?", (message_id,))
        c.commit()

def get_all_polls():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM polls ORDER BY message_id DESC LIMIT 50")]

# ── Reminders ────────────────────────────────────────────────────
def add_reminder(user_id, channel_id, testo, at):
    with _conn() as c:
        c.execute("INSERT INTO reminders(user_id,channel_id,testo,at,created_at) VALUES(?,?,?,?,?)",
                  (user_id, channel_id, testo, at, time.time()))
        c.commit()

def get_due_reminders():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM reminders WHERE at<=?", (time.time(),))]

def delete_reminder(rid):
    with _conn() as c:
        c.execute("DELETE FROM reminders WHERE id=?", (rid,))
        c.commit()

def get_user_reminders(user_id):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM reminders WHERE user_id=? ORDER BY at", (user_id,))]

# ── Reaction Roles ───────────────────────────────────────────────
def add_reaction_role(message_id, emoji, role_id):
    with _conn() as c:
        c.execute("INSERT INTO reaction_roles(message_id,emoji,role_id) VALUES(?,?,?)", (message_id, emoji, role_id))
        c.commit()

def remove_reaction_role(message_id, emoji):
    with _conn() as c:
        c.execute("DELETE FROM reaction_roles WHERE message_id=? AND emoji=?", (message_id, emoji))
        c.commit()

def get_reaction_role(message_id, emoji):
    with _conn() as c:
        r = c.execute("SELECT * FROM reaction_roles WHERE message_id=? AND emoji=?", (message_id, emoji)).fetchone()
        return dict(r) if r else None

def get_all_reaction_roles():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM reaction_roles")]

# ── Autoroles ────────────────────────────────────────────────────
def add_autorole(role_id):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO autoroles(role_id) VALUES(?)", (role_id,))
        c.commit()

def remove_autorole(role_id):
    with _conn() as c:
        c.execute("DELETE FROM autoroles WHERE role_id=?", (role_id,))
        c.commit()

def get_autoroles():
    with _conn() as c:
        return [r["role_id"] for r in c.execute("SELECT role_id FROM autoroles")]

# ── Welcome / Goodbye ────────────────────────────────────────────
def get_welcome():
    with _conn() as c:
        return dict(c.execute("SELECT * FROM welcome_config WHERE id=1").fetchone())

def set_welcome(channel_id, message):
    with _conn() as c:
        c.execute("UPDATE welcome_config SET channel_id=?,message=? WHERE id=1", (channel_id, message))
        c.commit()

def get_goodbye():
    with _conn() as c:
        return dict(c.execute("SELECT * FROM goodbye_config WHERE id=1").fetchone())

def set_goodbye(channel_id, message):
    with _conn() as c:
        c.execute("UPDATE goodbye_config SET channel_id=?,message=? WHERE id=1", (channel_id, message))
        c.commit()

# ── Automod ──────────────────────────────────────────────────────
def get_automod():
    with _conn() as c:
        return dict(c.execute("SELECT * FROM automod_config WHERE id=1").fetchone())

def set_automod(**kwargs):
    with _conn() as c:
        for k, v in kwargs.items():
            c.execute(f"UPDATE automod_config SET {k}=? WHERE id=1", (v,))
        c.commit()
