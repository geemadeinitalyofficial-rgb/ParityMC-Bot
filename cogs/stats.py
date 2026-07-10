import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import platform, psutil, os

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    @app_commands.command(name="serverinfo", description="Mostra le statistiche del server")
    async def slash_serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blue(), timestamp=datetime.utcnow())
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👑 Proprietario",   value=f"{g.owner.mention}",                        inline=True)
        embed.add_field(name="📅 Creato",          value=f"<t:{int(g.created_at.timestamp())}:D>",   inline=True)
        embed.add_field(name="🆔 ID",              value=g.id,                                        inline=True)
        embed.add_field(name="👥 Membri",          value=g.member_count,                              inline=True)
        embed.add_field(name="💬 Canali testo",    value=len(g.text_channels),                        inline=True)
        embed.add_field(name="🔊 Canali voce",     value=len(g.voice_channels),                       inline=True)
        embed.add_field(name="🎭 Ruoli",           value=len(g.roles),                                inline=True)
        embed.add_field(name="😀 Emoji",           value=len(g.emojis),                               inline=True)
        embed.add_field(name="🚀 Boost",           value=f"Lv {g.premium_tier} ({g.premium_subscription_count} boost)", inline=True)
        embed.add_field(name="✅ Verificati",      value=sum(1 for m in g.members if not m.bot),      inline=True)
        embed.add_field(name="🤖 Bot",             value=sum(1 for m in g.members if m.bot),          inline=True)
        embed.set_footer(text="ParityMC • Server Info")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Mostra informazioni su un utente")
    @app_commands.describe(utente="Utente (lascia vuoto per te)")
    async def slash_userinfo(self, interaction: discord.Interaction, utente: discord.Member = None):
        u = utente or interaction.user
        embed = discord.Embed(title=f"👤 {u}", color=u.color, timestamp=datetime.utcnow())
        embed.set_thumbnail(url=u.display_avatar.url)
        embed.add_field(name="🆔 ID",            value=u.id,                                         inline=True)
        embed.add_field(name="🤖 Bot",           value="Sì" if u.bot else "No",                      inline=True)
        embed.add_field(name="📅 Account creato", value=f"<t:{int(u.created_at.timestamp())}:D>",    inline=True)
        embed.add_field(name="📥 Entrato il",    value=f"<t:{int(u.joined_at.timestamp())}:D>" if u.joined_at else "N/A", inline=True)
        embed.add_field(name="🎨 Colore",        value=str(u.color),                                 inline=True)
        embed.add_field(name="🏆 Top ruolo",     value=u.top_role.mention,                           inline=True)
        roles = [r.mention for r in u.roles if r.name != "@everyone"]
        embed.add_field(name=f"🎭 Ruoli ({len(roles)})", value=" ".join(roles[:10]) or "Nessuno",   inline=False)
        embed.set_footer(text="ParityMC • User Info")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Mostra informazioni sul bot")
    async def slash_botinfo(self, interaction: discord.Interaction):
        uptime = datetime.utcnow() - self.start_time
        h, rem = divmod(int(uptime.total_seconds()), 3600)
        m, s   = divmod(rem, 60)
        embed  = discord.Embed(title="🤖 ParityMC Bot", color=discord.Color.from_rgb(0,180,120), timestamp=datetime.utcnow())
        embed.add_field(name="⏱️ Uptime",       value=f"{h}h {m}m {s}s",                           inline=True)
        embed.add_field(name="🏓 Latenza",      value=f"{round(self.bot.latency*1000)}ms",           inline=True)
        embed.add_field(name="🐍 Python",       value=platform.python_version(),                     inline=True)
        embed.add_field(name="📚 discord.py",   value=discord.__version__,                           inline=True)
        embed.add_field(name="🖥️ OS",          value=platform.system(),                             inline=True)
        embed.add_field(name="📡 Server",       value=len(self.bot.guilds),                          inline=True)
        embed.add_field(name="👥 Utenti",       value=sum(g.member_count for g in self.bot.guilds),  inline=True)
        embed.add_field(name="⚙️ Comandi",     value=len([c for c in self.bot.tree.get_commands()]),inline=True)
        embed.set_footer(text="ParityMC • Bot Info")
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="Mostra le statistiche rapide del server")
    async def slash_stats(self, interaction: discord.Interaction):
        g     = interaction.guild
        bots  = sum(1 for m in g.members if m.bot)
        human = g.member_count - bots
        online= sum(1 for m in g.members if m.status != discord.Status.offline and not m.bot)
        embed = discord.Embed(title=f"📈 Stats — {g.name}", color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.add_field(name="👥 Umani",    value=human,              inline=True)
        embed.add_field(name="🟢 Online",   value=online,             inline=True)
        embed.add_field(name="🤖 Bot",      value=bots,               inline=True)
        embed.add_field(name="💬 Canali",   value=len(g.channels),    inline=True)
        embed.add_field(name="🎭 Ruoli",    value=len(g.roles),       inline=True)
        embed.add_field(name="🚀 Boost",    value=g.premium_subscription_count, inline=True)
        embed.set_footer(text="ParityMC • Stats")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="ping")
    async def cmd_ping(self, ctx):
        await ctx.send(f"🏓 Pong! `{round(self.bot.latency*1000)}ms`")

async def setup(bot):
    await bot.add_cog(Stats(bot))
