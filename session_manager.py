import asyncio
import discord
import config, database, utils, bot_logger

ACTIVE_SESSIONS = {}
_matchmaker = None

def set_matchmaker(mm): global _matchmaker; _matchmaker = mm

async def create_session(bot, user: discord.Member, staff: discord.Member):
    guild = user.guild
    cat   = guild.get_channel(config.SUPPORT_CATEGORY_ID)
    n     = utils.next_free_number(cat, config.CHANNEL_NAME_PREFIX)
    name  = f"{config.CHANNEL_NAME_PREFIX} {n}"
    ow = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),
        guild.me:   discord.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True, move_members=True),
        user:       discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        staff:      discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
    }
    ch = await guild.create_voice_channel(name=name, category=cat, overwrites=ow)
    try:
        if user.voice:  await user.move_to(ch)
        if staff.voice: await staff.move_to(ch)
    except: pass

    from cogs.vocal_views import ControlPanelView
    embed = discord.Embed(title="🟢 Sessione supporto attiva", color=discord.Color.green(),
                          description="Usa i pulsanti per gestire questa sessione.")
    embed.add_field(name="Utente", value=user.mention, inline=True)
    embed.add_field(name="Staff",  value=staff.mention, inline=True)
    view = ControlPanelView(ch.id)
    msg  = await ch.send(content=f"{user.mention} {staff.mention}", embed=embed, view=view)

    database.create_session(ch.id, user.id, staff.id, msg.id)
    ACTIVE_SESSIONS[ch.id] = {
        "user_id": user.id, "staff_id": staff.id,
        "created_at": utils.now(), "no_auto_close": False, "empty_task": None
    }
    await bot_logger.log(bot, f"🟢 Sessione: {user} ↔ {staff} in #{name}", "OK")
    return ch

async def close_session(bot, channel_id, reason="Chiusa"):
    s = ACTIVE_SESSIONS.pop(channel_id, None)
    if s:
        if s.get("empty_task"): s["empty_task"].cancel()
        if _matchmaker: _matchmaker.release_staff(s["staff_id"])
    database.close_session_db(channel_id, reason)
    ch = bot.get_channel(channel_id)
    if ch:
        try: await ch.delete(reason=reason)
        except: pass
    await bot_logger.log(bot, f"🔴 Sessione chiusa ({channel_id}): {reason}")

def notify_member_joined(channel_id):
    s = ACTIVE_SESSIONS.get(channel_id)
    if s and s.get("empty_task") and not s["empty_task"].done():
        s["empty_task"].cancel(); s["empty_task"] = None

def notify_channel_empty(bot, channel_id):
    s = ACTIVE_SESSIONS.get(channel_id)
    if not s or s.get("no_auto_close"): return
    if s.get("empty_task") and not s["empty_task"].done(): return
    s["empty_task"] = asyncio.create_task(_countdown(bot, channel_id))

async def _countdown(bot, channel_id):
    try: await asyncio.sleep(config.EMPTY_CHANNEL_TIMEOUT)
    except asyncio.CancelledError: return
    s = ACTIVE_SESSIONS.get(channel_id)
    if not s or s.get("no_auto_close"): return
    ch = bot.get_channel(channel_id)
    if ch and not [m for m in ch.members if not m.bot]:
        await close_session(bot, channel_id, "Canale vuoto - chiusura automatica")

async def recover_sessions(bot):
    guild = bot.get_guild(config.GUILD_ID)
    if not guild: return
    from cogs.vocal_views import ControlPanelView
    for s in database.get_open_sessions():
        ch = guild.get_channel(s["channel_id"])
        if not ch:
            database.close_session_db(s["channel_id"], "Orfana al riavvio"); continue
        ACTIVE_SESSIONS[s["channel_id"]] = {
            "user_id": s["user_id"], "staff_id": s["staff_id"],
            "created_at": s["created_at"], "no_auto_close": False, "empty_task": None
        }
        if _matchmaker: _matchmaker.busy_staff.add(s["staff_id"])
        bot.add_view(ControlPanelView(s["channel_id"]), message_id=s["panel_message_id"])
        if not [m for m in ch.members if not m.bot]:
            notify_channel_empty(bot, s["channel_id"])
