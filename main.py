import discord
from discord.ext import commands
import time
import os
import sys
import subprocess
from dotenv import load_dotenv
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import tools


#   presences, members and message_content intents are privileged intents
#   This intent is privileged, meaning that bots in over 100 guilds that require this intent would need to request this intent on the Developer Portal.
#   https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.presences
intents = discord.Intents.all()

#   updating the bot through the git repo
#   requires apscheduler
scheduler = BackgroundScheduler()

load_dotenv()
client = commands.Bot(intents=intents, command_prefix=commands.when_mentioned)
    
@client.slash_command(name="invite", description="Generates an invite link for the bot")
async def generate_invite(ctx):
    """Generates an invite link for the bot"""
    permissions = discord.Permissions(permissions=8)  # Administrator permissions
    invite_link = discord.utils.oauth_url(client.user.id, permissions=permissions)
    await ctx.respond(f"Invite link: {invite_link}")


@client.slash_command(name="nanba", description="test command")
async def nanba(ctx):
    await ctx.respond("fortnite")

@client.command(name='await')
async def eval_await_command(ctx, *, code: str):
    """Evaluates code that needs to be awaited"""
    if not await client.is_owner(ctx.author) : return await ctx.send("fuck off")
    try:
        # Define an async function to execute the code
        async def execute_code(ctx):
            exec(
                f'async def __eval_function(ctx):\n await' +
                ''.join(f'    {line}\n' for line in code.split('\n'))
            )
            return await locals()['__eval_function'](ctx)

        result = await execute_code(ctx)
        if result != None:
            await ctx.send(f"Result: {result}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.command(name="eval")
async def eval_command(ctx, *, code: str):
    if not await client.is_owner(ctx.author) : return await ctx.send("fuck off")
    try:
        result = eval(code)
        await ctx.send(f"Result: {result}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.command(name="load")
async def load_cog(ctx, extension: str):
    """Loads a cog"""
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    try:
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded {extension} cog.")
    except Exception as e:
        await ctx.send(f"Failed to load {extension} cog. Error: {e}")

@client.command(name="unload")
async def unload_cog(ctx, extension: str):
    """Unloads a cog"""
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    try:
        client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unloaded {extension} cog.")
    except Exception as e:
        await ctx.send(f"Failed to unload {extension} cog. Error: {e}")

@client.command(name="reload")
async def reload_cog(ctx, extension: str):
    """Reloads a cog"""
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    try:
        client.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Reloaded {extension} cog.")
    except Exception as e:
        await ctx.send(f"Failed to reload {extension} cog. Error: {e}")

@client.command(name="embed")
async def embed_test(ctx):
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    msg = "The bot is up to date!"
    await tools.respondEmbed(
        title="Update check complete!",
        emoji="👍",
        msg=msg,
        type="message",
        ctx=ctx, client=client
    )

# Check if the bot was restarted using the restart command
restarted = os.getenv("RESTARTED", "false").lower() == "true"
restart_channel_id = int(os.getenv("RESTART_CHANNEL_ID", "0"))

@client.command(name="restart", aliases=["kys"])
async def restart_bot(ctx):
    """Restarts the bot"""
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    await ctx.send("Restarting bot...")
    os.environ["RESTARTED"] = "true"
    os.environ["RESTART_CHANNEL_ID"] = str(ctx.channel.id)
    os.execv(sys.executable, ['python'] + sys.argv)

@client.command(name="shutdown", aliases=["exit", "end"])
@commands.is_owner()
async def shutdown(ctx):
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    await ctx.send("Logging out...")
    sys.exit()

@client.command(name="update")
async def update_bot(ctx):
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    update_status = check_updates()
    if update_status == 0:
        msg = "The bot is up to date!"
        await tools.respondEmbed(
            title="Update check complete!",
            emoji="👍",
            msg=msg,
            type="message",
            ctx=ctx, client=client
        )
    elif update_status == 1:
        msg = "Update available, wanna install it?"
        await tools.respondEmbed(
            title="Update Available!",
            emoji="⚠️",
            msg=msg,
            type="warning",
            ctx=ctx, client=client
        )

        answer = False
        positiveAnswers = ['yes', 'y', 'ye', 'yeah']
        if str(answer.lower()) in positiveAnswers:
            pull = subprocess.run(args=['git', 'pull'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if pull.returncode != 0:
                tools.printFormat(f"Update failed! This can happen if you modified any files. I'll stop checking for updates until the next reboot of the bot. \n-----\n{pull.stderr} \n {pull.stdout}\n-----\n", "error")
                msg = "Update failed! Check the console."
                await tools.respondEmbed(
                    title="Update failed!",
                    emoji="🔴",
                    msg=msg,
                    type="error",
                    ctx=ctx, client=client
                )
                scheduler.pause()
            else:
                tools.printFormat("Update complete! Restarting in 10 seconds...", "warning")
                msg = "Restarting in 10 seconds..."
                await tools.respondEmbed(
                    title="Update complete!",
                    emoji="👍",
                    msg=msg,
                    type="warning",
                    ctx=ctx, client=client
                )
                
                time.sleep(10)
                os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    
    elif update_status == 2:
        tools.printFormat(f"Update failed! Git is not installed to PATH.", "error")
        msg = "Update failed! Git is not installed to PATH. "
        await tools.respondEmbed(
            title="Update failed!",
            emoji="🔴",
            msg=msg,
            type="error",
            ctx=ctx, client=client
        )
        scheduler.pause()

#    Startup

@client.event
async def on_ready():
    num_guilds = len(client.guilds)
    print('\n')
    tools.printFormat("Client online")
    tools.printFormat(f"Logged in as {client.user.name}")
    tools.printFormat(f"User ID: {client.user.id}")
    tools.printFormat(f"Currently in {num_guilds} guilds.")
    if restarted and restart_channel_id:
        channel = client.get_channel(restart_channel_id)
        if channel:
            await channel.send("back")
    print('\n')

@scheduler.scheduled_job('interval', hours=1)
def check_updates():
    """Update check, requires git installed to PATH. Originally from Aigis idk i was on crack when i wrote this."""
    tools.printFormat("Checking for bot updates...")
    notif = "Your branch is behind"
    notif2 = ", and can be fast-forwarded"   # just to be sure
    
    try:
        subprocess.run(args=['git', 'remote', 'update'])
        status = subprocess.run(args=['git', 'status'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        tools.printFormat("Git not found. Make sure it's installed to PATH.", "error")
        scheduler.pause()
        return 2
    if notif in status.stdout and notif2 in status.stdout:
        tools.printFormat("Update available! Run @bot update to get the new version.", "warning")
        return 1
    else:
        tools.printFormat("Update check complete, you're up to date!")

#    Add updates to schedule
check_updates()
#    Automatically load cogs from the cogs directory
cogs_dir = "cogs"
cogs = [f"{cogs_dir}.{filename[:-3]}" for filename in os.listdir(cogs_dir) if filename.endswith(".py")]
client.load_extensions(*cogs)
client.run(str(os.getenv('BOT_TOKEN')))