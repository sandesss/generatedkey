import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import hashlib
import random
import string
import os
import logging

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

log = logging.getLogger("vipchaetos_bot")


# ============================================================
# FLASK KEEP-ALIVE
# ============================================================

app = Flask(__name__)


@app.route("/")
def home():
    return "VIPCHAETOS Bot is alive!"


def run_flask():
    port = int(os.environ.get("PORT", "8080"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )


def keep_alive():
    thread = Thread(
        target=run_flask,
        daemon=True
    )
    thread.start()


# ============================================================
# KEY GENERATOR
# ============================================================

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


# ============================================================
# DISCORD BOT
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ============================================================
# ADMIN IDS
#
# You can also set ADMIN_IDS in Render.
#
# Example:
# ADMIN_IDS=1550004507239256174
#
# Multiple admins:
# ADMIN_IDS=123456789,987654321
# ============================================================

DEFAULT_ADMIN_IDS = {
    1550004507239256174
}


def load_admin_ids():
    raw = os.environ.get("ADMIN_IDS", "").strip()

    if not raw:
        return DEFAULT_ADMIN_IDS.copy()

    ids = set()

    for value in raw.split(","):
        value = value.strip()

        if value.isdigit():
            ids.add(int(value))

    return ids


ADMIN_IDS = load_admin_ids()


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    print("")
    print("============================================")
    print("🤖 VIPCHAETOS BOT")
    print("============================================")
    print(f"✅ Logged in as : {bot.user}")
    print(f"🆔 Bot ID      : {bot.user.id}")
    print(f"🌐 Guilds      : {len(bot.guilds)}")
    print("")

    print("🔐 ADMIN IDS:")
    for admin_id in ADMIN_IDS:
        print(f"   {admin_id}")

    print("")

    # --------------------------------------------------------
    # CLEAR OLD GLOBAL SLASH COMMANDS
    # --------------------------------------------------------

    try:
        bot.tree.clear_commands(guild=None)

        synced = await bot.tree.sync()

        print(
            f"✅ Global slash commands synced: {len(synced)}"
        )

        if synced:
            for command in synced:
                print(f"   /{command.name}")
        else:
            print("   No global slash commands.")

    except Exception as error:

        print(
            f"⚠️ Global command cleanup error: {error}"
        )


    # --------------------------------------------------------
    # CLEAR OLD GUILD SLASH COMMANDS
    # --------------------------------------------------------

    for guild in bot.guilds:

        try:

            guild_object = discord.Object(
                id=guild.id
            )

            bot.tree.clear_commands(
                guild=guild_object
            )

            synced = await bot.tree.sync(
                guild=guild_object
            )

            print(
                f"✅ Guild commands cleared: "
                f"{guild.name} ({guild.id})"
            )

        except Exception as error:

            print(
                f"⚠️ Guild cleanup error "
                f"{guild.id}: {error}"
            )


    print("")
    print("============================================")
    print("🟢 BOT READY")
    print("============================================")
    print("🔑 Use: !genkey")
    print("🚫 No /generate command")
    print("============================================")
    print("")


# ============================================================
# !GENKEY
# ============================================================

@bot.command(name="genkey")
async def gen_key(ctx):

    # --------------------------------------------------------
    # ACTUAL USER ID
    # --------------------------------------------------------

    user_id = ctx.author.id

    print("")
    print("========== GENKEY REQUEST ==========")
    print(f"👤 User       : {ctx.author}")
    print(f"🆔 User ID    : {user_id}")
    print(f"🔐 Admin IDs  : {sorted(ADMIN_IDS)}")


    # --------------------------------------------------------
    # ADMIN CHECK
    # --------------------------------------------------------

    if user_id not in ADMIN_IDS:

        print("❌ RESULT     : ACCESS DENIED")
        print("====================================")
        print("")

        await ctx.send(
            "❌ Wala kang permission!",
            delete_after=5
        )

        return


    print("✅ RESULT     : ADMIN VERIFIED")


    # --------------------------------------------------------
    # SECRET SALT CHECK
    # --------------------------------------------------------

    if not SECRET_SALT:

        print("❌ SECRET_SALT is missing!")
        print("====================================")

        await ctx.send(
            "❌ SECRET_SALT hindi na-set sa Render!",
            delete_after=5
        )

        return


    # --------------------------------------------------------
    # GENERATE KEY
    # --------------------------------------------------------

    key = generate_key()

    print(f"🔑 KEY GENERATED: {key}")


    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title="🔑 License Key Generated",
        description=f"||`{key}`||",
        color=0x00F2FE
    )

    embed.set_footer(
        text="VIPCHAETOS Neural Suite"
    )


    # --------------------------------------------------------
    # SEND TO ADMIN DM
    # --------------------------------------------------------

    try:

        await ctx.author.send(
            embed=embed
        )

        await ctx.send(
            "✅ Na-send na sa iyong DM!",
            delete_after=5
        )

        # Delete !genkey message
        try:

            await ctx.message.delete()

        except discord.Forbidden:

            pass

        except discord.HTTPException:

            pass

        print("✅ KEY SENT TO ADMIN DM")
        print("====================================")
        print("")

    except discord.Forbidden:

        print("❌ Cannot DM this user.")
        print("====================================")

        await ctx.send(
            "❌ Hindi kita ma-DM. "
            "I-check ang DM settings.",
            delete_after=5
        )

    except discord.HTTPException as error:

        print(
            f"❌ Discord HTTP error: {error}"
        )

        print("====================================")

        await ctx.send(
            "❌ Hindi na-send ang key.",
            delete_after=5
        )


# ============================================================
# COMMAND ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    print(
        f"❌ Prefix command error: {error}"
    )


# ============================================================
# START FLASK
# ============================================================

keep_alive()


# ============================================================
# DISCORD TOKEN
# ============================================================

DISCORD_TOKEN = os.environ.get(
    "DISCORD_TOKEN"
)

if not DISCORD_TOKEN:

    raise RuntimeError(
        "❌ DISCORD_TOKEN environment variable is missing!"
    )


# ============================================================
# START
# ============================================================

print("🚀 Starting Discord bot...")

bot.run(
    DISCORD_TOKEN
)
