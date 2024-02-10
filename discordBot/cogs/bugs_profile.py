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
    ):
        # VARIABLES
        command = command.lower()
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        bugsProfileIns = stokeIns.bugsProfile(discord, eth_address)
        logFlags = []
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        channel = "playerProfile"
        guildIns = stokeIns.Guilds(channel, guildId)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)

        # PULL BUGS PROFILE CHANNEL BASED ON GUILD
        flag2, ret = guildIns.pullChannel()
        logFlags.append(flag2)

        # MUST BE IN THE BUGS PROFILE CHANNEL
        if interaction.channel.id != ret:
            logIns.log(
                _channel=channel,
                _cmd="bugsProfile",
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
            create = bugsProfileIns.create()
            logFlags.append(create)
            if create == 2:
                logIns.log(
                    _channel=channel,
                    _cmd="Bcreate",
                )
                await interaction.response.send_message(
                    "All good profile created, Next you can create your player profile in the Server which you want to represent in the events."
                )
                return
            elif create == 5:
                logIns.log(
                    _channel=channel,
                    _cmd="Bcreate",
                )
                await interaction.response.send_message(
                    f"Sorry but this address already has a bugs profile attached to it."
                )
                return
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Bcreate",
                )
                await interaction.response.send_message(f"{create}")
                return

        # DELETE
        elif command == "delete":
            # CHECK FOR BUGS PROFILE
            bugsProfile = bugsProfileIns.hasProfile()
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                flag3, roles = bugsProfileIns.delete()
                logFlags.append(flag3)

                if flag3 == 3:
                    logIns.log(
                        _channel=channel,
                        _cmd="Bdelete",
                    )
                    await interaction.response.send_message(
                        "There was an error finding the roles to remove"
                    )
                    return

                if roles:
                    apexRoleId = roles[0]
                    xdefRoleId = roles[1]

                    try:
                        apexRole = nextcord.utils.get(
                            interaction.guild.roles, id=apexRoleId
                        )
                    except:
                        pass
                    try:
                        xdefRole = nextcord.utils.get(
                            interaction.guild.roles, id=xdefRoleId
                        )
                    except:
                        pass
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
                    logIns.log(
                        _channel=channel,
                        _cmd="Bdelete",
                    )
                    await interaction.response.send_message(
                        "Profile deleted and roles removed!"
                    )
                    return
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Bdelete",
                )
                await interaction.response.send_message(
                    "Sorry but I did not find a profile to delete"
                )
                return

        # RETRIEVE
        elif command == "retrieve":
            # CHECK FOR A PROFILE TO RETRIEVE
            bugsProfile = bugsProfileIns.hasProfile()
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                flag3, profile = bugsProfileIns.retrieve()
                logFlags.append(flag3)
                if flag3 == 2:
                    logIns.log(
                        _channel=channel,
                        _cmd="Bretrieve",
                    )
                    await interaction.response.send_message(
                        f"This is the Ethereum address for your bugs Profile\n{profile}"
                    )
                    return
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Bretrieve",
                    )
                    await interaction.response.send_message(
                        "An error occured when retrieving your Profile"
                    )
                    return
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Bretrieve",
                )
                await interaction.response.send_message(
                    "Sorry but I could not find a bugs Profile with your Discord Username."
                )
                return

        # UPDATE
        elif command == "update":
            # CHECK FOR A BUGS PROFILE
            bugsProfile = bugsProfileIns.hasProfile()
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                pass
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Bupdate",
                )
                await interaction.response.send_message(
                    "Sorry mate but you don't even have a bugs profile to begin with."
                )
                return

            # TAKE NEW ADDR AND CHECK FOR A PAYMENT MADE TO BUGS TREASURY
            update = bugsProfileIns.update()
            logFlags.append(update)

            if update == 2:
                logIns.log(
                    _channel=channel,
                    _cmd="Bupdate",
                )
                await interaction.response.send_message("Alright profile updated!")
                return
            elif update == 5:
                logIns.log(
                    _channel=channel,
                    _cmd="Bupdate",
                )
                await interaction.response.send_message(
                    "Sorry but this address already has a bugs profile attached."
                )
                return
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Bupdate",
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
