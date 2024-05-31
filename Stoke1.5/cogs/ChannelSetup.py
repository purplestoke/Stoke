import nextcord
from nextcord.ext import commands
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
            bugsId=None, guildId=guildId, flags=logFlags, discord=None
        )

        if guild:
            try:
                # CREATE BUGS CATEGORY
                existingCat = nextcord.utils.get(guild.categories, name=catName)
                if existingCat:
                    cat = existingCat
                else:
                    cat = await guild.create_category(catName)
                logFlags.append(2)
            except:
                logFlags.append(3)
                logIns.setupLog(cmd="channelSetup", guildName=guildName)

            # CREATE SPECIFIC CHANNELS
            try:
                channelNames = [
                    "intercom",
                    "buggin",
                    "sc_submission",
                ]
                roleNames = {
                    "apex": 0xFE0000,
                    "finals": 0xe4ba3f,
                    "xdefiant": 0x313f62,
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

                #CHECK IF ROLES ALREADY EXIST IN GUILD
                for role_name, color in roleNames.items():
                    existingRole = nextcord.utils.get(guild.roles, name=role_name)
                    if existingRole:
                        existingRoleId = existingRole.id
                        createdRoles.append(existingRoleId)
                    else:
                        role = await guild.create_role(name=role_name, color=color)
                        createdRoles.append(role.id)
                logFlags.append(2)
            except:
                logFlags.append(3)
                logIns.setupLog(cmd="channelSetup", guildName=guildName)
                return

            try:
                # STORE CHANNEL & ROLE IDS IN DATABSE
                conn = sqlite3.connect("bugs_DB.sqlite")
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO Stoke_Guilds (guild_name, guild, intercom, bugs_channel, sc_submission, apex_role, finals_role, xdefiant_role, competitor_role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        guildName,
                        guildId,
                        createdChannels[0],
                        createdChannels[1],
                        createdChannels[2],
                        createdRoles[0],
                        createdRoles[1],
                        createdRoles[2],
                        createdRoles[3]
                    ),
                )

                conn.commit()
                logFlags.append(2)
            except:
                logFlags.append(3)
                logIns.setupLog(cmd="channelSetup", guildName=guildName)
                return
            finally: conn.close()

            try:
                # CHANGE CHANNEL PERMISSIONS BASED ON ROLE
                # ROLE VARS
                apexRole = createdRoles[0]
                aRole = nextcord.utils.get(guild.roles, id=apexRole)
                finalsRole = createdRoles[1]
                fRole = nextcord.utils.get(guild.roles, id=finalsRole)
                xdefiantRole = createdRoles[2]
                xRole = nextcord.utils.get(guild.roles, id=xdefiantRole)
                competitorRole = createdRoles[3]
                cRole = nextcord.utils.get(guild.roles, id=competitorRole)
                everyone = guild.default_role
                # CHANNEL VARS
                scSubmissionChannel = createdChannels[2]
                sChannel = nextcord.utils.get(guild.channels, id=scSubmissionChannel)

                # SC SUBMISSION CHANNEL
                await sChannel.set_permissions(
                    aRole, read_messages=False, send_messages=False
                )
                await sChannel.set_permissions(
                    fRole, read_messages=False, send_messages=False
                )
                await sChannel.set_permissions(
                    xRole, read_messages=False, send_messages=False
                )
                await sChannel.set_permissions(
                    everyone, read_messages=False, send_messages=False
                )
                await sChannel.set_permissions(
                    cRole, read_messages=True, send_messages=True
                )
                logFlags.append(2)
                logIns.setupLog(cmd="channelSetup", guildName=guildName)
                return
            
            except:
                logFlags.append(3)
                logIns.setupLog(cmd="channelSetup", guildName=guildName)
                return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # GUILD VARIABLES
        guildId = guild.id
        guildName = guild.name
        logFlags = []
        stokeIns = Stoke()
        logIns = stokeIns.Log(bugsId=None, guildId=None, flags=logFlags, discord=None)

        try:
            # CONNECT TO DB AND REMOVE GUILD ROW
            conn = sqlite3.connect("bugs_DB.sqlite")
            cur = conn.cursor()

            # REMOVE ALL PLAYER PROFILES BELONGING TO THAT GUILD
            cur.execute(
                "DELETE FROM Apex_Profile WHERE guild_id IN(SELECT guild FROM Stoke_Guilds WHERE guild = ?)",
                (guildId,),
            )
            
            cur.execute(
                "DELETE FROM Finals_Profile WHERE guild_id IN(SELECT guild FROM Stoke_Guilds WHERE guild = ?)",
                (guildId,),
            )

            cur.execute(
                "DELETE FROM XDefiant_Profile WHERE guild_id IN(SELECT guild FROM Stoke_Guilds WHERE guild = ?)",
                (guildId,),
            )

            cur.execute("DELETE FROM Stoke_Guilds WHERE guild = ?", (guildId,))
            conn.commit()
            logFlags.append(2)
            logIns.leaveLog(cmd="Leftbugs", guildName=guildName)
            return
        except:
            logFlags.append(3)
            logIns.leaveLog(cmd="Leftbugs", guildName=guildName)

def setup(client):
    client.add_cog(channel_setup(client))
