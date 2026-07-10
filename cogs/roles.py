import discord
from discord.ext import commands
from discord import app_commands
from cogs.db import load, save

def get_db():
    db = load("roles")
    if "reaction_roles" not in db: db["reaction_roles"] = {}
    if "autoroles" not in db: db["autoroles"] = []
    return db

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        db = get_db()
        for role_id in db["autoroles"]:
            role = member.guild.get_role(role_id)
            if role:
                try: await member.add_roles(role)
                except Exception: pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        db  = get_db()
        key = f"{payload.message_id}_{str(payload.emoji)}"
        if key not in db["reaction_roles"]: return
        guild  = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member or member.bot: return
        role = guild.get_role(db["reaction_roles"][key])
        if role: await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        db  = get_db()
        key = f"{payload.message_id}_{str(payload.emoji)}"
        if key not in db["reaction_roles"]: return
        guild  = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member or member.bot: return
        role = guild.get_role(db["reaction_roles"][key])
        if role: await member.remove_roles(role)

    @app_commands.command(name="reaction-role", description="[ADMIN] Collega un'emoji a un ruolo su un messaggio")
    @app_commands.describe(message_id="ID del messaggio", emoji="Emoji da usare", ruolo="Ruolo da assegnare")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_rr(self, interaction: discord.Interaction, message_id: str, emoji: str, ruolo: discord.Role):
        db  = get_db()
        key = f"{message_id}_{emoji}"
        db["reaction_roles"][key] = ruolo.id
        save("roles", db)
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await msg.add_reaction(emoji)
        except Exception:
            pass
        await interaction.response.send_message(f"✅ Reaction role configurato: {emoji} → {ruolo.mention}", ephemeral=True)

    @app_commands.command(name="autorole", description="[ADMIN] Aggiunge/rimuove un ruolo automatico per i nuovi membri")
    @app_commands.describe(ruolo="Ruolo da gestire", azione="add o remove")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_autorole(self, interaction: discord.Interaction, ruolo: discord.Role, azione: str = "add"):
        db = get_db()
        if azione == "add":
            if ruolo.id not in db["autoroles"]: db["autoroles"].append(ruolo.id)
            msg = f"✅ {ruolo.mention} aggiunto agli autorole."
        else:
            db["autoroles"] = [r for r in db["autoroles"] if r != ruolo.id]
            msg = f"✅ {ruolo.mention} rimosso dagli autorole."
        save("roles", db)
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="ruolo-add", description="[MOD] Aggiunge un ruolo a un utente")
    @app_commands.describe(utente="Utente", ruolo="Ruolo da aggiungere")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_add_role(self, interaction: discord.Interaction, utente: discord.Member, ruolo: discord.Role):
        await utente.add_roles(ruolo)
        await interaction.response.send_message(f"✅ {ruolo.mention} aggiunto a {utente.mention}.")

    @app_commands.command(name="ruolo-remove", description="[MOD] Rimuove un ruolo da un utente")
    @app_commands.describe(utente="Utente", ruolo="Ruolo da rimuovere")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_remove_role(self, interaction: discord.Interaction, utente: discord.Member, ruolo: discord.Role):
        await utente.remove_roles(ruolo)
        await interaction.response.send_message(f"✅ {ruolo.mention} rimosso da {utente.mention}.")

async def setup(bot):
    await bot.add_cog(Roles(bot))
