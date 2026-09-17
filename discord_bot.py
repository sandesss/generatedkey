import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import hashlib
import random
import string
import os
import logging

# =====================
# LOGGING
# =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

log = logging.getLogger("vipchaetos_bot")

# =====================
# FLASK KEEP-ALIVE
# =====================
app = Flask("")

@app.route("/")
def home():
    return "VIPCHAETOS Bot is alive!"

def run_flask():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )

def keep_alive():
    thread = Thread(target=run_flask, daemon=True)
    thread.start()

# =====================
# KEY GENERATOR
# =====================
SECRET_SALT = os.environ.get("SECRET_SALT")

def generate_key():
    chars = string.ascii_uppercase + string.digits

    b1 = "".join(random.choices(chars, k=6))
    b2 = "".join(random.choices(chars, k=6))

    raw = f"{b1}-{b2}-{SECRET_SALT}"

    checksum = hashlib.md5(
        raw.encode("utf-8")
    ).hexdigest()[:4].upper()

    return f"CLEAN-{b1}-{b2}-{checksum}"

# =====================
# DISCORD BOT
# =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =====================
# ADMIN IDS
# =====================
ADMIN_IDS = [
    1550004507239256174
]

# =====================
# REMOVE OLD SLASH COMMANDS
# =====================
@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")

    # ---------------------------------
    # REMOVE OLD GLOBAL SLASH COMMANDS
    # ---------------------------------
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()

        print("✅ Old GLOBAL slash commands cleared.")
    except Exception as e:
        print(f"⚠️ Global command cleanup error: {e}")

    # ---------------------------------
    # REMOVE OLD GUILD SLASH COMMANDS
    # ---------------------------------
    for guild in bot.guilds:
        try:
            bot.tree.clear_commands(
                guild=discord.Object(id=guild.id)
            )

            await bot.tree.sync(
                guild=discord.Object(id=guild.id)
            )

            print(
                f"✅ Old slash commands cleared from: "
                f"{guild.name} ({guild.id})"
            )

        except Exception as e:
            print(
                f"⚠️ Guild cleanup error "
                f"({guild.id}): {e}"
            )

    print("================================")
    print("🤖 VIPCHAETOS BOT READY")
    print("🔑 Use: !genkey")
    print("================================")

# =====================
# !GENKEY
# =====================
@bot.command(name="genkey")
async def gen_key(ctx):

    # ADMIN CHECK
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send(
            "❌ Wala kang permission!",
            delete_after=5
        )
        return

    # SECRET CHECK
    if not SECRET_SALT:
        await ctx.send(
            "❌ SECRET_SALT hindi na-set!",
            delete_after=5
        )
        return

    # GENERATE KEY
    key = generate_key()

    embed = discord.Embed(
        title="🔑 License Key Generated",
        description=f"||`{key}`||",
        color=0x00F2FE
    )

    embed.set_footer(
        text="VIPCHAETOS Neural Suite"
    )

    try:
        # SEND KEY TO ADMIN DM
        await ctx.author.send(embed=embed)

        # CONFIRMATION
        await ctx.send(
            "✅ Na-send na sa iyong DM!",
            delete_after=5
        )

        # DELETE COMMAND MESSAGE
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    except discord.Forbidden:
        await ctx.send(
            "❌ Hindi kita ma-DM. "
            "I-check ang DM settings."
        )

# =====================
# ERROR HANDLER
# =====================
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ Wala kang permission!",
            delete_after=5
        )
        return

    print(f"❌ Command error: {error}")

# =====================
# START
# =====================
keep_alive()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable is missing!"
    )

bot.run(DISCORD_TOKEN)
