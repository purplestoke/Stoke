import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from API_Tokens import purpleStoke


class intercom(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="intercom")
    async def intercom(self, interaction: Interaction, announcement):
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


def setup(client):
    client.add_cog(intercom(client))
