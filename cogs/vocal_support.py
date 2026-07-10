import discord
from discord.ext import commands
from discord import app_commands
import config, session_manager, bot_logger, utils
from cogs.vocal_views import ControlPanelView
from matchmaking import Matchmaker

class VocalSupport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        mm = self.bot.matchmaker
        if before.channel == after.channel: return
        is_staff = config.SUPPORT_ROLE_ID and any(r.id == config.SUPPORT_ROLE_ID for r in member.roles)

        if before.channel:
            if before.channel.id == config.WAITING_CHANNEL_ID:
                mm.remove_waiting(member.id)
            elif before.channel.id == config.STAFF_CHANNEL_ID:
                mm.remove_staff(member.id)
            elif before.channel.id in session_manager.ACTIVE_SESSIONS:
                humans = [m for m in before.channel.members if not m.bot]
                if not humans: session_manager.notify_channel_empty(self.bot, before.channel.id)

        if after.channel:
            if after.channel.id == config.WAITING_CHANNEL_ID:
                mm.add_waiting(member.id)
                await bot_logger.log(self.bot, f"👤 {member} in attesa supporto.")
                await mm.try_match(self.bot)
            elif after.channel.id == config.STAFF_CHANNEL_ID and is_staff:
                mm.add_staff(member.id)
                await bot_logger.log(self.bot, f"🧑‍💼 {member} disponibile.")
                await mm.try_match(self.bot)
            elif after.channel.id in session_manager.ACTIVE_SESSIONS:
                session_manager.notify_member_joined(after.channel.id)

    @app_commands.command(name="status-supporto", description="Stato del sistema di supporto vocale")
    async def slash_status(self, interaction: discord.Interaction):
        mm = self.bot.matchmaker
        e = discord.Embed(title="📊 Supporto Vocale", color=discord.Color.blurple())
        e.add_field(name="In attesa",        value=len(mm.waiting_queue),             inline=True)
        e.add_field(name="Staff disponibili",value=len(mm.staff_queue),               inline=True)
        e.add_field(name="Sessioni attive",  value=len(session_manager.ACTIVE_SESSIONS), inline=True)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="sessioni", description="Elenca sessioni vocali attive")
    async def slash_sessioni(self, interaction: discord.Interaction):
        if not session_manager.ACTIVE_SESSIONS:
            return await interaction.response.send_message("Nessuna sessione attiva.", ephemeral=True)
        lines = [f"<#{cid}> — <@{s['user_id']}> ↔ <@{s['staff_id']}> ({utils.format_duration(utils.now()-s['created_at'])})"
                 for cid, s in session_manager.ACTIVE_SESSIONS.items()]
        e = discord.Embed(title=f"🗂️ Sessioni ({len(lines)})", description="\n".join(lines), color=discord.Color.blurple())
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="chiudi-sessione", description="[STAFF] Chiude forzatamente una sessione vocale")
    @app_commands.describe(canale="Canale vocale da chiudere")
    async def slash_chiudi(self, interaction: discord.Interaction, canale: discord.VoiceChannel):
        m = interaction.user
        auth = False
        if isinstance(m, discord.Member):
            if m.guild_permissions.administrator: auth = True
            elif any(r.id in (config.ADMIN_ROLE_ID, config.SUPPORT_ROLE_ID) for r in m.roles): auth = True
        if not auth: return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        if canale.id not in session_manager.ACTIVE_SESSIONS:
            return await interaction.response.send_message("❌ Nessuna sessione attiva in quel canale.", ephemeral=True)
        await interaction.response.send_message(f"Chiusura {canale.mention}...", ephemeral=True)
        await session_manager.close_session(self.bot, canale.id, f"Forzata da {interaction.user}")

    @app_commands.command(name="help-supporto", description="Come funziona il supporto vocale")
    async def slash_help(self, interaction: discord.Interaction):
        e = discord.Embed(title="ℹ️ Sistema Supporto Vocale", color=discord.Color.blurple(),
            description="1. Entra in **ATTESA SUPPORTO**\n2. Vieni messo in coda automaticamente\n"
                        "3. Uno staff disponibile ti viene assegnato\n4. Venite spostati in una vocale privata **Assistenza N**")
        await interaction.response.send_message(embed=e, ephemeral=True)

async def setup(bot):
    await bot.add_cog(VocalSupport(bot))
