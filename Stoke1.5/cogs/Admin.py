import nextcord
from nextcord.ext import commands
from stoke import Stoke
from nextcord import Interaction
from API_Tokens import purplestoke
from functions import Functions

# BUTTONS---------------------------------------------------
# GAME BUTTONS 
class GameView(nextcord.ui.View):
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

# FLAG BUTTONS
class FlagView(nextcord.ui.View):
    @nextcord.ui.button(label="On", style=nextcord.ButtonStyle.green)
    async def apex(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = 1
        self.stop()

    @nextcord.ui.button(label="Off", style=nextcord.ButtonStyle.red)
    async def finals(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = 0
        self.stop()

    @nextcord.ui.button(label="No, Cancel", style=nextcord.ButtonStyle.grey)
    async def cancel(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()

class AdminDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label='Pmnt Flag', value="pmnt"),
            nextcord.SelectOption(label='Sc Flag', value="sc"),
            nextcord.SelectOption(label="Winning Guild", value="winGuild"),
            nextcord.SelectOption(label="Guild Winner", value="guildWin"),
            nextcord.SelectOption(label="Raffle Draw", value="raffle")
        ]
        super().__init__(min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        selectedOption = self.values[0]
        # VARIABLES
        mem = interaction.user
        discord = mem.id
        # MAKE SURE USER IS PURPLESTOKE
        if discord != purplestoke:
            await interaction.response.send_message("You are not my dad!")
            return
        gView = GameView()
        stokeIns = Stoke()
        guildId = interaction.guild.id
        logFlags = []
        logIns = stokeIns.Log(mem, guildId, logFlags)
        # PAYMENT FLAG
        if selectedOption == "pmnt":
            await interaction.response.send_message("What pmnt flag we turning on pops?", view=gView)
            await gView.wait()
            fView = FlagView()
            # APEX
            if gView.value == 'apex':
                await interaction.followup.send(f"{gView.value} flag selected, what we doing with that?", view=fView)
                await fView.wait()
                eventIns = stokeIns.Event(discord, gView.value)
                f = eventIns.pmntFlag(fView.value)
                await interaction.followup.send(f"return flag of {f}, payment for {gView.value} is {fView.value}")
                return
            # FINALS
            elif gView.value == 'finals':
                await interaction.followup.send(f"{gView.value} flag selected, what we doing with that?", view=fView)
                await fView.wait()
                eventIns = stokeIns.Event(discord, gView.value)
                f = eventIns.pmntFlag(fView.value)
                await interaction.followup.send(f"return flag of {f}, payment for {gView.value} is {fView.value}")
                return
            # XDEFIANT
            elif gView.value == 'xdefiant':
                await interaction.followup.send(f"{gView.value} flag selected, what we doing with that?", view=fView)
                await fView.wait()
                eventIns = stokeIns.Event(discord, gView.value)
                f = eventIns.pmntFlag(fView.value)
                await interaction.followup.send(f"return flag of {f}, payment for {gView.value} is {fView.value}")
                return
            else:
                await interaction.followup.send("Copy that canceling.")
                return
        # SCREENSHOT FLAG
        elif selectedOption == "sc":
            await interaction.response.send_message("What sc flag we turning on pops?", view=gView)
            await gView.wait()
            fView = FlagView()
            # APEX
            if gView.value == 'apex':
                await interaction.followup.send(f"{gView.value} flag selected, what we doing with that?", view=fView)
                await fView.wait()
                eventIns = stokeIns.Event(discord, gView.value)
                f = eventIns.eventFlag(fView.value)
                await interaction.followup.send(f"return flag of {f}, payment for {gView.value} is {fView.value}")
                return
            # FINALS
            elif gView.value == 'finals':
                await interaction.followup.send(f"{gView.value} flag selected, what we doing with that?", view=fView)
                await fView.wait()
                eventIns = stokeIns.Event(discord, gView.value)
                f = eventIns.eventFlag(fView.value)
                await interaction.followup.send(f"return flag of {f}, payment for {gView.value} is {fView.value}")
                return
            # XDEFIANT
            elif gView.value == 'xdefiant':
                await interaction.followup.send(f"{gView.value} flag selected, what we doing with that?", view=fView)
                await fView.wait()
                eventIns = stokeIns.Event(discord, gView.value)
                f = eventIns.eventFlag(fView.value)
                await interaction.followup.send(f"return flag of {f}, payment for {gView.value} is {fView.value}")
                return
            else:
                await interaction.followup.send("Copy that canceling.")
                return
        # WINNING GUILD
        elif selectedOption == "winGuild":
            await interaction.response.send_message("What event are we picking a Winning Community for?", view=gView)
            await gView.wait()

            # FUNCTION METHOD FOR PICKING A WINNING GUILD
            try:
                winningGuild, bestAvgScore, tiedGuilds = Functions.winning_guild(gView.value)
                logFlags.append(2)
            except:
                logFlags.append(3)
                await interaction.followup.send("Error calculating the Winning Community.")
                logIns.log(channel="Admin", cmd='WinningGuild')
                return
            # AFTER METHOD USE
            if tiedGuilds:
                tiedResp = ','.join(tiedGuilds)
                await interaction.followup.send(f"Alright we had a tie! With an Average Score of {bestAvgScore} between the following communities.\n{tiedResp}")
                logFlags.append("Tie")
            else:
                await interaction.followup.send(f"Community {winningGuild} won! With an average score of {bestAvgScore}!")
                logFlags.append("1 Winner")

            logIns.log(channel="Admin", cmd='WinningGuild')
            return
        # GUILD WINNER
        elif selectedOption == 'guildWin':
            await interaction.response.send_message("What event are we picking a Community Winner for?", view=gView)
            await gView.wait()

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            await interaction.followup.send(f"Cool, cool we are picking a Winner from the {gView.value} Event. Who was the winning Guild?")
            message = await interaction.client.wait_for('message', check=check, timeout=60.0)
            msg = message.content
            # PICKING A COMMUNITY WINNER
            winner, flag = Functions.guild_winner(msg, gView.value)
            logFlags.append(flag)
            if flag == 2:
                winnerName = await self.client.fetch_user(winner)
                await interaction.followup.send(f"Alright Competitor @{winnerName} has won the Community Ethereum Prize for the {gView.value} Event!")
            else:
                await interaction.followup.send("There was an error when attempting to select a winner.")
            logIns.log(channel="Admin", cmd="GuildWinner")
            return
        # RAFFLE DRAW
        elif selectedOption == 'raffle':
            await interaction.response.send_message("What event are we picking Winners for?", view=gView)
            await gView.wait()

            # APEX
            if gView.value == 'apex':
                winners = Functions.apexRaffleDraw()
                if winners:
                    await interaction.followup.send(f"The following competitors have been chosen for the Apex Legends Event!\n{" @".join(winners)}")
                    logFlags.append(2)
                else:
                    await interaction.followup.send(f"Error {winners} when attempting to pick winners.")
                    logFlags.append(winner)
                
                logIns.log(channel="Admin", cmd="ApexRaffleDraw")
                return
            # FINALS 
            elif gView.value == 'finals':
                winners = Functions.finalsRaffleDraw()
                if winners:
                    await interaction.followup.send(f"The following competitors have been chosen for the The Finals Event!\n{" @".join(winners)}")
                    logFlags.append(2)
                else:
                    await interaction.followup.send(f"Error {winners} when attempting to pick winners.")
                    logFlags.append(winner)
                
                logIns.log(channel="Admin", cmd="FinalsRaffleDraw")
                return
            # XDEFIANT
            elif gView.value == 'xdefiant':
                winners = Functions.xdefRaffleDraw()
                if winners:
                    await interaction.followup.send(f"The following competitors have been chosen for the The Finals Event!\n{" @".join(winners)}")
                    logFlags.append(2)
                else:
                    await interaction.followup.send(f"Error {winners} when attempting to pick winners.")
                    logFlags.append(winner)
                
                logIns.log(channel="Admin", cmd="XDefiantRaffleDraw")
                return

class AdminDropDownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(AdminDropdown())

class AdminDropDownCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def admin(self, ctx):
        await ctx.send("What would you like to do", view=AdminDropDownView())

def setup(client):
    client.add_cog(AdminDropDownCog(client))