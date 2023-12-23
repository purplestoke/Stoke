import requests
from API_Tokens import *
import random
from datetime import datetime, time
import sqlite3
import math
import pytz

 
class Functions:
    # GET BLOCK NUMS FOR BUGS PROFILE
    def getBlockNums():
        endpoint = "https://api.etherscan.io/api"
        current_time = datetime.utcnow()
        startOfDay = datetime.combine(current_time.date(), time.min)
        ethTimezone = pytz.timezone('UTC')
        startOfDayEth = ethTimezone.localize(startOfDay)
        timestamp = int(startOfDayEth.timestamp())
        url = f"{endpoint}?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={ETHSCAN_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data["status"] == "1":
            block_number = int(data["result"])
            _startBlock = block_number
            _endBlock = int(_startBlock) + 5760
            # print(_startBlock, _endBlock)
            return _startBlock, _endBlock
        else:
            raise Exception("Failed to retrieve most recent block number")

    # APEX PLACEMENT SORTING
    def ApexPlacement(placed):
        if int(placed) > 10:
            points = 0
        elif int(placed) == 10:
            points = 3
        elif int(placed) == 9:
            points = 4
        elif int(placed) == 8:
            points = 5
        elif int(placed) == 7:
            points = 6
        elif int(placed) == 6:
            points = 7
        elif int(placed) == 5:
            points = 10
        elif int(placed) == 4:
            points = 12
        elif int(placed) == 3:
            points = 15
        elif int(placed) == 2:
            points = 20
        elif int(placed) == 1:
            points = 25
        return points

    # CREATING THE RAFFLE DRAW FUCNTION
    def raffle_draw(participants: dict, competitorNum) -> str:
        if sum(participants.values()) <= 0:
            normalized_participants = {
                key: value / sum(participants.values())
                for key, value in participants.items()
            }
        else:
            normalized_participants = {
                key: value / sum(participants.values())
                for key, value in participants.items()
            }
        population, weights = zip(*normalized_participants.items())
        winners = []
        for win in range(competitorNum):
            winner = random.choices(population=population, weights=weights)[0]
            winners.append(winner)
        return winners

    # GUILD WINNER
    def winning_guild(event):
        guilds = {}
        conn = sqlite3.connect("bugs_DB2.sqlite")
        cur = conn.cursor()
        if event == "apex":
            pull = cur.execute("SELECT points, guild_id FROM Apex_Profile")
            ret = pull.fetchall()
            for points, guild_id in ret:
                if guild_id in guilds:
                    guilds[guild_id] = +points
                else:
                    guilds[guild_id] = points
        elif event == "xdef":
            pull = cur.execute("SELECT points, guild_id FROM XDefiant_Profile")
            ret = pull.fetchall()
            for points, guild_id in ret:
                if guild_id in guilds:
                    guilds[guild_id] = +points
                else:
                    guilds[guild_id] = points

        max_guild_id = max(guilds, key=lambda k: guilds[k])
        max_points = guilds[max_guild_id]

        return max_guild_id, max_points

    # FRIDAY TIME
    def isItSaturday():
        now = datetime.now()
        if now.weekday() == 5:
            start_time = datetime(now.year, now.month, now.day, 10, 0, 0)
            end_time = datetime(now.year, now.month, now.day, 22, 0, 0)
            if start_time <= now <= end_time:
                return True

        return False

    # APEX RAFFLE DRAW
    def apexRaffleDraw(competitors: dict):
        brackets = [
            {
                "name": "bronze",
                "min_points": 10,
                "max_points": 35,
                "draw_percentage": 5,
                "players": {},
            },
            {
                "name": "silver",
                "min_points": 36,
                "max_points": 70,
                "draw_percentage": 15,
                "players": {},
            },
            {
                "name": "gold",
                "min_points": 71,
                "max_points": 105,
                "draw_percentage": 30,
                "players": {},
            },
            {
                "name": "buggin",
                "min_points": 106,
                "max_points": 140,
                "draw_percentage": 50,
                "players": {},
            },
        ]

        for gamertag, pts in competitors.items():
            for bracket in brackets:
                if bracket["min_points"] <= pts <= bracket["max_points"]:
                    bracket["players"][gamertag] = pts

        winners = []
        numOfWinners = math.floor(len(competitors) * 0.1)
        for _ in range(numOfWinners):
            # Randomly pick a bracket based on draw_percentage
            bracket_names = [bracket["name"] for bracket in brackets]
            draw_percentages = [bracket["draw_percentage"] for bracket in brackets]
            selected_bracket = random.choices(bracket_names, draw_percentages)[0]

            # Randomly pick a winner from the selected bracket's players using their points as weights
            selected_players = brackets[bracket_names.index(selected_bracket)][
                "players"
            ]
            winner = random.choices(
                list(selected_players.keys()), weights=list(selected_players.values())
            )[0]

            # Add the winner's info to the winners list as a dictionary
            winner_info = {
                "winner": winner,
                "bracket": selected_bracket,
                "score": selected_players[winner],
            }
            winners.append(winner_info)

            # Remove the selected winner from the players list to ensure they cannot be chosen again
            del selected_players[winner]

        return winners

    # XDEFIANT RAFFLE DRAW
    def xdefRaffleDraw(competitors: dict):
        brackets = [
            {
                "name": "bronze",
                "min_points": 1,
                "max_points": 40,
                "draw_percentage": 5,
                "players": {},
            },
            {
                "name": "silver",
                "min_points": 42,
                "max_points": 88,
                "draw_percentage": 15,
                "players": {},
            },
            {
                "name": "gold",
                "min_points": 90,
                "max_points": 108,
                "draw_percentage": 30,
                "players": {},
            },
            {
                "name": "buggin",
                "min_points": 110,
                "max_points": 130,
                "draw_percentage": 50,
                "players": {},
            },
        ]

        for gamertag, pts in competitors.items():
            for bracket in brackets:
                if bracket["min_points"] <= pts <= bracket["max_points"]:
                    bracket["players"][gamertag] = pts

        winners = []
        numOfWinners = math.floor(len(competitors) * 0.1)
        for _ in range(numOfWinners):
            # Randomly pick a bracket based on draw_percentage
            bracket_names = [bracket["name"] for bracket in brackets]
            draw_percentages = [bracket["draw_percentage"] for bracket in brackets]
            selected_bracket = random.choices(bracket_names, draw_percentages)[0]

            # Randomly pick a winner from the selected bracket's players using their points as weights
            selected_players = brackets[bracket_names.index(selected_bracket)][
                "players"
            ]
            winner = random.choices(
                list(selected_players.keys()), weights=list(selected_players.values())
            )[0]

            # Add the winner's info to the winners list as a dictionary
            winner_info = {
                "winner": winner,
                "bracket": selected_bracket,
                "score": selected_players[winner],
            }
            winners.append(winner_info)

            # Remove the selected winner from the players list to ensure they cannot be chosen again
            del selected_players[winner]

        return winners

        # APEX PLACEMENT SORTING

    def ApexPlacement(placed):
        if int(placed) > 10:
            points = 0
        elif int(placed) == 10:
            points = 3
        elif int(placed) == 9:
            points = 4
        elif int(placed) == 8:
            points = 5
        elif int(placed) == 7:
            points = 6
        elif int(placed) == 6:
            points = 7
        elif int(placed) == 5:
            points = 10
        elif int(placed) == 4:
            points = 12
        elif int(placed) == 3:
            points = 15
        elif int(placed) == 2:
            points = 20
        elif int(placed) == 1:
            points = 25
        return points
