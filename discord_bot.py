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

    b1 = "".join(
        random.choices(chars, k=6)
    )

    b2 = "".join(
        random.choices(chars, k=6)
    )

    raw = f"{b1}-{b2}-{SECRET_SALT}"

    checksum = hashlib.md5(
        raw.encode("utf-8")
    ).hexdigest()[:4].upper()

    return f"CLEAN-{b1}-{b2}-{checksum}"


# ============================================================
# DISCORD BOT
# ============================================================

intents = discord.Intents.default()

# Needed for !genkey
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ============================================================
# ADMIN IDS
# ============================================================

ADMIN_IDS = [
    1550004507239256174
]


# ============================================================
# READY / COMMAND CLEANUP
# ============================================================

@bot.event
async def on_ready():

    print("")
    print("============================================")
    print("🤖 VIPCHAETOS BOT STARTING")
    print("============================================")
    print(f"✅ Logged in as: {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🌐 Connected guilds: {len(bot.guilds)}")
    print("")


    # ========================================================
    # IMPORTANT:
    #
    # This bot uses !genkey.
    #
    # There should NOT be a /generate slash command.
    #
    # Clear old GLOBAL application commands.
    # ========================================================

    try:

        bot.tree.clear_commands(
            guild=None
        )

        synced = await bot.tree.sync()

        print(
            f"✅ Global slash-command sync complete."
        )

        print(
            f"   Current global commands: {len(synced)}"
        )

        for command in synced:
            print(
                f"   /{command.name}"
            )

    except Exception as error:

        print(
            f"❌ Global command cleanup failed: {error}"
        )


    # ========================================================
    # CLEAR OLD GUILD COMMANDS
    # ========================================================

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
                f"✅ Guild commands cleared:"
                f" {guild.name}"
                f" ({guild.id})"
                f" -> {len(synced)} commands"
            )

        except Exception as error:

            print(
                f"❌ Could not clear guild commands "
                f"for {guild.id}: {error}"
            )


    # ========================================================
    # FINAL STATUS
    # ========================================================

    print("")
    print("============================================")
    print("🟢 VIPCHAETOS BOT READY")
    print("============================================")
    print("🔑 Key command: !genkey")
    print("🚫 /generate: removed from local command tree")
    print("============================================")
    print("")


# ============================================================
# !GENKEY
# ============================================================

@bot.command(
    name="genkey"
)
async def gen_key(ctx):

    # --------------------------------------------------------
    # ADMIN CHECK
    # --------------------------------------------------------

    if ctx.author.id not in ADMIN_IDS:

        await ctx.send(
            "❌ Wala kang permission!",
            delete_after=5
        )

        return


    # --------------------------------------------------------
    # SECRET SALT CHECK
    # --------------------------------------------------------

    if not SECRET_SALT:

        await ctx.send(
            "❌ SECRET_SALT hindi na-set sa Render!",
            delete_after=5
        )

        return


    # --------------------------------------------------------
    # GENERATE KEY
    # --------------------------------------------------------

    key = generate_key()


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

        # Delete !genkey message if possible
        try:

            await ctx.message.delete()

        except discord.Forbidden:

            pass

        except discord.HTTPException:

            pass

    except discord.Forbidden:

        await ctx.send(
            "❌ Hindi kita ma-DM. "
            "I-check ang DM settings.",
            delete_after=5
        )

    except discord.HTTPException as error:

        print(
            f"❌ Discord HTTP error while sending key: {error}"
        )

        await ctx.send(
            "❌ Hindi na-send ang key.",
            delete_after=5
        )


# ============================================================
# COMMAND ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    # Ignore unknown prefix commands
    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return


    # Missing permission
    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "❌ Wala kang permission!",
            delete_after=5
        )

        return


    # Log other errors
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
# START BOT
# ============================================================

print("🚀 Starting Discord bot...")

bot.run(
    DISCORD_TOKEN
)
