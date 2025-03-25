import discord
from discord.ext import commands, tasks
import pymongo
from ezcord import emb

class DM_Queuing(commands.Cog):
    def __init__(self, bot):
        self.bot : discord.Bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.collection = self.DB.get_collection("User_DM_Queue")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.dm_users.is_running():
            self.dm_users.start()

    @tasks.loop(seconds=5)
    async def dm_users(self):
        user_data = self.collection.find_one_and_delete({})
        
        if user_data:
            user_id = user_data.get("UserID")
            message = user_data.get("Message", "Default message")

            if message == "Bot_Joined":
                GuildName = user_data.get("GuildName")
                embed_title = "Hello! I am Patrolly!"
                embed_description = (
                    f"Thank you for adding Patrolly to {GuildName}, a lightweight Discord bot for ERLC. "
                    "Remote server management made easy with Patrolly.\n\n"
                    "Please make sure to run `/set-erlc-token` to set your ERLC token. "
                    "We are actively working on adding a dashboard to this bot!"
                )

            user = self.bot.get_user(user_id)
            if user:
                try:
                    await emb.info(target=user, txt=embed_description, title=embed_title)
                except Exception as e:
                    print(f"Error sending DM to {user.name}#{user.discriminator}: {e}")

    async def send_message(self, user, message, embed):
        try:
            if embed:
                await user.send(embed=embed)
            else:
                await user.send(message)
        except discord.Forbidden:
            print(f"Could not send DM to {user.name}#{user.discriminator} (Forbidden)")
        except discord.HTTPException as e:
            print(f"Error sending DM to {user.name}#{user.discriminator}: {e}")

    @dm_users.before_loop
    async def before_dm_users(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(DM_Queuing(bot))
