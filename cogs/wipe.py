import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from API_Tokens import *
import sqlite3
from stoke import Stoke


class wipe(commands.Cog):
    def __init__(self, client):
        self.client = client

    # MAIN COMMAND
    @nextcord.slash_command(
        name="wipe",
        description="wipe roles",
    )
    async def wipe(self, interaction: Interaction):
        pass

    # SUBCOMMANDS

    # WIPE DATABASE
    @wipe.subcommand(name="bugs_db", description=("wipe the bugs database"))
    async def bugs_db(self, interaction: Interaction):
        # VARIABLES
        mem = interaction.user
        guild = mem.guild

        # CHECK IF USER HAS ADMIN ROLE
        if "admin" in [role.name.lower() for role in mem.roles]:
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            cur.executescript(
                """
            DROP TABLE IF EXISTS bugs_Profile;
            DROP TABLE IF EXISTS XDefiant_Profile;
            DROP TABLE IF EXISTS Apex_Profile;
            DROP TABLE IF EXISTS Stoke_Guilds;
            DROP TABLE IF EXISTS Events;
            DROP TABLE IF EXISTS Private_Event;
            DROP TABLE IF EXISTS Rate;

            CREATE TABLE bugs_Profile (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            discord INTEGER UNIQUE,
            eth_addr TEXT UNIQUE,
            hash TEXT UNIQUE,
            xdefiant_profile BOOLEAN,
            apex_profile BOOLEAN
            );
            
            CREATE TABLE XDefiant_Profile (
            bugs_id INTEGER UNIQUE,
            gamertag TEXT UNIQUE,
            elligible TEXT UNIQUE,
            submission TEXT,
            points INTEGER,
            guild_id INTEGER
            );

            CREATE TABLE Apex_Profile (
            bugs_id INTEGER UNIQUE,
            gamertag TEXT UNIQUE,
            elligible TEXT UNIQUE,
            submission TEXT,
            points INTEGER,
            guild_id INTEGER
            );

            CREATE TABLE Stoke_Guilds (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            guild_name TEXT,
            guild TEXT,
            intercom TEXT,
            player_profile TEXT,
            payment_verify TEXT,
            sc_submission TEXT,
            apex_role TEXT,
            xdef_role TEXT,
            competitor_role TEXT,
            community_score INTEGER,
            priv_event_channel TEXT,
            priv_event_role TEXT
            );

            CREATE TABLE Events (
            game TEXT,
            pmnt_flag INTEGER,
            submission_flag INTEGER
            );

            CREATE TABLE Private_Event (
            bugs_id INTEGER UNIQUE,
            points INTEGER,
            submission TEXT UNIQUE
            );

            CREATE TABLE Rate (
            bugs_id INTEGER UNIQUE,
            player_profile INTEGER,
            pmnt_verify INTEGER,
            sc_submission INTEGER
            )
            """
            )

            # JOINING bugs_Profile INFO WITH ALL PLAYER PROFILE TABLES
            cur.execute(
                "SELECT * FROM bugs_Profile JOIN XDefiant_Profile ON bugs_Profile.id = XDefiant_Profile.bugs_id"
            )
            cur.execute(
                "SELECT * FROM bugs_Profile JOIN Apex_Profile ON bugs_Profile.id = Apex_Profile.bugs_id"
            )
            cur.execute(
                "SELECT * FROM Stoke_Guilds JOIN XDefiant_Profile on Stoke_Guilds.id = XDefiant_Profile.guild_id"
            )
            cur.execute(
                "SELECT * FROM Stoke_Guilds JOIN Apex_Profile on Stoke_Guilds.id = Apex_Profile.guild_id"
            )
            cur.execute(
                "SELECT * FROM bugs_Profile JOIN Private_Event ON bugs_Profile.id = Private_Event.bugs_id"
            )
            cur.execute(
                "SELECT * FROM bugs_Profile JOIN Rate ON bugs_Profile.id = Rate.bugs_id"
            )
            conn.commit()
            conn.close()

            await interaction.response.send_message(f"Database wiped!")
            return
        else:
            await interaction.response.send_message(
                "You are not my father, get lost Bozo."
            )
            return

    @wipe.subcommand(name="event")
    async def event(self, interaction: Interaction, event):
        # VARIABLES
        mem = interaction.user
        discord = str(mem)
        guild = interaction.guild
        stokeIns = Stoke()
        logFlags = []

        if discord != "purplestoke#0":
            return

        if event == "apex":
            cmd = "Awipe"
        elif event == "xdef":
            cmd = "Xwipe"
        else:
            flag = 1
            cmd = "e"
            logFlags.append(flag)
            stokeIns.Log().wipeLog(discord, cmd, flags=logFlags)

        # RESET PLAYER PROFILES
        flag2 = stokeIns.Wipe().wipeEvent(event)
        logFlags.append(flag2)
        if flag2 == 2:
            try:
                #   GET ROLE AND REMOVE FROM ALL MEMBERS
                role_name = "competitor"
                for guild in self.client.guilds:
                    role = nextcord.utils.get(guild.roles, name=role_name)

                    if role:
                        for member in guild.members:
                            if role in member.roles:
                                await member.remove_roles(role)
                stokeIns.Log().wipeLog(discord, cmd, flags=logFlags)
                await interaction.response.send_message(
                    f"Removed the {role_name} role from all servers."
                )
            except:
                stokeIns.Log().wipeLog(discord, cmd, flags=logFlags)
                await interaction.response.send_message("Error")
                return


def setup(client):
    client.add_cog(wipe(client))
