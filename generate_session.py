"""
Sirf tab chalao agar tum PERSONAL ACCOUNT (SESSION_STRING) use karna chahte ho.
Bot account use kar rahe ho to iski zaroorat nahi hai.

Run: python generate_session.py
Phone number + OTP maangega, phir ek session string print karega.
Us string ko SESSION_STRING env var me daal do.
"""

from pyrogram import Client

API_ID = int(input("API_ID: "))
API_HASH = input("API_HASH: ")

with Client("session_gen", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
    print("\nYour SESSION_STRING (isko safe rakho, kisi ko mat do):\n")
    print(app.export_session_string())
