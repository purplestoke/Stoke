import nextcord
from nextcord.ext import commands
import os
from API_Tokens import Bot_Token
import asyncio
import sqlite3
from image_reader import APEXREADER
from functions import Functions


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)


async def readApexImgs():
    await client.wait_until_ready()

    while not client.is_closed():
        x = Functions.isItSaturday()
        if x == False:
            break
        # PULL ALL USER INFORMATION FROM APEX PLAYER PROFILES
        conn = sqlite3.connect("bugs_DB2.sqlite")
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        apexCompInfo = cur.execute("SELECT * FROM Apex_Profile")
        apexCompetitors = {}
        for player in apexCompInfo:
            bugsId = player[0]
            gt = player[1]
            elligible = player[2]
            submission = player[3]
            points = player[4]
            guildId = player[5]

            if elligible != None and points == None and submission != None:
                apexCompetitors[bugsId] = (gt, submission, points, guildId)

        for k, tup in apexCompetitors.items():
            gamertag = tup[0]
            file = tup[1]
            filepath = f"apex_sc/{k}/{file}"
            guildId = tup[3]
            AR = APEXREADER(filepath, gamertag, k, guildId)
            newScore, f = AR.ReadApex()
            if f == 2:
                cur.execute(
                    "UPDATE Apex_Profile SET points = ? WHERE bugs_id = ?",
                    (newScore, k),
                )
                conn.commit()
                conn.close()
            else:
                fhand = open("manualRev/apexManualReview.txt", "w")
                fhand.write(
                    f"gamertag: {gamertag} | file: {filepath} | User: {bugsId} | guild: {guildId}"
                )

        await asyncio.sleep(1 * 60 * 60)

async def readFinalsImgs():
    await client.wait_until_ready()

    while not client.is_closed():
        x = Functions.isItSaturday()
        if x == False:
            break
        # PULL ALL USER INFORMATION FROM APEX PLAYER PROFILES
        conn = sqlite3.connect("bugs_DB2.sqlite")
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        finalsCompInfo = cur.execute("SELECT * FROM Finals_Profile")
        finalsCompetitors = {}
        for player in finalsCompInfo:
            bugsId = player[0]
            gt = player[1]
            elligible = player[2]
            submission = player[3]
            points = player[4]
            guildId = player[5]

            if elligible != None and points == None and submission != None:
                finalsCompetitors[bugsId] = (gt, submission, points, guildId)

        for k, tup in finalsCompetitors.items():
            gamertag = tup[0]
            file = tup[1]
            filepath = f"apex_sc/{k}/{file}"
            guildId = tup[3]
            AR = APEXREADER(filepath, gamertag, k, guildId)
            newScore, f = AR.ReadFinals()
            if f == 2:
                cur.execute(
                    "UPDATE Finals_Profile SET points = ? WHERE bugs_id = ?",
                    (newScore, k),
                )
                conn.commit()
                conn.close()
            else:
                fhand = open("manualRev/apexManualReview.txt", "w")
                fhand.write(
                    f"gamertag: {gamertag} | file: {filepath} | User: {bugsId} | guild: {guildId}"
                )

        await asyncio.sleep(1 * 60 * 60)


@client.event
async def on_ready():
    await client.change_presence(
        status=nextcord.Status, activity=nextcord.Game("Games")
    )
    asyncio.create_task(readApexImgs())
    asyncio.create_task(readFinalsImgs())
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
