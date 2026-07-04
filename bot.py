"""
Telegram Join-Request Auto-DM Bot
----------------------------------
Kya karta hai:
1. Group/Channel me jitni PENDING join requests hain (purani) unko startup pe DM bhejta hai
2. Naye jo bhi join request bhejega, use turant DM bhejta hai
3. Optionally auto-approve bhi kar sakta hai (env var se control)

Works with either:
- BOT_TOKEN (recommended, safe)
- SESSION_STRING (your personal account, riskier - Telegram spam flag ho sakta hai)
"""

import asyncio
import os
import logging
from datetime import datetime

import aiosqlite
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, InputUserDeactivated
from pyrogram.types import ChatJoinRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("joinrequest-bot")

# ---------------- CONFIG (env vars) ----------------
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

BOT_TOKEN = os.environ.get("BOT_TOKEN")          # use this OR SESSION_STRING
SESSION_STRING = os.environ.get("SESSION_STRING")  # your personal account session

CHAT_ID = int(os.environ["CHAT_ID"])             # group/channel id (e.g. -100xxxxxxxxxx)
DM_MESSAGE = os.environ.get(
    "DM_MESSAGE",
    "Hi {name}! 👋\nThanks for requesting to join. Aapki request note kar li gayi hai."
)
AUTO_APPROVE = os.environ.get("AUTO_APPROVE", "false").lower() == "true"
DELAY_BETWEEN_DMS = float(os.environ.get("DELAY_BETWEEN_DMS", "2"))  # seconds, spam-safety ke liye

DB_PATH = "dmed_users.db"

if not BOT_TOKEN and not SESSION_STRING:
    raise SystemExit("Set either BOT_TOKEN or SESSION_STRING in environment variables.")

if BOT_TOKEN:
    app = Client("joinrequest_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    log.info("Running with BOT account.")
else:
    app = Client("joinrequest_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
    log.info("Running with USER account (higher ban risk - be careful with volume).")


# ---------------- DB HELPERS ----------------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS dmed_users (
                user_id INTEGER PRIMARY KEY,
                dmed_at TEXT
            )"""
        )
        await db.commit()


async def already_dmed(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM dmed_users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row is not None


async def mark_dmed(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO dmed_users (user_id, dmed_at) VALUES (?, ?)",
            (user_id, datetime.utcnow().isoformat()),
        )
        await db.commit()


# ---------------- CORE LOGIC ----------------
async def send_dm(user_id: int, name: str):
    """Send DM safely, handling flood wait + blocked users."""
    try:
        await app.send_message(user_id, DM_MESSAGE.format(name=name))
        await mark_dmed(user_id)
        log.info(f"DM sent to {user_id} ({name})")
    except FloodWait as e:
        log.warning(f"FloodWait {e.value}s, sleeping...")
        await asyncio.sleep(e.value + 2)
        await send_dm(user_id, name)  # retry once after wait
    except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated):
        log.info(f"Cannot DM {user_id} (blocked/invalid/deactivated). Marking done anyway.")
        await mark_dmed(user_id)
    except Exception as e:
        log.error(f"Failed to DM {user_id}: {e}")


async def handle_request(user_id: int, name: str, approve: bool):
    if await already_dmed(user_id):
        return
    await send_dm(user_id, name)
    if approve:
        try:
            await app.approve_chat_join_request(CHAT_ID, user_id)
        except Exception as e:
            log.error(f"Failed to approve {user_id}: {e}")
    await asyncio.sleep(DELAY_BETWEEN_DMS)


# ---------------- STARTUP: CLEAR EXISTING PENDING REQUESTS ----------------
async def process_pending_requests():
    log.info("Fetching existing pending join requests...")
    count = 0
    try:
        async for req in app.get_chat_join_requests(CHAT_ID):
            user = req.user
            name = user.first_name or "there"
            await handle_request(user.id, name, AUTO_APPROVE)
            count += 1
    except Exception as e:
        log.error(f"Error fetching pending requests: {e}")
    log.info(f"Processed {count} existing pending requests.")


# ---------------- LIVE HANDLER: NEW REQUESTS ----------------
@app.on_chat_join_request(filters.chat(CHAT_ID))
async def on_new_join_request(client: Client, request: ChatJoinRequest):
    user = request.from_user
    name = user.first_name or "there"
    log.info(f"New join request from {user.id} ({name})")
    await handle_request(user.id, name, AUTO_APPROVE)


# ---------------- MAIN ----------------
async def main():
    await init_db()
    await app.start()
    log.info("Bot started. Processing pending requests first...")
    await process_pending_requests()
    log.info("Now listening for new join requests...")
    await asyncio.Event().wait()  # keep running forever


if __name__ == "__main__":
    app.run(main())
