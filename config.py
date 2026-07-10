"""
Configurazione centrale — ParityMC Bot
Compila tutti i valori prima di avviare con python main.py
Compatibile con hosting su Wispbyte (VPS/Panel).
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ── Token & Server ──────────────────────────────────────────────
BOT_TOKEN   = os.getenv("DISCORD_TOKEN", "IL_TUO_TOKEN")
GUILD_ID    = int(os.getenv("GUILD_ID", "0"))
PREFIX      = os.getenv("PREFIX", "!")

# ── Ruoli ───────────────────────────────────────────────────────
SUPPORT_ROLE_ID = int(os.getenv("SUPPORT_ROLE_ID", "0"))
ADMIN_ROLE_ID   = int(os.getenv("ADMIN_ROLE_ID",   "0"))

# ── Canali generali ─────────────────────────────────────────────
LOG_CHANNEL_ID          = int(os.getenv("LOG_CHANNEL_ID",          "0"))
TICKET_CATEGORY_ID      = int(os.getenv("TICKET_CATEGORY_ID",      "0"))
PARTNERSHIP_CATEGORY_ID = int(os.getenv("PARTNERSHIP_CATEGORY_ID", "0"))
LEVEL_CHANNEL_ID        = int(os.getenv("LEVEL_CHANNEL_ID",        "0"))
CONTROL_PANEL_CHANNEL_ID= int(os.getenv("CONTROL_PANEL_CHANNEL_ID","0"))

# ── Supporto vocale ─────────────────────────────────────────────
WAITING_CHANNEL_ID  = int(os.getenv("WAITING_CHANNEL_ID",  "0"))
STAFF_CHANNEL_ID    = int(os.getenv("STAFF_CHANNEL_ID",    "0"))
SUPPORT_CATEGORY_ID = int(os.getenv("SUPPORT_CATEGORY_ID", "0"))

# ── Impostazioni supporto vocale ─────────────────────────────────
CHANNEL_NAME_PREFIX   = "Assistenza"
EMPTY_CHANNEL_TIMEOUT = 60

# ── Database & Web Panel ─────────────────────────────────────────
DATABASE_PATH  = "database/sessions.db"

# Su Wispbyte il web panel deve bindare su 0.0.0.0 per essere raggiungibile
# dall'esterno tramite IP:porta o reverse proxy (Nginx/Caddy incluso nel panel).
# In locale puoi usare 127.0.0.1.
WEB_HOST       = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT       = int(os.getenv("WEB_PORT", "8080"))
WEB_SECRET_KEY = os.getenv("WEB_SECRET", "cambia_questa_chiave_segreta_paritymc")
WEB_USERNAME   = os.getenv("WEB_USERNAME", "admin")
WEB_PASSWORD   = os.getenv("WEB_PASSWORD", "admin123")

# URL pubblico del panel (mostrato nei comandi help e nei footer)
# Su Wispbyte imposta il dominio assegnato es: https://panel.paritymc.it
WEB_PUBLIC_URL = os.getenv("WEB_PUBLIC_URL", f"http://localhost:{WEB_PORT}")
