import re
from stoke import Stoke
from functions import Functions

class ImageParser:
    def __init__(self, filepath, gamertag, bugsId, guildId):
        self.filepath = filepath
        self.gamertag = gamertag
        self.bugsId = bugsId
        self.guildId = guildId

    # APEX PARSING 
    def apexPlacement(self, imgText):
        stokeIns = Stoke()
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        try:
            # FILTER PLACEMENT
            placePattern = r'\b(1[0-9]|20|[1-9])\b'
            placeMatch = re.search(placePattern, imgText)
            if placeMatch:
                placement = placeMatch.group(1).rstrip()
                placed = int(placement)
                placementPts = Functions.ApexPlacement(placed)
                return placementPts
            else:
                flag = "Else Hit" 
                logFlags.append(flag)
                logIns.log(channel='score', cmd="Ascore/Placement")
                return None 

        except AttributeError:
            flag = "Attribute Error, no match found"
            logFlags.append(flag)
            logIns.log(channel='score', cmd="Ascore/Placement")
            return None 
        except IndexError:
            flag = "Index Error, no match found"
            logFlags.append(flag)
            logIns.log(channel='score', cmd="Ascore/Placement")
            return None 

    def apexKills(self, imgText): 
            stokeIns = Stoke()
            logFlags = []
            logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
            try:
                # FILTER PLACEMENT
                killsPattern = r"(\d{1,2})(?=[\da-zA-Z/])"
                killsMatch = re.search(killsPattern, imgText)
                if killsMatch:
                    kills = killsMatch.group(1).rstrip()
                    totalKills = int(kills)
                    killPts = abs(totalKills * 5)
                    if killPts > 75:
                        killPts = 75
                    return killPts
                else:
                    flag = "Else Hit"
                    logFlags.append(flag)
                    logIns.log(channel='score', cmd="Ascore/Kills")
                    return None 

            except AttributeError:
                flag = "Attribute Error, no match found"
                logFlags.append(flag)
                logIns.log(channel='score', cmd="Ascore/Kills")
                return None
            except IndexError:
                flag = "Index Error, no match found"
                logFlags.append(flag)
                logIns.log(channel='score', cmd="Ascore/Kills")
                return None  
            
    def apexDamage(self, imgText):
        stokeIns = Stoke()
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        try:
            # FILTER PLACEMENT
            dmgPattern = r"(\d+)"
            dmgMatch = re.search(dmgPattern, imgText)
            if dmgMatch:
                dmg = dmgMatch.group(1).rstrip()
                totalDmg = int(dmg)
                dmgPts = round(totalDmg * 0.01)
                if dmgPts > 40:
                    dmgPts = 40
                return abs(dmgPts)
            else:
                flag = "Else Hit"
                logFlags.append(flag)
                logIns.log(channel='score', cmd="Ascore/Dmg")
                return None 

        except AttributeError:
            flag = "Attribute Error, no match found"
            logFlags.append(flag)
            logIns.log(channel='score', cmd="Ascore/Dmg")
            return None 
        except IndexError:
            flag = "Index Error, no match found"
            logFlags.append(flag)
            logIns.log(channel='score', cmd="Ascore/Dmg")
            return None 

    # FINALS PARSING
    def finalsPlacement(self, imgText):
        stokeIns = Stoke()
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        try:
            pattern = r"\$(\d{1,3}(?:,\d{3})*)"
            match = re.search(pattern, imgText)
            if match:
                cashExtracted = match.group(1).rstrip()
                totalCash = int(cashExtracted.replace(",", ""))
                totalCash = round(totalCash / 1000, 1) 
                return abs(totalCash)
            else:
                flag = "Else Hit"
                logFlags.append(flag)
                logIns.log(channel='score', cmd="Fscore/CashExtracted")
                return None 

        except AttributeError:
            flag = "Attribute Error, no match found"
            logFlags.append(flag)
            logIns.log(channel='score', cmd="Fscore/CashExtracted")
            return None 

    def finalsScores(self, imgText):
        stokeIns = Stoke()
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        try:
            pattern = r"(\d{1,3}(?:,\d{3})*)"
            match = re.search(pattern, imgText)
            if match:
                scoreNum = match.group(1).rstrip()
                scoreInt = int(scoreNum.replace(",", ""))
                roundedVal = round(scoreInt / 1000, 1)
                return abs(roundedVal)
            else:
                flag = "Else Hit"
                logFlags.append(flag)
                logIns.log(channel='score', cmd="Fscore/Scores")
                return None 

        except AttributeError:
            flag = "Attribute Error, no match found"
            logFlags.append(flag)
            logIns.log(channel='score', cmd="Fscore/Scores")
            return None

    # XDEFIANT PARSING
    def xdefScores(self, imgText):
        stokeIns = Stoke()
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        userInfo = []
        try:

            split = imgText.split(" ")
            for item in split:
                item = re.sub(r"[,]", "", item)
                userInfo.append(item)
            if len(userInfo) != 8:
                logFlags.append("Length of list Error")
                logIns.log(channel='score', cmd="Xdcore/Scores")
                return None
            kills = float(userInfo[2])
            deaths = float(userInfo[3])
            objScore = float(userInfo[5])
            suppScore = float(userInfo[6])
            dmg = float(userInfo[7])
            # DEBUG
            scoreSumm = kills + objScore + suppScore + dmg
            perfGame = False
            if deaths == 0:
                perfGame = True
            if perfGame == False:
                kd = kills / deaths
            else:
                kd = kills
            roundKd = round(kd, 2)
            multiplierScore = scoreSumm * roundKd
            finalScore = multiplierScore * .1
            roundedFinal = round(finalScore)
            return roundedFinal

        except ValueError as e:
            logFlags.append(f"ValueError: {e}")
            logIns.log(channel='score', cmd="Xdcore/Scores")
            return None
        except ZeroDivisionError as e:
            logFlags.append(f"ZeroDivisionError: {e}")
            logIns.log(channel='score', cmd="Xdcore/Scores")
            return None
        except IndexError as e:
            logFlags.append(f"IndexError: {e}")
            logIns.log(channel='score', cmd="Xdcore/Scores")
            return None
        except TypeError as e:
            logFlags.append(f"TypeError: {e}")
            logIns.log(channel='score', cmd="Xdcore/Scores")
            return None
        except Exception as e:
            logFlags.append(f"Unexpected error: {e}")
            logIns.log(channel='score', cmd="Xdcore/Scores")
            return None




