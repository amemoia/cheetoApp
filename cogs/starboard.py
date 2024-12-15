import discord
from discord.ext import commands
import json
import os

class Starboard(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.settings = self.load_settings()

    def load_settings(self):
        data_path = "data"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        settings_file = os.path.join(data_path, "starboard_settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                return json.load(f)
        return {}

    def save_settings(self):
        data_path = "data"
        settings_file = os.path.join(data_path, "starboard_settings.json")
        with open(settings_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def initialize_guild_settings(self, guild_id):
        if guild_id not in self.settings:
            self.settings[guild_id] = {
                "starboard_channel": None,
                "required_stars": 3,
                "emojis": ["⭐"],
                "user_blacklist": [],
                "channel_blacklist": []
            }
            self.save_settings()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.initialize_guild_settings(guild.id)

    starboard = discord.SlashCommandGroup("starboard", "Commands related to the starboard")
    blacklist = starboard.create_subgroup("blacklist", "Manage the starboard blacklist")

    @starboard.command(name="settings", description="Edit the starboard configuration")
    @discord.option("channel", description="Where to send starred messages", type=discord.TextChannel)
    @discord.option("required-stars", description="Number of stars required to be added", type=int)
    @discord.option("emojis", description="Emojis to use for starring messages (comma-separated, max 10)", type=str)
    async def star_settings(
        self,
        ctx,
        channel: discord.TextChannel,
        required_stars: int,
        emojis: str):
        guild_id = ctx.guild.id
        self.initialize_guild_settings(guild_id)
        emojis_list = emojis.split(",")[:10]
        self.settings[guild_id]["starboard_channel"] = channel.id
        self.settings[guild_id]["required_stars"] = required_stars
        self.settings[guild_id]["emojis"] = emojis_list
        self.save_settings()
        await ctx.respond(f"Starboard settings updated: Channel - {channel.mention}, Required Stars - {required_stars}, Emojis - {', '.join(emojis_list)}")

    @blacklist.command(name="add", description="Add a user or channel to the blacklist")
    @discord.option("user", description="The user to add", type=discord.User, required=False)
    @discord.option("channel", description="The channel to add", type=discord.TextChannel, required=False)
    async def blacklist_add(
        self,
        ctx,
        user: discord.User = None,
        channel: discord.TextChannel = None):
        guild_id = ctx.guild.id
        self.initialize_guild_settings(guild_id)
        if user:
            if user.id not in self.settings[guild_id]["user_blacklist"]:
                self.settings[guild_id]["user_blacklist"].append(user.id)
                self.save_settings()
                await ctx.respond(f"User {user.mention} added to the blacklist.")
            else:
                await ctx.respond(f"User {user.mention} is already in the blacklist.")
        elif channel:
            if channel.id not in self.settings[guild_id]["channel_blacklist"]:
                self.settings[guild_id]["channel_blacklist"].append(channel.id)
                self.save_settings()
                await ctx.respond(f"Channel {channel.mention} added to the blacklist.")
            else:
                await ctx.respond(f"Channel {channel.mention} is already in the blacklist.")
        else:
            await ctx.respond("Please specify either a user or a channel to add to the blacklist.")

    @blacklist.command(name="remove", description="Remove a user or channel from the blacklist")
    @discord.option("user", description="The user to remove", type=discord.User, required=False)
    @discord.option("channel", description="The channel to remove", type=discord.TextChannel, required=False)
    async def blacklist_remove(
        self,
        ctx,
        user: discord.User = None,
        channel: discord.TextChannel = None):
        guild_id = ctx.guild.id
        self.initialize_guild_settings(guild_id)
        if user:
            if user.id in self.settings[guild_id]["user_blacklist"]:
                self.settings[guild_id]["user_blacklist"].remove(user.id)
                self.save_settings()
                await ctx.respond(f"User {user.mention} removed from the blacklist.")
            else:
                await ctx.respond(f"User {user.mention} is not in the blacklist.")
        elif channel:
            if channel.id in self.settings[guild_id]["channel_blacklist"]:
                self.settings[guild_id]["channel_blacklist"].remove(channel.id)
                self.save_settings()
                await ctx.respond(f"Channel {channel.mention} removed from the blacklist.")
            else:
                await ctx.respond(f"Channel {channel.mention} is not in the blacklist.")
        else:
            await ctx.respond("Please specify either a user or a channel to remove from the blacklist.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_id = payload.guild_id
        if guild_id not in self.settings:
            return
        settings = self.settings[guild_id]
        if str(payload.emoji) in settings["emojis"]:
            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.author.id in settings["user_blacklist"] or channel.id in settings["channel_blacklist"]:
                return
            star_count = sum(1 for reaction in message.reactions if str(reaction.emoji) in settings["emojis"])
            if star_count >= settings["required_stars"]:
                starboard_channel = self.client.get_channel(settings["starboard_channel"])
                if starboard_channel:
                    embed = discord.Embed(description=message.content, color=discord.Color.gold())
                    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                    embed.add_field(name="Original", value=f"[Jump to message]({message.jump_url})")
                    await starboard_channel.send(embed=embed)

def setup(client):
    client.add_cog(Starboard(client))