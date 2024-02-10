import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from stoke import Stoke


class wallet(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(
        name="wallet",
        description="check the balance of bugs wallets",
    )
    async def wallet(self, interaction: Interaction):
        # VARBIABLES
        mem = interaction.user
        discord = mem.id
        guildId = interaction.guild.id
        stokeIns = Stoke()
        logFlags = []
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag, bugsId = bugsProfileIns.bugsId()
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        logFlags.append(flag)
        walletIns = stokeIns.Wallet()

        # QUERY FOR WALLET BALANCE
        try:
            flag2, bals = walletIns.pullBal()
            logFlags.append(flag2)
            if flag2 == 2:
                logIns.log(
                    _channel="other",
                    _cmd="walletBal",
                )
                await interaction.response.send_message(
                    f"The bugs Treasury wallet currently contains {bals[0]} ETH\nThe bugs Apex wallet holds {bals[1]} ETH\nThe bugs XDefiant wallet holds {bals[2]} ETH"
                )
                return
            else:
                logIns.log(
                    _channel="other",
                    _cmd="walletBal",
                )
                await interaction.response.send_message(
                    "Sorry but I am having trouble fetching that information."
                )
            return
        except:
            logIns.log(
                _channel="other",
                _cmd="walletBal",
            )
            await interaction.response.send_message(
                "Sorry but I am having trouble fetching that information."
            )
            return


def setup(client):
    client.add_cog(wallet(client))
