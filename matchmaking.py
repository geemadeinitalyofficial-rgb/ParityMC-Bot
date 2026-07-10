import asyncio
from collections import deque
import bot_logger
import config

class Matchmaker:
    def __init__(self, session_manager):
        self.waiting_queue = deque()
        self.staff_queue   = deque()
        self.busy_staff    = set()
        self.lock          = asyncio.Lock()
        self.sm            = session_manager

    def add_waiting(self, uid):
        if uid not in self.waiting_queue: self.waiting_queue.append(uid)
    def remove_waiting(self, uid):
        try: self.waiting_queue.remove(uid)
        except ValueError: pass
    def add_staff(self, sid):
        if sid not in self.busy_staff and sid not in self.staff_queue:
            self.staff_queue.append(sid)
    def remove_staff(self, sid):
        try: self.staff_queue.remove(sid)
        except ValueError: pass
    def release_staff(self, sid):
        self.busy_staff.discard(sid)

    async def try_match(self, bot):
        async with self.lock:
            while self.waiting_queue and self.staff_queue:
                uid = self.waiting_queue[0]
                sid = self.staff_queue[0]
                guild = bot.get_guild(config.GUILD_ID)
                if not guild: return
                mu = guild.get_member(uid)
                ms = guild.get_member(sid)
                if not mu or not (mu.voice and mu.voice.channel and mu.voice.channel.id == config.WAITING_CHANNEL_ID):
                    self.waiting_queue.popleft(); continue
                if not ms or not (ms.voice and ms.voice.channel and ms.voice.channel.id == config.STAFF_CHANNEL_ID):
                    self.staff_queue.popleft(); continue
                self.waiting_queue.popleft()
                self.staff_queue.popleft()
                self.busy_staff.add(sid)
                try:
                    await self.sm.create_session(bot, mu, ms)
                except Exception as e:
                    await bot_logger.log(bot, f"Errore matchmaking: {e}", "ERROR")
                    self.busy_staff.discard(sid)
                    self.waiting_queue.appendleft(uid)
                    self.staff_queue.appendleft(sid)
                    return
