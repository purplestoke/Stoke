import nextcord
from nextcord.ext import commands
import os
from API_Tokens import Bot_Token
import asyncio
from stoke import Stoke


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)


async def reset_rate_table():
    await client.wait_until_ready()

    while not client.is_closed():
        stokeIns = Stoke()
        stokeIns.Rate().resetRate()
        await asyncio.sleep(24 * 60 * 60)


@client.event
async def on_ready():
    await client.change_presence(
        status=nextcord.Status, activity=nextcord.Game("Games")
    )
    asyncio.create_task(reset_rate_table())
    print("Stoke is ready")
    print("-----------------")


initial_extensions = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        initial_extensions.append("cogs." + filename[:-3])

if __name__ == "__main__":
    for extension in initial_extensions:
        client.load_extension(extension)

client.run(Bot_Token)
