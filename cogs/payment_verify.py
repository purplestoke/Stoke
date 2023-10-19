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
        logFlags = []
        flag, bugsId = stokeIns.bugsProfile().bugsId(discord)
        logFlags.append(flag)
        channel = "pmntVerify"

        # RATE CHECK
        rateCheck = stokeIns.Rate().rateCheck(discord, channel=channel)
        logFlags.append(rateCheck)
        if rateCheck == 2:
            pass
        elif rateCheck == 5:
            stokeIns.Log().log(
                bugsId, guildId=guildId, flags=logFlags, channel=channel, cmd="Averify"
            )
            return
        elif rateCheck == 1:
            stokeIns.Log().log(
                bugsId, guildId=guildId, flags=logFlags, channel=channel, cmd="Averify"
            )
            return

        if game == "apex":
            # CHECK IF PAYMENT IS ON
            gameCheck = "apex"
            f, retFlag = stokeIns.Event().pmntOn(gameCheck)
            logFlags.append(f)
            if retFlag == 1:
                pass
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Averify",
                )
                await interaction.response.send_message("Apex event is not active")
                return

            # USER MUST HAVE CREATED A BUGS PROFILE
            bugsProfile = stokeIns.bugsProfile().hasProfile(discord)
            logFlags.append(bugsProfile)

            if bugsProfile == 2:
                # CHECK FOR APEX ROLE
                if "apex" in [role.name.lower() for role in mem.roles]:
                    # PULL ADDRESS FROM BUGS PROFILE
                    addr = stokeIns.PaymentVerify().pullAddr(discord)
                    # CHECK PAYMENT
                    flag2, role = stokeIns.PaymentVerify().checkPayment(
                        discord, addr, guildId, event="apex"
                    )
                    logFlags.append(flag2)
                    if flag2 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Averify",
                        )
                        await interaction.response.send_message(
                            f"Payment verified! You are competing in the Apex Legends Event!"
                        )
                        return
                    else:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Averify",
                        )
                        await interaction.response.send_message(f"{role}")
                        return
        elif game == "xdef":
            # CHECK IF PAYMENT IS ON
            gameCheck = "xdefiant"
            f, retFlag = stokeIns.Event().pmntOn(gameCheck)
            logFlags.append(f)
            if retFlag == 1:
                pass
            else:
                stokeIns.Log().log(
                    bugsId,
                    guildId=guildId,
                    flags=logFlags,
                    channel=channel,
                    cmd="Xverify",
                )
                await interaction.response.send_message("XDefiant event is not active")
                return

            # USER MUST HAVE CREATED A BUGS PROFILE
            bugsProfile = stokeIns.bugsProfile().hasProfile(discord)
            if bugsProfile == 2:
                # CHECK FOR APEX ROLE
                if "xdef" in [role.name.lower() for role in mem.roles]:
                    # PULL ADDRESS FROM BUGS PROFILE
                    retAddr = stokeIns.PaymentVerify().pullAddr(discord)

                    # CHECK PAYMENT
                    flag2, role = stokeIns.PaymentVerify().checkPayment(
                        discord, retAddr, guildId, event="xdef"
                    )
                    logFlags.append(flag2)
                    if flag2 == 2:
                        compRole = nextcord.utils.get(interaction.guild.roles, id=role)
                        await mem.add_roles(compRole)
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xverify",
                        )
                        await interaction.response.send_message(
                            "Payment verified! You are competing in the Apex Legends Event!"
                        )
                        return
                    else:
                        stokeIns.Log().log(
                            bugsId,
                            guildId=guildId,
                            flags=logFlags,
                            channel=channel,
                            cmd="Xverify",
                        )
                        await interaction.response.send_message(f"{role}")
                        return
        else:
            await interaction.response.send_message("Command options are apex or xdef")
            return


def setup(client):
    client.add_cog(payment_verify(client))
