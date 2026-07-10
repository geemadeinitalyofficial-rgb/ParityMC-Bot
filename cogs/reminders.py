import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from cogs.db import load, save

def get_db():
    db = load("reminders")
    if "reminders" not in db: db["reminders"] = []
    return db

def parse_duration(s: str) -> int:
    total, num = 0, ""
    for c in s:
        if c.isdigit(): num += c
        elif c == "d" and num: total += int(num)*86400; num=""
        elif c == "h" and num: total += int(num)*3600;  num=""
        elif c == "m" and num: total += int(num)*60;    num=""
        elif c == "s" and num: total += int(num);        num=""
    return total

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_reminders())

    async def check_reminders(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            db  = get_db()
            now = datetime.utcnow().timestamp()
            changed = False
            for rem in list(db["reminders"]):
                if now >= rem["at"]:
                    try:
                        ch = self.bot.get_channel(rem["channel_id"])
                        if ch:
                            user = self.bot.get_user(rem["user_id"])
                            await ch.send(f"⏰ {user.mention if user else ''} **Reminder:** {rem['testo']}")
                    except Exception:
                        pass
                    db["reminders"].remove(rem)
                    changed = True
            if changed:
                save("reminders", db)
            await asyncio.sleep(10)

    @app_commands.command(name="reminder", description="Imposta un promemoria")
    @app_commands.describe(durata="Durata (es: 1h, 30m, 2d)", testo="Cosa vuoi ricordare")
    async def slash_reminder(self, interaction: discord.Interaction, durata: str, testo: str):
        secondi = parse_duration(durata)
        if secondi <= 0:
            return await interaction.response.send_message("❌ Durata non valida.", ephemeral=True)
        at = (datetime.utcnow() + timedelta(seconds=secondi)).timestamp()
        db = get_db()
        db["reminders"].append({
            "user_id": interaction.user.id, "channel_id": interaction.channel.id,
            "testo": testo, "at": at,
            "creato": datetime.utcnow().isoformat()
        })
        save("reminders", db)
        await interaction.response.send_message(f"⏰ Reminder impostato! Ti ricorderò di **{testo}** tra **{durata}**.", ephemeral=True)

    @app_commands.command(name="reminder-lista", description="Mostra i tuoi reminder attivi")
    async def slash_lista(self, interaction: discord.Interaction):
        db  = get_db()
        miei = [r for r in db["reminders"] if r["user_id"] == interaction.user.id]
        if not miei:
            return await interaction.response.send_message("✅ Nessun reminder attivo.", ephemeral=True)
        embed = discord.Embed(title="⏰ I tuoi Reminder", color=discord.Color.blue())
        for i, r in enumerate(miei[:10], 1):
            embed.add_field(name=f"#{i} — {r['testo']}", value=f"<t:{int(r['at'])}:R>", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reminder-cancella", description="Cancella un tuo reminder per numero")
    @app_commands.describe(numero="Numero del reminder dalla lista")
    async def slash_cancella(self, interaction: discord.Interaction, numero: int):
        db   = get_db()
        miei = [r for r in db["reminders"] if r["user_id"] == interaction.user.id]
        if numero < 1 or numero > len(miei):
            return await interaction.response.send_message("❌ Numero non valido.", ephemeral=True)
        rem = miei[numero - 1]
        db["reminders"].remove(rem)
        save("reminders", db)
        await interaction.response.send_message(f"✅ Reminder **{rem['testo']}** cancellato.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Reminders(bot))
