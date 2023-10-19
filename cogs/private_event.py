import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from API_Tokens import *
import sqlite3
from functions import Functions
import requests
from datetime import datetime
import os
from stoke import Stoke
from API_Tokens import purpleStoke


class private_event(commands.Cog):
    def __init__(self, client):
        self.client = client

    # MAIN COMMAND
    @nextcord.slash_command(
        name="private_event",
        description="create a private event for the winning community",
    )
    async def private_event(self, interaction: Interaction):
        pass

    # SETUP EVENT IN WINNING SERVER --------------------------------------------------------------------------------------------
    @private_event.subcommand(name="setup")
    async def setup(self, interaction: Interaction, event):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        logFlags = []

        if discord != purpleStoke:
            return

        winGuild, guildPoints = Functions.winning_guild(event)

        # CREATE A CHANNEL IN GUILD FOR SPECIAL EVENT
        try:
            channelName = "community_event"
            roleName = "buggin"
            color = 0x907FAD
            cat = nextcord.utils.get(guild.categories, name="bugs")

            makeChannel = await guild.create_text_channel(channelName, category=cat)
            makeRole = await guild.create_role(name=roleName, color=color)
            channelId = makeChannel.id
            roleId = makeRole.id
            privChannel = guild.get_channel(channelId)

            bugginRole = nextcord.utils.get(guild.roles, name=roleName)

            await privChannel.set_permissions(
                bugginRole, read_messages=True, send_messages=True
            )
            flag = 2
            logFlags.append(flag)
        except:
            flag = 3
            logFlags.append(flag)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="setup")
            await interaction.response.send_message("e")
            return

        # PULL GUILD ID BASED ON WINNER
        conn = sqlite3.connect("bugs_DB2.sqlite")
        cur = conn.cursor()

        try:
            # INSERT PRIV CHANNEL INFO INTO STOKE_GUILDS
            cur.execute(
                "UPDATE Stoke_Guilds SET priv_event_channel = ?, priv_event_role = ?, community_score = ? WHERE guild = ?",
                (
                    channelId,
                    roleId,
                    guildPoints,
                    guildId,
                ),
            )
            conn.commit()
            flag2 = 2
            logFlags.append(flag2)
        except:
            flag2 = 3
            logFlags.append(flag2)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="setup")
            await interaction.response.send_message("e")
            return

        try:
            # STORE ALL USERS WHO COMPETED UNDER THAT GUILD
            pullComp = cur.execute(
                "SELECT bugs_id FROM Apex_Profile WHERE guild_id = ?",
                (winGuild,),
            )
            retComp = pullComp.fetchall()

            for bugsId in retComp:
                cur.execute(
                    "INSERT INTO Private_Event (bugs_id) VALUES (?)",
                    (bugsId,),
                )
                conn.commit()
            conn.close()
            flag3 = 2
            logFlags.append(flag3)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="setup")
            await interaction.response.send_message("Done!")
            return
        except:
            flag3 = 3
            logFlags.append(flag3)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="setup")
            await interaction.response.send_message("e")
            return

    # TEAR DOWN EVENT IN SERVER --------------------------------------------------------------------------------------------
    @private_event.subcommand(name="finished")
    async def finsished(self, interaction: Interaction):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        logFlags = []

        if discord != purpleStoke:
            return

        try:
            # REMOVE CHANNEL FROM GUILD
            channelName = "community_event"
            channel = nextcord.utils.get(guild.channels, name=channelName)
            await channel.delete()

            # REMOVE ROLE FROM GUILD
            roleName = "buggin"
            role = nextcord.utils.get(guild.roles, name=roleName)
            await role.delete()
            flag = 2
            logFlags.append(flag)
        except:
            flag = 3
            logFlags.append(flag)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="teardown")
            await interaction.response.send_message("e")
            return

        try:
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            cur.execute("DELETE FROM Private_Event")
            cur.execute(
                "UPDATE Stoke_Guilds SET priv_event_channel = NULL, priv_event_role = NULL WHERE guild = ?",
                (guildId,),
            )
            conn.commit()
            conn.close()
            f = 2
        except:
            flag2 = 3
            logFlags.append(flag2)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="teardown")
            await interaction.response.send_message("e")
            return

        logFlags.append(f)
        stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="teardown")
        await interaction.response.send_message("Done!")
        return

    # RAFFLE DRAW  --------------------------------------------------------------------------------------------
    @private_event.subcommand(name="draw")
    async def draw(self, interaction: Interaction, event):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        stokeIns = Stoke()
        logFlags = []

        # CHECK IF USER HAS ADMIN ROLE
        if discord == purpleStoke:
            drawFlag, winString = stokeIns.PrivateEvent().privEventDraw(event)
            logFlags.append(drawFlag)
            if drawFlag == 2:
                stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="draw")
                await interaction.response.send_message(
                    f"The winner(s) are,\n{winString}"
                )
                return
        else:
            flag3 = 5
            logFlags.append(flag3)
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="draw")
            await interaction.response.send_message("You are not my dad")
            return

    @private_event.subcommand(name="compete")
    async def compete(self, interaction: Interaction):
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        logFlags = []

        # CHECK IF IN COMMUNITY EVENT CHANNEL
        f, privateChannel = stokeIns.Guilds().pullChannel(guildId, find="privEvent")
        if interaction.channel.id == privateChannel:
            pass
        else:
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="compete")
            await interaction.response.send_message(f"e {f}")
            return

        # CHECK IF USER CAN COMPETE IN EVENT
        try:
            bugsIdFlag, bugsId = stokeIns.bugsProfile().bugsId(discord)
            logFlags.append(bugsIdFlag)
            if bugsIdFlag == 2:
                pass
            else:
                stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="compete")
                await interaction.response.send_message(
                    "You do not have a bugs Profile."
                )
                return

            compListFlag, retCompetitors = stokeIns.PrivateEvent().competitorList()
            logFlags.append(compListFlag)
            if compListFlag == 2:
                pass
            else:
                await interaction.response.send_message(f"Error {compListFlag}")
                return

            for id in retCompetitors:
                if id == bugsId:
                    # FETCH THE BUGGIN ROLE AND ASSIGN
                    roleFlag, role = stokeIns.Guilds().pullRole(
                        guildId, find="privEventRole"
                    )
                    logFlags.append(roleFlag)
                    if roleFlag == 2:
                        bugginRole = nextcord.utils.get(
                            interaction.guild.roles, id=role
                        )
                        await mem.add_roles(bugginRole)
                        stokeIns.Log().privEventLog(
                            discord, flags=logFlags, cmd="compete"
                        )
                        await interaction.response.send_message(
                            f"Boom you are now competing in the private event."
                        )
                        return
                else:
                    continue

            await interaction.response.send_message(
                f"Sorry lad but you did not compete in the original event.\nOnly those that competed in the original event can compete in the private event."
            )
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="compete")
            return
        except:
            stokeIns.Log().privEventLog(discord, flags=logFlags, cmd="compete")
            await interaction.response.send_message(
                "It looks like you do not have a bugs Profile, in order to compete in bugs private events you must create a bugs profile for 0.005 ETH and you must have competed in the previous event in order to compete in this one."
            )
            return

    # EVENT LISTENER --------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        # ONLY RESPONDS TO MESSAGES IN THE PRIVATE CHANNEL
        guildId = message.guild.id
        sender = message.author
        str_sender = sender.id
        stokeIns = Stoke()
        logFlags = []

        try:
            pull = cur.execute(
                "SELECT priv_event_channel FROM Stoke_Guilds WHERE guild = ?",
                (guildId,),
            )
            ret = pull.fetchone()[0]
            channel = int(ret)
            logFlags.append(2)
        except sqlite3.Error as e:
            logFlags.append(3)
            stokeIns.Log().privEventLog(str_sender, flags=logFlags, cmd="scSubmission")
            return
        except:
            return

        if message.channel.id != channel:
            return

        # CHECK TO MAKE SURE STOKE DOESNT RESPOND TO HIS OWN MSG
        if str_sender == stoke:
            return

        # CHECK FOR BUGGIN ROLE
        if "buggin" in [role.name.lower() for role in sender.roles]:
            # CHECKING FOR AN IMG IN CHANNEL
            if not message.attachments:
                return

            # CHECK DB FOR A SUBMISSION
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pull_submission = cur.execute(
                    "SELECT submission FROM Private_Event WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (str_sender,),
                )
                check = pull_submission.fetchone()[0]
                logFlags.append(2)
            except:
                logFlags.append(3)
                stokeIns.Log().privEventLog(
                    str_sender, flags=logFlags, cmd="scSubmission"
                )
                await message.channel.send("Error")

            if check is not None:
                stokeIns.Log().privEventLog(
                    str_sender, flags=logFlags, cmd="scSubmission"
                )
                await message.channel.send(
                    f"You have already used a submission for this tournament.\n\nIf you wish to submit a new screenshot you have to delete the previous.\n\nIn order to delete your previous screenshot use the following command.\n\n/xdefiant_event submission_delete"
                )
                conn.close()
                return

            # HANDLING IMG IN CHANNEL
            attachments = message.attachments[0]
            imgs = ("png", "jpg")
            if attachments.url.endswith(imgs):
                screenshot_url = attachments.url

                # SAVING SC TO SUB-DIRECTORY ON MACHINE
                response = requests.get(screenshot_url)
                now = datetime.now()
                file_name = (
                    f"priv_event_{str_sender + now.strftime('%Y%m%d_%H%M%S')}.jpg"
                )

                # SAVE FILENAME TO DB
                cur.execute(
                    "UPDATE Private_Event SET submission = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (
                        file_name,
                        str_sender,
                    ),
                )
                conn.commit()

                # CREATE FOLDER OF DISCORD MEMBER
                parent_folder = "priv_event"
                file_folder = str_sender
                path = os.path.join(parent_folder, file_folder)
                try:
                    os.makedirs(path)

                except FileExistsError:
                    pass

                file_path = f"priv_event/{file_folder}/{file_name}"
                with open(file_path, "wb") as file:
                    file.write(response.content)

                # SEND MSG TO USER
                stokeIns.Log().privEventLog(
                    str_sender, flags=logFlags, cmd="scSubmission"
                )
                await message.channel.send(
                    f"Got your screenshot, you are all set to potentially win the Eth prize!\n\nRemember in the bugs Private Event you can only submit 1 screenshot.\nYOU CANNOT DELETE PREVIOUS SCREENSHOTS IN THIS EVENT."
                )
                return
            else:
                logFlags.append(3)
                stokeIns.Log().privEventLog(
                    str_sender, flags=logFlags, cmd="scSubmission"
                )
                return


def setup(client):
    client.add_cog(private_event(client))
