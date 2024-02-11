import nextcord
from nextcord.ext import commands
import requests
from API_Tokens import stoke, purpleStoke
import sqlite3
import os
from nextcord import Interaction
from functions import Functions
from stoke import Stoke


class xdefiant_event(commands.Cog):
    def __init__(self, client):
        self.client = client

    # EVENT LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        sender = message.author
        senderId = sender.id
        guildId = message.guild.id
        logFlags = []
        channel = "scSubmission"
        stokeIns = Stoke()
        bugsProfileIns = stokeIns.bugsProfile(senderId, ethAddr=None)
        fflag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(fflag)
        guildIns = stokeIns.Guilds(channel, guildId)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, senderId)

        # CHECK IF EVENT IS ON
        game = "xdefiant"
        eventIns = stokeIns.Event(senderId, game)
        flag, check = eventIns.isOn(_event=game)
        logFlags.append(flag)
        if check == 1:
            pass
        else:
            return

        # CHECKS IF IT IS FRIDAY BETWEEN TOURNEY HOURS
        friday = Functions.isItSaturday()
        if friday == True:
            pass
        else:
            if senderId == stoke:
                return

        # ONLY RESPONDS TO MESSAGES IN THE SUBMISSION CHANNEL
        flag3, ret = guildIns.pullChannel()
        logFlags.append(flag3)

        if message.channel.id != ret:
            logIns.log(_channel=channel, _cmd="Xsc")
            return

        # CHECK TO MAKE SURE STOKE DOESNT RESPOND TO HIS OWN MSG
        if senderId == stoke:
            return

        # CHECK FOR XDEF ROLE
        if "xdef" in [role.name.lower() for role in sender.roles]:
            # CHECK FOR COMPETITOR ROLE
            if "competitor" in [role.name.lower() for role in sender.roles]:
                # CHECKING FOR AN IMG IN CHANNEL
                if not message.attachments:
                    return

                flag4, check = eventIns.checkSubmission(_event="xdef")
                logFlags.append(flag4)
                if flag4 == 2:
                    pass
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Xsc",
                    )
                    await message.channel.send(
                        f"Sorry, but an error occurred and I did not save your screenshot properly.\nFlag {flag}"
                    )
                    return
                if check is not None:
                    logIns.log(
                        _channel=channel,
                        _cmd="Xsc",
                    )
                    await message.channel.send(
                        f"You have already used a submission for this tournament.\n\nIf you wish to submit a new screenshot you have to delete the previous.\n\nIn order to delete your previous screenshot use the following command.\n\n/xdefiant_event submission_delete"
                    )
                    return

                # CHECKING FOR AN IMG IN CHANNEL
                attachments = message.attachments
                for attachment in attachments:
                    if any(
                        attachment.filename.lower().endswith(ext)
                        for ext in [".png", ".jpg"]
                    ):
                        screenshot_url = attachment.url

                    # SAVING SC TO SUB-DIRECTORY ON MACHINE
                    response = requests.get(screenshot_url)
                    file_name = f"xdefSc{bugsId}.jpg"

                    # SAVE FILENAME TO DB
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE XDefiant_Profile SET submission = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            file_name,
                            senderId,
                        ),
                    )
                    conn.commit()
                    conn.close()

                    # CREATE FOLDER OF DISCORD MEMBER
                    parent_folder = "xdef_sc"
                    file_folder = str(bugsId)
                    path = os.path.join(parent_folder, file_folder)
                    try:
                        os.makedirs(path)

                    except FileExistsError:
                        pass

                    file_path = f"xdef_sc/{file_folder}/{file_name}"
                    with open(file_path, "wb") as file:
                        file.write(response.content)

                    # SEND MSG TO USER
                    logIns.log(
                        _channel=channel,
                        _cmd="Xsc",
                    )
                    await message.channel.send(
                        f"Got your screenshot, you are all set to potentially win the Eth prize!\n\nRemember if you want to upload a different screenshot you must use the following command first.\n\n/xdefiant_event submission_delete"
                    )
                    return

    # XDEFIANT EVENT COMMANDS
    @nextcord.slash_command(
        name="xdefiant_event",
        description="leads to all xdefiant event commands",
    )
    async def xdefiant_event(self, interaction: Interaction):
        pass

    # SUBCOMMANDS------------------------------------------------

    # SUBMISSION DELETE --------------------------------------------------------------------------------------------
    @xdefiant_event.subcommand(
        name="submission_delete", description="delete your current sc submission"
    )
    async def submission_delete(self, interaction: Interaction):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        logFlags = []
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        channel = "scSubmission"
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        guildIns = stokeIns.Guilds(channel, guildId)

        # CHECK IF EVENT IS ON
        eventIns = stokeIns.Event(discord, game="xdefiant")
        flag2, eventCheck = eventIns.isOn(_event="xdef")
        logFlags.append(flag2)
        if eventCheck == 1:
            pass
        else:
            logIns.log(
                _channel=channel,
                _cmd="XscDelete",
            )
            await interaction.response.send_message("XDefiant event is not active")
            return

        # PULL SC_SUBMISSION CHANNEL BASED ON GUILD
        flag3, ret = guildIns.pullChannel()
        logFlags.append(flag3)

        # MUST BE IN THE SC_SUBMISSION CHANNEL
        if interaction.channel.id != ret:
            logIns.log(
                _channel=channel,
                _cmd="XscDelete",
            )
            await interaction.response.send_message(
                "You have to use this command in the sc_submission channel"
            )
            return

        # USER MUST HAVE THE COMPETITOR ROLE
        # PULL THE ROLE ID OF THE COMPETITOR ROLE BASED ON GUILD
        f, compRole = guildIns.pullRole(_find="xdef")
        logFlags.append(f)
        fleg = False
        for role in mem.roles:
            if role.id == compRole:
                fleg = True
                break

        if fleg == True:
            pass
        else:
            logIns.log(
                _channel=channel,
                _cmd="XscDelete",
            )
            await interaction.response.send_message(
                "You must have the competitor role to post in this channel."
            )
            return

        delete = eventIns.submissionDelete(_event="xdef", _bugsId=bugsId)
        logFlags.append(delete)
        if delete == 2:
            logIns.log(
                _channel=channel,
                _cmd="XscDelete",
            )
            # SEND MSG TO USER
            await interaction.response.send_message(
                "Your submission has now been deleted."
            )
            return
        elif delete == 3:
            logIns.log(
                _channel=channel,
                _cmd="XscDelete",
            )
            await interaction.response.send_message(
                "Sorry but something wen't wrong when deleting your submission."
            )
            return

    # RAFFLE DRAW --------------------------------------------------------------------------------------------
    @xdefiant_event.subcommand(name="draw")
    async def draw(self, interaction: Interaction):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guildId = interaction.guild.id
        event = "xdef"
        stokeIns = Stoke()
        logFlags = []
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)

        # CHECK IF USER HAS ADMIN ROLE
        if discord == purpleStoke:
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            # PULL COMPETITORS DISCORD AND POINTS THEN ADD TO DIC
            pull = cur.execute("SELECT gamertag, points FROM XDefiant_Profile")
            info = pull.fetchall()

            # CREATE A DIC OF COMPETITORS SCORES
            competitors = {}
            for item in info:
                competitors[item[0]] = item[1]

            try:
                winningGuild, guildPoints = Functions.winning_guild(event)
                winners = Functions.xdefRaffleDraw(competitors)
                guildName = cur.execute(
                    "SELECT guild_name FROM Stoke_Guilds WHERE id = ?", (winningGuild,)
                )
                guild = guildName.fetchone()[0]
                Wflag = 2

            except:
                await interaction.response.send_message("Error")
                Wflag = 3
            logFlags.append(Wflag)
            logIns.log(_channel="Admin", _cmd="XDraw")
            await interaction.response.send_message(
                f"The winner(s) are,\n{winners}\nThe winning community is {guild} with {guildPoints} points!"
            )
        else:
            logIns.log(_channel="Admin", _cmd="XDraw")
            await interaction.response.send_message("You are not my dad")
            return


def setup(client):
    client.add_cog(xdefiant_event(client))
