import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio, io, os
from cogs.db import load, save

SUPPORT_ROLE_ID       = int(os.getenv("SUPPORT_ROLE_ID", "0"))
LOG_CHANNEL_ID        = int(os.getenv("LOG_CHANNEL_ID", "0"))
TICKET_CATEGORY_ID    = int(os.getenv("TICKET_CATEGORY_ID", "0"))

CATEGORIE = {
    "generale":    {"emoji": "💬", "label": "Generale",    "color": discord.Color.blue()},
    "partnership": {"emoji": "🤝", "label": "Partnership", "color": discord.Color.green()},
    "donazioni":   {"emoji": "💎", "label": "Donazioni",   "color": discord.Color.gold()},
    "servizi":     {"emoji": "🛠️", "label": "Servizi",    "color": discord.Color.orange()},
    "pagamenti":   {"emoji": "💳", "label": "Pagamenti",   "color": discord.Color.red()},
}

def get_db():
    db = load("tickets")
    if "tickets" not in db: db["tickets"] = {}
    if "counter" not in db: db["counter"] = 0
    return db

def get_tid_by_channel(channel_id):
    db = get_db()
    for tid, t in db["tickets"].items():
        if t["channel_id"] == channel_id:
            return tid
    return None

def is_ticket(channel_id):
    return get_tid_by_channel(channel_id) is not None

# =============================================
#  VIEWS
# =============================================
class CategoriaSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=v["label"], value=k, emoji=v["emoji"])
            for k, v in CATEGORIE.items()
        ]
        super().__init__(placeholder="📂 Seleziona categoria...", options=options, custom_id="ticket_cat_select")

    async def callback(self, interaction: discord.Interaction):
        cog = interaction.client.cogs.get("Tickets")
        if cog:
            await cog.apri_ticket(interaction, self.values[0])

