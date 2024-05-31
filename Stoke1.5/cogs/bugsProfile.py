import nextcord
from nextcord.ext import commands
from stoke import Stoke
from nextcord import Interaction

# BUTTONS
class bugsPView(nextcord.ui.View):
    def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None

    @nextcord.ui.button(label="Yes Delete", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="No, Cancel", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()

class bugsDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label='create', description='create a bugs profile', value="create"),
            nextcord.SelectOption(label='delete', description='delete your bugs profile', value="delete"),
            nextcord.SelectOption(label='update', description='update your bugs profile', value="update"),
            nextcord.SelectOption(label='retrieve', description='retrieve your bugs profile', value="retrieve")
        ]
        super().__init__(placeholder='Choose an option', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        selectedOption = self.values[0]
        
        #VARIABLES
        mem = interaction.user
        discord = interaction.user.id
        guildId = interaction.guild.id
        logFlags = []

        #CREATE STOKE INSTANCES
        stokeIns = Stoke()
        bugsId = None
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        channel = 'buggin'
        guildIns = stokeIns.Guilds(channel, guildId)

        #PULL CHANNEL ID
        flag2, ret = guildIns.pullChannel()
        logFlags.append(flag2)
        #MUST BE IN THE BUGGIN CHANNEL
        if interaction.channel.id != ret:
            logIns.log(channel, cmd='Bcreate')
            await interaction.response.send_message("Use this command in the buggin channel please.")
            return
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        #CREATE A BUGS PROFILE
        if selectedOption == 'create':
            await interaction.response.send_message(f"You selected option {selectedOption} please paste your Ethereum address which sent 0.003 ETH to the bugs Treasury wallet.")
            message = await interaction.client.wait_for('message', check=check, timeout=60.0)

            #INTEGRITY CHECK
            msg = message.content
            if len(msg) < 42:
                await interaction.followup.send("That is not an Ethereum address and I am unable to use ENS address at this time")
            else:
                pass

            # CONNECT TO ETH API AND VERIFY A TRANSACTION MADE TO THE BUGS WALLET
            bugsProfileIns = stokeIns.bugsProfile(discord, msg)
            create = bugsProfileIns.create()
            logFlags.append(create)
            if create == 2:
                logIns.log(
                    channel=channel,
                    cmd="Bcreate",
                )
                await interaction.followup.send(
                    "All good profile created, Next you can create your player profile in the Server which you want to represent in the events."
                )
                return
            elif create == 5:
                logIns.log(
                    channel=channel,
                    cmd="Bcreate",
                )
                await interaction.followup.send(
                    f"Sorry but this address already has a bugs profile attached to it."
                )
                return
            else:
                logIns.log(
                    channel=channel,
                    cmd="Bcreate",
                )
                await interaction.followup.send(f"{create}")
                return

        #DELETE BUGS PROFILE
        elif selectedOption == 'delete':
            view = bugsPView()
            await interaction.response.send_message(f"You selected option {selectedOption}, please click a button to continue", view=view)
            await view.wait()
            #MESSAGE CHECK
            if view.value is True:
                # CHECK FOR BUGS PROFILE
                bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
                bugsProfile = bugsProfileIns.hasProfile()
                logFlags.append(bugsProfile)
                if bugsProfile == 2:
                    if "competitor" in [role.name.lower() for role in mem.roles]:
                        await interaction.followup.send("Cannot delete a bugs Profile when you are currently competing in an event.")
                        return
                    flag3, roles = bugsProfileIns.delete()
                    logFlags.append(flag3)
                    if flag3 == 3:
                        logIns.log(
                            channel=channel,
                            cmd="Bdelete",
                        )
                        await interaction.followup.send(
                            "There was an error finding the roles to remove"
                        )
                        return
                    nRoles = []
                    for r in roles:  
                        nRole = nextcord.utils.get(
                            interaction.guild.roles, id=r
                        )
                        if nRole is not None:
                            nRoles.append(nRole)
                        
                    if nRoles:
                        await mem.remove_roles(*nRoles)
                        msgToUser = "Profile deleted and roles removed!"
                    else:
                        msgToUser = "Profile deleted and no roles found to remove!"
                
                    logIns.log(
                            channel=channel,
                            cmd="Bdelete",
                        )
                    await interaction.followup.send(msgToUser)
                    return

                else:
                    logIns.log(
                        channel=channel,
                        cmd="Bdelete",
                    )
                    await interaction.followup.send(
                        "Sorry but I did not find a profile to delete"
                    )
                    return
                
            elif view.value is False:
                await interaction.followup.send("Profile will not be deleted, goodbye.")
                return
            elif view.value is None:
                await interaction.followup.send("Timeout reached goodbye!")
                return
            
        #UPDATE BUGS PROFILE
        elif selectedOption == 'update':
            #CHECK FOR A BUGS PROFILE
            bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
            boo = bugsProfileIns.hasProfile()
            if boo == 2:
                await interaction.response.send_message(f"You selected option {selectedOption} please paste your new Ethereum address which sent 0.003 ETH to the bugs Treasury wallet.")
                message = await interaction.client.wait_for('message', check=check, timeout=60.0)
                msg = message.content
                bugsProfileIns2 = stokeIns.bugsProfile(discord, msg)
                update = bugsProfileIns2.update()
                if update == 2:
                    logIns.log(
                        channel=channel,
                        cmd="Bupdate",
                    )
                    await interaction.followup.send("Alright profile updated!")
                    return
                elif update == 5:
                    logIns.log(
                        channel=channel,
                        cmd="Bupdate",
                    )
                    await interaction.followup.send(
                        "Sorry but this address already has a bugs profile attached."
                    )
                    return
                else:
                    logIns.log(
                        channel=channel,
                        cmd="Bupdate",
                    )
                    await interaction.followup.send(
                        "Sorry but an error occurred when check that transaction."
                    )
                    return

            else:
                logIns.log(
                    channel=channel,
                    cmd="Bupdate",
                )
                await interaction.response.send_message("You do not have a bugs Profile to update.")
                return

        #RETRIEVE BUGS PROFILE
        elif selectedOption == 'retrieve':
            # CHECK FOR A PROFILE TO RETRIEVE
            bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
            bugsProfile = bugsProfileIns.hasProfile()
            logFlags.append(bugsProfile)
            if bugsProfile == 2:
                flag4, profile = bugsProfileIns.retrieve()
                logFlags.append(flag4)
                if flag4 == 2:
                    logIns.log(
                        channel=channel,
                        cmd="Bretrieve",
                    )
                    await interaction.response.send_message(
                        f"This is the Ethereum address for your bugs Profile\n{profile}"
                    )
                    return
                else:
                    logIns.log(
                        channel=channel,
                        cmd="Bretrieve",
                    )
                    await interaction.response.send_message(
                        "An error occured when retrieving your Profile"
                    )
                    return
            else:
                logIns.log(
                    channel=channel,
                    cmd="Bretrieve",
                )
                await interaction.response.send_message(
                    "Sorry but I could not find a bugs Profile with your Discord Username."
                )
                return
            
        else:
            return

class dropDownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(bugsDropdown())

class dropDownCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def bugs(self, ctx):
        await ctx.send("What would you like to do", view=dropDownView())

def setup(client):
    client.add_cog(dropDownCog(client))


