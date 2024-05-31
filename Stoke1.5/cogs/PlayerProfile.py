import nextcord
from nextcord.ext import commands
from stoke import Stoke
from nextcord import Interaction
from API_Tokens import bugsServerId


# BUTTONS
class PlayerView(nextcord.ui.View):
    def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None

    @nextcord.ui.button(label="Apex Legends", style=nextcord.ButtonStyle.red)
    async def apex(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = "apex"
        self.stop()

    @nextcord.ui.button(label="The Finals", style=nextcord.ButtonStyle.blurple)
    async def finals(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = "finals"
        self.stop()

    @nextcord.ui.button(label="XDefiant", style=nextcord.ButtonStyle.green)
    async def xdefiant(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = "xdefiant"
        self.stop()
    
    @nextcord.ui.button(label="No, Cancel", style=nextcord.ButtonStyle.grey)
    async def cancel(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()

class PlayerDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label='create', description='create a player profile', value="create"),
            nextcord.SelectOption(label='delete', description='delete your player profile', value="delete"),
            nextcord.SelectOption(label='retrieve', description='retrieve your player profile', value="retrieve")
        ]
        super().__init__(placeholder='Choose an option', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        selectedOption = self.values[0]
        
        # VARIABLES
        mem = interaction.user
        discord = interaction.user.id
        guildId = interaction.guild.id
        logFlags = []

        # CREATE STOKE INSTANCES
        stokeIns = Stoke()
        channel = 'buggin'
        guildIns = stokeIns.Guilds(channel, guildId)

        # PULL CHANNEL ID
        flag, ret = guildIns.pullChannel()
        logFlags.append(flag)
        #MUST BE IN THE BUGGIN CHANNEL
        if interaction.channel.id != ret:
            await interaction.response.send_message("Use this command in the buggin channel please.")
            return
        
        # CHECK FOR A BUGS PROFILE
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag2, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag2)

        if bugsId == None:
            await interaction.response.send_message("You must have a bugs Profile in order to access these commands.")
            return
        
        # CREATE MORE STOKE INSTANCES
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        view = PlayerView()
        # CREATE A PLAYER PROFILE
        if selectedOption == 'create':
            await interaction.response.send_message(f"You selected option {selectedOption} click the button for which game you want to {selectedOption} a profile.", view=view)
            await view.wait()
            
            # APEX
            if view.value == 'apex':
                await interaction.followup.send("Alright lets make your Apex Legends player profile all I need is your Apex Legends gamertag.")
                message2 = await interaction.client.wait_for('message', check=check, timeout=60.0)
                if guildId == bugsServerId:
                    await interaction.followup.send("And what community are you a part of?")
                    message3 = await interaction.client.wait_for('message', check=check, timeout=60.0)
                    msg3 = message3.content
                else:
                    msg3 = None
                msg2 = message2.content
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, msg3)
                flag3 = playerProfileIns.create(msg2)
                if flag3 == 2:
                    #PULL APEX ROLL
                    flag4, role = guildIns.pullRole(find='apex')
                    logFlags.append(flag4)
                    if role:
                        apexRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(apexRole)
                        await interaction.followup.send(f"Awesome your player profile for Apex Legends is created with gamertag {msg2}\nIf this gamertag differs from the one in your screenshot during the event you will not earn any points.")
                    else:
                        await interaction.followup.send(f"Awesome your player profile for Apex Legends is created with gamertag {msg2} but I was unable to add the Apex Role.\nIf this gamertag differs from the one in your screenshot during the event you will not earn any points.")
                    
                elif flag3 == 5:
                    await interaction.followup.send(f"The gamertag {msg2} is already attached to a player profile")
                    
                else:
                    logFlags.append(flag3)
                    await interaction.followup.send(f"An error of some kind occured, player profile not created.")
                
                logIns.log(channel, cmd="Acreate")
                return 
                

            elif view.value == 'finals':
                await interaction.followup.send("Alright lets make your The Finals player profile all I need is your The Finals gamertag.")
                message2 = await interaction.client.wait_for('message', check=check, timeout=60.0)
                msg2 = message2.content.upper()
                if guildId == bugsServerId:
                    await interaction.followup.send("And what community are you a part of?")
                    message3 = await interaction.client.wait_for('message', check=check, timeout=60.0)
                    msg3 = message3.content
                else:
                    msg3 = None
                msg2 = message2.content
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, msg3)
                flag3 = playerProfileIns.create(msg2)
                if flag3 == 2:
                    #PULL APEX ROLL
                    flag4, role = guildIns.pullRole(find='finals')
                    logFlags.append(flag4)
                    if role:
                        finalsRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(finalsRole)
                        await interaction.followup.send(f"Awesome your player profile for The Finals is created with gamertag {msg2}\nIf this gamertag differs from the one in your screenshot during the event you will not earn any points.")
                    else:
                        await interaction.followup.send(f"Awesome your player profile for The Finals is created with gamertag {msg2} but I was unable to add the The Finals Role.\nIf this gamertag differs from the one in your screenshot during the event you will not earn any points.")
                    
                elif flag3 == 5:
                    await interaction.followup.send(f"The gamertag {msg2} is already attached to a player profile")
                    
                else:
                    await interaction.followup.send(f"An error of some kind occured, player profile not created.")
                
                logIns.log(channel, cmd="Fcreate")
                return 
            
            elif view.value == 'xdefiant':
                await interaction.followup.send("Alright lets make your XDefiant player profile all I need is your XDefiant gamertag.")
                message2 = await interaction.client.wait_for('message', check=check, timeout=60.0)
                msg2 = message2.content
                if guildId == bugsServerId:
                    await interaction.followup.send("And what community are you a part of?")
                    message3 = await interaction.client.wait_for('message', check=check, timeout=60.0)
                    msg3 = message3.content
                else:
                    msg3 = None
                msg2 = message2.content
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, msg3)
                flag3 = playerProfileIns.create(msg2)
                if flag3 == 2:
                    #PULL APEX ROLL
                    flag4, role = guildIns.pullRole(find='xdefiant')
                    logFlags.append(flag4)
                    if role:
                        xdefiantRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(xdefiantRole)
                        await interaction.followup.send(f"Awesome your player profile for XDefiant is created with gamertag {msg2}\nIf this gamertag differs from the one in your screenshot during the event you will not earn any points.")
                    else:
                        await interaction.followup.send(f"Awesome your player profile for XDefiant is created with gamertag {msg2} but I was unable to add the XDefiant Role.\nIf this gamertag differs from the one in your screenshot during the event you will not earn any points.")
                    
                elif flag3 == 5:
                    await interaction.followup.send(f"The gamertag {msg2} is already attached to a player profile")
                    
                else:
                    await interaction.followup.send(f"An error of some kind occured, player profile not created.")
                
                logIns.log(channel, cmd="Xcreate")
                return 
            
            else:
                await interaction.followup.send(f"Timeout reached, goodbye!")
                return

        # DELETE A PLAYER PROFILE
        if selectedOption == "delete":
            await interaction.response.send_message(f"You selected option {selectedOption} if you would like to continue click the button for which profile to {selectedOption}.", view=view)
            await view.wait()

            if view.value == 'apex':
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, hosted=None)
                flag3 = playerProfileIns.delete()
                logFlags.append(flag3)
                if flag3 == 2:
                    flag4, role = guildIns.pullRole(find='apex')
                    logFlags.append(flag4)
                    roleObj = nextcord.utils.get(interaction.guild.roles, id=role)
                    await mem.remove_roles(roleObj)
                    await interaction.followup.send("Apex Legends player profile deleted!")

                else:
                    await interaction.followup.send("There was an error when attempting to delete your player profile.\nUnfortunately it has not been deleted.")

                logIns.log(channel, cmd="Adelete")
                return
        
            elif view.value == 'finals':
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, hosted=None)
                flag3 = playerProfileIns.delete()
                logFlags.append(flag3)
                if flag3 == 2:
                    flag4, role = guildIns.pullRole(find='finals')
                    logFlags.append(flag4)
                    roleObj = nextcord.utils.get(interaction.guild.roles, id=role)
                    await mem.remove_roles(roleObj)
                    await interaction.followup.send("The Finals player profile deleted!")

                else:
                    await interaction.followup.send("There was an error when attempting to delete your player profile.\nUnfortunately it has not been deleted.")

                logIns.log(channel, cmd="Fdelete")
                return
            
            elif view.value == 'xdefiant':
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, hosted=None)
                flag3 = playerProfileIns.delete()
                logFlags.append(flag3)
                if flag3 == 2:
                    flag4, role = guildIns.pullRole(find='xdefiant')
                    logFlags.append(flag4)
                    roleObj = nextcord.utils.get(interaction.guild.roles, id=role)
                    await mem.remove_roles(roleObj)
                    await interaction.followup.send("XDefiant player profile deleted!")

                else:
                    await interaction.followup.send("There was an error when attempting to delete your player profile.\nUnfortunately it has not been deleted.")

                logIns.log(channel, cmd="Xdelete")
                return
            
            elif view.value == None:
                await interaction.followup.send("Profile will not be deleted, goodbye.")
                return
            else:
                await interaction.followup.send("Timeout reached, goodbye!")
                return

        # RETRIEVE A PLAYER PROFILE
        if selectedOption == 'retrieve':
            await interaction.response.send_message(f"Which Player Profile would you like to retrieve?", view=view)
            await view.wait()
            if view.value == 'apex':
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, hosted=None)
                flag3, gt = playerProfileIns.retrieve() 
                logFlags.append(flag3)
                await interaction.followup.send(f"Your Apex Legends Player Profile has this gamertag {gt}")  
                logIns.log(channel, cmd="Aretrieve")
                return

            elif view.value == 'finals':
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, hosted=None)
                flag3, gt = playerProfileIns.retrieve() 
                logFlags.append(flag3)
                await interaction.followup.send(f"Your The Finals Player Profile has this gamertag {gt}")
                logIns.log(channel, cmd="Fretrieve")
                return
            
            elif view.value == 'xdefiant':
                playerProfileIns = stokeIns.PlayerProfile(discord, guildId, view.value, hosted=None)
                flag3, gt = playerProfileIns.retrieve() 
                logFlags.append(flag3)
                await interaction.followup.send(f"Your XDefiant Player Profile has this gamertag {gt}")
                logIns.log(channel, cmd="Xretrieve")
                return

            elif view.value == False:
                await interaction.followup.send(f"Goodbye!")
                return
            else:
                await interaction.followup.send("Timeout reached, goodbye!")
                return
            
class PlayerDropDownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(PlayerDropdown())

class PlayerDropDownCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def player(self, ctx):
        await ctx.send("What would you like to do", view=PlayerDropDownView())

def setup(client):
    client.add_cog(PlayerDropDownCog(client))