import sqlite3
from functions import Functions
from API_Tokens import *
from requests import get
import os
import datetime
from datetime import datetime
import math

# FLAGS
# 1, METHOD ERROR
# 2, SUCCESS
# 3, LIBRARY/SQLITE ERROR
# 4, ARG ERROR
# 5, MALICIOUS INTENT


class Stoke:
    class bugsProfile:
        def hasProfile(self, discord):
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pullProfile = cur.execute(
                    "SELECT id FROM bugs_profile WHERE discord = ?", (discord,)
                )
                retProfile = pullProfile.fetchone()[0]

                if retProfile:
                    flag = 2

                return flag
            except:
                flag = 1
                return flag

        def create(self, discord, ethAddr):
            startBlock, endBlock = Functions.getBlockNums()

            url = f"https://api.etherscan.io/api?module=account&action=txlist&address={ethAddr}&startblock={startBlock}&endblock={endBlock}&offset=10&sort=desc&apikey={ETHSCAN_API_KEY}"

            req = get(url).json()
            _value = False
            _toAddr = False
            result = req["result"]
            for item in result:
                toAddr = item["to"]
                if toAddr == bugsAddr:
                    value = item["value"]
                    txHash = item["hash"]
                    if value == ProfileFee:
                        _value = True
                        _toAddr = True
            if not (_value and _toAddr):
                flag = "No Transaction Found"
                return flag

            if _value == True and _toAddr == True:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()

                # ADD USER TO BUGS DATABASE
                try:
                    apex = 0
                    xdef = 0
                    cur.execute(
                        "INSERT INTO bugs_Profile (discord, eth_addr, hash, xdefiant_profile, apex_profile) VALUES (?, ?, ?, ?, ?)",
                        (discord, ethAddr, txHash, xdef, apex),
                    )
                    conn.commit()
                except sqlite3.IntegrityError as e:
                    conn.close()
                    Eflag = 5
                    return Eflag

                # ENTER BUGS ID INTO PLAYER PROFILE TABLES
                pull = cur.execute(
                    "SELECT id FROM bugs_Profile WHERE discord = ?", (discord,)
                )
                ret = pull.fetchone()[0]

                cur.execute("INSERT INTO Apex_Profile (bugs_id) VAlUES (?)", (ret,))
                cur.execute("INSERT INTO XDefiant_Profile (bugs_id) VALUES(?)", (ret,))

                # ENTER USER INTO RATE TABLE
                cur.execute("INSERT INTO Rate (bugs_id) VALUES (?)", (ret,))

                conn.commit()
                conn.close()
                flag = 2
                return flag

        def delete(self, discord, guildId):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            try:
                # DELETE PROFILES
                cur.execute(
                    "DELETE FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                cur.execute(
                    "DELETE FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                cur.execute("DELETE FROM bugs_Profile WHERE discord = ?", (discord,))

                conn.commit()
                # REMOVE ROLES
                pullRoles = cur.execute(
                    "SELECT apex_role, xdef_role, competitor_role FROM Stoke_Guilds WHERE guild = ?",
                    (guildId,),
                )
                retRoles = pullRoles.fetchone()
                apexRole = int(retRoles[0])
                xdefRole = int(retRoles[1])
                compRole = int(retRoles[2])
                roleLst = [apexRole, xdefRole, compRole]
                flag = 2
                conn.close()

                return flag, roleLst

            except:
                flag = 3
                return flag

        def retrieve(self, discord):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            try:
                profile = cur.execute(
                    "SELECT eth_addr FROM bugs_Profile WHERE discord = ?", (discord,)
                )
                retProfile = profile.fetchone()[0]
                flag = 2
                conn.close()
                return flag, retProfile

            except:
                flag = 3
                return flag

        def update(self, discord, ethAddr):
            startBlock, endBlock = Functions.getBlockNums()

            url = f"https://api.etherscan.io/api?module=account&action=txlist&address={ethAddr}&startblock={startBlock}&endblock={endBlock}&offset=10&sort=desc&apikey={ETHSCAN_API_KEY}"

            req = get(url).json()
            _value = False
            _toAddr = False
            result = req["result"]
            for item in result:
                toAddr = item["to"]
                if toAddr == bugsAddr:
                    value = item["value"]
                    txHash = item["hash"]
                    if value == updateProfileFee:
                        _value = True
                        _toAddr = True
            if not (_value and _toAddr):
                flag = "No Transaction Found"
                return flag

            if _value == True and _toAddr == True:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()

                # UPDATE USERS ADDR
                try:
                    cur.execute(
                        "UPDATE bugs_Profile SET eth_addr = ?, hash = ? WHERE discord = ?",
                        (
                            ethAddr,
                            txHash,
                            discord,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    flag = 2
                    return flag
                except sqlite3.IntegrityError as e:
                    conn.close()
                    Eflag = 5
                    return Eflag

        def bugsId(self, discord):
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()

                pull = cur.execute(
                    "SELECT id FROM bugs_Profile WHERE discord = ?", (discord,)
                )
                ret = pull.fetchone()[0]
                flag = 2
                return flag, ret
            except:
                ret = None
                flag = 3
                return flag, ret

    class Guilds:
        # METHOD TO PULL CHANNEL IDS
        # ID'S RETURN AS AN INT
        def pullChannel(self, _id, find):
            # PULLPLAYER PROFILE CHANNEL BASED ON GUILD
            if find == "playerProfile":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT player_profile FROM Stoke_Guilds WHERE guild = ?",
                        (_id,),
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    conn.close()
                    flag = 2

                    return flag, ret
                except:
                    flag = 3
                    ret = None
                    return flag, ret

            # PULL PMNT VERIFY CHANNEL BASED ON GUILD
            elif find == "pmntVerify":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT payment_verify FROM Stoke_Guilds WHERE guild = ?",
                        (_id,),
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()

                    return flag, ret
                except:
                    flag = 3
                    ret = None
                    return flag, ret

            # PULL SC SUBMISSION CHANNEL BASED ON GUILD
            elif find == "scSubmission":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT sc_submission FROM Stoke_Guilds WHERE guild = ?", (_id,)
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()

                    return flag, ret
                except:
                    flag = 3
                    ret = None
                    return flag, ret

            # PULL PRIV EVENT CHANNEL BASED ON GUILD
            elif find == "privEvent":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT priv_event_channel FROM Stoke_Guilds WHERE guild = ?",
                        (_id,),
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()

                    return flag, ret
                except:
                    flag = 3
                    ret = None
                    return flag, ret

        # METHOD TO PULL SERVER/COMMUNITY NAME
        # NAME RETURNS AS AN STR
        def pullName(self, _id):
            # PULL GUILD NAME
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT guild_name FROM Stoke_Guilds WHERE guild = ?",
                    (_id,),
                )
                ret = pull.fetchone()[0]
                conn.close()

                return ret
            except:
                flag = 3
                return flag

        # METHOD TO PULL SERVER/COMMUNITY IDS
        # ID'S RETURN AS AN INT
        def pullId(self, _id):
            # PULL GUILD ID
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT id FROM Stoke_Guilds WHERE guild = ?",
                    (_id,),
                )
                ret = pull.fetchone()[0]
                ret = int(ret)
                conn.close()

                return ret
            except:
                flag = 3
                return flag

        # METHOD TO PULL SERVER/COMMUNITY SCORE
        # SCORE RETURNS AS AN INT
        def pullScore(self, _id):
            # PULL COMMUNITY SCORE
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT community_score FROM Stoke_Guilds WHERE guild = ?",
                    (_id,),
                )
                ret = pull.fetchone()[0]
                ret = int(ret)
                conn.close()

                return ret
            except:
                flag = 3
                return flag

        # METHOD TO PULL DISCORD ROLE
        # ROLE RETURNS AS AN INT
        def pullRole(self, guildId, find):
            # FIND APEX ROLE
            if find == "apex":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT apex_role FROM Stoke_Guilds WHERE guild = ?", (guildId,)
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()
                    return flag, ret
                except:
                    flag = 1
                    return flag

            # FIND XDEFIANT ROLE
            elif find == "xdef":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT xdef_role FROM Stoke_Guilds WHERE guild = ?", (guildId,)
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()
                    return flag, ret
                except:
                    flag = 3
                    return flag

            # FIND COMPETITOR ROLE
            elif find == "competitor":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                        (guildId,),
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()
                    return flag, ret
                except:
                    flag = 3
                    return flag

            # FIND PRIVATE EVENT ROLE
            elif find == "privEventRole":
                try:
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT priv_event_role FROM Stoke_Guilds WHERE guild = ?",
                        (guildId,),
                    )
                    ret = pull.fetchone()[0]
                    ret = int(ret)
                    flag = 2
                    conn.close()
                    return flag, ret
                except:
                    flag = 3
                    ret = None
                    return flag, ret

            else:
                flag = 4
                ret = None
                return flag, ret

    class PlayerProfile:
        def create(self, discord, gamertag, guildId, type):
            # CONNECT TO DB AND PULL BUGS ID
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            pull = cur.execute(
                "SELECT id FROM bugs_Profile WHERE discord = ?", (discord,)
            )
            ret = pull.fetchone()[0]

            if ret:
                # ADD INFO TO DB
                try:
                    # FIND GUILD ID FROM STOKE
                    pullGuild = cur.execute(
                        "SELECT id FROM Stoke_Guilds WHERE guild = ?", (guildId,)
                    )
                    retGuild = pullGuild.fetchone()[0]
                    retGuild = int(retGuild)

                    # INSERT INFO INTO PLAYER PROFILE

                    # APEX
                    if type == "apex":
                        try:
                            cur.execute(
                                "UPDATE Apex_Profile SET gamertag = ?, guild_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                (gamertag, retGuild, discord),
                            )

                            # SET FLAG FOR APEX PROFILE IN BUGS PROFILE TABLE
                            apex = 1
                            cur.execute(
                                "UPDATE bugs_Profile SET apex_profile = ? WHERE discord = ?",
                                (apex, discord),
                            )
                            conn.commit()
                            conn.close()
                            flag = 2
                            return flag
                        except sqlite3.IntegrityError as e:
                            conn.close()
                            Eflag = 5
                            return Eflag

                    # XDEFIANT
                    elif type == "xdef":
                        try:
                            cur.execute(
                                "UPDATE XDefiant_Profile SET gamertag = ?, guild_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                (gamertag, retGuild, discord),
                            )

                            # SET FLAG FOR APEX PROFILE IN BUGS PROFILE TABLE
                            apex = 1
                            cur.execute(
                                "UPDATE bugs_Profile SET xdefiant_profile = ? WHERE discord = ?",
                                (apex, discord),
                            )
                            conn.commit()
                            conn.close()
                            flag = 2
                            return flag
                        except sqlite3.IntegrityError as e:
                            conn.close()
                            Eflag = 5
                            return Eflag
                    else:
                        flag = 4
                        return flag
                except:
                    flag = 3
                    return 3
            else:
                flag = 3
                return flag

        def delete(self, discord, type):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            if type == "apex":
                try:
                    cur.execute(
                        "UPDATE Apex_Profile SET gamertag = NULL, guild_id = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (discord,),
                    )
                    cur.execute(
                        "UPDATE bugs_Profile SET apex_profile = 0 WHERE discord = ?",
                        (discord,),
                    )
                    conn.commit()
                    conn.close()
                    flag = 2
                    return flag
                except:
                    flag = 3
                    return flag

            elif type == "xdef":
                try:
                    cur.execute(
                        "UPDATE XDefiant_Profile SET gamertag = NULL, guild_id = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (discord,),
                    )
                    cur.execute(
                        "UPDATE bugs_Profile SET xdefiant_profile = 0 WHERE discord = ?",
                        (discord,),
                    )
                    conn.commit()
                    conn.close()
                    flag = 2
                    return flag
                except:
                    flag = 3
                    return flag

            else:
                flag = 4
                return flag

        def retrieve(self, discord, type):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            if type == "apex":
                try:
                    pull = cur.execute(
                        "SELECT gamertag FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (discord,),
                    )
                    info = pull.fetchone()[0]
                    flag = 2
                    conn.close()
                    return flag, info
                except:
                    flag = 3
                    conn.close()
                    return flag

            elif type == "xdef":
                try:
                    pull = cur.execute(
                        "SELECT gamertag FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (discord,),
                    )
                    info = pull.fetchone()[0]
                    flag = 2
                    conn.close()
                    return flag, info
                except:
                    flag = 3
                    conn.close()
                    return flag

            else:
                flag = 4
                conn.close()
                return flag

    class Event:
        def isOn(self, event):
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT submission_flag FROM Events WHERE game = ?", (event,)
                )
                ret = pull.fetchone()[0]
                flag = 2

                return flag, ret
            except:
                flag = 3
                ret = None
                return flag, ret

        def submissionDelete(self, discord, event):
            if event == "xdef":
                # PULL BUGS DB
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()

                pullFP = cur.execute(
                    "SELECT submission FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                retFP = pullFP.fetchone()[0]

                if retFP:
                    # NOW DELETE FILE FROM SYSTEM
                    filePath = os.path.join(f"xdef_sc/{discord}/{retFP}")
                    os.remove(filePath)

                    cur.execute(
                        "UPDATE XDefiant_Profile SET submission = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (discord,),
                    )
                    conn.commit()
                    conn.close()

                    flag = 2
                    return flag
                else:
                    flag = 3
                    return flag

            elif event == "apex":
                # PULL BUGS DB
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()

                pullFP = cur.execute(
                    "SELECT submission FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                retFP = pullFP.fetchone()[0]

                if retFP:
                    # NOW DELETE FILE FROM SYSTEM
                    filePath = os.path.join(f"apex_sc/{discord}/{retFP}")
                    os.remove(filePath)

                    cur.execute(
                        "UPDATE Apex_Profile SET submission = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (discord,),
                    )
                    conn.commit()
                    conn.close()

                    flag = 2
                    return flag
                else:
                    flag = 3
                    return flag
            else:
                flag = 1
                return flag

        def checkSubmission(self, discord, event):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            if event == "apex":
                pull = cur.execute(
                    "SELECT submission FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                ret = pull.fetchone()[0]
                conn.close()
                flag = 2
                return flag, ret
            elif event == "xdef":
                pull = cur.execute(
                    "SELECT submission FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                ret = pull.fetchone()[0]
                conn.close()
                flag = 2
                return flag, ret
            else:
                conn.close()
                flag = 1
                return flag

        def eventFlag(self, game, flag):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE Events SET submission_flag = ? WHERE game = ?",
                    (
                        flag,
                        game,
                    ),
                )
                conn.commit()
                conn.close()
                flag = 2
                return flag
            except:
                conn.close()
                flag = 3
                return flag

        def pmntFlag(self, game, flag):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE Events SET pmnt_flag = ? WHERE game = ?",
                    (
                        flag,
                        game,
                    ),
                )
                conn.commit()
                conn.close()
                flag = 2
                return flag
            except:
                conn.close()
                flag = 3
                return flag

        def pmntOn(self, event):
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT pmnt_flag FROM Events WHERE game = ?", (event,)
                )
                ret = pull.fetchone()[0]
                flag = 2

                return flag, ret
            except:
                flag = 3
                ret = None
                return flag, ret

    class PrivateEvent:
        def competitorList(self):
            try:
                conn = sqlite3.connect("bugs_DB2.sqlite")
                cur = conn.cursor()

                pullCompetitors = cur.execute("SELECT bugs_id FROM Private_Event")
                retCompetitors = pullCompetitors.fetchall()
                if retCompetitors:
                    conn.close()
                    flag = 2
                    return flag, retCompetitors
            except:
                flag = 3
                retCompetitors = None
                return flag, retCompetitors

        def privEventDraw(self, event):
            try:
                competitors = {}
                conn = sqlite3.connect("bugs_Db2.sqlite")
                cur = conn.cursor()

                pull = cur.execute("SELECT bugs_id, points FROM Private_Event")
                info = pull.fetchall()
                competitorNum = len(info)
                numOfWinners = math.floor(competitorNum * 0.1)
                for item in info:
                    competitors[item[0]] = item[1]

                winners = Functions.raffle_draw(competitors, numOfWinners)
                winString = ""
                for win in winners:
                    if event == "apex":
                        pullWinner = cur.execute(
                            "SELECT gamertag FROM Apex_Profile WHERE bugs_id = ?",
                            (win,),
                        )
                        retWinner = pullWinner.fetchone()[0]
                    elif event == "xdefiant":
                        pullWinner = cur.execute(
                            "SELECT gamertag FROM XDefiant_Profile WHERE bugs_id = ?",
                            (win,),
                        )
                        retWinner = pullWinner.fetchone()[0]
                    winString += f"{retWinner}\n"
                flag = 2
                conn.close()
                return flag, winString
            except:
                flag = 3
                winString = None
                return flag, winString

    class PaymentVerify:
        def pullAddr(self, discord):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            try:
                pull = cur.execute(
                    "SELECT eth_addr FROM bugs_Profile WHERE discord = ?", (discord,)
                )
                ret = pull.fetchone()[0]

                return ret

            except:
                flag = 3
                return flag

        def checkPayment(self, discord, addr, guildId, event):
            if event == "apex":
                wallet = bugsApexAddr
            elif event == "xdef":
                wallet = bugsXDefAddr

            startBlock, endBlock = Functions.getBlockNums()
            EtherscanUrl = f"{BASE_URL}?module=account&action=txlist&address={addr}&startblock={startBlock}&endblock={endBlock}&offset=10&sort=dec&apikey={ETHSCAN_API_KEY}"
            data = get(EtherscanUrl).json()
            _value = False
            _toAddr = False
            result = data["result"]
            for item in result:
                toAddr = item["to"]
                if toAddr == wallet:
                    value = item["value"]
                    txHash = item["hash"]
                    if value == eventEntryCost:
                        _value = True
                        _toAddr = True
            if not (_value and _toAddr):
                flag = 3
                msg = f"Sorry mate looks like you haven't sent the Entry Cost of 0.005 ETH sent to this wallet {bugsApexAddr} "
                return flag, msg
            if _value == True and _toAddr == True:
                if event == "apex":
                    # UPDATE BUGS PROFILE AND ASSIGN COMPETITOR ROLE
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pullRole = cur.execute(
                        "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                        (guildId,),
                    )
                    retRole = pullRole.fetchone()[0]
                    competitorRole = int(retRole)

                    cur.execute(
                        "UPDATE Apex_Profile SET elligible = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            txHash,
                            discord,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    flag = 2
                    return flag, competitorRole
                elif event == "xdef":
                    # UPDATE BUGS PROFILE AND ASSIGN COMPETITOR ROLE
                    conn = sqlite3.connect("bugs_DB2.sqlite")
                    cur = conn.cursor()
                    pullRole = cur.execute(
                        "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                        (guildId,),
                    )
                    retRole = pullRole.fetchone()[0]
                    competitorRole = int(retRole)

                    cur.execute(
                        "UPDATE XDefiant_Profile SET elligible = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            txHash,
                            discord,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    flag = 2
                    return flag, competitorRole
                else:
                    flag = 3
                    msg = "Transaction not found"
                    return flag, msg
            else:
                flag = 4
                msg = "Transaction not found"
                return flag, msg

    class Wipe:
        def wipeEvent(self, event):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()
            stokeIns = Stoke()

            if event == "apex":
                cur.execute(
                    "UPDATE Apex_Profile SET elligible = NULL, submission = NULL, points = NULL"
                )
                conn.commit()
                conn.close()
                flag = 2
                return flag

            elif event == "xdef":
                cur.execute(
                    "UPDATE XDefiant_Profile SET elligible = NULL, submission = NULL, points = NULL"
                )
                conn.commit()
                conn.close()
                flag = 2
                return flag

            else:
                flag = 3
                return flag

    class Wallet:
        def pullBal(self):
            try:
                bals = []
                pullTreasury = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullTreasury = int(pullTreasury) / ETH_VALUE
                bals.append(pullTreasury)
                pullApex = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsApexAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullApex = int(pullApex) / ETH_VALUE
                bals.append(pullApex)
                pullXdef = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsXDefAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullXdef = int(pullXdef) / ETH_VALUE
                bals.append(pullXdef)

                flag = 2
                return flag, bals
            except:
                flag = 3
                return flag

    class Rate:
        def rateCheck(self, discord, channel):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            if channel == "playerProfile":
                pullRate = cur.execute(
                    "SELECT player_profile FROM Rate WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                rate = pullRate.fetchone()[0]
                if rate is None:
                    rate = 0

                else:
                    rate = int(rate)
                if rate < 9:
                    rate = rate + 1
                    cur.execute(
                        "UPDATE Rate SET player_profile = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            rate,
                            discord,
                        ),
                    )
                    conn.commit()
                    flag = 2
                    return flag
                else:
                    flag = 5
                    return flag

            elif channel == "pmntVerify":
                pullRate = cur.execute(
                    "SELECT pmnt_verify FROM Rate WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                rate = pullRate.fetchone()[0]
                if rate == None:
                    rate = 0
                else:
                    rate = int(rate)
                if rate < 9:
                    rate = rate + 1
                    cur.execute(
                        "UPDATE Rate SET pmnt_verify = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            rate,
                            discord,
                        ),
                    )
                    conn.commit()
                    flag = 2
                    return flag
                else:
                    flag = 5
                    return flag

            elif channel == "scSubmission":
                pullRate = cur.execute(
                    "SELECT sc_submission FROM Rate WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                    (discord,),
                )
                rate = pullRate.fetchone()[0]
                if rate == None:
                    rate = 0
                else:
                    rate = int(rate)
                if rate < 9:
                    rate = rate + 1
                    cur.execute(
                        "UPDATE Rate SET sc_submission = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (
                            rate,
                            discord,
                        ),
                    )
                    conn.commit()
                    flag = 2
                    return flag
                else:
                    flag = 5
                    return flag
            else:
                flag = 1
                return flag

        def resetRate(self):
            conn = sqlite3.connect("bugs_DB2.sqlite")
            cur = conn.cursor()

            cur.execute(
                "UPDATE Rate SET player_profile = 0, pmnt_verify = 0, sc_submission = 0"
            )
            conn.commit()
            conn.close()
            return

    class Log:
        def log(self, bugs_id, guildId, channel, cmd, flags):
            time = datetime.now()
            if channel == "playerProfile":
                fhand = open("logs/playerProfile.txt", "a")
                fhand.write(
                    f"Time: {time} | Guild: {guildId} | User: {bugs_id} | Cmd: {cmd} | Flags: {flags}\n"
                )
                fhand.close()
            elif channel == "pmntVerify":
                fhand = open("logs/pmntVerify.txt", "a")
                fhand.write(
                    f"Time: {time} | Guild: {guildId} | User: {bugs_id} | Cmd: {cmd} | Flags: {flags}\n"
                )
                fhand.close()
            elif channel == "scSubmission":
                fhand = open("logs/scSubmission.txt", "a")
                fhand.write(
                    f"Time: {time} | Guild: {guildId} | User: {bugs_id} | Cmd: {cmd} | Flags: {flags}\n"
                )
                fhand.close()
            elif channel == "Admin":
                fhand = open("logs/Admin.txt", "a")
                fhand.write(
                    f"Time: {time} | Guild: {guildId} | User: {bugs_id} | Cmd: {cmd} | Flags: {flags}\n"
                )
                fhand.close()
            elif channel == "other":
                fhand = open("logs/other.txt", "a")
                fhand.write(
                    f"Time: {time} | Guild: {guildId} | User: {bugs_id} | Cmd: {cmd} | Flags: {flags}\n"
                )
                fhand.close()
            elif channel == "score":
                fhand = open("logs/score.txt", "a")
                fhand.write(
                    f"Time: {time} | Guild: {guildId} | User: {bugs_id} | Cmd: {cmd} | Flags: {flags}\n"
                )
                fhand.close()

        def setupLog(self, guildName, cmd, flags):
            time = datetime.now()
            fhand = open("logs/backend.txt", "a")
            fhand.write(
                f"Time: {time} | Guild: {guildName} | Cmd: {cmd} | Flags: {flags}\n"
            )
            fhand.close()
            return

        def leaveLog(self, guildName, cmd, flags):
            time = datetime.now()
            fhand = open("logs/backend.txt", "a")
            fhand.write(
                f"Time: {time} | Guild: {guildName} | Cmd: {cmd} | Flags: {flags}\n"
            )
            fhand.close()
            return

        def wipeLog(self, discord, cmd, flags):
            time = datetime.now()
            fhand = open("logs/backend.txt", "a")
            fhand.write(
                f"Time: {time} | User: {discord} | Cmd: {cmd} | Flags: {flags}\n"
            )
            fhand.close()
            return

        def privEventLog(self, discord, cmd, flags):
            time = datetime.now()
            fhand = open("logs/privEvent.txt", "a")
            fhand.write(
                f"Time: {time} | User: {discord} | Cmd: {cmd} | Flags: {flags}\n"
            )
            fhand.close()
            return
