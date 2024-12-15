import discord
from discord.ext import commands
import datetime
import os
import sys
from dotenv import load_dotenv

#   presences, members and message_content intents are privileged intents
#   This intent is privileged, meaning that bots in over 100 guilds that require this intent would need to request this intent on the Developer Portal.
#   https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.presences
intents = discord.Intents.all()

load_dotenv()
client = commands.Bot(intents=intents, command_prefix=commands.when_mentioned)

def printFormat(msg: str, type: str = "message"):
    """small function to simplify console output formatting

    Args:
        msg (str): the message we want to print
        type (str): "message", "warning" or "error". Set to "message" by default.
    """

    #    symbols used for formatting
    types = {
        "message" : ">>>",
        "warning" : "###",
        "error"   : "!!!"
    }

    #    check if right type is used
    if type not in types.keys():
        return printFormat(
            f"Incorrect type argument in printFormat()\n" +
            f"Original message: \n{msg}",
            type="error"
            )

    #    number of spaces preceding the console message (i just think it looks neat)
    indentation = 4
    #    time for timestamp, formatted as hrs:min:sec
    cur_time = datetime.datetime.now().strftime("%H:%M:%S")

    print(
        f"{' ' * indentation}"  # print {indentation} amount of spaces
        + f"[{cur_time}]  "     # formatted timestamp plus two spaces
        + f"{types[type]}  "     # type symbol as seen in {types} dict plus two spaces
        + msg                   # the message itself
        )
    
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

#    Startup

@client.event
async def on_ready():
    num_guilds = len(client.guilds)
    print('\n')
    printFormat("Client online")
    printFormat(f"Logged in as {client.user.name}")
    printFormat(f"User ID: {client.user.id}")
    printFormat(f"Currently in {num_guilds} guilds.")
    if restarted and restart_channel_id:
        channel = client.get_channel(restart_channel_id)
        if channel:
            await channel.send("back")
    print('\n')

#    Automatically load cogs from the cogs directory
cogs_dir = "cogs"
cogs = [f"{cogs_dir}.{filename[:-3]}" for filename in os.listdir(cogs_dir) if filename.endswith(".py")]
client.load_extensions(*cogs)
client.run(str(os.getenv('BOT_TOKEN')))