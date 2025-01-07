from datetime import datetime, timezone
import discord

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
    cur_time = datetime.now().strftime("%H:%M:%S")

    print(
        f"{' ' * indentation}"  # print {indentation} amount of spaces
        + f"[{cur_time}]  "     # formatted timestamp plus two spaces
        + f"{types[type]}  "     # type symbol as seen in {types} dict plus two spaces
        + msg                   # the message itself
        )
    
def get_color(c: str):
    colors = {
        "message" : 0x9472da,
        "warning" : 0xdd2e44,
        "error"   : 0xdd2e44,
        "default" : discord.Color.default,
        }
    if c in colors:
        return colors[c]
    else:
        printFormat("Invalid color provided to get_color()", "warn")
        return discord.Color.default
    
async def respondEmbed(
    title: str,
    emoji = None,
    msg = None,
    type: str = "message",
    ctx = None,
    client = None
):
    #    check if right type is used
    types = ["message", "warning", "error"]
    if type not in types: type = "message" # fallback message type
    if not msg: msg = "(No message provided)" # fallback embed content
    if emoji: title = emoji + " " + title # format title string if emoji was provided
    color = get_color(type)
    if not ctx or not client:
        printFormat("respondEmbed didn't get ctx and/or client", "error")
        return ctx.respond(f"check the console dumbass.\nOriginal message: '{msg}'")
    
    embed = discord.Embed(title=title, description=msg, color=color, timestamp=datetime.now(timezone.utc))
    embed.set_footer(icon_url=client.user.avatar.url, text=client.user.name)
    await ctx.respond(embed=embed)