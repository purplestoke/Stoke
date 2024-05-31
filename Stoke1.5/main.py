import nextcord
from nextcord.ext import commands
import os
from API_Tokens import Bot_Token, BASE_URL, ETHSCAN_API_KEY, TESTNET_BASE_URL
import asyncio
from datetime import datetime, time
import pytz
from blocks import Blocks
import aiohttp


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

async def getBlockNums():
    await client.wait_until_ready()

    while not client.is_closed():
        current_time = datetime.now()
        startOfDay = datetime.combine(current_time.date(), time.min)
        ethTimezone = pytz.timezone('UTC')
        startOfDayEth = ethTimezone.localize(startOfDay)
        timestamp = int(startOfDayEth.timestamp())
        url = f"{TESTNET_BASE_URL}?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={ETHSCAN_API_KEY}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data["status"] == "1":
                        block_number = int(data["result"])
                        _startBlock = block_number
                        _endBlock = int(_startBlock) + 10000
                        print(_startBlock, _endBlock)
                        Blocks.startBlock, Blocks.endBlock = _startBlock, _endBlock
                        await asyncio.sleep(24 * 60 * 60)
        
        except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as e:
            error_message = str(e) if not isinstance(e, asyncio.TimeoutError) else "Asyncio Timeout"
            logg = f"Time: {datetime.now()} | User: Bot | Cmd: blockNums | Error: {error_message}"
            with open('/logs/other.txt', 'a') as f:
                f.write(logg)
        
            newStart = Blocks.endBlock 
            newStart += 8500
            newEnd = newStart + 8500
            Blocks.startBlock, Blocks.endBlock = newStart, newEnd
            await asyncio.sleep(24 * 60 * 60)

@client.event
async def on_ready():
    await client.change_presence(
        status=nextcord.Status, activity=nextcord.Game("Games")
    )
    asyncio.create_task(getBlockNums())
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
