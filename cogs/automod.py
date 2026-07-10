import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import re
from cogs.db import load, save

def get_cfg():
    db = load("automod")
    if "config" not in db:
        db["config"] = {"enabled": False, "filter_parole": True, "filter_link": True, "filter_spam": True,
                        "parole": ["badword1", "badword2"], "whitelist_channels": [], "spam_limit": 5}
    return db

LINK_PATTERN = re.compile(r"https?://\S+|discord\.gg/\S+|\.gg/\S+", re.IGNORECASE)
spam_tracker = {}  # {user_id: [timestamps]}

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild: return
        if not isinstance(message.channel, discord.TextChannel): return
        db  = get_cfg()
        cfg = db["config"]
        if not cfg["enabled"]: return
        if message.channel.id in cfg.get("whitelist_channels", []): return
        if message.author.guild_permissions.manage_messages: return

        content = message.content.lower()

        # Filtro parole
        if cfg["filter_parole"]:
            for parola in cfg["parole"]:
                if parola.lower() in content:
                    await message.delete()
                    w = await message.channel.send(f"⚠️ {message.author.mention} Messaggio rimosso per linguaggio inappropriato.", delete_after=5)
                    return

        # Filtro link
        if cfg["filter_link"] and LINK_PATTERN.search(message.content):
            await message.delete()
            await message.channel.send(f"🔗 {message.author.mention} I link non sono permessi qui.", delete_after=5)
            return

        # Anti-spam
        if cfg["filter_spam"]:
            uid = message.author.id
            now = datetime.utcnow()
            if uid not in spam_tracker: spam_tracker[uid] = []
            spam_tracker[uid] = [t for t in spam_tracker[uid] if (now - t).seconds < 5]
            spam_tracker[uid].append(now)
            if len(spam_tracker[uid]) >= cfg.get("spam_limit", 5):
                await message.delete()
                until = discord.utils.utcnow() + timedelta(minutes=1)
                try:
                    await message.author.timeout(until, reason="Automod: spam rilevato")
                except Exception:
                    pass
                await message.channel.send(f"🚫 {message.author.mention} Rilevato spam. Timeout di 1 minuto.", delete_after=8)
                spam_tracker[uid] = []

    @app_commands.command(name="automod-setup", description="[ADMIN] Attiva/disattiva l'automod")
    @app_commands.describe(attivo="True = attiva, False = disattiva")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_setup(self, interaction: discord.Interaction, attivo: bool):
        db = get_cfg()
        db["config"]["enabled"] = attivo
        save("automod", db)
        stato = "✅ **Attivato**" if attivo else "❌ **Disattivato**"
        await interaction.response.send_message(f"🤖 Automod {stato}.")

    @app_commands.command(name="automod-parole", description="[ADMIN] Aggiunge una parola alla blacklist automod")
    @app_commands.describe(parola="Parola da aggiungere o rimuovere", azione="add o remove")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_parole(self, interaction: discord.Interaction, parola: str, azione: str = "add"):
        db = get_cfg()
        if azione == "add":
            if parola not in db["config"]["parole"]:
                db["config"]["parole"].append(parola)
            msg = f"✅ `{parola}` aggiunta alla blacklist."
        else:
            db["config"]["parole"] = [p for p in db["config"]["parole"] if p != parola]
            msg = f"✅ `{parola}` rimossa dalla blacklist."
        save("automod", db)
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="automod-status", description="Mostra lo stato e la configurazione dell'automod")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_status(self, interaction: discord.Interaction):
        db  = get_cfg()
        cfg = db["config"]
        embed = discord.Embed(title="🤖 Automod Status", color=discord.Color.green() if cfg["enabled"] else discord.Color.red())
        embed.add_field(name="Stato",        value="✅ Attivo" if cfg["enabled"] else "❌ Disattivo", inline=True)
        embed.add_field(name="Filtro link",  value="✅" if cfg["filter_link"]   else "❌", inline=True)
        embed.add_field(name="Anti-spam",    value="✅" if cfg["filter_spam"]   else "❌", inline=True)
        embed.add_field(name="Spam limit",   value=f"{cfg['spam_limit']} msg/5s", inline=True)
        embed.add_field(name="Parole bloccate", value=", ".join(f"`{p}`" for p in cfg["parole"]) or "Nessuna", inline=False)
        embed.set_footer(text="ParityMC • Automod")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Automod(bot))
