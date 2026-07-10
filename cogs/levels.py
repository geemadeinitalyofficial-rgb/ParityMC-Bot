import discord
from discord.ext import commands
from discord import app_commands
import random, os
from datetime import datetime
from cogs.db import load, save

LEVEL_CHANNEL_ID = int(os.getenv("LEVEL_CHANNEL_ID", "0"))
XP_COOLDOWN = 60  # secondi tra un guadagno XP e l'altro
xp_cd = {}  # {user_id: last_xp_time}

def get_db():
    db = load("levels")
    if "users" not in db: db["users"] = {}
    if "level_channel" not in db: db["level_channel"] = LEVEL_CHANNEL_ID
    return db

def xp_per_level(level: int) -> int:
    return 100 * (level ** 2) + 100

def calc_level(xp: int) -> int:
    level = 0
    while xp >= xp_per_level(level + 1):
        xp -= xp_per_level(level + 1)
        level += 1
    return level

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user(self, db, uid):
        if uid not in db["users"]:
            db["users"][uid] = {"xp": 0, "level": 0, "messages": 0}
        return db["users"][uid]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild: return
        uid = str(message.author.id)
        now = datetime.utcnow().timestamp()
        if uid in xp_cd and now - xp_cd[uid] < XP_COOLDOWN: return
        xp_cd[uid] = now

        db   = get_db()
        user = self.get_user(db, uid)
        user["messages"] += 1
        gained = random.randint(15, 30)
        user["xp"] += gained
        old_lv = user["level"]
        user["level"] = calc_level(user["xp"])

        if user["level"] > old_lv:
            save("levels", db)
            ch_id = db.get("level_channel") or (message.channel.id)
            ch    = message.guild.get_channel(ch_id) or message.channel
            embed = discord.Embed(
                title="⭐ Level Up!",
                description=f"{message.author.mention} è salito al **livello {user['level']}**! 🎉",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            await ch.send(embed=embed)
        else:
            save("levels", db)

    @app_commands.command(name="rank", description="Mostra il tuo livello e XP")
    @app_commands.describe(utente="Utente (lascia vuoto per te stesso)")
    async def slash_rank(self, interaction: discord.Interaction, utente: discord.Member = None):
        utente = utente or interaction.user
        db     = get_db()
        user   = self.get_user(db, str(utente.id))
        lv     = user["level"]
        xp     = user["xp"]
        needed = xp_per_level(lv + 1)
        bar_len = 20
        filled  = int((xp % needed) / needed * bar_len) if needed else bar_len
        bar     = "█" * filled + "░" * (bar_len - filled)

        embed = discord.Embed(title=f"⭐ Rank di {utente.display_name}", color=discord.Color.gold())
        embed.set_thumbnail(url=utente.display_avatar.url)
        embed.add_field(name="Livello", value=f"**{lv}**", inline=True)
        embed.add_field(name="XP", value=f"**{xp}**", inline=True)
        embed.add_field(name="Messaggi", value=f"**{user['messages']}**", inline=True)
        embed.add_field(name=f"Progresso → Lv {lv+1}", value=f"`{bar}` {xp % needed}/{needed} XP", inline=False)
        embed.set_footer(text="ParityMC • Leveling")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Mostra la classifica XP del server")
    async def slash_lb(self, interaction: discord.Interaction):
        db   = get_db()
        top  = sorted(db["users"].items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
        embed = discord.Embed(title="🏆 Classifica XP — ParityMC", color=discord.Color.gold(), timestamp=datetime.utcnow())
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, data) in enumerate(top):
            m = interaction.guild.get_member(int(uid))
            name = m.display_name if m else f"Utente {uid}"
            prefix = medals[i] if i < 3 else f"`#{i+1}`"
            embed.add_field(name=f"{prefix} {name}", value=f"Lv **{data['level']}** • **{data['xp']}** XP", inline=False)
        embed.set_footer(text="ParityMC • Leveling")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setxp", description="[ADMIN] Imposta l'XP di un utente")
    @app_commands.describe(utente="Utente", xp="Quantità XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setxp(self, interaction: discord.Interaction, utente: discord.Member, xp: int):
        db = get_db()
        u  = self.get_user(db, str(utente.id))
        u["xp"]    = xp
        u["level"] = calc_level(xp)
        save("levels", db)
        await interaction.response.send_message(f"✅ XP di {utente.mention} impostato a **{xp}** (Lv {u['level']}).", ephemeral=True)

    @app_commands.command(name="level-channel", description="[ADMIN] Imposta il canale per i level up")
    @app_commands.describe(canale="Canale dove inviare i messaggi di level up")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_lvchannel(self, interaction: discord.Interaction, canale: discord.TextChannel):
        db = get_db()
        db["level_channel"] = canale.id
        save("levels", db)
        await interaction.response.send_message(f"✅ Messaggi level up inviati in {canale.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Levels(bot))
