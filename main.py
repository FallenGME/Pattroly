
import ezcord
import discord
import os
from Functions.Formatters.FormatTime import Format_Time
import time
from ezcord import Bot, emb
import pymongo
from dotenv import load_dotenv
load_dotenv()  

bot: discord.Bot = Bot(
    intents=discord.Intents.all(),
    error_webhook_url=os.environ.get("ERROR_WEBHOOK_URL"),  
    language="en",
)

bot.MongoClient = pymongo.MongoClient("mongodb://localhost:27017")

emb.set_embed_templates(
    info_embed=discord.Embed(
        color=discord.Color(0xf84412),
        footer=discord.EmbedFooter(text="©2024, Callum's IT Services. All rights reserved.")
    ),
)

start_time = time.time()
error_count = 0

def GetUptime():
    return Format_Time(round(time.time() - start_time))

bot.add_status_changer(
    [
        "🌍 Innovating Your Digital Future",
        "⚡ Uptime: {Uptime}",
        "👀 Watching {user_count} users.",
        "🛠️ Managing {guild_count} server(s).",
    ],
    Uptime=GetUptime,
    interval=30,
)

if __name__ == "__main__":
    bot.load_cogs(subdirectories=True)
    bot.run(token_var="DISCORD_BOT_TOKEN")