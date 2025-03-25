import discord
from discord.ext import commands
import pymongo
from ezcord import emb
import pymongo.collection
import time

class ERLC_Run_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.Guilds: pymongo.collection.Collection = self.DB.get_collection("Guilds")
        self.CommandQueue: pymongo.collection.Collection = self.DB.get_collection("CommandQueue")
        self.Banned = ["kick", "ban", "tp", "admin", "unadmin", "mod", "unmod", "unban"]

    @discord.slash_command(name="erlc-command")
    @discord.option(
        "command", 
        description="The command to run ingame.", 
        choices=["ban", "kick", "tp", "m", "startfire", "pm", "prty", "pt", "jail", "wanted", "unjail", "mod", "unmod", "admin", "unadmin", "unban"]
    )
    async def set_erlc_token(self, ctx: discord.context.ApplicationContext, command: str, input: str):
        guild_id = ctx.guild.id
        Entry: pymongo.collection.Collection = self.Guilds.find_one({"GuildID": guild_id})

        if command not in ["ban", "kick", "tp", "m", "startfire", "pm", "prty", "pt", "jail", "wanted", "unjail", "mod", "unmod", "admin", "unadmin", "unban"]:
            await emb.error(target=ctx, txt="Invalid command selected.", title="**⛔ ⨯ Invalid Command**", ephemeral=True)
            return

        if not Entry or "ERLC-Token" not in Entry or Entry["ERLC-Token"] is None:
            await emb.error(target=ctx, txt="You cannot execute a command without having set a proper token. Ask the Server-Owner to run `/set-erlc-token` first!", title="**⛔ ⨯ Inproper token parsed.**", ephemeral=True)
            return
        
        if command in self.Banned:
            args = input.split()  
            if any(arg in ["all", "others"] for arg in args):  
                await emb.error(target=ctx, txt=f"You cannot execute `{command}` with arguments `{', '.join(args)}`.", title="**⛔ ⨯ Why? No!**", ephemeral=True)
                return

        command_data = {
            "Executor": ctx.author.id,
            "Command": command,
            "Input": input,
            "Timestamp": time.time(),
        }

        result = self.CommandQueue.update_one(
            {"GuildID": guild_id},  
            {
                "$set": {"ERLC-Token": Entry["ERLC-Token"]},
                "$push": {"Commands": command_data}, 
                "$inc": {"RemainingCommands": 1}  
            },
            upsert=True  
        )

        if result.modified_count == 0 and result.upserted_id is None:
            await emb.error(target=ctx, title="**⛔ ⨯ Failure while queing.**",txt="Failed to add the command to the queue. Please try again later.", ephemeral=True)
            return

        await emb.success(target=ctx, title="**🌍 ⨯ Queing**", txt="You have successfully queued the command. It may take up to several minutes for the command to be executed.", ephemeral=True)

    @discord.slash_command(name="command-queue")
    async def check_queue(self, ctx: discord.context.ApplicationContext):
        guild_id = ctx.guild.id

        queue_data = self.CommandQueue.find_one({"GuildID": guild_id})

        if not queue_data or "RemainingCommands" not in queue_data:
            await emb.error(target=ctx, txt="No command queue found for this server.", title="**⛔ ⨯ No Queue Found**", ephemeral=True)
            return

        remaining_commands = queue_data["RemainingCommands"]
        await emb.success(target=ctx, title="**📊 ⨯ Command Queue Status**", txt=f"There are {remaining_commands} commands remaining in the queue.", ephemeral=True)

def setup(bot):
    bot.add_cog(ERLC_Run_Command(bot))