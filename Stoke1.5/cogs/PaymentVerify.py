import nextcord
from nextcord.ext import commands
from stoke import Stoke
from nextcord import Interaction

class PaymentDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label='verify apex', description="Verify Eth payment made to Apex Legends Event Wallet", value='pmntApex'),
            nextcord.SelectOption(label='verify finals', description="Verify Eth payment made to The Finals Event Wallet", value="pmntFinals"),
            nextcord.SelectOption(label='verify xdefiant', description="Verfiy Eth payment made to the XDefiant Event Wallet", value="pmntXDefiant")
        ]
        super().__init__(placeholder="Choose an option", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        selectedOption = self.values[0]

        #VARIABLES
        mem = interaction.user
        discord = interaction.user.id
        guildId = interaction.guild.id
        logFlags = []

        #CREATE STOKE INSTANCES
        stokeIns = Stoke()
        channel = 'buggin'
        guildIns = stokeIns.Guilds(channel, guildId)

        #PULL CHANNEL ID
        flag, ret = guildIns.pullChannel()
        logFlags.append(flag)

        #MUST BE IN THE BUGGIN CHANNEL
        if interaction.channel.id != ret:
            await interaction.response.send_message("Use this command in the buggin channel please.")
            return
        
        #CHECK FOR A BUGS PROFILE
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        flag2, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag2)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        if bugsId == None:
            await interaction.response.send_message("You must have a bugs Profile in order to access these commands.")
            return
        
        # CHECK APEX PAYMENT
        if selectedOption == 'pmntApex':
            # CHECK IF APEX PAYMENT IS ON
            eventIns = stokeIns.Event(discord, game='apex')
            flag3, pmntFlag = eventIns.pmntOn()
            logFlags.append(flag3)
            if not pmntFlag:
                await interaction.response.send_message("The Apex Legends Event is not currently on.")
                logIns.log(channel, cmd='Averify')
                return

            # CHECK FOR A APEX PLAYER PROFILE
            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, type='apex', hosted=None)
            flag3, gt = playerProfileIns.retrieve()
            logFlags.append(flag3)
            if gt:
                # PAYMENT INSTANCE
                paymentIns = stokeIns.PaymentVerify(discord, guildId, event='apex')
                ethAddr = paymentIns.pullAddr()
                if ethAddr:
                    flag4, role = paymentIns.checkPayment(ethAddr)
                    logFlags.append(flag4)
                    if flag4 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        await interaction.response.send_message("Payment Verified you are all set to compete in the Apex Legends Event!")
                    else:
                        await interaction.response.send_message(f"Error occured {role}")
                else:
                    await interaction.response.send_message("Could not find your Ethereum address in my system.")

                logIns.log(channel, cmd="Averify")
                return
            else:
                await interaction.response.send_message("You do not have a player profile for this game.")
                return

        # CHECK FINALS PAYMENT
        if selectedOption == 'pmntFinals':
            # CHECK IF APEX PAYMENT IS ON
            eventIns = stokeIns.Event(discord, game='finals')
            flag3, pmntFlag = eventIns.pmntOn()
            logFlags.append(flag3)
            if not pmntFlag:
                await interaction.response.send_message("The Finals Event is not currently on.")
                logIns.log(channel, cmd='Fverify')
                return
            
            # CHECK FOR A FINALS PLAYER PROFILE
            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, type='finals', hosted=None)
            flag3, gt = playerProfileIns.retrieve()
            logFlags.append(flag3)
            if gt:
                # PAYMENT INSTANCE
                paymentIns = stokeIns.PaymentVerify(discord, guildId, event='finals')
                ethAddr = paymentIns.pullAddr()
                if ethAddr:
                    flag4, role = paymentIns.checkPayment(ethAddr)
                    logFlags.append(flag4)
                    if flag4 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        await interaction.response.send_message("Payment Verified you are all set to compete in The Finals Event!")
                    else:
                        await interaction.response.send_message(f"Error occured {role}")
                else:
                    await interaction.response.send_message("Could not find your Ethereum address in my system.")

                logIns.log(channel, cmd="Fverify")
                return
            else:
                await interaction.response.send_message("You do not have a player profile for this game.")
                return
            
        # CHECK XDEFIANT PAYMENT
        if selectedOption == 'pmntXDefiant':
            # CHECK IF XDEFIANT PAYMENT IS ON
            eventIns = stokeIns.Event(discord, game='xdefiant')
            flag3, pmntFlag = eventIns.pmntOn()
            logFlags.append(flag3)
            if not pmntFlag:
                await interaction.response.send_message("The XDefiant Event is not currently on.")
                logIns.log(channel, cmd='Xverify')
                return
            
            # CHECK FOR A FINALS PLAYER PROFILE
            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, type='xdefiant', hosted=None)
            flag3, gt = playerProfileIns.retrieve()
            logFlags.append(flag3)
            if gt:
                # PAYMENT INSTANCE
                paymentIns = stokeIns.PaymentVerify(discord, guildId, event='xdefiant')
                ethAddr = paymentIns.pullAddr()
                if ethAddr:
                    flag4, role = paymentIns.checkPayment(ethAddr)
                    logFlags.append(flag4)
                    if flag4 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        await interaction.response.send_message("Payment Verified you are all set to compete in The XDefiant Event!")
                    else:
                        await interaction.response.send_message(f"Error occured {role}")
                else:
                    await interaction.response.send_message("Could not find your Ethereum address in my system.")

                logIns.log(channel, cmd="Xverify")
                return
            else:
                await interaction.response.send_message("You do not have a player profile for this game.")
                return
            
        else:
            return

            



class PaymentDropDownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(PaymentDropdown())

class PaymentDropDownCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def payment(self, ctx):
        await ctx.send("What would you like to do", view=PaymentDropDownView())

def setup(client):
    client.add_cog(PaymentDropDownCog(client))