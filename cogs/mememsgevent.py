import discord
from discord.ext import commands

class MemeMsgEvent(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.msgEvents = {
            "massive" : "https://tenor.com/view/ninja-any-haircut-recommendations-low-taper-fade-you-know-what-else-is-massive-gif-3708438262570242561",
            "dragon"  : "LIKE A WHAT 🐉🔥",
            "egypt" : "https://tenor.com/view/eye-of-rah-adrian-explain-our-friendgroup-tiktok-meme-reels-gif-8580965088318146552"
        }

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        if message.guild.id != 571632708833378321: return
        if message.author == self.client.user: return
        for keyword, answer in self.msgEvents.items():
            if keyword in message.content:
                return await message.channel.send(answer)

def setup(client):
    client.add_cog(MemeMsgEvent(client))