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

        # CHECK IF EVENT IS ON
        game = "xdefiant"
        flag, check = stokeIns.Event().isOn(game)
        logFlags.append(flag)
        if check == 1:
            flag2, bugsId = stokeIns.bugsProfile().bugsId(senderId)
            logFlags.append(flag2)
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
        guildId = message.guild.id
        stokeIns = Stoke()
        flag3, ret = stokeIns.Guilds().pullChannel(guildId, find=channel)
        logFlags.append(flag3)

        if message.channel.id != ret:
            stokeIns.Log().log(
                bugsId, guildId=guildId, flags=logFlags, channel=channel, cmd="Xsc"
            )
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

                flag4, check = stokeIns.Event().checkSubmission(senderId, event="xdef")
                logFlags.append(flag4)
                if flag4 == 2:
                    pass
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xsc",
                    )
                    await message.channel.send(
                        f"Sorry, but an error occurred and I did not save your screenshot properly.\nFlag {flag}"
                    )
                    return
                if check is not None:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xsc",
                    )
                    await message.channel.send(
                        f"You have already used a submission for this tournament.\n\nIf you wish to submit a new screenshot you have to delete the previous.\n\nIn order to delete your previous screenshot use the following command.\n\n/xdefiant_event submission_delete"
                    )
                    return

                # CHECKING FOR AN IMG IN CHANNEL
                attachments = message.attachments[0]
                imgs = ("png", "jpg")
                if attachments.url.endswith(imgs):
                    screenshot_url = attachments.url
                    # print(screenshot)

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
                    file_folder = bugsId
                    path = os.path.join(parent_folder, file_folder)
                    try:
                        os.makedirs(path)

                    except FileExistsError:
                        pass

                    file_path = f"xdef_sc/{file_folder}/{file_name}"
                    with open(file_path, "wb") as file:
                        file.write(response.content)

                    # SEND MSG TO USER
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xsc",
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
        flag, bugsId = stokeIns.bugsProfile().bugsId(discord)
        logFlags.append(flag)
        channel = "scSubmission"

        # CHECK IF EVENT IS ON
        flag2, eventCheck = stokeIns.Event().isOn(event="xdefiant")
        logFlags.append(flag2)
        if eventCheck == 1:
            pass
        else:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="XscDelete",
            )
            await interaction.response.send_message("XDefiant event is not active")
            return

        # RATE CHECK
        rateCheck = stokeIns.Rate().rateCheck(discord, channel="scSubmission")
        logFlags.append(rateCheck)
        if rateCheck == 2:
            pass
        elif rateCheck == 5:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="XscDelete",
            )
            return
        elif rateCheck == 1:
            stokeIns.Log().log(bugsId, flags=logFlags, channel=channel, cmd="XscDelete")
            return

        # PULL SC_SUBMISSION CHANNEL BASED ON GUILD
        flag3, ret = stokeIns.Guilds().pullChannel(guildId, find=channel)
        logFlags.append(flag3)

        # MUST BE IN THE SC_SUBMISSION CHANNEL
        if interaction.channel.id != ret:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="XscDelete",
            )
            await interaction.response.send_message(
                "You have to use this command in the sc_submission channel"
            )
            return

        # USER MUST HAVE THE COMPETITOR ROLE
        # PULL THE ROLE ID OF THE COMPETITOR ROLE BASED ON GUILD
        f, compRole = stokeIns.Guilds().pullRole(guildId, find="competitor")
        logFlags.append(f)
        fleg = False
        for role in mem.roles:
            if role.id == compRole:
                fleg = True
                break

        if fleg == True:
            pass
        else:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="XscDelete",
            )
            await interaction.response.send_message(
                "You must have the competitor role to post in this channel."
            )
            return

        delete = stokeIns.Event().submissionDelete(discord, event="xdef")
        logFlags.append(delete)
        if delete == 2:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="XscDelete",
            )
            # SEND MSG TO USER
            await interaction.response.send_message(
                "Your submission has now been deleted."
            )
            return
        elif delete == 3:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="XscDelete",
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
        flag, bugsId = stokeIns.bugsProfile().bugsId(discord)
        logFlags.append(flag)

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
            stokeIns.Log().log(
                bugsId, guildId=guildId, flags=logFlags, channel="Admin", cmd="XDraw"
            )
            await interaction.response.send_message(
                f"The winner(s) are,\n{winners}\nThe winning community is {guild} with {guildPoints} points!"
            )
        else:
            stokeIns.Log().log(
                bugsId, guildId=guildId, flags=logFlags, channel="Admin", cmd="XDraw"
            )
            await interaction.response.send_message("You are not my dad")
            return


def setup(client):
    client.add_cog(xdefiant_event(client))
