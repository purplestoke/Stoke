import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from stoke import Stoke


class player_profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    # PLAYER PROFILE MAIN COMMAND
    @nextcord.slash_command(
        name="player_profile",
        description="create your player profile // GAME OPTIONS: apex, xdef // COMMAND OPTIONS: create, delete, retrieve",
    )
    async def player_profile(
        self, interaction: Interaction, game: str, command: str, gamertag: str = None
    ):
        # VARS
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        logFlags = []
        game = game.lower()
        command = command.lower()
        channel = "playerProfile"

        # PULL PLAYER PROFILE CHANNEL BASED ON GUILD
        find = "playerProfile"
        flag2, ret = stokeIns.Guilds().pullChannel(guildId, find)
        logFlags.append(flag2)

        # MUST BE IN THE BUGS PROFILE CHANNEL
        if interaction.channel.id != ret:
            await interaction.response.send_message(
                "You have to use this command in the player profile channel"
            )
            return

        # CHECK FOR BUGS PROFILE
        flag, bugsId = stokeIns.bugsProfile().bugsId(discord)
        logFlags.append(flag)
        if flag == 2:
            pass
        else:
            await interaction.response.send_message(
                "You need a bugs Profile in order to create a player profile."
            )
            return

        if flag2 == 3:
            logFlags.append(flag)
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="playerProfile",
            )
            await interaction.response.send_message(
                "Sorry but something went wrong internally when executing your command.\nTry again later or contact purplestoke"
            )
            return

        # RATE CHECK
        rateCheck = stokeIns.Rate().rateCheck(discord, channel="playerProfile")
        if rateCheck == 2:
            logFlags.append(rateCheck)
            pass
        elif rateCheck == 5:
            logFlags.append(rateCheck)
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="create",
            )
            return
        elif rateCheck == 1:
            logFlags.append(rateCheck)
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="create",
            )
            return

        # CREATE PROFILE
        if command == "create":
            if gamertag != None and len(gamertag) < 20:
                if game == "apex":
                    insert = stokeIns.PlayerProfile().create(
                        discord, gamertag, guildId, game
                    )
                    logFlags.append(insert)
                    if insert == 1:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Acreate",
                        )
                        await interaction.response.send_message(
                            "You need to create a bugs profile first in order to create a player profile."
                        )
                        return
                    elif insert == 5:
                        logFlags.append(flag3)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Acreate",
                        )
                        await interaction.response.send_message(
                            f"This gamertag is already being used."
                        )
                        return
                    elif insert > 2:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Acreate",
                        )
                        await interaction.response.send_message(
                            "Sorry but something happened on my end and I was unable to create that profile."
                        )
                        return
                    elif insert == 2:
                        pass

                    # PULL THE APEX ROLE FROM DATABASE
                    fleg = "apex"
                    flag3, apexRole = stokeIns.Guilds().pullRole(guildId, fleg)
                    if flag3 == 2:
                        logFlags.append(flag3)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Acreate",
                        )
                        apex_role = nextcord.utils.get(
                            interaction.guild.roles, id=apexRole
                        )

                        # SEND USER A MESSAGE AND ADD ROLE
                        await mem.add_roles(apex_role)
                        await interaction.response.send_message(
                            f"Cool cool, I got your gamertag {gamertag} added."
                        )
                        return
                    else:
                        logFlags.append(flag3)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Acreate",
                        )
                        await interaction.response.send_message(
                            "Sorry but something went wrong when fetching the Apex Role. I have your info I was just unable to give you the Apex role."
                        )
                        return

                elif game == "xdef":
                    # CREATE PROFILE
                    insert = stokeIns.PlayerProfile().create(
                        discord, gamertag, guildId, game
                    )
                    logFlags.append(insert)
                    if insert == 1:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xcreate",
                        )
                        await interaction.response.send_message(
                            "You need to create a bugs profile first in order to create a player profile."
                        )
                        return
                    elif insert == 5:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xcreate",
                        )
                        await interaction.response.send_message(
                            "This gamertag is already being used."
                        )
                        return
                    elif insert > 2:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xcreate",
                        )
                        await interaction.response.send_message(
                            "Sorry but something happened on my end and I was unable to create that profile."
                        )
                        return
                    elif insert == 2:
                        pass

                    # PULL XDEF ROLE
                    flag3, xdefRole = stokeIns.Guilds().pullRole(guildId, find="xdef")
                    logFlags.append(flag3)
                    if flag3 == 2:
                        xdef_role = nextcord.utils.get(
                            interaction.guild.roles, id=xdefRole
                        )
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xcreate",
                        )
                        # SEND MSG AND ASSIGN ROLE
                        await mem.add_roles(xdef_role)
                        await interaction.response.send_message(
                            f"Alright XDefiant profile created with gamertag, {gamertag}"
                        )
                        return
                    else:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xcreate",
                        )
                        await interaction.response.send_message(
                            "Sorry but something went wrong when fetching the XDefiant Role. I have your info I was just unable to give you the XDefiant role."
                        )
                        return

            else:
                await interaction.response.send_message(
                    "Sorry mate but you need to provide your gamertag to create a profile.\nThis gamertag is specific to the game you are creating the profile for."
                )
                return

        # DELETE PROFILE
        elif command == "delete":
            if gamertag == None:
                pass
            else:
                await interaction.response.send_message(
                    "You do not need to provide a gamertag in order to delete your profile."
                )
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="delete",
                )
                return

            if game == "apex":
                # DELETE PROFILE
                deleteProfile = stokeIns.PlayerProfile().delete(discord, type="apex")
                logFlags.append(deleteProfile)
                if deleteProfile == 2:
                    # FETCH ROLE
                    flag3, role = stokeIns.Guilds().pullRole(guildId, find="apex")
                    logFlags.append(flag3)
                    if flag3 == 2:
                        apex_role = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.remove_roles(apex_role)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Adelete",
                        )
                        await interaction.response.send_message(
                            "Apex Profile deleted and role removed!"
                        )
                        return
                    else:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Adelete",
                        )
                        await interaction.response.send_message(
                            "Sorry but I was unable to pull the Apex role at this time."
                        )
                        return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Adelete",
                    )
                    await interaction.response.send_message(
                        "I encountered an error when deleting your profile please try again."
                    )
                    return

            elif game == "xdef":
                # DELETE PROFILE
                deleteProfile = stokeIns.PlayerProfile().delete(discord, type="xdef")
                logFlags.append(deleteProfile)
                if deleteProfile == 2:
                    # FETCH ROLE
                    flag3, role = stokeIns.Guilds().pullRole(guildId, find="xdef")
                    logFlags.append(flag3)
                    if flag3 == 2:
                        xdef_role = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.remove_roles(xdef_role)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xdelete",
                        )
                        await interaction.response.send_message(
                            "XDefiant Profile deleted and role removed!"
                        )
                        return
                    else:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xdelete",
                        )
                        await interaction.response.send_message(
                            "Sorry but I was unable to pull the XDefiant role at this time."
                        )
                        return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xdelete",
                    )
                    await interaction.response.send_message(
                        "Sorry but something went wrong, please try again."
                    )
                    return

        # RETRIEVE PROFILE
        elif command == "retrieve":
            if gamertag == None:
                pass
            else:
                await interaction.response.send_message(
                    "You do not need to provide a gamertag in order to delete your profile."
                )
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="delete",
                )
                return

            if game == "apex":
                # FETCH INFORMATION IN DB
                flag3, profile = stokeIns.PlayerProfile().retrieve(discord, type="apex")
                logFlags.append(flag3)

                if flag3 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aretrieve",
                    )
                    await interaction.response.send_message(
                        f"This is the gamertag I have for your Apex Legends Player Profile \n{profile}"
                    )
                    return

                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aretrieve",
                    )
                    await interaction.response.send_message(
                        f"Sorry something went wrong and I was unable to retrieve your profile.\nFlag {profile}"
                    )

            elif game == "xdef":
                flag3, profile = stokeIns.PlayerProfile().retrieve(discord, type="xdef")
                logFlags.append(flag3)

                if flag3 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xretrieve",
                    )
                    await interaction.response.send_message(
                        f"This is the gamertag I have for your XDefiant Player Profile \n{profile}"
                    )
                    return

                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xretrieve",
                    )
                    await interaction.response.send_message(
                        f"Sorry something went wrong and I was unable to retrieve your profile.\nFlag {profile}"
                    )
                    return
        else:
            return


def setup(client):
    client.add_cog(player_profile(client))
