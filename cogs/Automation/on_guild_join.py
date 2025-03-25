import discord
from discord.ext import commands
import ezcord
from ezcord import emb
import pymongo

class on_guild_join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.Collection = self.DB.get_collection("Guilds")
        self.User_DM_Queue = self.DB.get_collection("User_DM_Queue")
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = guild.system_channel
        embed_title = "Hello! I am Patrolly!"
        embed_description = (
            "Thank you for adding Patrolly, a lightweight Discord bot for ERLC. "
            "Remote server management made easy with Patrolly.\n\n"
            "Please make sure to run `/set-erlc-token` to set your ERLC token. "
            "We are actively working on adding a dashboard to this bot!"
        )
        
        if self.Collection.count_documents({"GuildID": guild.id}) == 0:
            self.Collection.insert_one({
                "GuildID": guild.id,
                "ERLC-Token": None,
                "Roles": [],
                "Shifts": [],
                "Active_Shifts": [],
                "Command_Queue": []
            })

        owner_id = guild.owner.id  


        if channel:
            await emb.info(target=channel, txt=embed_description, title=embed_title)
        else:
            self.User_DM_Queue.insert_one({
                "UserID": owner_id,
                "Message": "Bot_Joined",
                "GuildName": guild.id
            })

def setup(bot):
    bot.add_cog(on_guild_join(bot))
