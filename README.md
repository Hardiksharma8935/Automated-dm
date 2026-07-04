Join Request Auto-DM Bot
Group/channel ki join requests (purani + nayi) wale users ko automatically DM bhejta hai.
Setup
1. Credentials lo
https://my.telegram.org → API_ID aur API_HASH lo
Bot account ke liye: @BotFather → /newbot → BOT_TOKEN milega
2. Bot ko admin banao
Apne group/channel me bot (ya apna account agar SESSION_STRING use kar rahe ho) ko admin banao,
"Add Users" / "Approve New Members" permission zaroor do — isi se join request events milte hain.
3. CHAT_ID aur ADMIN_ID pata karo
Group/channel ka ID -100 se start hota hai. @userinfobot ya @RawDataBot group me add karke pata kar sakte ho.
Apna personal ADMIN_ID (numeric) @userinfobot ko personally DM karke pata karo.
4. Local test (optional)
Bash
Deploy on Railway (GitHub se)
Ye poora folder GitHub repo me push karo
https://railway.app → New Project → Deploy from GitHub repo
Apna repo select karo
Railway Variables tab me ye env vars daalo:
API_ID
API_HASH
BOT_TOKEN (ya SESSION_STRING agar personal account use kar rahe ho)
CHAT_ID
DM_MESSAGE
AUTO_APPROVE
DELAY_BETWEEN_DMS
ADMIN_ID
Railway Procfile dekh ke automatically python bot.py run kar dega
Deploy hote hi bot pending requests process karega, phir naye requests ke liye listen karega
Message relay (chat with users via bot)
Koi bhi user bot ko private message bhejega → woh message tumhare (ADMIN_ID) DM me forward ho jayega, saath me uska naam/username/id.
Us forwarded message pe reply karo (Telegram me swipe/long-press → Reply) → tumhara reply automatically usi user ko bhej diya jayega.
Bina reply kiye normal message bheja to relay nahi hoga — reply karna zaroori hai taaki bot ko pata chale kis user ko bhejna hai.
Important notes
Bot account safe hai — Telegram officially isi use-case ke liye chat_join_request events deta hai.
Personal account (SESSION_STRING) risky hai — bulk automated DMs se spam-report/ban ho sakta hai. Agar use karna hi hai to DELAY_BETWEEN_DMS zyada rakho (5-10 sec) aur volume kam rakho.
dmed_users.db (SQLite) duplicate DM rokta hai — restart hone par purane users ko dubara DM nahi jayega.
Railway free tier restart pe local SQLite file reset ho sakti hai agar persistent volume attach nahi kiya — agar ye chahiye to Railway me Volume add karke dmed_users.db ko usme point karo.
