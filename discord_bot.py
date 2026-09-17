import os
import hashlib
import random
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord import app_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger("vipchaetos_bot")

# ✅ FIX 1: Tamang env var name (may fallback kung "token" ang gamit mo sa Render)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("token")
SECRET_SALT = os.getenv("SECRET_SALT", "VIPCHAETOS_SECRET_KEY_2026")

# ✅ FIX 2: Port para sa Render (auto-detect ng Render ang PORT env var)
PORT = int(os.getenv("PORT", "10000"))

TEST_GUILD_ID = 0


# ---------- Keep-alive HTTP server (para ma-detect ng Render ang port) ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive")

    def log_message(self, fmt, *args):
        pass  # huwag i-log ang mga health check


def start_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        log.info(f"Health server running on port {PORT}")
    except Exception:
        log.exception("Failed to start health server")


# ---------- Bot ----------
class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if TEST_GUILD_ID:
            guild = discord.Object(id=TEST_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info(f"Synced to guild {TEST_GUILD_ID}")
        else:
            synced = await self.tree.sync()
            log.info(f"Synced {len(synced)} global command(s)")


client = Bot()


@client.event
async def on_ready():
    log.info(f"Logged in as {client.user} ({client.user.id})")
    log.info(f"Connected to {len(client.guilds)} server(s)")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for /generate"
        )
    )


@client.tree.command(name="generate", description="Gumawa ng License Key")
async def generate(interaction: discord.Interaction):
    log.info(f"/generate ni {interaction.user} ({interaction.user.id})")
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)

        b1 = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4))
        b2 = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4))

        raw = f"{b1}-{b2}-{SECRET_SALT}"
        checksum = hashlib.md5(raw.encode()).hexdigest()[:4].upper()
        key = f"CLEAN-{b1}-{b2}-{checksum}"

        await interaction.followup.send(
            f"🔑 **Generated License Key:**\n`{key}`",
            ephemeral=True
        )
        log.info("Generated key successfully")
    except Exception:
        log.exception("Error sa /generate")
        try:
            await interaction.followup.send("❌ May error. Subukan ulit.", ephemeral=True)
        except Exception:
            log.exception("Hindi ma-send ang error message")


@client.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    log.error(f"App command error: {error}")
    try:
        if interaction.response.is_done():
            await interaction.followup.send("❌ May error sa command.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ May error sa command.", ephemeral=True)
    except Exception:
        log.exception("Error handler failed")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN environment variable is missing. "
            "Add it in Render Dashboard -> Environment."
        )
    start_health_server()   # ✅ FIX 2: buksan ang port bago mag-login ang bot
    client.run(DISCORD_TOKEN)
