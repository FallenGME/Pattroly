import discord
from discord.ext import commands, tasks
import pytz
from datetime import datetime
import os

class BotAnalytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.analytics_channel_id = os.environ.get("ANALYTICS_CHANNEL_ID")
        self.MAIN_SERVER = os.environ.get("MAIN_SERVER")

        self.commands_executed = 0
        self.buttons_pressed = 0
        self.bot_added = 0
        self.bot_removed = 0
        self.errors_logged = 0

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready.")
        if not self.analytics_report.is_running():
            self.analytics_report.start()

    def cog_unload(self):
        self.analytics_report.cancel()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            self.commands_executed += 1

        elif interaction.type == discord.InteractionType.component:
            if interaction.data and interaction.data.get("component_type") == 2: 
                self.buttons_pressed += 1
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot_added += 1

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot_removed += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.errors_logged += 1

    @tasks.loop(seconds=60)
    async def analytics_report(self):
        berlin_tz = pytz.timezone("Europe/Berlin")
        now = datetime.now(berlin_tz)
        if now.hour == 0 and now.minute == 0:
            report_message = (
                "📋 › **Daily Bot Analytics Report**\n\n"
                "This message provides an overview of bot activity in the last **24 hours**.\n\n"
                f"📌 › **Commands Executed:** {self.commands_executed}\n"
                f"📌 › **Buttons Pressed:** {self.buttons_pressed}\n\n"
                f"➕ › **Bot Added to Servers:** {self.bot_added}\n"
                f"➖ › **Bot Removed from Servers:** {self.bot_removed}\n\n"
                f"⚠️ › **Errors Logged:** {self.errors_logged}\n\n"
                "_As of now, this data has been **permanently deleted** from the database._"
            )

            if not self.MAIN_SERVER or not self.analytics_channel_id:
                print("Error: Missing environment variables for MAIN_SERVER or ANALYTICS_CHANNEL_ID.")
                return

            guild = self.bot.get_guild(int(self.MAIN_SERVER))
            if guild is None:
                print(f"Error: Could not find guild with ID {self.MAIN_SERVER}.")
                return

            channel = guild.get_channel(int(self.analytics_channel_id))
            if channel is None:
                print(f"Error: Could not find channel with ID {self.analytics_channel_id}.")
                return

            await channel.send(report_message)

            self.commands_executed = 0
            self.buttons_pressed = 0
            self.bot_added = 0
            self.bot_removed = 0
            self.errors_logged = 0

    @analytics_report.before_loop
    async def before_analytics_report(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BotAnalytics(bot))
