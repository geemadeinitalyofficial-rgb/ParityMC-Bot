import discord
from discord.ext import commands
from discord import app_commands
import os

PARTNERSHIP_CATEGORY_ID = int(os.getenv("PARTNERSHIP_CATEGORY_ID", "0"))

class Partnership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="partnership", description="Crea un canale partnership con nome e descrizione")
    @app_commands.describe(nome="Nome del server/progetto partner", testo="Descrizione completa della partnership")
    async def slash_partnership(self, interaction: discord.Interaction, nome: str, testo: str):
        channel_name = interaction.channel.name.lower()
        if "partnership" not in channel_name and "ticket" not in channel_name:
            return await interaction.response.send_message("❌ Usa questo comando solo nel ticket partnership.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        guild    = interaction.guild
        categoria = guild.get_channel(PARTNERSHIP_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }

        nuovo = await guild.create_text_channel(name=f"🤝｜{nome}", overwrites=overwrites, category=categoria, topic=f"Partnership con {nome}")

        embed = discord.Embed(title=f"🤝 Partnership — {nome}", description=testo, color=discord.Color.green(), timestamp=discord.utils.utcnow())
        embed.set_footer(text="ParityMC • Partnership")
        if guild.icon: embed.set_thumbnail(url=guild.icon.url)
        await nuovo.send(embed=embed)

        await interaction.followup.send(f"✅ Canale partnership creato: {nuovo.mention}", ephemeral=True)
        await interaction.channel.send(f"✅ Partnership **{nome}** pubblicata in {nuovo.mention}!")

    @app_commands.command(name="modifica-partnership", description="[STAFF] Modifica embed nel canale partnership corrente")
    @app_commands.describe(nome="Nuovo nome", testo="Nuovo testo")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_modifica(self, interaction: discord.Interaction, nome: str, testo: str):
        if "🤝" not in interaction.channel.name and "partnership" not in interaction.channel.name.lower():
            return await interaction.response.send_message("❌ Funziona solo in un canale partnership.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        async for msg in interaction.channel.history(limit=10, oldest_first=True):
            if msg.author == interaction.guild.me and msg.embeds:
                embed = discord.Embed(title=f"🤝 Partnership — {nome}", description=testo, color=discord.Color.green(), timestamp=discord.utils.utcnow())
                embed.set_footer(text="ParityMC • Partnership")
                if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
                await msg.edit(embed=embed)
                await interaction.channel.edit(name=f"🤝｜{nome}")
                return await interaction.followup.send("✅ Partnership aggiornata!", ephemeral=True)
        await interaction.followup.send("❌ Nessun embed trovato.", ephemeral=True)

    @app_commands.command(name="elimina-partnership", description="[STAFF] Elimina il canale partnership corrente")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_elimina(self, interaction: discord.Interaction):
        if "🤝" not in interaction.channel.name and "partnership" not in interaction.channel.name.lower():
            return await interaction.response.send_message("❌ Funziona solo in un canale partnership.", ephemeral=True)
        await interaction.response.send_message("🗑️ Canale eliminato.")
        await interaction.channel.delete()

async def setup(bot):
    await bot.add_cog(Partnership(bot))
