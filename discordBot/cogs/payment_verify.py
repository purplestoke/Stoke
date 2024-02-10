import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from stoke import Stoke


class payment_verify(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(
        name="payment_verify",
        description="verify your payment to compete in a bugs event.",
    )
    async def payment_verify(self, interaction: Interaction, game):
        # VARIABLES
        game = game.lower()
        mem = interaction.user
        discord = mem.id
        guild = interaction.guild
        guildId = guild.id
        stokeIns = Stoke()
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        logFlags = []
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        channel = "pmntVerify"
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)
        eventIns = stokeIns.Event(discord, game)

        if game == "apex":
            # CHECK IF PAYMENT IS ON
            gameCheck = "apex"
            f, retFlag = eventIns.pmntOn(gameCheck)
            logFlags.append(f)
            if retFlag == 1:
                pass
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Averify",
                )
                await interaction.response.send_message("Apex event is not active")
                return

            # USER MUST HAVE CREATED A BUGS PROFILE
            bugsProfile = bugsProfileIns.hasProfile()
            logFlags.append(bugsProfile)

            if bugsProfile == 2:
                pmntVerifyIns = stokeIns.PaymentVerify(discord, guildId, game)
                # CHECK FOR APEX ROLE
                if "apex" in [role.name.lower() for role in mem.roles]:
                    # PULL ADDRESS FROM BUGS PROFILE
                    addr = pmntVerifyIns.pullAddr()

                    # CHECK PAYMENT
                    flag2, role = pmntVerifyIns.checkPayment(addr)
                    logFlags.append(flag2)
                    if flag2 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        logIns.log(
                            _channel=channel,
                            _cmd="Averify",
                        )
                        await interaction.response.send_message(
                            f"Payment verified! You are competing in the Apex Legends Event!"
                        )
                        return
                    else:
                        logIns.log(
                            _channel=channel,
                            _cmd="Averify",
                        )
                        await interaction.response.send_message(f"{role}")
                        return
        elif game == "xdef":
            # CHECK IF PAYMENT IS ON
            gameCheck = "xdefiant"
            f, retFlag = eventIns.pmntOn(gameCheck)
            logFlags.append(f)
            if retFlag == 1:
                pass
            else:
                logIns.log(
                    _channel=channel,
                    _cmd="Xverify",
                )
                await interaction.response.send_message("XDefiant event is not active")
                return

            # USER MUST HAVE CREATED A BUGS PROFILE
            bugsProfile = bugsProfileIns.hasProfile()
            if bugsProfile == 2:
                # CHECK FOR APEX ROLE
                if "xdef" in [role.name.lower() for role in mem.roles]:
                    # PULL ADDRESS FROM BUGS PROFILE
                    pmntVerifyIns = stokeIns.PaymentVerify(discord, guildId, game)
                    retAddr = stokeIns.PaymentVerify().pullAddr()

                    # CHECK PAYMENT
                    flag2, role = pmntVerifyIns.checkPayment(retAddr)
                    logFlags.append(flag2)
                    if flag2 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        logIns.log(
                            _channel=channel,
                            _cmd="Xverify",
                        )
                        await interaction.response.send_message(
                            "Payment verified! You are competing in the Apex Legends Event!"
                        )
                        return
                    else:
                        logIns.log(
                            _channel=channel,
                            _cmd="Xverify",
                        )
                        await interaction.response.send_message(f"{role}")
                        return
        else:
            await interaction.response.send_message("Command options are apex or xdef")
            return


def setup(client):
    client.add_cog(payment_verify(client))
