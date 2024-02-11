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
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)
        logFlags = []
        flag, bugsId = bugsProfileIns.bugsId()
        logFlags.append(flag)
        channel = "other"
        eventIns = stokeIns.Event(discord, game)
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)

        if discord != purpleStoke:
            return

        if game == "apex":
            if command == "on":
                game = "apex"
                fleg = 1
                flag2 = eventIns.eventFlag(fleg)
                logFlags.append(flag2)
                if flag2 == 2:
                    logIns.log(
                        _channel=channel,
                        _cmd="Aon",
                    )
                    await interaction.response.send_message(
                        "Apex event has now started!"
                    )
                    return
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Aon",
                    )
                    await interaction.response.send_message(f"Error {flag2}")
                    return
            elif command == "off":
                game = "apex"
                f = 0
                flag2 = eventIns.eventFlag(f)
                logFlags.append(flag2)
                if flag2 == 2:
                    logIns.log(
                        _channel=channel,
                        _cmd="Aoff",
                    )
                    await interaction.response.send_message("Apex is now off!")
                    return
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Aoff",
                    )
                    await interaction.response.send_message(f"Error {flag}")
                    return

            elif command == "payment_on":
                game = "apex"
                turnOn = 1
                flag3 = eventIns.pmntFlag(turnOn)
                logIns.log(_channel=channel, _cmd="ApexPmntOn")

                if flag3 == 2:
                    await interaction.response.send_message("Apex Payment is now on!")
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return

            elif command == "payment_off":
                game = "apex"
                turnOn = 0
                flag3 = eventIns.pmntFlag(turnOn)
                logIns.log(_channel=channel, _cmd="ApexPmntOff")

                if flag3 == 2:
                    await interaction.response.send_message("Apex Payment is now off!")
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return
            else:
                logIns.log(_channel=channel, _cmd="Aoff")
                return

        elif game == "xdef":
            if command == "on":
                game = "xdefiant"
                f = 1
                flag2 = eventIns.eventFlag(f)
                logFlags.append(flag2)

                if flag2 == 2:
                    logIns.log(
                        _channel=channel,
                        _cmd="Xon",
                    )
                    await interaction.response.send_message(
                        "XDefiant event has now started!"
                    )
                    return
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Xon",
                    )
                    await interaction.response.send_message(f"Error {flag}")
                    return
            elif command == "off":
                game = "xdefiant"
                f = 0
                flag2 = eventIns.eventFlag(f)
                logFlags.append(flag2)
                if flag2 == 2:
                    logIns.log(
                        _channel=channel,
                        _cmd="Aoff",
                    )
                    await interaction.response.send_message("XDefiant event is off!")
                    return
                else:
                    logIns.log(
                        _channel=channel,
                        _cmd="Aoff",
                    )
                    await interaction.response.send_message(f"Error {flag}")
                    return

            elif command == "payment_on":
                game = "xdefiant"
                turnOn = 1
                flag3 = eventIns.pmntFlag(turnOn)
                logIns.log(_channel=channel, _cmd="XdefPmntOn")

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
                flag3 = eventIns.pmntFlag(turnOn)
                logIns.log(_channel=channel, _cmd="XdefPmntOff")

                if flag3 == 2:
                    await interaction.response.send_message(
                        "XDefiant Payment is now off!"
                    )
                    return

                else:
                    await interaction.response.send_message(f"Error {flag3}")
                    return
            else:
                logIns.log(_channel=channel, _cmd="Aoff")
                return
        else:
            logIns.log(_channel=channel, _cmd="Aoff")
            return


def setup(client):
    client.add_cog(gamemaster(client))
