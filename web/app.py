"""
Web Panel — ParityMC
Avviato in un thread separato da main.py
Accessibile su http://127.0.0.1:8080
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import threading, time, json
import config, database

app = Flask(__name__)
app.secret_key = config.WEB_SECRET_KEY

# riferimento al bot Discord (impostato da main.py)
_bot = None
def set_bot(bot): global _bot; _bot = bot

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── Auth ─────────────────────────────────────────────────────────
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == config.WEB_USERNAME and request.form["password"] == config.WEB_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Credenziali errate.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Dashboard ────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    guild = _bot.get_guild(config.GUILD_ID) if _bot else None
    import session_manager
    stats = {
        "members":      guild.member_count if guild else 0,
        "bots":         sum(1 for m in guild.members if m.bot) if guild else 0,
        "channels":     len(guild.channels) if guild else 0,
        "roles":        len(guild.roles) if guild else 0,
        "tickets_open": len(database.get_tickets("open")),
        "sessions":     len(session_manager.ACTIVE_SESSIONS),
        "warns":        len(database.get_warns()),
        "giveaways":    len(database.get_active_giveaways()),
    }
    events = database.get_events(20)
    return render_template("dashboard.html", stats=stats, events=events, guild=guild)

# ── Tickets ──────────────────────────────────────────────────────
@app.route("/tickets")
@login_required
def tickets():
    status = request.args.get("status", "open")
    tickets = database.get_tickets(status if status != "all" else None)
    return render_template("tickets.html", tickets=tickets, status=status)

@app.route("/tickets/close/<int:channel_id>", methods=["POST"])
@login_required
def close_ticket(channel_id):
    database.close_ticket_db(channel_id)
    if _bot:
        import asyncio
        ch = _bot.get_channel(channel_id)
        if ch:
            asyncio.run_coroutine_threadsafe(ch.delete(reason="Chiuso dal web panel"), _bot.loop)
    flash("Ticket chiuso.", "success")
    return redirect(url_for("tickets"))

# ── Sessioni vocali ───────────────────────────────────────────────
@app.route("/sessions")
@login_required
def sessions():
    import session_manager
    active = [{"channel_id": cid, **s} for cid, s in session_manager.ACTIVE_SESSIONS.items()]
    history = database.get_all_sessions(50)
    return render_template("sessions.html", active=active, history=history)

@app.route("/sessions/close/<int:channel_id>", methods=["POST"])
@login_required
def close_session_web(channel_id):
    if _bot:
        import asyncio, session_manager
        asyncio.run_coroutine_threadsafe(
            session_manager.close_session(_bot, channel_id, "Chiusa dal web panel"), _bot.loop)
    flash("Sessione chiusa.", "success")
    return redirect(url_for("sessions"))

# ── Membri ───────────────────────────────────────────────────────
@app.route("/members")
@login_required
def members():
    guild = _bot.get_guild(config.GUILD_ID) if _bot else None
    mlist = []
    if guild:
        for m in sorted(guild.members, key=lambda x: x.display_name):
            mlist.append({
                "id": m.id, "name": str(m), "display": m.display_name,
                "bot": m.bot, "avatar": str(m.display_avatar.url),
                "roles": [r.name for r in m.roles if r.name != "@everyone"],
                "joined": m.joined_at.strftime("%d/%m/%Y") if m.joined_at else "N/A",
                "top_role": m.top_role.name,
            })
    return render_template("members.html", members=mlist, guild=guild)

# ── Ruoli ────────────────────────────────────────────────────────
@app.route("/roles")
@login_required
def roles():
    guild = _bot.get_guild(config.GUILD_ID) if _bot else None
    rlist = []
    if guild:
        for r in sorted(guild.roles, reverse=True):
            if r.name == "@everyone": continue
            rlist.append({"id": r.id, "name": r.name, "color": str(r.color),
                          "members": len(r.members), "mentionable": r.mentionable,
                          "hoist": r.hoist, "position": r.position})
    autoroles = database.get_autoroles()
    rr = database.get_all_reaction_roles()
    return render_template("roles.html", roles=rlist, autoroles=autoroles, reaction_roles=rr, guild=guild)

@app.route("/roles/autorole/add", methods=["POST"])
@login_required
def add_autorole():
    role_id = int(request.form["role_id"])
    database.add_autorole(role_id)
    flash("Autorole aggiunto.", "success")
    return redirect(url_for("roles"))

@app.route("/roles/autorole/remove/<int:role_id>", methods=["POST"])
@login_required
def remove_autorole(role_id):
    database.remove_autorole(role_id)
    flash("Autorole rimosso.", "success")
    return redirect(url_for("roles"))

@app.route("/roles/rr/remove/<int:rr_id>", methods=["POST"])
@login_required
def remove_rr(rr_id):
    import sqlite3
    with database._conn() as c:
        c.execute("DELETE FROM reaction_roles WHERE id=?", (rr_id,))
        c.commit()
    flash("Reaction role rimosso.", "success")
    return redirect(url_for("roles"))

# ── Log ──────────────────────────────────────────────────────────
@app.route("/logs")
@login_required
def logs():
    level  = request.args.get("level", "")
    events = database.get_events(200)
    if level: events = [e for e in events if e["level"] == level]
    return render_template("logs.html", events=events, level=level)

# ── Giveaway ─────────────────────────────────────────────────────
@app.route("/giveaways")
@login_required
def giveaways():
    all_gw = database.get_all_giveaways()
    return render_template("giveaways.html", giveaways=all_gw)

@app.route("/giveaways/end/<int:message_id>", methods=["POST"])
@login_required
def end_giveaway_web(message_id):
    database.end_giveaway(message_id, "")
    flash("Giveaway terminato.", "success")
    return redirect(url_for("giveaways"))

# ── Sondaggi ─────────────────────────────────────────────────────
@app.route("/polls")
@login_required
def polls():
    all_polls = database.get_all_polls()
    return render_template("polls.html", polls=all_polls)

# ── Configurazione ────────────────────────────────────────────────
@app.route("/config", methods=["GET","POST"])
@login_required
def bot_config():
    guild = _bot.get_guild(config.GUILD_ID) if _bot else None
    channels = list(guild.text_channels) if guild else []
    v_channels = list(guild.voice_channels) if guild else []
    all_roles = list(guild.roles) if guild else []
    welcome  = database.get_welcome()
    goodbye  = database.get_goodbye()
    automod  = database.get_automod()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "welcome":
            database.set_welcome(int(request.form["channel_id"]), request.form["message"])
            flash("✅ Benvenuto aggiornato.", "success")
        elif action == "goodbye":
            database.set_goodbye(int(request.form["channel_id"]), request.form["message"])
            flash("✅ Addio aggiornato.", "success")
        elif action == "automod":
            database.set_automod(
                enabled=1 if request.form.get("enabled") else 0,
                filter_links=1 if request.form.get("filter_links") else 0,
                filter_spam=1 if request.form.get("filter_spam") else 0,
                spam_limit=int(request.form.get("spam_limit", 5)),
                blacklist=request.form.get("blacklist", "")
            )
            flash("✅ Automod aggiornato.", "success")
        return redirect(url_for("bot_config"))

    return render_template("config.html",
        channels=channels, v_channels=v_channels, roles=all_roles,
        welcome=welcome, goodbye=goodbye, automod=automod, guild=guild)

# ── Livelli ───────────────────────────────────────────────────────
@app.route("/levels")
@login_required
def levels():
    lb = database.get_leaderboard(50)
    guild = _bot.get_guild(config.GUILD_ID) if _bot else None
    enriched = []
    for row in lb:
        m = guild.get_member(row["user_id"]) if guild else None
        enriched.append({**row, "name": str(m) if m else f"ID:{row['user_id']}",
                         "avatar": str(m.display_avatar.url) if m else ""})
    return render_template("levels.html", leaderboard=enriched)

# ── API JSON (per grafici live) ───────────────────────────────────
@app.route("/api/stats")
@login_required
def api_stats():
    import session_manager
    guild = _bot.get_guild(config.GUILD_ID) if _bot else None
    return jsonify({
        "members": guild.member_count if guild else 0,
        "sessions": len(session_manager.ACTIVE_SESSIONS),
        "tickets_open": len(database.get_tickets("open")),
        "latency": round(_bot.latency * 1000) if _bot else 0,
    })

@app.route("/api/logs")
@login_required
def api_logs():
    return jsonify(database.get_events(50))

def run_web(bot):
    set_bot(bot)
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=False, use_reloader=False)

def start_web_thread(bot):
    t = threading.Thread(target=run_web, args=(bot,), daemon=True)
    t.start()
    print(f"🌐 Web panel avviato su http://{config.WEB_HOST}:{config.WEB_PORT}")
