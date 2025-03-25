import discord
from discord.ext import commands
import aiohttp
import pymongo
from ezcord import emb

class ERLCSetToken(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MongoClient: pymongo.MongoClient = bot.MongoClient
        self.DB = self.MongoClient.get_database("Patrolly")
        self.Collection = self.DB.get_collection("Guilds")

    async def validate_erlc_token(self, token: str) -> bool:
        headers = {
            "Server-Key": token 
        }
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.policeroleplay.community/v1/server/players", headers=headers) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    @discord.slash_command(name="set-erlc-token")
    async def set_erlc_token(self, ctx: discord.commands.ApplicationContext, token: str):
        Entry = self.Collection.find_one({"GuildID": guild_id})

        if not Entry:
            await emb.error(
                target=ctx,
                txt="So that should not happen! Please seek for support on our Support Server.",
                title="**⛔ ⨯ Uh oh! What?**"
            )
            return

        if not ctx.author != ctx.author.guild.owner.id:
                await emb.error(
                    target=ctx,
                    txt="You need to be the server owner inorder to use this command,",
                    title="**⛔ ⨯ Uh oh! Access Denied?**"
                )

        is_valid = await self.validate_erlc_token(token)
        if is_valid:
            guild_id = ctx.guild.id

            if Entry and "ERLC-Token" in Entry and Entry["ERLC-Token"] is token:
                await emb.error(
                    target=ctx,
                    txt="You cannot replace $Token with the same $Token!",
                    title="**⛔ ⨯ Uh oh! What?**"
                )
                return


            if Entry and "ERLC-Token" in Entry and Entry["ERLC-Token"] is not None:
                view = discord.ui.View()

                async def continue_callback(interaction: discord.Interaction):
                    self.Collection.update_one(
                        {"GuildID": guild_id},
                        {"$set": {"ERLC-Token": token}},
                        upsert=True
                    )
                    await Message.edit(view=None)
                    await emb.success(
                        target=ctx, 
                        txt=f"ERLC Token has been successfully set for **{ctx.guild.name}**.", 
                        title="Success",
                        ephemeral=True
                    )

                async def cancel_callback(interaction: discord.Interaction):
                    cancel_embed = await emb.warn(
                        target=ctx, 
                        txt="Token change has been cancelled.", 
                        title="Operation Cancelled"
                    )
                    await Message.edit(view=None)
                    await interaction.response.send_message(embed=cancel_embed, ephemeral=True)

                continue_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Continue")
                cancel_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Cancel")

                continue_button.callback = continue_callback
                cancel_button.callback = cancel_callback

                view.add_item(continue_button)
                view.add_item(cancel_button)
                Message : discord.Message = await emb.info(
                    target=ctx, 
                    txt="Are you sure you want to overwrite the currently set API key?", 
                    title="Overwrite ERLC Token", 
                    ephemeral=True,
                    view=view
                )
            else:
                self.Collection.update_one(
                    {"GuildID": guild_id},
                    {"$set": {"ERLC-Token": token}},
                    upsert=True
                )
                success_embed = await emb.success(
                    target=ctx, 
                    txt=f"ERLC Token has been successfully set for **{ctx.guild.name}**.", 
                    title="Success"
                )
                await ctx.send(embed=success_embed)
        else:
            await emb.error(
                target=ctx, 
                txt="Invalid ERLC Token. Please ensure the token is correct.", 
                title="**⛔ ⨯ Authentication Failed!**"
            )

def setup(bot):
    bot.add_cog(ERLCSetToken(bot))
