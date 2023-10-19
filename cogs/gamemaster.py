import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from stoke import Stoke
from API_Tokens import purpleStoke


class gamemaster(commands.Cog):
    def __init__(self, client):
        self.client = client

    # EVENT COMMANDS
    @nextcord.slash_command(name="games")
    async def games(self, interaction: Interaction, game: str, command: str):
        # VARS
        game = game.lower()
        command = command.lower()
        guildId = interaction.guild.id
        mem = interaction.user
        discord = mem.id
        stokeIns = Stoke()
        logFlags = []
        flag, bugsId = stokeIns.bugsProfile().bugsId(discord)
        logFlags.append(flag)
        channel = "other"

        if discord != purpleStoke:
            return

        if game == "apex":
            if command == "on":
                game = "apex"
                fleg = 1
                flag2 = stokeIns.Event().eventFlag(game, fleg)
                logFlags.append(flag2)
                if flag2 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aon",
                    )
                    await interaction.response.send_message(
                        "Apex event has now started!"
                    )
                    return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aon",
                    )
                    await interaction.response.send_message(f"Error {flag2}")
                    return
            elif command == "off":
                game = "apex"
                f = 0
                flag2 = stokeIns.Event().eventFlag(game, f)
                logFlags.append(flag2)
                if flag2 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aoff",
                    )
                    await interaction.response.send_message("Apex is now off!")
                    return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aoff",
                    )
                    await interaction.response.send_message(f"Error {flag}")
                    return

            elif command == "payment_on":
                game = "apex"
                turnOn = 1
                flag3 = stokeIns.Event().pmntFlag(game, turnOn)
                stokeIns.Log().log(
                    bugsId, guildId, channel, flags=logFlags, cmd="ApexPmntOn"
                )

                if flag3 == 2:
                    await interaction.response.send_message("Apex Payment is now on!")
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return

            elif command == "payment_off":
                game = "apex"
                turnOn = 0
                flag3 = stokeIns.Event().pmntFlag(game, turnOn)
                stokeIns.Log().log(
                    bugsId, guildId, channel, flags=logFlags, cmd="ApexPmntOff"
                )

                if flag3 == 2:
                    await interaction.response.send_message("Apex Payment is now off!")
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return
            else:
                stokeIns.Log().log(
                    bugsId, guildId=guildId, flags=logFlags, channel=channel, cmd="Aoff"
                )
                return

        elif game == "xdef":
            if command == "on":
                game = "xdefiant"
                f = 1
                flag2 = stokeIns.Event().eventFlag(game, f)
                logFlags.append(flag2)

                if flag2 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xon",
                    )
                    await interaction.response.send_message(
                        "XDefiant event has now started!"
                    )
                    return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Xon",
                    )
                    await interaction.response.send_message(f"Error {flag}")
                    return
            elif command == "off":
                game = "xdefiant"
                f = 0
                stokeIns = Stoke()
                flag2 = stokeIns.Event().eventFlag(game, f)
                logFlags.append(flag2)
                if flag2 == 2:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aoff",
                    )
                    await interaction.response.send_message("XDefiant event is off!")
                    return
                else:
                    stokeIns.Log().log(
                        bugsId,
                        guildId=guildId,
                        flags=logFlags,
                        channel=channel,
                        cmd="Aoff",
                    )
                    await interaction.response.send_message(f"Error {flag}")
                    return

            elif command == "payment_on":
                game = "xdefiant"
                turnOn = 1
                flag3 = stokeIns.Event().pmntFlag(game, turnOn)
                stokeIns.Log().log(
                    bugsId, guildId, channel, flags=logFlags, cmd="XdefPmntOn"
                )

                if flag3 == 2:
                    await interaction.response.send_message(
                        "XDefiant Payment is now on!"
                    )
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return

            elif command == "payment_off":
                game = "xdefiant"
                turnOn = 0
                flag3 = stokeIns.Event().pmntFlag(game, turnOn)
                stokeIns.Log().log(
                    bugsId, guildId, channel, flags=logFlags, cmd="XdefPmntOff"
                )

                if flag3 == 2:
                    await interaction.response.send_message(
                        "XDefiant Payment is now off!"
                    )
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return
            else:
                stokeIns.Log().log(
                    bugsId, guildId=guildId, flags=logFlags, channel=channel, cmd="Aoff"
                )
                return
        else:
            stokeIns.Log().log(
                bugsId, guildId=guildId, flags=logFlags, channel=channel, cmd="Aoff"
            )
            return


def setup(client):
    client.add_cog(gamemaster(client))