class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategoriaSelect())

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Chiudi", style=discord.ButtonStyle.danger, custom_id="t_close")
    async def chiudi(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.cogs.get("Tickets")
        if cog: await cog.cmd_chiudi(interaction)

    @discord.ui.button(label="📋 Trascrizione", style=discord.ButtonStyle.secondary, custom_id="t_transcript")
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.cogs.get("Tickets")
        if cog: await cog.cmd_transcript(interaction)

    @discord.ui.button(label="🙋 Claim", style=discord.ButtonStyle.success, custom_id="t_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.cogs.get("Tickets")
        if cog: await cog.cmd_claim(interaction)

class ConfermaChiusura(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=30)
        self.channel = channel

    @discord.ui.button(label="✅ Conferma", style=discord.ButtonStyle.danger)
    async def conferma(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        cog = interaction.client.cogs.get("Tickets")
        if cog: await cog.elimina_ticket(interaction, self.channel)
        self.stop()

    @discord.ui.button(label="❌ Annulla", style=discord.ButtonStyle.secondary)
    async def annulla(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Chiusura annullata.", ephemeral=True)
        self.stop()

# =============================================
#  COG
# =============================================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(PanelView())
        bot.add_view(TicketControlView())

    async def apri_ticket(self, interaction: discord.Interaction, categoria: str):
        guild = interaction.guild
        user  = interaction.user
        cat   = CATEGORIE[categoria]
        db    = get_db()

        for t in db["tickets"].values():
            if t["user_id"] == user.id and t["status"] == "open":
                ch = guild.get_channel(t["channel_id"])
                if ch:
                    await interaction.response.send_message(f"⚠️ Hai già un ticket aperto: {ch.mention}", ephemeral=True)
                    return

        db["counter"] += 1
        tid = db["counter"]
        support = guild.get_role(SUPPORT_ROLE_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        if support:
            overwrites[support] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        cat_discord = guild.get_channel(TICKET_CATEGORY_ID)
        channel = await guild.create_text_channel(
            name=f"ticket-{tid:04d}-{user.name[:10]}",
            overwrites=overwrites,
            category=cat_discord,
            topic=f"Ticket #{tid:04d} | {cat['label']} | {user}"
        )

        db["tickets"][str(tid)] = {
            "channel_id": channel.id, "user_id": user.id,
            "username": str(user), "categoria": categoria,
            "status": "open", "claimed_by": None,
            "opened_at": datetime.utcnow().isoformat(), "id": tid,
        }
        save("tickets", db)

        embed = discord.Embed(
            title=f"{cat['emoji']} Ticket #{tid:04d} — {cat['label']}",
            description=f"Benvenuto {user.mention}!\nDescrivi il problema dettagliatamente.\n\n📁 **Categoria:** {cat['label']}\n🕐 **Aperto:** <t:{int(datetime.utcnow().timestamp())}:F>",
            color=cat["color"], timestamp=datetime.utcnow()
        )
        embed.set_footer(text="ParityMC • Ticket System")
        msg = await channel.send(content=f"{user.mention} {support.mention if support else ''}", embed=embed, view=TicketControlView())
        await msg.pin()
        await interaction.response.send_message(f"✅ Ticket aperto: {channel.mention}", ephemeral=True)
        await self.log(guild, "🟢 Ticket Aperto", user, tid, categoria, cat["color"])

    async def elimina_ticket(self, interaction: discord.Interaction, channel: discord.TextChannel):
        tid = get_tid_by_channel(channel.id)
        db  = get_db()
        if tid:
            db["tickets"][tid]["status"] = "closed"
            save("tickets", db)
            t = db["tickets"][tid]
            await self.log(interaction.guild, "🔴 Ticket Chiuso", interaction.user, int(tid), t["categoria"], discord.Color.red(), f"Chiuso da {interaction.user.mention}")
        await channel.send("🔒 Chiusura in 5 secondi...")
        await asyncio.sleep(5)
        await channel.delete()

    async def cmd_chiudi(self, interaction: discord.Interaction):
        if not is_ticket(interaction.channel.id):
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        embed = discord.Embed(title="🔒 Chiudi Ticket", description="Confermi la chiusura? Il canale verrà eliminato.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=ConfermaChiusura(interaction.channel))

    async def cmd_transcript(self, interaction: discord.Interaction):
        if not is_ticket(interaction.channel.id):
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        file = await self.genera_transcript(interaction.channel)
        await interaction.followup.send("📋 Trascrizione:", file=file, ephemeral=True)

    async def cmd_claim(self, interaction: discord.Interaction):
        tid = get_tid_by_channel(interaction.channel.id)
        if not tid:
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        support = interaction.guild.get_role(SUPPORT_ROLE_ID)
        if support and support not in interaction.user.roles:
            return await interaction.response.send_message("❌ Solo lo staff può fare claim.", ephemeral=True)
        db = get_db()
        db["tickets"][tid]["claimed_by"] = interaction.user.id
        save("tickets", db)
        await interaction.response.send_message(f"✅ Ticket preso in carico da {interaction.user.mention}")

    async def genera_transcript(self, channel):
        lines = [f"TRASCRIZIONE: {channel.name}\n{'='*40}"]
        async for msg in channel.history(limit=None, oldest_first=True):
            ts = msg.created_at.strftime("%d/%m/%Y %H:%M")
            lines.append(f"[{ts}] {msg.author}: {msg.content or '[embed/allegato]'}")
        buf = io.BytesIO("\n".join(lines).encode("utf-8"))
        return discord.File(buf, filename=f"transcript-{channel.name}.txt")

    async def log(self, guild, titolo, user, ticket_id, categoria, color, extra=""):
        ch = guild.get_channel(LOG_CHANNEL_ID)
        if not ch: return
        cat = CATEGORIE.get(categoria, {"emoji": "📁", "label": categoria})
        e = discord.Embed(title=titolo, color=color, timestamp=datetime.utcnow())
        e.add_field(name="Utente", value=f"{user.mention}", inline=True)
        e.add_field(name="Ticket", value=f"#{ticket_id:04d}", inline=True)
        e.add_field(name="Categoria", value=f"{cat['emoji']} {cat['label']}", inline=True)
        if extra: e.add_field(name="Note", value=extra, inline=False)
        e.set_footer(text="ParityMC • Log")
        await ch.send(embed=e)

    # Slash commands
    @app_commands.command(name="ticket-panel", description="[ADMIN] Invia il pannello ticket")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Sistema Ticket — ParityMC",
            description="💬 **Generale** — Domande generali\n🤝 **Partnership** — Proposte di collaborazione\n💎 **Donazioni** — Info rank e donazioni\n🛠️ **Servizi** — Richiesta servizi\n💳 **Pagamenti** — Problemi di pagamento",
            color=discord.Color.from_rgb(0, 180, 120)
        )
        embed.set_footer(text="ParityMC • Ticket System")
        await interaction.response.send_message("✅ Pannello inviato!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=PanelView())

    @app_commands.command(name="chiudi", description="Chiude il ticket corrente")
    async def slash_chiudi(self, interaction: discord.Interaction):
        await self.cmd_chiudi(interaction)

    @app_commands.command(name="transcript", description="Genera la trascrizione del ticket")
    async def slash_transcript(self, interaction: discord.Interaction):
        await self.cmd_transcript(interaction)

    @app_commands.command(name="claim", description="[STAFF] Prendi in carico il ticket")
    async def slash_claim(self, interaction: discord.Interaction):
        await self.cmd_claim(interaction)

    @app_commands.command(name="aggiungi", description="[STAFF] Aggiunge un utente al ticket")
    @app_commands.describe(utente="Utente da aggiungere")
    async def slash_aggiungi(self, interaction: discord.Interaction, utente: discord.Member):
        if not is_ticket(interaction.channel.id):
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        await interaction.channel.set_permissions(utente, view_channel=True, send_messages=True, read_message_history=True)
        await interaction.response.send_message(f"✅ {utente.mention} aggiunto al ticket.")

    @app_commands.command(name="rimuovi", description="[STAFF] Rimuove un utente dal ticket")
    @app_commands.describe(utente="Utente da rimuovere")
    async def slash_rimuovi(self, interaction: discord.Interaction, utente: discord.Member):
        if not is_ticket(interaction.channel.id):
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        await interaction.channel.set_permissions(utente, overwrite=None)
        await interaction.response.send_message(f"✅ {utente.mention} rimosso dal ticket.")

    @app_commands.command(name="rename", description="[STAFF] Rinomina il canale ticket")
    @app_commands.describe(nome="Nuovo nome")
    async def slash_rename(self, interaction: discord.Interaction, nome: str):
        if not is_ticket(interaction.channel.id):
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        await interaction.channel.edit(name=nome)
        await interaction.response.send_message(f"✅ Rinominato in `{nome}`.")

    @app_commands.command(name="lista-ticket", description="[STAFF] Mostra tutti i ticket aperti")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_lista(self, interaction: discord.Interaction):
        db = get_db()
        aperti = [(tid, t) for tid, t in db["tickets"].items() if t["status"] == "open"]
        if not aperti:
            return await interaction.response.send_message("✅ Nessun ticket aperto.", ephemeral=True)
        embed = discord.Embed(title=f"🎫 Ticket Aperti ({len(aperti)})", color=discord.Color.blue())
        for tid, t in aperti[:20]:
            cat = CATEGORIE.get(t["categoria"], {"emoji": "📁", "label": t["categoria"]})
            ch = interaction.guild.get_channel(t["channel_id"])
            embed.add_field(name=f"#{int(tid):04d} {cat['emoji']} {cat['label']}", value=f"👤 <@{t['user_id']}>\n📌 {ch.mention if ch else 'eliminato'}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ticket-info", description="Info sul ticket corrente")
    async def slash_info(self, interaction: discord.Interaction):
        tid = get_tid_by_channel(interaction.channel.id)
        if not tid:
            return await interaction.response.send_message("❌ Non sei in un canale ticket.", ephemeral=True)
        db = get_db()
        t  = db["tickets"][tid]
        cat = CATEGORIE.get(t["categoria"], {"emoji": "📁", "label": t["categoria"], "color": discord.Color.greyple()})
        embed = discord.Embed(title=f"ℹ️ Ticket #{int(tid):04d}", color=cat["color"])
        embed.add_field(name="Utente", value=f"<@{t['user_id']}>", inline=True)
        embed.add_field(name="Categoria", value=f"{cat['emoji']} {cat['label']}", inline=True)
        embed.add_field(name="Staff", value=f"<@{t['claimed_by']}>" if t["claimed_by"] else "Nessuno", inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
