import sqlite3
import math
import secrets
import random
import re

 
class Functions:
    # WINNING GUILD
    def winning_guild(event):
        guilds = {}
        conn = sqlite3.connect("bugs_DB2.sqlite")
        cur = conn.cursor()
        if event == "apex":
            pull = cur.execute("SELECT points, guild_id, hosted_id FROM Apex_Profile")
        elif event == "finals":
            pull = cur.execute("SELECT points, guild_id, hosted_id FROM Finals_Profile")
        elif event == "xdefiant":
            pull = cur.execute("SELECT points, guild_id, hosted_id FROM XDefiant_Profile")
        else:
            return None, None
        
        ret = pull.fetchall()
        for points, guild_id, hosted_id in ret:
            # GETS THE SUM OF POINTS PER GUILD
            if guild_id in guilds:
                if guild_id == 1:
                    k = str(guild_id) + "_" + str(hosted_id)
                    if k in guilds:
                        guilds[k][0] += 1
                        guilds[k][1] += points
                    else:
                        guilds[k] = [1, points]
                else:
                    guilds[guild_id][0] += 1
                    guilds[guild_id][1] += points 
            else:
                guilds[guild_id] = [1, points]
        # FIND THE AVERAGE SCORE FOR EACH GUILD 
        avgScores = {}
        for k, value in guilds.items():
            mems = value[0]
            pts = value[1]
            avg = pts / mems
            avgScores[k] = avg 

        bestGuildAvg = max(avgScores, key=avgScores.get)
        bestAvgScore = avgScores[bestGuildAvg]
        tiedGuilds = [k for k, v in avgScores.items() if v == bestAvgScore]
        if "1_" in bestGuildAvg:
            hostedId = re.sub(r"[^1_]", "", bestGuildAvg)
            pullName = cur.execute('SELECT name FROM Hosted_Comm WHERE id = ?', (hostedId, ))
            name = pullName.fetchone()[0]
        else:
            pullName = cur.execute('SELECT name FROM Stoke_Guilds WHERE guild_id = ?', (bestGuildAvg, ))
            name = pullName.fetchone()[0]

        if tiedGuilds:
            tiedStr = ""
            for id in tiedGuilds:
                if "1_" in id:
                    hostedId = re.sub(r"[^1_]", "", id)
                    pullName = cur.execute('SELECT name FROM Hosted_Comm WHERE id = ?', (hostedId, ))
                    name = pullName.fetchone()[0]
                else:
                    pullName = cur.execute('SELECT name FROM Stoke_Guilds WHERE guild_id = ?', (id, ))
                    name = pullName.fetchone()[0]
                tiedStr += name + " "
            conn.close()
            return bestGuildAvg, bestAvgScore, tiedStr 
        conn.close()
        return name, bestAvgScore, None

    # GUILD WINNER
    def guild_winner(guildName, event):
        conn = sqlite3.connect('bugs_DB2.sqlite')
        cur = conn.cursor()
        try:
            # PULL GUILDID USING NAME
            pullGuildId = cur.execute("SELECT guild_id FROM Stoke_Guilds WHERE guild_name = ?", (guildName, ))
            guildId = pullGuildId.fetchone()[0]
            if guildId:
                try:
                    if event == 'apex':
                        pullPlayers = cur.execute('SELECT bugs_id FROM Apex_Profile WHERE guild_id = ?', (guildId, ))
                    elif event == 'finals':
                        pullPlayers = cur.execute('SELECT bugs_id FROM Finals_Profile WHERE guild_id = ?', (guildId, ))
                    elif event == 'xdefiant':
                        pullPlayers = cur.execute('SELECT bugs_id FROM XDefiant_Profile WHERE guild_id = ?', (guildId, ))
                    else:
                        return None, 3
                    
                    players = pullPlayers.fetchall()
                    winner = secrets.choice(players)
                    return winner, 2
                except:
                    return None, 3
            
            elif guildId == None:
                # MUST BE A HOSTED NAME
                pullHostedId = cur.execute('SELECT id FROM Hosted_Comm WHERE name = ?', (guildName, ))
                hostedId = pullHostedId.fetchone()[0]
                if hostedId:
                    try:
                        if event == 'apex':
                            pullPlayers = cur.execute('SELECT bugs_id FROM Apex_Profile WHERE hosted_id = ?', (hostedId, ))
                        elif event == 'finals':
                            pullPlayers = cur.execute('SELECT bugs_id FROM Finals_Profile WHERE hosted_id = ?', (hostedId, ))
                        elif event == 'xdefiant':
                            pullPlayers = cur.execute('SELECT bugs_id FROM XDefiant_Profile WHERE hosted_id = ?', (hostedId, ))
                        else:
                            return None, 3
                        
                        players = pullPlayers.fetchall()
                        winner = secrets.choice(players)
                        pulldiscord = cur.execute('SELECT discord FROM bugs_Profile WHERE id = ?', (winner, ))
                        discord = pulldiscord.fetchone()[0]
                        return discord, 2
                    except:
                        return None, 3
        except:
            return None, 4
        finally: conn.close()
            
    # APEX RAFFLE DRAW
    def apexRaffleDraw():
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

        # PULL GAMERTAG AND POINTS FOR THE COMPETITORS
        try:
            conn = sqlite3.connect('bugs_DB.sqlite')
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            playersNpts = cur.execute('SELECT gamertag, points FROM Apex_Profile')
            allPlayersNpts = playersNpts.fetchall()
            competitors = {player: pts for player, pts in allPlayersNpts}
        except:
            return None
        finally:
            conn.close() 

        # ASSIGN PLAYERS TO BRACKETS BASED ON POINTS
        for gamertag, pts in competitors.items():
            for bracket in brackets:
                if bracket["min_points"] <= pts <= bracket["max_points"]:
                    bracket["players"][gamertag] = pts

        winners = []
        numOfWinners = math.floor(len(competitors) * 0.1)
        draw_percentages = [bracket["draw_percentage"] for bracket in brackets]

        # ITERATE FOR RANGE IN 10%
        for _ in range(numOfWinners):

            # PICKS A BRACKET BASED ON INITIAL DRAW PERCENTAGES
            selected_bracket = random.choices(brackets, weights=draw_percentages, k=1)[0]
            selected_players = selected_bracket["players"]

            if selected_players:
                # PICKS A WINNER RANDOMLY USING SCORES AS WEIGHTS  
                winner = random.choices(
                    list(selected_players.keys()), weights=list(selected_players.values()), k=1
                )[0]

                winner_info = {
                    "winner": winner,
                    "bracket": selected_bracket["name"],
                    "score": selected_players[winner],
                }
                # ADDS WINNER TO WINNERS DICT AND REMOVES THEM FROM DICT IN BRACKET
                winners.append(winner_info)
                del selected_players[winner]  

        return winners

    # XDEFIANT RAFFLE DRAW
    def xdefRaffleDraw(competitors: dict):
        brackets = [
            {
                "name": "bronze",
                "min_points": 100,
                "max_points": 502,
                "draw_percentage": 5,
                "players": {},
            },
            {
                "name": "silver",
                "min_points": 503,
                "max_points": 1005,
                "draw_percentage": 15,
                "players": {},
            },
            {
                "name": "gold",
                "min_points": 1006,
                "max_points": 1509,
                "draw_percentage": 30,
                "players": {},
            },
            {
                "name": "buggin",
                "min_points": 1509,
                "max_points": 2012,
                "draw_percentage": 50,
                "players": {},
            },
        ]

        # ASSIGN PLAYERS TO BRACKETS BASED ON POINTS
        for gamertag, pts in competitors.items():
            for bracket in brackets:
                if bracket["min_points"] <= pts <= bracket["max_points"]:
                    bracket["players"][gamertag] = pts

        winners = []
        numOfWinners = math.floor(len(competitors) * 0.1)
        draw_percentages = [bracket["draw_percentage"] for bracket in brackets]

        # ITERATE FOR RANGE IN 10%
        for _ in range(numOfWinners):
            
            # PICKS A BRACKET BASED ON INITIAL DRAW PERCENTAGES
            selected_bracket = random.choices(brackets, weights=draw_percentages, k=1)[0]
            selected_players = selected_bracket["players"]

            if selected_players:
                # PICKS A WINNER RANDOMLY USING SCORES AS WEIGHTS  
                winner = random.choices(
                    list(selected_players.keys()), weights=list(selected_players.values()), k=1
                )[0]

                winner_info = {
                    "winner": winner,
                    "bracket": selected_bracket["name"],
                    "score": selected_players[winner],
                }
                # ADDS WINNER TO WINNERS DICT AND REMOVES THEM FROM DICT IN BRACKET
                winners.append(winner_info)
                del selected_players[winner]  

        return winners

        # APEX PLACEMENT SORTING

    # APEX PLACEMENT PTS 
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

    # FINALS RAFFLE DRAW
    def finalsRaffleDraw():
        brackets = [
            {
                "name": "bronze",
                "min_points": 1,
                "max_points": 65,
                "draw_percentage": 5,
                "players": {},
            },
            {
                "name": "silver",
                "min_points": 66,
                "max_points": 116,
                "draw_percentage": 15,
                "players": {},
            },
            {
                "name": "gold",
                "min_points": 117,
                "max_points": 167,
                "draw_percentage": 30,
                "players": {},
            },
            {
                "name": "buggin",
                "min_points": 168,
                "max_points": 185,
                "draw_percentage": 50,
                "players": {},
            },
        ]

         # PULL GAMERTAG AND POINTS FOR THE COMPETITORS
        try:
            conn = sqlite3.connect('bugs_DB.sqlite')
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            playersNpts = cur.execute('SELECT gamertag, points FROM Finals_Profile')
            allPlayersNpts = playersNpts.fetchall()
            competitors = {player: pts for player, pts in allPlayersNpts}
        except:
            return None
        finally:
            conn.close()

        # ASSIGN PLAYERS TO BRACKETS BASED ON POINTS
        for gamertag, pts in competitors.items():
            for bracket in brackets:
                if bracket["min_points"] <= pts <= bracket["max_points"]:
                    bracket["players"][gamertag] = pts

        winners = []
        numOfWinners = math.floor(len(competitors) * 0.1)
        draw_percentages = [bracket["draw_percentage"] for bracket in brackets]

        # ITERATE FOR RANGE IN 10%
        for _ in range(numOfWinners):
            
            # PICKS A BRACKET BASED ON INITIAL DRAW PERCENTAGES
            selected_bracket = random.choices(brackets, weights=draw_percentages, k=1)[0]
            selected_players = selected_bracket["players"]

            if selected_players:
                # PICKS A WINNER RANDOMLY USING SCORES AS WEIGHTS  
                winner = random.choices(
                    list(selected_players.keys()), weights=list(selected_players.values()), k=1
                )[0]

                winner_info = {
                    "winner": winner,
                    "bracket": selected_bracket["name"],
                    "score": selected_players[winner],
                }
                # ADDS WINNER TO WINNERS DICT AND REMOVES THEM FROM DICT IN BRACKET
                winners.append(winner_info)
                del selected_players[winner]  

        return winners