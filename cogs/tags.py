import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from cogs.db import load, save

def get_db():
    db = load("tags")
    if "tags" not in db: db["tags"] = {}
    return db

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tag-crea", description="[STAFF] Crea un tag/risposta rapida")
    @app_commands.describe(nome="Nome del tag", contenuto="Contenuto del tag")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_crea(self, interaction: discord.Interaction, nome: str, contenuto: str):
        db = get_db()
        nome = nome.lower()
        db["tags"][nome] = {"contenuto": contenuto, "autore": str(interaction.user), "creato": datetime.utcnow().isoformat(), "usi": 0}
        save("tags", db)
        await interaction.response.send_message(f"✅ Tag `{nome}` creato!", ephemeral=True)

    @app_commands.command(name="tag", description="Mostra un tag")
    @app_commands.describe(nome="Nome del tag da mostrare")
    async def slash_tag(self, interaction: discord.Interaction, nome: str):
        db = get_db()
        nome = nome.lower()
        if nome not in db["tags"]:
            return await interaction.response.send_message(f"❌ Tag `{nome}` non trovato.", ephemeral=True)
        db["tags"][nome]["usi"] += 1
        save("tags", db)
        await interaction.response.send_message(db["tags"][nome]["contenuto"])

    @app_commands.command(name="tag-lista", description="Mostra tutti i tag disponibili")
    async def slash_lista(self, interaction: discord.Interaction):
        db = get_db()
        if not db["tags"]:
            return await interaction.response.send_message("❌ Nessun tag creato.", ephemeral=True)
        embed = discord.Embed(title="🏷️ Tag Disponibili", color=discord.Color.blue(), timestamp=datetime.utcnow())
        for nome, data in list(db["tags"].items())[:25]:
            embed.add_field(name=f"`{nome}`", value=f"Usi: {data['usi']} | Autore: {data['autore']}", inline=True)
        embed.set_footer(text="ParityMC • Tags")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tag-elimina", description="[STAFF] Elimina un tag")
    @app_commands.describe(nome="Nome del tag da eliminare")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_elimina(self, interaction: discord.Interaction, nome: str):
        db = get_db()
        nome = nome.lower()
        if nome not in db["tags"]:
            return await interaction.response.send_message(f"❌ Tag `{nome}` non trovato.", ephemeral=True)
        del db["tags"][nome]
        save("tags", db)
        await interaction.response.send_message(f"✅ Tag `{nome}` eliminato.", ephemeral=True)

    @commands.command(name="tag")
    async def cmd_tag(self, ctx, nome: str = None):
        if not nome:
            return await ctx.send("Uso: `!tag <nome>`")
        db = get_db()
        nome = nome.lower()
        if nome not in db["tags"]:
            return await ctx.send(f"❌ Tag `{nome}` non trovato.")
        db["tags"][nome]["usi"] += 1
        save("tags", db)
        await ctx.send(db["tags"][nome]["contenuto"])

async def setup(bot):
    await bot.add_cog(Tags(bot))
