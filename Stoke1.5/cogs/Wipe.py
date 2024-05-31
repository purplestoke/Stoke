import nextcord
from nextcord.ext import commands
from stoke import Stoke
from nextcord import Interaction
from API_Tokens import purplestoke

class WipeDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label='apex', description='wipe data in apex player profiles regarding event', value='apex'),
            nextcord.SelectOption(label='finals', description='wipe data in finals player profiles regarding event', value='finals'),
            nextcord.SelectOption(label='xdefiant', description='wipe data in xdefiant player profiles regarding event', value='xdefiant')
        ]
        super().__init__(placeholder="choose an option", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        selectedOption = self.values[0]

        # VARIABLES
        mem = interaction.user
        discord = mem.id
        guildId = interaction.guild.id
        logFlags = []
        stokeIns = Stoke()
        logIns = stokeIns.Log(bugs_id=None, guildId=guildId, flags=logFlags, discord=discord)

        if discord != purplestoke:
            await interaction.response.send_message("You are not my dad!")
            logFlags.append(5)
            logIns.wipeLog(cmd="WipeEvent")
            return
        
        wipeIns = stokeIns.Wipe(selectedOption)
        flag = wipeIns.wipeEvent()
        logFlags.append(flag)
        if flag == 2:
            try:
                for guild in interaction.client.guilds:
                    role = nextcord.utils.get(guild.roles, name="competitor")
                    if role:
                        for member in guild.members:
                            if role in member.roles:
                                await member.remove_roles(role)
                loopFlag = 2
            except:
                loopFlag = 3
            
            logFlags.append(loopFlag)
            if loopFlag == 2:
                await interaction.response.send_message(f"{selectedOption} player profiles have been wiped and Competitor roles removed! {flag} ^ {loopFlag}")

            else:
                await interaction.response.send_message(f"{selectedOption} player profiles wiped but error with role removal. {flag} ^ {loopFlag}")
            
        else:
            await interaction.response.send_message(f"Error attempting to wipe {selectedOption} event. {flag}")
        
        logIns.wipeLog(cmd="WipeEvent")
        return

class WipeDropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(WipeDropdown())

class WipeDropdownCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def wipe(self, ctx):
        await ctx.send("What would you like to do", view=WipeDropdownView())

def setup(client):
    client.add_cog(WipeDropdownCog(client))