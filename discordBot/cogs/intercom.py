import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from API_Tokens import purpleStoke
from stoke import Stoke


class intercom(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="intercom")
    async def intercom(self, interaction: Interaction):
        pass

    @intercom.subcommand(name="loudspeaker")
    async def loudspeaker(self, interaction, announcement):
        # VARS
        mem = interaction.user
        discord = mem.id

        if discord != purpleStoke:
            return
        try:
            for guild in self.client.guilds:
                for channel in guild.channels:
                    if channel.name == "intercom":
                        await channel.send(announcement)

            await interaction.response.send_message("Done!")
            return
        except:
            await interaction.response.send_message("e")
            return

    """@intercom.subcommand(name="scores")
    async def scores(self, interaction: Interaction, event):
        # VARS
        mem = interaction.user
        discord = mem.id

        if discord != purpleStoke:
            return

        for guild in self.client.guilds:
            for channel in guild.channels:
                if channel.name == "intercom":
                    try:
                        stokeIns = Stoke()
                        intercomIns = stokeIns.Intercom(guild)
                        f, msg = intercomIns.scores(event)
                        print(f)
                        if f == 5:
                            pass
                        elif f == 2:
                            await channel.send(msg)
                        else:
                            pass
                    except:
                        pass
"""


def setup(client):
    client.add_cog(intercom(client))
