import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from stoke import Stoke


class bugs_profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(
        name="bugs_profile",
        description="main command that leads to creating, deleting, and retrieving your bugs profile",
    )
    async def bugs_profile(
        self,
        interaction: Interaction,
        command: str,
        eth_address: str = None,
        update_addr: str = None,
    ):
        # VARIABLES
        command = command.lower()
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        logFlags = []
        flag, bugsId = stokeIns.bugsProfile().bugsId(discord)
        logFlags.append(flag)
        channel = "playerProfile"

        # PULL BUGS PROFILE CHANNEL BASED ON GUILD
        flag2, ret = stokeIns.Guilds().pullChannel(guildId, find=channel)
        logFlags.append(flag2)

        # MUST BE IN THE BUGS PROFILE CHANNEL
        if interaction.channel.id != ret:
            stokeIns.Log().log(
                bugsId,
                guildId=guildId,
                flags=logFlags,
                channel=channel,
                cmd="bugsProfile",
            )
            await interaction.response.send_message(
                "You have to use this command in the player profile channel"
            )
            return

        # IF STATEMENTS FOR COMMAND PARAM
        if command == "create":
            # DATA CHECK
            if eth_address == None:
                await interaction.response.send_message(
                    "You must provide your ethereum address in this command."
                )
                return
            elif len(eth_address) < 42:
                await interaction.response.send_message(
                    "This is not an ethereum address"
                )
                return

            # CONNECT TO ETH API AND VERIFY A TRANSACTION MADE TO THE BUGS WALLET
            create = stokeIns.bugsProfile().create(discord, ethAddr=eth_address)
            logFlags.append(create)
            if create == 2:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bcreate",
                )
                await interaction.response.send_message(
                    "All good profile created, Next you can create your player profile in the Server which you want to represent in the events."
                )
                return
            elif create == 5:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bcreate",
                )
                await interaction.response.send_message(
                    f"Sorry but this address already has a bugs profile attached to it."
                )
                return
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bcreate",
                )
                await interaction.response.send_message(f"{create}")
                return

        # DELETE
        elif command == "delete":
            # CHECK FOR BUGS PROFILE
            bugsProfile = stokeIns.bugsProfile.hasProfile(discord)
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                flag3, roles = stokeIns.bugsProfile().delete(discord, guildId)
                logFlags.append(flag3)

                if flag3 == 3:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Bdelete",
                    )
                    await interaction.response.send_message(
                        "There was an error finding the roles to remove"
                    )
                    return

                if roles:
                    apexRoleId = roles[0]
                    xdefRoleId = roles[1]
                    competitorRoleId = roles[2]

                    apexRole = nextcord.utils.get(
                        interaction.guild.roles, id=apexRoleId
                    )
                    xdefRole = nextcord.utils.get(
                        interaction.guild.roles, id=xdefRoleId
                    )
                    competitorRole = nextcord.utils.get(
                        interaction.guild.roles, id=competitorRoleId
                    )
                    # REMOVE APEX ROLE
                    try:
                        await mem.remove_roles(apexRole)
                    except:
                        pass
                    # REMOVE XDEF ROLE
                    try:
                        await mem.remove_roles(xdefRole)
                    except:
                        pass
                    # REMOVE COMPETITOR ROLE
                    try:
                        await mem.remove_roles(competitorRole)
                    except:
                        pass
                    stokeIns.Log().log(
                        guildId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Bdelete",
                    )
                    await interaction.response.send_message(
                        "Profile deleted and roles removed!"
                    )
                    return
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bdelete",
                )
                await interaction.response.send_message(
                    "Sorry but I did not find a profile to delete"
                )
                return

        # RETRIEVE
        elif command == "retrieve":
            # CHECK FOR A PROFILE TO RETRIEVE
            bugsProfile = stokeIns.bugsProfile().hasProfile(discord)
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                flag3, profile = stokeIns.bugsProfile().retrieve(discord)
                logFlags.append(flag3)
                if flag3 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Bretrieve",
                    )
                    await interaction.response.send_message(
                        f"This is the Ethereum address for your bugs Profile\n{profile}"
                    )
                    return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Bretrieve",
                    )
                    await interaction.response.send_message(
                        "An error occured when retrieving your Profile"
                    )
                    return
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bretrieve",
                )
                await interaction.response.send_message(
                    "Sorry but I could not find a bugs Profile with your Discord Username."
                )
                return

        # UPDATE
        elif command == "update":
            # CHECK FOR A BUGS PROFILE
            bugsProfile = stokeIns.bugsProfile().hasProfile(discord)
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                pass
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bupdate",
                )
                await interaction.response.send_message(
                    "Sorry mate but you don't even have a bugs profile to begin with."
                )
                return

            # TAKE NEW ADDR AND CHECK FOR A PAYMENT MADE TO BUGS TREASURY
            update = stokeIns.bugsProfile().update(discord, update_addr)
            logFlags.append(update)

            if update == 2:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bupdate",
                )
                await interaction.response.send_message(f"Alright profile updated!")
                return
            elif update == 5:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bupdate",
                )
                await interaction.response.send_message(
                    "Sorry but this address already has a bugs profile attached."
                )
                return
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Bupdate",
                )
                await interaction.response.send_message(
                    "Sorry but an error occurred when check that transaction."
                )
                return

        else:
            await interaction.response.send_message(
                "The command options and their requirements are:\ncmd = create, enter eth_addr\ncmd = delete\ncmd = retrieve\ncmd = update, enter update_addr"
            )
            return


def setup(client):
    client.add_cog(bugs_profile(client))
