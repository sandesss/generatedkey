# bot.py
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import hashlib
import random
import string
import os

# =====================
# FLASK KEEP-ALIVE
# =====================
app = Flask('')

@app.route('/')
def home():
    return 'VIPCHAETOS Bot is alive!'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# =====================
# KEY GENERATOR
# =====================
SECRET_SALT = os.environ.get("SECRET_SALT")  # Sa Render env vars ito, HINDI sa code!

def generate_key():
    chars = string.ascii_uppercase + string.digits
    b1 = ''.join(random.choices(chars, k=6))
    b2 = ''.join(random.choices(chars, k=6))
    raw = f"{b1}-{b2}-{SECRET_SALT}"
    checksum = hashlib.md5(raw.encode()).hexdigest()[:4].upper()
    return f"CLEAN-{b1}-{b2}-{checksum}"

# =====================
# DISCORD BOT
# =====================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Ilagay ang iyong Discord User ID dito (pwede marami)
ADMIN_IDS = [
    1504729516742807623,  # <-- palitan ng iyong actual Discord ID
]

@bot.event
async def on_ready():
    print(f'✅ Bot online: {bot.user}')

@bot.command(name='genkey')
async def gen_key(ctx):
    # Admin check
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send("❌ Wala kang permission na mag-generate ng key!")
        return

    if not SECRET_SALT:
        await ctx.send("❌ SECRET_SALT hindi na-set sa server!")
        return

    key = generate_key()

    embed = discord.Embed(
        title="🔑 License Key Generated",
        description=f"||`{key}`||",
        color=0x00f2fe
    )
    embed.set_footer(text="VIPCHAETOS Neural Suite")

    try:
        await ctx.author.send(embed=embed)
        await ctx.send("✅ Na-send na ang key sa iyong DM!", delete_after=5)
        await ctx.message.delete()  # Para hindi makita ng iba ang command
    except discord.Forbidden:
        await ctx.send("❌ Hindi ko ma-DM ka. I-check ang iyong DM settings.")

keep_alive()
bot.run(os.environ.get("DISCORD_TOKEN"))
