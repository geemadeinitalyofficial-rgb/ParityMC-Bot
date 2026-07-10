import datetime
import discord
import config
import database

async def log(bot, message, level="INFO"):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {message}")
    try: database.log_event(message, level)
    except: pass
    if not config.LOG_CHANNEL_ID: return
    ch = bot.get_channel(config.LOG_CHANNEL_ID)
    if not ch: return
    color = {"INFO": discord.Color.blurple(), "WARN": discord.Color.orange(),
             "ERROR": discord.Color.red(), "OK": discord.Color.green()}.get(level, discord.Color.blurple())
    embed = discord.Embed(description=message, color=color, timestamp=datetime.datetime.now())
    try: await ch.send(embed=embed)
    except: pass
