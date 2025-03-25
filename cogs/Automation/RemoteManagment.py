import discord
from discord.ext import commands, tasks
import pymongo
import aiohttp
import json
import ezcord

class RemoteServer(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.collection = self.DB.get_collection("CommandQueue")
        self.Guilds: pymongo.collection.Collection = self.DB.get_collection("Guilds")
        
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.Handle_RemoteServerManagment.is_running():
            self.Handle_RemoteServerManagment.start()

    @tasks.loop(seconds=10)
    async def Handle_RemoteServerManagment(self):
        for entry in self.collection.find({"RemainingCommands": {"$gt": 0}}):
            token = entry["ERLC-Token"]
            guild_id = entry["GuildID"]
            commands = entry["Commands"]
            webhook = None
            GuildEntry = self.Guilds.find_one({"GuildID": guild_id})
            if GuildEntry["CommandLogs-Webhook"]:
                webhook = GuildEntry["CommandLogs-Webhook"] or None

            remaining_commands = entry["RemainingCommands"]

            if remaining_commands > 0:
                next_command = commands[0]

                executor_id = next_command["Executor"]
                command = next_command["Command"]
                input_value = next_command["Input"]
                await self.execute_command(guild_id, executor_id, command, input_value, token, webhook)

                commands.pop(0)

                remaining_commands -= 1
                if remaining_commands > 0:
                    self.collection.update_one(
                        {"_id": entry["_id"]},
                        {
                            "$set": {
                                "Commands": commands,
                                "RemainingCommands": remaining_commands
                            }
                        }
                    )
                else:
                    self.collection.delete_one({"_id": entry["_id"]})

    async def execute_command(self, guild_id, executor_id, command, input_value, token, webhook):
        url = "https://api.policeroleplay.community/v1/server/command"
        headers = {
            "Server-Key": token,  
            "Content-Type": "application/json"
        }
        payload = {
            "command": f":{command} {input_value}"
        }

        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                success = True
                result = json.dumps(data, indent=2)
            else:
                success = False
                result = await response.text()

        if webhook:
            webhook_obj = discord.Webhook.from_url(webhook, session=self.session)
            embed = discord.Embed(
                title="Patrolly Audit Log",
                color=discord.Color(0xf84412),
            )
            embed.add_field(name="Type", value="ER:LC Command Ran", inline=False)
            embed.add_field(name="Description", value=f"01 - Used the command `:{command} {input_value}`", inline=False)
            embed.add_field(name="Result", value=success and "Completed" or "Failed", inline=False)

            User : discord.User = self.bot.get_user(executor_id)
            embed.set_author(name=User.global_name, icon_url=User.avatar or User.default_avatar)

            await webhook_obj.send(embed=embed)


    @Handle_RemoteServerManagment.before_loop
    async def before_dm_users(self):
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        if not self.session.closed:
            await self.session.close()
            print("Session closed successfully!")
        if self.Handle_RemoteServerManagment.is_running():
            self.Handle_RemoteServerManagment.cancel()

def setup(bot):
    bot.add_cog(RemoteServer(bot))
