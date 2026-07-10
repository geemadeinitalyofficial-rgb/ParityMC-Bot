import discord
import config, utils

def _auth(interaction, session):
    if not session: return False
    if interaction.user.id in (session["user_id"], session["staff_id"]): return True
    m = interaction.user
    if isinstance(m, discord.Member):
        if m.guild_permissions.administrator: return True
        if any(r.id in (config.ADMIN_ROLE_ID, config.SUPPORT_ROLE_ID) for r in m.roles): return True
    return False

class RenameModal(discord.ui.Modal, title="Rinomina canale"):
    new_name = discord.ui.TextInput(label="Nuovo nome", max_length=90)
    def __init__(self, channel_id):
        super().__init__(); self.channel_id = channel_id
    async def on_submit(self, interaction: discord.Interaction):
        ch = interaction.guild.get_channel(self.channel_id)
        if ch: await ch.edit(name=str(self.new_name.value))
        await interaction.response.send_message(f"✅ Rinominato in **{self.new_name.value}**.", ephemeral=True)

class ControlPanelView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        for label, emoji, style, cid, cb in [
            ("Chiudi", "🛑", discord.ButtonStyle.danger,    f"panel:close:{channel_id}",         self._close),
            ("Rinomina","✏️",discord.ButtonStyle.secondary, f"panel:rename:{channel_id}",         self._rename),
            ("Auto-chiusura","🔒",discord.ButtonStyle.secondary,f"panel:ac:{channel_id}",         self._toggle_ac),
            ("Info","ℹ️",discord.ButtonStyle.primary,       f"panel:info:{channel_id}",           self._info),
        ]:
            b = discord.ui.Button(label=label, emoji=emoji, style=style, custom_id=cid)
            b.callback = cb
            self.add_item(b)

    async def _close(self, interaction):
        import session_manager as sm
        s = sm.ACTIVE_SESSIONS.get(self.channel_id)
        if not _auth(interaction, s): return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        await interaction.response.send_message("Chiusura...", ephemeral=True)
        await sm.close_session(interaction.client, self.channel_id, f"Chiusa da {interaction.user}")

    async def _rename(self, interaction):
        import session_manager as sm
        s = sm.ACTIVE_SESSIONS.get(self.channel_id)
        if not _auth(interaction, s): return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        await interaction.response.send_modal(RenameModal(self.channel_id))

    async def _toggle_ac(self, interaction):
        import session_manager as sm
        s = sm.ACTIVE_SESSIONS.get(self.channel_id)
        if not _auth(interaction, s): return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        if not s: return await interaction.response.send_message("❌ Sessione non trovata.", ephemeral=True)
        s["no_auto_close"] = not s.get("no_auto_close", False)
        stato = "bloccata" if s["no_auto_close"] else "attiva"
        await interaction.response.send_message(f"🔒 Auto-chiusura **{stato}**.", ephemeral=True)

    async def _info(self, interaction):
        import session_manager as sm
        s = sm.ACTIVE_SESSIONS.get(self.channel_id)
        if not s: return await interaction.response.send_message("❌ Sessione non trovata.", ephemeral=True)
        e = discord.Embed(title="ℹ️ Info sessione", color=discord.Color.blurple())
        e.add_field(name="Utente", value=f"<@{s['user_id']}>", inline=True)
        e.add_field(name="Staff",  value=f"<@{s['staff_id']}>", inline=True)
        e.add_field(name="Durata", value=utils.format_duration(utils.now()-s["created_at"]), inline=True)
        e.add_field(name="Auto-chiusura", value="Bloccata" if s.get("no_auto_close") else "Attiva", inline=True)
        await interaction.response.send_message(embed=e, ephemeral=True)
