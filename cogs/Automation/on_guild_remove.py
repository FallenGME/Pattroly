import discord
from discord.ext import commands
import pymongo

class on_guild_leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.Collection = self.DB.get_collection("Guilds")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        result = self.Collection.delete_one({"GuildID": guild.id})
        
        if result.deleted_count > 0:
            print(f"Data for guild {guild.name} (ID: {guild.id}) has been removed from the database.")
        else:
            print(f"No data found for guild {guild.name} (ID: {guild.id}) in the database.")

def setup(bot):
    bot.add_cog(on_guild_leave(bot))
