import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from requests import get
from API_Tokens import *
import sqlite3
from stoke import Stoke


class channel_setup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # CREATE BUGS CATEGORY
        guildName = guild.name
        guildId = guild.id
        catName = "bugs"
        logFlags = []
        stokeIns = Stoke()
        logIns = stokeIns.Log(
            bugs_id=None, guildId=guildId, flags=logFlags, discord=None
        )

        if guild:
            try:
                # CREATE BUGS CATEGORY
                existingCat = nextcord.utils.get(guild.categories, name=catName)
                if existingCat:
                    cat = existingCat
                else:
                    cat = await guild.create_category(catName)
                flag = 2
                logFlags.append(flag)
            except:
                flag = 3
                logFlags.append(flag)
                logIns.setupLog(_cmd="channelSetup", _guildName=guildName)

            # CREATE SPECIFIC CHANNELS
            try:
                channelNames = [
                    "intercom",
                    "player_profile",
                    "payment_verify",
                    "sc_submission",
                ]
                roleNames = {
                    "apex": 0xFE0000,
                    "xdef": 0x037096,
                    "competitor": 0x907FAD,
                }
                createdChannels = []
                createdRoles = []

                # CHECK IF CHANNEL ALREADY EXISTS IN SERVER
                for channel in channelNames:
                    existingChannel = nextcord.utils.get(guild.channels, name=channel)
                    if existingChannel:
                        existingChannelId = existingChannel.id
                        createdChannels.append(existingChannelId)
                    else:
                        channel = await guild.create_text_channel(channel, category=cat)
                        createdChannels.append(channel.id)

                for role_name, color in roleNames.items():
                    existingRole = nextcord.utils.get(guild.roles, name=role_name)
                    if existingRole:
                        existingRoleId = existingRole.id
                        createdRoles.append(existingRoleId)
                    else:
                        role = await guild.create_role(name=role_name, color=color)
                        createdRoles.append(role.id)
                flag2 = 2
                logFlags.append(flag2)
            except:
                flag2 = 3
                logFlags.append(flag2)
                logIns.setupLog(_cmd="channelSetup", _guildName=guildName)
                return

            try:
                # STORE CHANNEL & ROLE IDS IN DATABSE
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO Stoke_Guilds (guild_name, guild, intercom, player_profile, payment_verify, sc_submission, apex_role, xdef_role, competitor_role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        guildName,
                        guildId,
                        createdChannels[0],
                        createdChannels[1],
                        createdChannels[2],
                        createdChannels[3],
                        createdRoles[0],
                        createdRoles[1],
                        createdRoles[2],
                    ),
                )

                conn.commit()
                conn.close()
                flag3 = 2
                logFlags.append(flag3)
            except:
                conn.close()
                flag3 = 3
                logFlags.append(flag3)
                logIns.setupLog(_cmd="channelSetup", _guildName=guildName)
                return

            try:
                # CHANGE CHANNEL PERMISSIONS BASED ON ROLE
                # ROLE VARS
                apexRole = createdRoles[0]
                apexRole = guild.get_role(int(apexRole))
                xdefRole = createdRoles[1]
                xdefRole = guild.get_role(int(xdefRole))
                competitorRole = createdRoles[2]
                competitorRole = guild.get_role(int(competitorRole))
                everyone = guild.default_role

                # CHANNEL VARS
                paymentVerifyChannel = createdChannels[1]
                paymentVerifyChannel = guild.get_channel(paymentVerifyChannel)

                scSubmissionChannel = createdChannels[2]
                scSubmissionChannel = guild.get_channel(scSubmissionChannel)

                # PAYMENT VERIFY CHANNEL
                await paymentVerifyChannel.set_permissions(
                    apexRole, read_messages=True, send_messages=True
                )
                await paymentVerifyChannel.set_permissions(
                    xdefRole, read_messages=True, send_messages=True
                )
                await paymentVerifyChannel.set_permissions(
                    competitorRole, read_messages=True, send_messages=True
                )
                await paymentVerifyChannel.set_permissions(
                    everyone, read_messages=False, send_messages=False
                )
                # SC SUBMISSION CHANNEL
                await scSubmissionChannel.set_permissions(
                    xdefRole, read_messages=False, send_messages=False
                )
                await scSubmissionChannel.set_permissions(
                    apexRole, read_messages=False, send_messages=False
                )
                await scSubmissionChannel.set_permissions(
                    competitorRole, read_messages=True, send_messages=True
                )
                await scSubmissionChannel.set_permissions(
                    everyone, read_messages=False, send_messages=False
                )
                flag4 = 2
                logFlags.append(flag4)
                logIns.setupLog(_cmd="channelSetup", _guildName=guildName)
                return
            except:
                flag4 = 3
                logFlags.append(flag4)
                logIns.setupLog(_cmd="channelSetup", _guildName=guildName)
                return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # GUILD VARIABLES
        guildId = guild.id
        guildName = guild.name
        logFlags = []
        stokeIns = Stoke()
        logIns = stokeIns.Log(bugs_id=None, guildId=None, flags=logFlags, discord=None)

        try:
            # CONNECT TO DB AND REMOVE GUILD ROW
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            # REMOVE ALL PLAYER PROFILES BELONGING TO THAT GUILD
            cur.execute(
                "DELETE FROM Apex_Profile WHERE guild_id IN(SELECT guild FROM Stoke_Guilds WHERE guild = ?)",
                (guildId,),
            )

            cur.execute("DELETE FROM Stoke_Guilds WHERE guild = ?", (guildId,))
            conn.commit()
            conn.close()
            flag = 2
            logFlags.append(flag)
            logIns.leaveLog(_cmd="Leftbugs", _guildName=guildName)
            return
        except:
            flag = 3
            logFlags.append(flag)
            logIns.leaveLog(_cmd="Leftbugs", _guildName=guildName)


def setup(client):
    client.add_cog(channel_setup(client))
