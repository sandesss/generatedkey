@bot.command(name="genkey")
async def gen_key(ctx):

    print("")
    print("========== GENKEY REQUEST ==========")
    print(f"👤 User    : {ctx.author}")
    print(f"🆔 User ID : {ctx.author.id}")
    print(f"🔐 Admins  : {sorted(ADMIN_IDS)}")

    if ctx.author.id not in ADMIN_IDS:
        print("❌ ACCESS DENIED")

        await ctx.send(
            "❌ Wala kang permission!",
            delete_after=5
        )
        return

    print("✅ ADMIN VERIFIED")

    if not SECRET_SALT:
        print("❌ SECRET_SALT MISSING")

        await ctx.send(
            "❌ SECRET_SALT hindi na-set sa Render!",
            delete_after=5
        )
        return

    key = generate_key()

    print(f"🔑 GENERATED: {key}")

    embed = discord.Embed(
        title="🔑 License Key Generated",
        description=f"||`{key}`||",
        color=0x00F2FE
    )

    embed.set_footer(
        text="VIPCHAETOS Neural Suite"
    )

    try:
        await ctx.author.send(embed=embed)

        await ctx.send(
            "✅ Na-send na sa iyong DM!",
            delete_after=5
        )

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        print("✅ KEY SENT")
        print("==================================")
        print("")

    except discord.Forbidden:
        await ctx.send(
            "❌ Hindi kita ma-DM. I-check ang DM settings.",
            delete_after=5
        )

    except discord.HTTPException as error:
        print(f"❌ Discord error: {error}")

        await ctx.send(
            "❌ Hindi na-send ang key.",
            delete_after=5
        )
