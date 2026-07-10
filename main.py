"""
ParityMC — Bot Unificato
Avvio: python main.py
"""
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import config, database, session_manager, bot_logger
from matchmaking import Matchmaker
from web.app import start_web_thread

COGS = [
    "cogs.tickets", "cogs.partnership", "cogs.moderation",
    "cogs.automod", "cogs.welcome", "cogs.roles", "cogs.levels",
    "cogs.tags", "cogs.giveaway", "cogs.polls", "cogs.reminders",
    "cogs.stats", "cogs.vocal_support",
]

intents = discord.Intents.all()

class ParityMCBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.PREFIX, intents=intents, help_command=None)
        self.matchmaker = None

    async def setup_hook(self):
        database.init_db()
        mm = Matchmaker(session_manager)
        session_manager.set_matchmaker(mm)
        self.matchmaker = mm

        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"  ✅ {cog}")
            except Exception as e:
                print(f"  ❌ {cog}: {e}")

        guild = discord.Object(id=config.GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        print(f"\n🔄 {len(synced)} comandi slash sincronizzati")

    async def on_ready(self):
        guild = self.get_guild(config.GUILD_ID)
        if guild:
            wc = guild.get_channel(config.WAITING_CHANNEL_ID)
            sc = guild.get_channel(config.STAFF_CHANNEL_ID)
            if wc:
                for m in wc.members: self.matchmaker.add_waiting(m.id)
            if sc:
                for m in sc.members:
                    if config.SUPPORT_ROLE_ID and any(r.id == config.SUPPORT_ROLE_ID for r in m.roles):
                        self.matchmaker.add_staff(m.id)
            await session_manager.recover_sessions(self)
            await self.matchmaker.try_match(self)

        from cogs.vocal_views import ControlPanelView
        self.add_view(ControlPanelView(0))  # dummy per persistenza

        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="ParityMC ⚖️"))

        print(f"\n{'='*48}")
        print(f"  ✅ {self.user} ONLINE")
        print(f"  Server  : {config.GUILD_ID}")
        print(f"  Prefisso: {config.PREFIX}")
        print(f"  Web     : http://{config.WEB_HOST}:{config.WEB_PORT}")
        print(f"{'='*48}\n")
        await bot_logger.log(self, f"✅ Bot avviato: {self.user}", "OK")

# ── Filtri Jinja2 ─────────────────────────────────────────────────
from web.app import app as flask_app
import time as _time

@flask_app.template_filter("format_ts")
def format_ts(ts):
    try: return datetime.fromtimestamp(int(ts)).strftime("%d/%m/%Y %H:%M")
    except: return "—"

@flask_app.template_filter("format_dur")
def format_dur(ts):
    try:
        from utils import format_duration, now
        return format_duration(now() - float(ts))
    except: return "—"

# ── Comandi prefisso extra ────────────────────────────────────────
bot = ParityMCBot()

@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync_cmd(ctx):
    guild = discord.Object(id=config.GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    await ctx.send(f"✅ Sincronizzati {len(synced)} comandi slash!")

@bot.command(name="ping")
async def ping_cmd(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency*1000)}ms`")

@bot.command(name="help")
async def help_cmd(ctx):
    e = discord.Embed(title="📚 ParityMC — Comandi",
                      color=discord.Color.from_rgb(0,180,120), timestamp=datetime.utcnow())
    e.add_field(name="🎫 Ticket", value="`/ticket-panel` `/chiudi` `/claim` `/aggiungi` `/rimuovi` `/rename` `/lista-ticket`", inline=False)
    e.add_field(name="🤝 Partnership", value="`/partnership` `/modifica-partnership` `/elimina-partnership`", inline=False)
    e.add_field(name="🛡️ Moderazione", value="`/ban` `/kick` `/mute` `/unmute` `/warn` `/warns` `/clearwarn` `/purge` `/slowmode` `/lock` `/unlock`", inline=False)
    e.add_field(name="🤖 Automod", value="`/automod-setup` `/automod-parole` `/automod-status`", inline=False)
    e.add_field(name="👋 Welcome", value="`/welcome-setup` `/goodbye-setup` `/welcome-test`", inline=False)
    e.add_field(name="🎭 Ruoli", value="`/reaction-role` `/autorole` `/ruolo-add` `/ruolo-remove`", inline=False)
    e.add_field(name="⭐ Livelli", value="`/rank` `/leaderboard` `/setxp` `/level-channel`", inline=False)
    e.add_field(name="🏷️ Tag", value="`/tag-crea` `/tag` `/tag-lista` `/tag-elimina`", inline=False)
    e.add_field(name="🎉 Giveaway", value="`/giveaway-start` `/giveaway-end` `/giveaway-reroll`", inline=False)
    e.add_field(name="📊 Sondaggi", value="`/poll` `/poll-fine`", inline=False)
    e.add_field(name="⏰ Reminder", value="`/reminder` `/reminder-lista` `/reminder-cancella`", inline=False)
    e.add_field(name="🎙️ Supporto Vocale", value="`/status-supporto` `/sessioni` `/chiudi-sessione` `/help-supporto`", inline=False)
    e.add_field(name="📈 Stats", value="`/stats` `/serverinfo` `/userinfo` `/botinfo`", inline=False)
    e.add_field(name="🌐 Web Panel", value=f"`http://{config.WEB_HOST}:{config.WEB_PORT}`", inline=False)
    e.set_footer(text=f"ParityMC • Prefisso: {config.PREFIX}")
    await ctx.send(embed=e)

if __name__ == "__main__":
    start_web_thread(bot)
    bot.run(config.BOT_TOKEN)
