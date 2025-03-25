import discord
from discord.ext import commands
import aiohttp
import pymongo
from ezcord import emb

class ShiftManage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.Guids = self.DB.get_collection("Guilds")
    
    @commands.slash_command(name="shift-manage")
    async def slash_command(ctx):
        



def setup(bot):
    bot.add_cog(ShiftManage(bot))
