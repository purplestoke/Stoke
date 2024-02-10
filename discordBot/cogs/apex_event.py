import nextcord
from nextcord.ext import commands
import requests
import sqlite3
import os
from nextcord import Interaction
from functions import Functions
from stoke import Stoke
from API_Tokens import stoke, purpleStoke
from image_reader import APEXREADER


class apex_event(commands.Cog):
    def __init__(self, client):
        self.client = client

    # EVENT LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        # CHECK IF EVENT IS ON
        sender = message.author
        discord = str(sender)
        senderId = sender.id
        channel = "scSubmission"
        stokeIns = Stoke()
        guildId = message.guild.id
        game = "apex"
        logFlags = []
        eventIns = stokeIns.Event(senderId, game)
        bugsProfileIns = stokeIns.bugsProfile(senderId, ethAddr=None)

        # CHECK IF EVENT ON
        flag, check = eventIns.isOn(_event=game)
        logFlags.append(flag)
        if check == 1:
            flag1, bugsId = bugsProfileIns.bugsId()
            logFlags.append(flag1)
            pass
        else:
            if senderId == stoke:
                return
            else:
                return
        logIns = stokeIns.Log(bugsId, guildId, logFlags, senderId)
        # CHECKS IF IT IS FRIDAY BETWEEN TOURNEY HOURS
        friday = Functions.isItSaturday()
        if friday == True:
            pass
        else:
            # return
            pass

        # ONLY RESPONDS TO MESSAGES IN THE SUBMISSION CHANNEL
        guildIns = stokeIns.Guilds(channel, guildId)
        flag2, ret = guildIns.pullChannel()
        logFlags.append(flag2)

        if message.channel.id != ret:
            print("channel yes")
            logIns.log(_channel=channel, _cmd="Asc")
            return

        # CHECK TO MAKE SURE STOKE DOESNT RESPOND TO HIS OWN MSG
        if senderId == stoke:
            return

        # CHECK FOR APEX ROLE
        if "apex" in [role.name.lower() for role in sender.roles]:
            # CHECK FOR COMPETITOR ROLE
            if "competitor" in [role.name.lower() for role in sender.roles]:
                # CHECKING FOR AN IMG IN CHANNEL
                if not message.attachments:
                    print("not image")
                    return

                flag3, check = eventIns.checkSubmission(_event="apex")
                logFlags.append(flag3)
                if flag3 == 2:
                    pass
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Asc",
                    )
                    await message.channel.send(
                        f"Sorry, but an error occurred and I did not save your screenshot properly.\nFlag {flag3}"
                    )
                    return

                if check is not None:
                    logIns.log(
                        _channel=channel,
                        _cmd="Asc",
                    )
                    await message.channel.send(
                        f"You have already used a submission for this tournament.\n\nIf you wish to submit a new screenshot you have to delete the previous.\n\nIn order to delete your previous screenshot use the following command.\n\n/xdefiant_event submission_delete"
                    )
                    return

                # DEALING WITH IMG
                attachments = message.attachments
                for attachment in attachments:
                    if any(
                        attachment.filename.lower().endswith(ext)
                        for ext in [".png", ".jpg"]
                    ):
                        screenshot_url = attachment.url

                    # SAVING SC TO SUB-DIRECTORY ON MACHINE
                    response = requests.get(screenshot_url)
                    file_name = f"apexSc{bugsId}.jpg"

                    # SAVE FILENAME TO DB
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE Apex_Profile SET submission = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            file_name,
                            senderId,
                        ),
                    )
                    conn.commit()
                    conn.close()

                    # CREATE FOLDER OF DISCORD MEMBER
                    parent_folder = "apex_sc"
                    file_folder = str(bugsId)
                    path = os.path.join(parent_folder, file_folder)
                    try:
                        os.makedirs(path)

                    except FileExistsError:
                        pass

                    file_path = f"apex_sc/{file_folder}/{file_name}"
                    with open(file_path, "wb") as file:
                        file.write(response.content)

                    # SEND MSG TO USER
                    logIns.log(
                        _channel=channel,
                        _cmd="Asc",
                    )
                    await message.channel.send(
                        f"Got your screenshot! You are all set to potentially win the Eth Prize!\n\nRemember if you want to upload a different screenshot you must use the following command first.\n\n/xdefiant_event submission_delete"
                    )
                    return

                else:
                    print("E")

    # APEX EVENT COMMANDS --------------------------------------------------------------------------------------------
    @nextcord.slash_command(
        name="apex_event",
        description="leads to all apex event commands",
    )
    async def apex_event(self, interaction: Interaction):
        pass

    # SUBCOMMANDS------------------------------------------------

    # SUBMISSION DELETE --------------------------------------------------------------------------------------------
    @apex_event.subcommand(
        name="submission_delete", description="delete your current sc submission"
    )
    async def submission_delete(self, interaction: Interaction):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        logFlags = []
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        channel = "scSubmission"
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        guildIns = stokeIns.Guilds(channel, guildId)

        # CHECK IF EVENT IS ON
        eventIns = stokeIns.Event(discord, game=None)
        flag, eventCheck = eventIns.isOn(_event="apex")
        logFlags.append(flag)
        if eventCheck == 1:
            pass
        else:
            logIns.log(
                _channel=channel,
                _cmd="AscDelete",
            )
            await interaction.response.send_message("Apex event is not active")
            return

        # PULL SC_SUBMISSION CHANNEL BASED ON GUILD
        flag, ret = guildIns.pullChannel()
        logFlags.append(flag)

        # MUST BE IN THE SC_SUBMISSION CHANNEL
        if interaction.channel.id != ret:
            logIns.log(
                _channel=channel,
                _cmd="AscDelete",
            )
            await interaction.response.send_message(
                "You have to use this command in the sc_submission channel"
            )
            return

        # USER MUST HAVE THE COMPETITOR ROLE
        # PULL THE ROLE ID OF THE COMPETITOR ROLE BASED ON GUILD
        f, compRole = guildIns.pullRole(_find="competitor")
        logFlags.append(f)
        flag = False
        for role in mem.roles:
            if role.id == compRole:
                flag = True
                break

        if flag == True:
            pass
        else:
            logIns.log(
                _channel=channel,
                _cmd="AscDelete",
            )
            await interaction.response.send_message(
                "You must have the competitor role to post in this channel."
            )
            return

        delete = eventIns.submissionDelete(_event="apex", _bugsId=bugsId)
        logFlags.append(delete)
        if delete == 2:
            logIns.log(
                _channel=channel,
                _cmd="AscDelete",
            )
            # SEND MSG TO USER
            await interaction.response.send_message(
                "Your submission has now been deleted."
            )
            return
        elif delete == 3:
            logIns.log(
                _channel=channel,
                _cmd="AscDelete",
            )
            await interaction.response.send_message(
                "Sorry but something wen't wrong when deleting your submission."
            )
            return

    # RAFFLE DRAW --------------------------------------------------------------------------------------------
    @apex_event.subcommand(name="draw")
    async def draw(self, interaction: Interaction):
        # VARIABLES
        guildId = interaction.guild.id
        mem = interaction.user
        discord = mem.id
        event = "apex"
        stokeIns = Stoke()
        logFlags = []
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag, bugsId = bugsProfileIns.bugsId(discord)
        logFlags.append(flag)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)

        # CHECK IF USER HAS ADMIN ROLE
        if discord == purpleStoke:
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            # PULL COMPETITORS DISCORD AND POINTS THEN ADD TO DIC
            pull = cur.execute("SELECT gamertag, points FROM Apex_Profile")
            info = pull.fetchall()

            # CREATE A DIC OF COMPETITORS SCORES
            competitors = {}
            for item in info:
                competitors[item[0]] = item[1]

            try:
                winners = Functions.apexRaffleDraw(competitors)
                winningGuild, guildPoints = Functions.winning_guild(event)
                guildName = cur.execute(
                    "SELECT guild_name FROM Stoke_Guilds WHERE id = ?", (winningGuild,)
                )
                guild = guildName.fetchone()[0]
                Wflag = 2
            except:
                await interaction.response.send_message("Error")
                Wflag = 3
                return
            logFlags.append(Wflag)
            logIns.log(_channel="Admin", _cmd="ADraw")
            await interaction.response.send_message(
                f"The winner(s) are,\n{winners}\nThe winning community is {guild} with {guildPoints} points!"
            )
            return
        else:
            logIns.log(_channel="Admin", _cmd="ADraw")
            await interaction.response.send_message("You are not my dad")
            return

    @apex_event.subcommand(name="score")
    async def score(self, interaction: Interaction):
        guildId = interaction.guild.id
        mem = interaction.user
        channel = "scSubmission"
        discord = mem.id
        event = "apex"
        stokeIns = Stoke()
        logFlags = []
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        pProfileIns = stokeIns.PlayerProfile(discord, guildId, type="apex")

        # CHECK IF EVENT IS ON
        eventIns = stokeIns.Event(discord, game=None)
        flag, eventCheck = eventIns.isOn(_event=event)
        logFlags.append(flag)
        if eventCheck == 1:
            pass
        else:
            logIns.log(
                _channel=channel,
                _cmd="AScore",
            )
            await interaction.response.send_message("Apex event is not active")
            return

        # PULL USERS GAMERTAG, POINTS FROM APEX EVENT
        flag1, gt = pProfileIns.retrieve()
        logFlags.append(flag1)
        # GET FILEPATH
        flag3, file = eventIns.checkSubmission(_event=event)
        logFlags.append(flag3)
        # CREATE FILEPATH
        filePath = f"apex_sc/{bugsId}/{file}"

        # CREATED AN AR OBJECT
        AR = APEXREADER(filePath, gt, bugsId, guildId)
        # READ IMG
        score, flag4 = AR.ReadApex()
        logFlags.append(flag4)

        flag5 = eventIns.addPoints(_event=event, _points=score)
        logFlags.append(flag5)
        if flag5 == 2:
            await interaction.response.send_message(
                f"You scored a total of {score} points!"
            )
            return
        else:
            fhand = open("manualRev/apexManualReview.txt", "w")
            fhand.write(
                f"gamertag: {gt} | file: {filePath} | User: {bugsId} | guild: {guildId}"
            )
            fhand.close()
            await interaction.response.send_message(
                "There was an error counting your score. Your screenshot has been sent for manual review."
            )
            return


def setup(client):
    client.add_cog(apex_event(client))
