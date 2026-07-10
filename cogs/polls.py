import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from cogs.db import load, save

EMOJI_NUMS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

def get_db():
    db = load("polls")
    if "polls" not in db: db["polls"] = {}
    return db

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Crea un sondaggio (fino a 10 opzioni, separate da |)")
    @app_commands.describe(domanda="La domanda del sondaggio", opzioni="Opzioni separate da | (es: Sì|No|Forse)")
    async def slash_poll(self, interaction: discord.Interaction, domanda: str, opzioni: str = "Sì|No"):
        opts  = [o.strip() for o in opzioni.split("|") if o.strip()][:10]
        if len(opts) < 2:
            return await interaction.response.send_message("❌ Servono almeno 2 opzioni.", ephemeral=True)

        desc  = "\n".join(f"{EMOJI_NUMS[i]} {o}" for i, o in enumerate(opts))
        embed = discord.Embed(
            title=f"📊 {domanda}",
            description=desc,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Sondaggio di {interaction.user.display_name} • ParityMC")
        await interaction.response.send_message("✅ Sondaggio creato!", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        for i in range(len(opts)):
            await msg.add_reaction(EMOJI_NUMS[i])

        db = get_db()
        db["polls"][str(msg.id)] = {
            "domanda": domanda, "opzioni": opts,
            "channel_id": interaction.channel.id,
            "autore": str(interaction.user), "status": "open"
        }
        save("polls", db)

    @app_commands.command(name="poll-fine", description="[STAFF] Chiude un sondaggio e mostra i risultati")
    @app_commands.describe(message_id="ID del messaggio del sondaggio")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_fine(self, interaction: discord.Interaction, message_id: str):
        db = get_db()
        if message_id not in db["polls"]:
            return await interaction.response.send_message("❌ Sondaggio non trovato.", ephemeral=True)

        p   = db["polls"][message_id]
        ch  = interaction.guild.get_channel(p["channel_id"])
        try:
            msg = await ch.fetch_message(int(message_id))
        except Exception:
            return await interaction.response.send_message("❌ Messaggio non trovato.", ephemeral=True)

        risultati = {}
        for r in msg.reactions:
            if str(r.emoji) in EMOJI_NUMS:
                idx = EMOJI_NUMS.index(str(r.emoji))
                if idx < len(p["opzioni"]):
                    risultati[p["opzioni"][idx]] = r.count - 1

        totale = sum(risultati.values())
        lines  = []
        for opt, voti in sorted(risultati.items(), key=lambda x: -x[1]):
            perc = int(voti / totale * 100) if totale else 0
            bar  = "█" * (perc // 5) + "░" * (20 - perc // 5)
            lines.append(f"**{opt}**\n`{bar}` {voti} voti ({perc}%)")

        embed = discord.Embed(
            title=f"📊 Risultati — {p['domanda']}",
            description="\n\n".join(lines) or "Nessun voto",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="ParityMC • Sondaggi")
        await interaction.response.send_message(embed=embed)

        db["polls"][message_id]["status"] = "closed"
        save("polls", db)

async def setup(bot):
    await bot.add_cog(Polls(bot))
