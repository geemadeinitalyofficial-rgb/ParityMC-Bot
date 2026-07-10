import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from cogs.db import load, save

def get_cfg():
    db = load("welcome")
    if "welcome" not in db: db["welcome"] = {"channel_id": None, "message": "Benvenuto {mention} in **{server}**! Sei il membro numero **{count}**! 🎉"}
    if "goodbye" not in db: db["goodbye"] = {"channel_id": None, "message": "{name} ha lasciato **{server}**. Ci mancherà! 👋"}
    return db

def format_msg(template: str, member: discord.Member) -> str:
    return (template
        .replace("{mention}", member.mention)
        .replace("{name}", member.display_name)
        .replace("{server}", member.guild.name)
        .replace("{count}", str(member.guild.member_count))
        .replace("{id}", str(member.id))
    )

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        db  = get_cfg()
        cfg = db["welcome"]
        if not cfg["channel_id"]: return
        ch = member.guild.get_channel(cfg["channel_id"])
        if not ch: return
        embed = discord.Embed(
            description=format_msg(cfg["message"], member),
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        db  = get_cfg()
        cfg = db["goodbye"]
        if not cfg["channel_id"]: return
        ch = member.guild.get_channel(cfg["channel_id"])
        if not ch: return
        embed = discord.Embed(
            description=format_msg(cfg["message"], member),
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ch.send(embed=embed)

    @app_commands.command(name="welcome-setup", description="[ADMIN] Configura il messaggio di benvenuto")
    @app_commands.describe(canale="Canale di benvenuto", messaggio="Messaggio ({mention} {name} {server} {count})")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_welcome(self, interaction: discord.Interaction, canale: discord.TextChannel, messaggio: str = None):
        db = get_cfg()
        db["welcome"]["channel_id"] = canale.id
        if messaggio: db["welcome"]["message"] = messaggio
        save("welcome", db)
        await interaction.response.send_message(f"✅ Benvenuto configurato in {canale.mention}.", ephemeral=True)

    @app_commands.command(name="goodbye-setup", description="[ADMIN] Configura il messaggio di addio")
    @app_commands.describe(canale="Canale addio", messaggio="Messaggio ({name} {server})")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_goodbye(self, interaction: discord.Interaction, canale: discord.TextChannel, messaggio: str = None):
        db = get_cfg()
        db["goodbye"]["channel_id"] = canale.id
        if messaggio: db["goodbye"]["message"] = messaggio
        save("welcome", db)
        await interaction.response.send_message(f"✅ Addio configurato in {canale.mention}.", ephemeral=True)

    @app_commands.command(name="welcome-test", description="[ADMIN] Testa il messaggio di benvenuto")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_test(self, interaction: discord.Interaction):
        await self.on_member_join(interaction.user)
        await interaction.response.send_message("✅ Messaggio di test inviato.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
