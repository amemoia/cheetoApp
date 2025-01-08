import discord
from discord.ext import commands

# just some inside jokes for a server im in
# that being said, this could eventually be used to make a proper message triggers feature

class MsgEvent(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.msgEvents = {
            "massive" : "https://tenor.com/view/ninja-any-haircut-recommendations-low-taper-fade-you-know-what-else-is-massive-gif-3708438262570242561",
            "dragon"  : "LIKE A WHAT 🐉🔥",
            "egypt" : "https://tenor.com/view/eye-of-rah-adrian-explain-our-friendgroup-tiktok-meme-reels-gif-8580965088318146552",
            "crazy" : "https://tenor.com/view/vaas-far-cry3-that-is-crazy-gif-26006603"
        }

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        if message.guild.id != 571632708833378321: return
        if message.author == self.client.user: return
        for keyword, answer in self.msgEvents.items():
            if keyword in message.content.lower():
                return await message.channel.send(answer)

def setup(client):
    client.add_cog(MsgEvent(client))