import discord
from discord.ext import commands
from discord import app_commands
import asyncio, random
from datetime import datetime, timedelta
from cogs.db import load, save

def get_db():
    db = load("giveaways")
    if "giveaways" not in db: db["giveaways"] = {}
    return db

def parse_duration(s: str) -> int:
    """Converte '1h30m', '2d', '45m' in secondi"""
    total = 0
    num   = ""
    for c in s:
        if c.isdigit(): num += c
        elif c == "d" and num: total += int(num) * 86400; num = ""
        elif c == "h" and num: total += int(num) * 3600;  num = ""
        elif c == "m" and num: total += int(num) * 60;    num = ""
        elif c == "s" and num: total += int(num);          num = ""
    return total

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_giveaways())

    async def check_giveaways(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            db  = get_db()
            now = datetime.utcnow().timestamp()
            for gid, g in list(db["giveaways"].items()):
                if g["status"] == "active" and now >= g["ends_at"]:
                    await self.conclude(gid, g)
            await asyncio.sleep(10)

    async def conclude(self, gid: str, g: dict):
        db = get_db()
        if db["giveaways"].get(gid, {}).get("status") != "active": return

        ch  = self.bot.get_channel(g["channel_id"])
        if not ch: return
        try:
            msg = await ch.fetch_message(g["message_id"])
        except Exception:
            return

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        partecipanti = []
        if reaction:
            async for user in reaction.users():
                if not user.bot:
                    partecipanti.append(user)

        vincitori = random.sample(partecipanti, min(g["vincitori"], len(partecipanti))) if partecipanti else []

        embed = discord.Embed(
            title=f"🎉 Giveaway Concluso — {g['premio']}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        if vincitori:
            embed.description = f"🏆 **Vincitori:** {', '.join(v.mention for v in vincitori)}\n\n🎁 **Premio:** {g['premio']}"
            await ch.send(f"🎉 Congratulazioni {', '.join(v.mention for v in vincitori)}! Hai vinto **{g['premio']}**!")
        else:
            embed.description = "❌ Nessun partecipante valido."
        embed.set_footer(text="ParityMC • Giveaway")
        await msg.edit(embed=embed)

        db["giveaways"][gid]["status"]   = "ended"
        db["giveaways"][gid]["winners"]  = [v.id for v in vincitori]
        save("giveaways", db)

    @app_commands.command(name="giveaway-start", description="[STAFF] Avvia un giveaway")
    @app_commands.describe(durata="Durata (es: 1h30m, 2d, 45m)", vincitori="Numero di vincitori", premio="Premio del giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_start(self, interaction: discord.Interaction, durata: str, vincitori: int, premio: str):
        secondi = parse_duration(durata)
        if secondi <= 0:
            return await interaction.response.send_message("❌ Durata non valida. Usa es: `1h`, `30m`, `2d`.", ephemeral=True)

        ends_at = datetime.utcnow() + timedelta(seconds=secondi)
        embed   = discord.Embed(
            title=f"🎉 GIVEAWAY — {premio}",
            description=f"Reagisci con 🎉 per partecipare!\n\n🏆 **Vincitori:** {vincitori}\n⏰ **Fine:** <t:{int(ends_at.timestamp())}:R>",
            color=discord.Color.gold(),
            timestamp=ends_at
        )
        embed.set_footer(text=f"Termina il • {ends_at.strftime('%d/%m/%Y %H:%M')} UTC")
        await interaction.response.send_message("✅ Giveaway avviato!", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("🎉")

        db = get_db()
        db["giveaways"][str(msg.id)] = {
            "message_id": msg.id, "channel_id": interaction.channel.id,
            "premio": premio, "vincitori": vincitori,
            "ends_at": ends_at.timestamp(), "status": "active",
            "host": str(interaction.user), "winners": []
        }
        save("giveaways", db)

    @app_commands.command(name="giveaway-end", description="[STAFF] Termina subito un giveaway")
    @app_commands.describe(message_id="ID del messaggio giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_end(self, interaction: discord.Interaction, message_id: str):
        db = get_db()
        if message_id not in db["giveaways"]:
            return await interaction.response.send_message("❌ Giveaway non trovato.", ephemeral=True)
        await interaction.response.send_message("✅ Giveaway terminato.", ephemeral=True)
        await self.conclude(message_id, db["giveaways"][message_id])

    @app_commands.command(name="giveaway-reroll", description="[STAFF] Riesegue l'estrazione di un giveaway")
    @app_commands.describe(message_id="ID del messaggio giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_reroll(self, interaction: discord.Interaction, message_id: str):
        db = get_db()
        if message_id not in db["giveaways"]:
            return await interaction.response.send_message("❌ Giveaway non trovato.", ephemeral=True)
        g = db["giveaways"][message_id]
        g["status"] = "active"
        save("giveaways", db)
        await interaction.response.send_message("🔄 Reroll in corso...", ephemeral=True)
        await self.conclude(message_id, g)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
