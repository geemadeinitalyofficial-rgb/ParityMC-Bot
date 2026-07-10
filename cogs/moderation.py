import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import os
from cogs.db import load, save

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

def get_warns():
    db = load("warns")
    if "warns" not in db: db["warns"] = {}
    return db

async def send_log(guild, embed):
    ch = guild.get_channel(LOG_CHANNEL_ID)
    if ch: await ch.send(embed=embed)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def mod_embed(self, titolo, color, **fields):
        e = discord.Embed(title=titolo, color=color, timestamp=datetime.utcnow())
        for k, v in fields.items():
            e.add_field(name=k, value=v, inline=True)
        e.set_footer(text="ParityMC • Moderazione")
        return e

    # ── BAN ──
    @app_commands.command(name="ban", description="[MOD] Banna un utente dal server")
    @app_commands.describe(utente="Utente da bannare", motivo="Motivo del ban", giorni_messaggi="Giorni di messaggi da eliminare (0-7)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_ban(self, interaction: discord.Interaction, utente: discord.Member, motivo: str = "Nessun motivo", giorni_messaggi: int = 0):
        await utente.ban(reason=f"{interaction.user}: {motivo}", delete_message_days=min(7, giorni_messaggi))
        embed = self.mod_embed("🔨 Ban", discord.Color.red(), Utente=f"{utente} (`{utente.id}`)", Moderatore=str(interaction.user), Motivo=motivo)
        await interaction.response.send_message(embed=embed)
        await send_log(interaction.guild, embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def cmd_ban(self, ctx, utente: discord.Member, *, motivo="Nessun motivo"):
        await utente.ban(reason=f"{ctx.author}: {motivo}")
        embed = self.mod_embed("🔨 Ban", discord.Color.red(), Utente=str(utente), Moderatore=str(ctx.author), Motivo=motivo)
        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    # ── UNBAN ──
    @app_commands.command(name="unban", description="[MOD] Rimuove il ban di un utente")
    @app_commands.describe(user_id="ID dell'utente da sbannare")
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user} è stato sbannato.")
        except Exception:
            await interaction.response.send_message("❌ Utente non trovato o non bannato.", ephemeral=True)

    # ── KICK ──
    @app_commands.command(name="kick", description="[MOD] Espelle un utente dal server")
    @app_commands.describe(utente="Utente da espellere", motivo="Motivo del kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, utente: discord.Member, motivo: str = "Nessun motivo"):
        await utente.kick(reason=f"{interaction.user}: {motivo}")
        embed = self.mod_embed("👟 Kick", discord.Color.orange(), Utente=str(utente), Moderatore=str(interaction.user), Motivo=motivo)
        await interaction.response.send_message(embed=embed)
        await send_log(interaction.guild, embed)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def cmd_kick(self, ctx, utente: discord.Member, *, motivo="Nessun motivo"):
        await utente.kick(reason=f"{ctx.author}: {motivo}")
        embed = self.mod_embed("👟 Kick", discord.Color.orange(), Utente=str(utente), Moderatore=str(ctx.author), Motivo=motivo)
        await ctx.send(embed=embed)

    # ── MUTE (timeout) ──
    @app_commands.command(name="mute", description="[MOD] Silenzia un utente (timeout)")
    @app_commands.describe(utente="Utente da mutare", minuti="Durata in minuti", motivo="Motivo")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_mute(self, interaction: discord.Interaction, utente: discord.Member, minuti: int = 10, motivo: str = "Nessun motivo"):
        until = discord.utils.utcnow() + timedelta(minutes=minuti)
        await utente.timeout(until, reason=motivo)
        embed = self.mod_embed("🔇 Mute", discord.Color.orange(), Utente=str(utente), Durata=f"{minuti} minuti", Motivo=motivo)
        await interaction.response.send_message(embed=embed)
        await send_log(interaction.guild, embed)

    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def cmd_mute(self, ctx, utente: discord.Member, minuti: int = 10, *, motivo="Nessun motivo"):
        until = discord.utils.utcnow() + timedelta(minutes=minuti)
        await utente.timeout(until, reason=motivo)
        await ctx.send(f"🔇 {utente.mention} mutato per {minuti} minuti.")

    # ── UNMUTE ──
    @app_commands.command(name="unmute", description="[MOD] Rimuove il mute di un utente")
    @app_commands.describe(utente="Utente da smutare")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_unmute(self, interaction: discord.Interaction, utente: discord.Member):
        await utente.timeout(None)
        await interaction.response.send_message(f"✅ {utente.mention} non è più mutato.")

    @commands.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def cmd_unmute(self, ctx, utente: discord.Member):
        await utente.timeout(None)
        await ctx.send(f"✅ {utente.mention} non è più mutato.")

    # ── WARN ──
    @app_commands.command(name="warn", description="[MOD] Aggiunge un warn a un utente")
    @app_commands.describe(utente="Utente da warnare", motivo="Motivo del warn")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_warn(self, interaction: discord.Interaction, utente: discord.Member, motivo: str = "Nessun motivo"):
        db = get_warns()
        uid = str(utente.id)
        if uid not in db["warns"]: db["warns"][uid] = []
        db["warns"][uid].append({"motivo": motivo, "mod": str(interaction.user), "data": datetime.utcnow().isoformat()})
        save("warns", db)
        n = len(db["warns"][uid])
        embed = self.mod_embed(f"⚠️ Warn #{n}", discord.Color.yellow(), Utente=str(utente), Moderatore=str(interaction.user), Motivo=motivo, Totale=f"{n} warn")
        await interaction.response.send_message(embed=embed)
        await send_log(interaction.guild, embed)

    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def cmd_warn(self, ctx, utente: discord.Member, *, motivo="Nessun motivo"):
        db = get_warns()
        uid = str(utente.id)
        if uid not in db["warns"]: db["warns"][uid] = []
        db["warns"][uid].append({"motivo": motivo, "mod": str(ctx.author), "data": datetime.utcnow().isoformat()})
        save("warns", db)
        await ctx.send(f"⚠️ {utente.mention} warnato. ({len(db['warns'][uid])} warn totali)")

    # ── WARNS ──
    @app_commands.command(name="warns", description="Mostra i warn di un utente")
    @app_commands.describe(utente="Utente di cui vedere i warn")
    async def slash_warns(self, interaction: discord.Interaction, utente: discord.Member):
        db  = get_warns()
        uid = str(utente.id)
        ws  = db["warns"].get(uid, [])
        if not ws:
            return await interaction.response.send_message(f"✅ {utente.mention} non ha warn.", ephemeral=True)
        embed = discord.Embed(title=f"⚠️ Warn di {utente}", color=discord.Color.yellow())
        for i, w in enumerate(ws, 1):
            embed.add_field(name=f"Warn #{i}", value=f"**Motivo:** {w['motivo']}\n**Mod:** {w['mod']}\n**Data:** {w['data'][:10]}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── CLEARWARN ──
    @app_commands.command(name="clearwarn", description="[MOD] Rimuove tutti i warn di un utente")
    @app_commands.describe(utente="Utente")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_clearwarn(self, interaction: discord.Interaction, utente: discord.Member):
        db = get_warns()
        db["warns"][str(utente.id)] = []
        save("warns", db)
        await interaction.response.send_message(f"✅ Warn di {utente.mention} azzerati.")

    # ── PURGE ──
    @app_commands.command(name="purge", description="[MOD] Elimina N messaggi dal canale")
    @app_commands.describe(quantita="Numero di messaggi da eliminare (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(self, interaction: discord.Interaction, quantita: int):
        quantita = min(100, max(1, quantita))
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=quantita)
        await interaction.followup.send(f"🗑️ Eliminati {len(deleted)} messaggi.", ephemeral=True)

    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def cmd_purge(self, ctx, quantita: int = 10):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=min(100, quantita))
        msg = await ctx.send(f"🗑️ Eliminati {len(deleted)} messaggi.")
        await msg.delete(delay=3)

    # ── SLOWMODE ──
    @app_commands.command(name="slowmode", description="[MOD] Imposta la modalità lenta nel canale")
    @app_commands.describe(secondi="Secondi di slowmode (0 = disabilita)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_slowmode(self, interaction: discord.Interaction, secondi: int = 0):
        await interaction.channel.edit(slowmode_delay=secondi)
        msg = f"⏱️ Slowmode impostato a {secondi}s." if secondi > 0 else "⏱️ Slowmode disabilitato."
        await interaction.response.send_message(msg)

    # ── LOCK / UNLOCK ──
    @app_commands.command(name="lock", description="[MOD] Blocca il canale corrente")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Canale bloccato.")

    @app_commands.command(name="unlock", description="[MOD] Sblocca il canale corrente")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("🔓 Canale sbloccato.")

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def cmd_lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Canale bloccato.")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def cmd_unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send("🔓 Canale sbloccato.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
