import discord
from discord.ext import commands
import time
import os
import sys
import subprocess
from dotenv import load_dotenv
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
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

@client.command(name="print", aliases=['gimme'])
async def print_log_contents(ctx, lines):
    if not await client.is_owner(ctx.author): return await ctx.send("fuck off")
    if os.path.isfile("./log.txt"):
        msg  =  "```\n"
        msg += f"Last {lines} lines in log.txt:\n\n"
        with open("log.txt") as file:
            # print last n lines
            lines = int(lines)
            if len(file.readlines()) < lines: lines = len(file.readlines())
            for line in (file.readlines() [-lines:]):
                msg += f"{line}\n"
        msg +=  "```"
    else:
        msg = "Couldn't do that as the log file doesn't exist."
        await tools.respondEmbed(
            title="Error",
            emoji="⚠️",
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

        class UpdateButtons(discord.ui.View):

            @discord.ui.button(style=discord.ButtonStyle.green, custom_id="yea", label="Update")
            async def yesbutton(self, button, interaction: discord.Interaction):
                if not await client.is_owner(interaction.user): return
                self.disable_all_items()
                origin = interaction.message
                await origin.edit(view=self)
                pull = subprocess.run(args=['git', 'pull'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if pull.returncode != 0:
                    tools.printFormat(f"Update failed! This can happen if you modified any files. I'll stop checking for updates until the next reboot of the bot. \n-----\n{pull.stderr} \n {pull.stdout}\n-----\n", "error")
                    msg = "Update failed! Check the console."
                    await interaction.response.send_message(content=msg)
                    try: scheduler.pause()
                    except SchedulerNotRunningError: pass
                else:
                    tools.printFormat("Update complete! Restarting in 5 seconds...", "warning")
                    msg = "Restarting in 5 seconds..."
                    await interaction.response.send_message(content=msg)
                    
                    time.sleep(5)
                    os.environ["RESTARTED"] = "true"
                    os.environ["RESTART_CHANNEL_ID"] = str(ctx.channel.id)
                    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
                await interaction.delete_original_response()

            @discord.ui.button(style=discord.ButtonStyle.red, custom_id="nah", label="Nope")
            async def nobutton(self, button, interaction):
                if not await client.is_owner(interaction.user): return
                self.disable_all_items()
                origin = interaction.message
                await origin.edit(view=self)
                msg = "Okay, not updating."
                await interaction.response.send_message(content=msg)
                

        await tools.respondEmbed(
            title="Update Available!",
            emoji="⚠️",
            msg=msg,
            type="warning",
            ctx=ctx, client=client, view=UpdateButtons(timeout=30)
        )

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
        try: scheduler.pause()
        except SchedulerNotRunningError: pass
    
    else:
        tools.printFormat(f"Something went wrong while updating.", "error")
        msg = "Something went wrong while updating. "
        await tools.respondEmbed(
            title="Update failed!",
            emoji="🔴",
            msg=msg,
            type="error",
            ctx=ctx, client=client
        )
        try: scheduler.pause()
        except SchedulerNotRunningError: pass

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
        return 0

#    Add updates to schedule
check_updates()
#    Automatically load cogs from the cogs directory
cogs_dir = "cogs"
cogs = [f"{cogs_dir}.{filename[:-3]}" for filename in os.listdir(cogs_dir) if filename.endswith(".py")]
client.load_extensions(*cogs)
client.run(str(os.getenv('BOT_TOKEN')))