import sqlite3
from functions import Functions
from API_Tokens import *
from requests import get
from requests.exceptions import RequestException
import datetime
from datetime import datetime
import math
from API_Tokens import TESTNET_BASE_URL, BASE_URL 
from blocks import Blocks
import piexif
from PIL import Image
from io import BytesIO

# FLAGS
# 1, METHOD ERROR
# 2, SUCCESS
# 3, LIBRARY/SQLITE ERROR
# 4, ARG ERROR
# 5, MALICIOUS INTENT
# 6, API CALL ERROR 


class Stoke:
    class bugsProfile:
        def __init__(self, discord, ethAddr):
            self.discord = discord
            self.ethAddr = ethAddr

        def hasProfile(self):
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                pullProfile = cur.execute(
                    "SELECT id FROM bugs_profile WHERE discord = ?", (self.discord,)
                )
                retProfile = pullProfile.fetchone()[0]

                if retProfile:
                    return 2
            except:
                return 1
            finally:
                conn.close()

        def create(self):
            startBlock, endBlock = Blocks.startBlock, Blocks.endBlock 
            if startBlock is not None and endBlock is not None:
                pass
            else:
                return None, flag
            url = f"{TESTNET_BASE_URL}?module=account&action=txlist&address={self.ethAddr}&startblock={startBlock}&endblock={endBlock}&page=1&offset=10&sort=desc&apikey={ETHSCAN_API_KEY}"
            try:
                req = get(url)
                req.raise_for_status()
                data = req.json()

                if data.get("status") != '1':
                    raise ValueError(f"API ERROR: {data.get('message')}")
            except RequestException as e:
                return f"Network-related error occurred: {e}", 6 
            except ValueError as e:
                return f"Network-related error occurred: {e}", 6
            except Exception as e:
                return f"Network-related error occurred: {e}", 6            
            _value = False
            _toAddr = False
            result = data["result"]
            for item in result:
                toAddr = item["to"]
                value = item["value"]
                if toAddr == bugsAddr and value == ProfileFee:
                    txHash = item["hash"]
                    _value = True
                    _toAddr = True
                    break
            if not (_value and _toAddr):
                flag = "No Transaction Found"
                return flag

            if _value and _toAddr:

                # ADD USER TO BUGS DATABASE
                try:
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    conn.execute("PRAGMA foreign_keys = ON;")
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO bugs_Profile (discord, eth_addr, hash, apex_profile, finals_profile, xdefiant_profile) VALUES (?, ?, ?, ?, ?, ?)",
                        (self.discord, self.ethAddr, txHash, 0, 0, 0),
                    )
                    conn.commit()
                    # ENTER BUGS ID INTO PLAYER PROFILE TABLES
                    pull = cur.execute(
                        "SELECT id FROM bugs_Profile WHERE discord = ?", (self.discord,)
                    )
                    ret = pull.fetchone()[0]

                    cur.execute("INSERT INTO Apex_Profile (bugs_id) VAlUES (?)", (ret,))
                    cur.execute("INSERT INTO Finals_Profile (bugs_id) VALUES(?)", (ret,))
                    cur.execute("INSERT INTO XDefiant_Profile (bugs_id) VALUES (?)", (ret, ))
                    conn.commit()
                    return 2
                
                except sqlite3.IntegrityError as e:
                    return 5
                finally:
                    conn.close()
      
        def delete(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            cur = conn.cursor()
            conn.execute("PRAGMA foreign_keys = ON;")
            roleLst = []
            try:
                # PULL GUILD ID FOR EACH PLAYER PROFILE
                try:
                    # APEX
                    pullApex = cur.execute(
                        "SELECT guild_id FROM Apex_Profile WHERE bugs_id IN(SELECT bugs_id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    apexRoleGuild = pullApex.fetchone()[0]
                    # APEX ROLE ID
                    apexRoleId = cur.execute(
                        "SELECT apex_role FROM Stoke_Guilds WHERE guild_id = ?",
                        (apexRoleGuild,),
                    )
                    roleLst.append(int(apexRoleId.fetchone()[0]))
                except:
                    roleLst.append(None)

                try:
                    # FINALS
                    pullFinals = cur.execute(
                        "SELECT guild_id FROM Finals_Profile WHERE bugs_id IN(SELECT bugs_id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    finalsRoleGuild = pullFinals.fetchone()[0]
                    # FINALS ROLE ID
                    finalsRoleId = cur.execute(
                        "SELECT finals_role FROM Stoke_Guilds WHERE guild_id = ?",
                        (finalsRoleGuild,),
                    )
                    roleLst.append(int(finalsRoleId.fetchone()[0]))
                except:
                    roleLst.append(None)
                cur.execute("DELETE FROM bugs_Profile WHERE discord = ?", (self.discord,))
                conn.commit()

                try:
                    # XDEFIANT
                    pullXdef = cur.execute(
                        "SELECT guild_id FROM XDefiant_Profile WHERE bugs_id IN(SELECT bugs_id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    xdefRoleGuild = pullXdef.fetchone()[0]
                    # FINALS ROLE ID
                    xdefRoleId = cur.execute(
                        "SELECT xdefiant_role FROM Stoke_Guilds WHERE guild_id = ?",
                        (xdefRoleGuild,),
                    )
                    roleLst.append(int(xdefRoleId.fetchone()[0]))
                except:
                    roleLst.append(None)
                cur.execute("DELETE FROM bugs_Profile WHERE discord = ?", (self.discord,))
                conn.commit()

                return 2, roleLst

            except:
                return 3, None
            finally: 
                conn.close()

        def retrieve(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            try:
                profile = cur.execute(
                    "SELECT eth_addr FROM bugs_Profile WHERE discord = ?", (self.discord,)
                )
                retProfile = profile.fetchone()[0]
                return 2, retProfile

            except:
                return 3
            finally:
                conn.close()

        def update(self):
            startBlock, endBlock = Blocks.startBlock, Blocks.endBlock
            if startBlock is not None and endBlock is not None:
                pass
            else:
                return None, 6 
            url = f"https://api-sepolia.etherscan.io/api?module=account&action=txlist&address={self.ethAddr}&startblock={startBlock}&endblock={endBlock}&offset=10&sort=desc&apikey={ETHSCAN_API_KEY}"
            try:
                req = get(url)
                req.raise_for_status()
                data = req.json()
                if data.get("status") != '1':
                    raise ValueError(f"API ERROR: {data.get('message')}")
            except RequestException as e:
                info = f"Network-related error occurred: {e}"
                return info, 6
            except ValueError as e:
                info = f"Data processing error occurred: {e}"
                return info, 6
            except Exception as e:
                info = f"An unexpected error occurred: {e}"
                return info, 6

            _value = False
            _toAddr = False
            result = req["result"]
            for item in result:
                toAddr = item["to"]
                value = item["value"]
                if toAddr == bugsAddr and value == updateProfileFee:
                    txHash = item["hash"]
                    _value = True
                    _toAddr = True
                    break
            if not (_value and _toAddr):
                flag = "No Transaction Found"
                return flag

            if _value and _toAddr:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()

                # UPDATE USERS ADDR
                try:
                    cur.execute(
                        "UPDATE bugs_Profile SET eth_addr = ?, hash = ? WHERE discord = ?",
                        (
                            self.ethAddr,
                            txHash,
                            self.discord,
                        ),
                    )
                    conn.commit()
                    return 2
                except sqlite3.IntegrityError as e:
                    return 5
                finally: conn.close()


        def bugsId(self):
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()

                pull = cur.execute(
                    "SELECT id FROM bugs_Profile WHERE discord = ?", (self.discord,)
                )
                ret = pull.fetchone()[0]
                if ret:
                    return 2, ret
                else:
                    return 4, None
            except:
                return 3, None

            finally: conn.close()

    class Guilds:
        def __init__(self, find, guildId):
            self.find = find
            self.guildId = guildId

        # METHOD TO PULL CHANNEL IDS
        # ID'S RETURN AS AN INT
        def pullChannel(self):
            # CHECK IF WE ARE DEALING WITH A HOSTED COMMUNITY
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            try:     
                # PULLPLAYER PROFILE CHANNEL BASED ON GUILD
                if self.find == "buggin":
                    pull = cur.execute(
                        "SELECT bugs_channel FROM Stoke_Guilds WHERE guild = ?",
                        (self.guildId,),
                    )
                    ret = int(pull.fetchone()[0])
                    return 2, ret
                    
                # PULL SC SUBMISSION CHANNEL BASED ON GUILD
                elif self.find == "scSubmission":
                    pull = cur.execute(
                        "SELECT sc_submission FROM Stoke_Guilds WHERE guild = ?", (self.guildId,)
                    )
                    ret = int(pull.fetchone()[0])
                    return 2, ret
            except:
                return 3, None
            finally:
                conn.close()

        # METHOD TO PULL SERVER/COMMUNITY NAME
        # NAME RETURNS AS AN STR
        def pullName(self):
            # PULL GUILD NAME
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT guild_name FROM Stoke_Guilds WHERE guild = ?",
                    (self.guildId,),
                )
                ret = pull.fetchone()[0]
                if ret:
                    return ret
                else:
                    return 4
            
            except:
                return 3
            finally:
                conn.close()

        # METHOD TO PULL SERVER/COMMUNITY IDS
        # ID'S RETURN AS AN INT
        def pullId(self):
            # PULL GUILD ID
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT guild_id FROM Stoke_Guilds WHERE guild = ?",
                    (self.guildId,),
                )
                ret = pull.fetchone()[0]
                if ret:
                    ret = int(ret)
                    return ret
                else:
                    return None
            except:
                return None
            finally:
                conn.close()

        # METHOD TO PULL SERVER/COMMUNITY SCORE
        # SCORE RETURNS AS AN INT
        def pullScore(self):
            # PULL COMMUNITY SCORE
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT community_score FROM Stoke_Guilds WHERE guild = ?",
                    (self.guildId,),
                )
                ret = pull.fetchone()[0]
                if ret:
                    return int(ret)
                else:
                    return 4
            except:
                return 3
            finally:
                conn.close()

        # METHOD TO PULL DISCORD ROLE
        # ROLE RETURNS AS AN INT
        def pullRole(self, find):
            # FIND APEX ROLE
            if find == "apex":
                try:
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    conn.execute("PRAGMA foreign_keys = ON;")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT apex_role FROM Stoke_Guilds WHERE guild = ?",
                        (self.guildId,),
                    )
                    ret = pull.fetchone()[0]
                    if ret:
                        ret = int(ret)
                        return 2, ret
                    else:
                        return 4, None
                except:
                    return 3, None
                finally:
                    conn.close()

            #FIND FINALS ROLE
            elif find == "finals":
                try:
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    conn.execute("PRAGMA foreign_keys = ON;")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT finals_role FROM Stoke_Guilds WHERE guild = ?",
                        (self.guildId,),
                    )
                    ret = pull.fetchone()[0]
                    if ret:
                        ret = int(ret)
                        return 2, ret
                    else:
                        return 4, None
                except:
                    return 3
                finally:
                    conn.close()

            #FIND XDEFIANT  ROLE
            elif find == "xdefiant":
                try:
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    conn.execute("PRAGMA foreign_keys = ON;")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT xdefiant_role FROM Stoke_Guilds WHERE guild = ?",
                        (self.guildId,),
                    )
                    ret = pull.fetchone()[0]
                    if ret:
                        ret = int(ret)
                        return 2, ret
                    else:
                        return 4, None
                except:
                    return 3
                finally:
                    conn.close()

            # FIND COMPETITOR ROLE
            elif find == "competitor":
                try:
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    conn.execute("PRAGMA foreign_keys = ON;")
                    cur = conn.cursor()
                    pull = cur.execute(
                        "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                        (self.guildId,),
                    )
                    ret = pull.fetchone()[0]
                    if ret:
                        return 2, int(ret)
                    else:
                        return 4, None
                except:
                    return 3
                finally:
                    conn.close()

            else:
                return 4, None

    class PlayerProfile:
        def __init__(self, discord, guildId, type, hosted):
            self.discord = discord
            self.guildId = guildId
            self.type = type
            self.hosted = hosted

        def create(self, gamertag):
            # CONNECT TO DB AND PULL BUGS ID
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            pull = cur.execute(
                "SELECT id FROM bugs_Profile WHERE discord = ?", (self.discord,)
            )
            ret = pull.fetchone()[0]

            if ret:
                # ADD INFO TO DB
                try:
                    # FIND GUILD ID FROM STOKE
                    pullGuild = cur.execute(
                        "SELECT guild_id FROM Stoke_Guilds WHERE guild = ?", (self.guildId,)
                    )
                    retGuild =int(pullGuild.fetchone()[0])

                    # INSERT INFO INTO PLAYER PROFILE

                    # APEX
                    if self.type == "apex":
                        try:
                            if not self.hosted:
                                cur.execute(
                                    "UPDATE Apex_Profile SET gamertag = ?, guild_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                    (gamertag, retGuild, self.discord),
                                )
                            else:
                                try:
                                    pullHost = cur.execute('SELECT id FROM Hosted_Comm WHERE name = ?', (self.hosted,))
                                    hostedId = pullHost.fetchone()[0]
                                    cur.execute(
                                    "UPDATE Apex_Profile SET gamertag = ?, guild_id = ?, hosted_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                    (gamertag, retGuild, hostedId, self.discord,),
                                    )
                                except:
                                    return "Hosted Community Name Not Found"
                                
                            # SET FLAG FOR APEX PROFILE IN BUGS PROFILE TABLE
                            cur.execute(
                                "UPDATE bugs_Profile SET apex_profile = ? WHERE discord = ?",
                                (1, self.discord),
                            )
                            conn.commit()
                            return 2
                        except sqlite3.IntegrityError as e:
                            return 5
                        except sqlite3.Error as e:
                            return e
                        except Exception as e:
                            return e
                    
                    # THE FINALS
                    elif self.type == "finals":
                        try:
                            if not self.hosted:
                                cur.execute(
                                    "UPDATE Finals_Profile SET gamertag = ?, guild_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                    (gamertag, retGuild, self.discord,),
                                )
                            else:
                                try:
                                    pullHost = cur.execute('SELECT id FROM Hosted_Comm WHERE name = ?', (self.hosted,))
                                    hostedId = pullHost.fetchone()[0]
                                    cur.execute(
                                    "UPDATE Finals_Profile SET gamertag = ?, guild_id = ?, hosted_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                    (gamertag, retGuild, hostedId, self.discord,),
                                    )
                                except:
                                    return "Hosted Community Name Not Found"
                                
                            # SET FLAG FOR FINALS PROFILE IN BUGS PROFILE TABLE
                            cur.execute(
                                "UPDATE bugs_Profile SET finals_profile = ? WHERE discord = ?",
                                (1, self.discord),
                            )
                            conn.commit()
                            return 2
                        except sqlite3.IntegrityError as e:
                            return 5
                        except sqlite3.Error as e:
                            return e
                        except Exception as e:
                            return e
                        
                    # XDEFIANT
                    elif self.type == "xdefiant":
                        try:
                            if not self.hosted:
                                cur.execute(
                                    "UPDATE XDefiant_Profile SET gamertag = ?, guild_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                    (gamertag, retGuild, self.discord),
                                )
                            else:
                                try:
                                    pullHost = cur.execute('SELECT id FROM Hosted_Comm WHERE name = ?', (self.hosted,))
                                    hostedId = pullHost.fetchone()[0]
                                    cur.execute(
                                    "UPDATE XDefiant_Profile SET gamertag = ?, guild_id = ?, hosted_id = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                                    (gamertag, retGuild, hostedId, self.discord,),
                                    )
                                except:
                                    return "Hosted Community Name Not Found"
                                
                            # SET FLAG FOR FINALS PROFILE IN BUGS PROFILE TABLE
                            cur.execute(
                                "UPDATE bugs_Profile SET xdefiant_profile = ? WHERE discord = ?",
                                (1, self.discord),
                            )
                            conn.commit()
                            return 2
                        except sqlite3.IntegrityError as e:
                            return 5
                        except sqlite3.Error as e:
                            return e
                        except Exception as e:
                            return e
                    else:
                        return 4
                except:
                    return 3
                finally:
                    conn.close()
            else:
                conn.close()
                return 3

        def delete(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            if self.type == "apex":
                try:
                    cur.execute(
                        "UPDATE Apex_Profile SET gamertag = NULL, guild_id = NULL, hosted_id = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    cur.execute(
                        "UPDATE bugs_Profile SET apex_profile = 0 WHERE discord = ?",
                        (self.discord,),
                    )
                    conn.commit()
                    return 2
                except:
                    return 3
                finally:
                    conn.close()

            elif self.type == "finals":
                try:
                    cur.execute(
                        "UPDATE Finals_Profile SET gamertag = NULL, guild_id = NULL, hosted_id = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    cur.execute(
                        "UPDATE bugs_Profile SET finals_profile = 0 WHERE discord = ?",
                        (self.discord,),
                    )
                    conn.commit()
                    return 2
                except:
                    return 3
                finally:
                    conn.close()

            elif self.type == "xdefiant":
                try:
                    cur.execute(
                        "UPDATE XDefiant_Profile SET gamertag = NULL, guild_id = NULL, hosted_id = NULL WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    cur.execute(
                        "UPDATE bugs_Profile SET xdefiant_profile = 0 WHERE discord = ?",
                        (self.discord,),
                    )
                    conn.commit()
                    return 2
                except:
                    return 3
                finally:
                    conn.close()
            else:
                return 4

        def retrieve(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            if self.type == "apex":
                try:
                    pull = cur.execute(
                        "SELECT gamertag FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    info = pull.fetchone()[0]
                    return 2, info
                except:
                    return 3, None
                finally:
                    conn.close()

            elif self.type == "finals":
                try:
                    pull = cur.execute(
                        "SELECT gamertag FROM Finals_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    info = pull.fetchone()[0]
                    return 2, info
                except:
                    return 3, None
                finally:
                    conn.close()

            elif self.type == "xdefiant":
                try:
                    pull = cur.execute(
                        "SELECT gamertag FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    info = pull.fetchone()[0]
                    return 2, info
                except:
                    return 3, None
                finally:
                    conn.close()
            else:
                conn.close()
                return 4, None

        def pullPoints(self):
            try:
                if self.type == "apex":
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    conn.execute("PRAGMA foreign_keys = ON;")
                    cur = conn.cursor()
                    pullPts = cur.execute(
                        "SELECT points FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    pts = pullPts.fetchone()
                    if pts[0] == None:
                        pts = 0
                    return 2, pts
                
                elif self.type == "finals":
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()
                    pullPts = cur.execute(
                        "SELECT points FROM Finals_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    pts = pullPts.fetchone()
                    if pts[0] == None:
                        pts = 0
                    return 2, pts
                elif self.type == "xdefiant":
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()
                    pullPts = cur.execute(
                        "SELECT points FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    pts = pullPts.fetchone()
                    if pts[0] == None:
                        pts = 0
                    return 2, pts
            except:
                return 4, None
            finally: conn.close()

        def ppGuildId(self):
            try:
                conn = sqlite3.connect('bugs_DB.sqlite')
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                if self.type == 'apex':
                    pull = cur.execute('SELECT guild_id from Apex_Profile WHERE bugs_id IN (SELECT id FROM bugs_Profile WHERE discord = ?)', (self.discord, ))
                elif self.type == "finals":
                    pull = cur.execute('SELECT guild_id from Finals_Profile WHERE bugs_id IN (SELECT id FROM bugs_Profile WHERE discord = ?)', (self.discord, ))
                elif self.type == "xdefiant":
                    pull = cur.execute('SELECT guild_id from XDefiant_Profile WHERE bugs_id IN (SELECT id FROM bugs_Profile WHERE discord = ?)', (self.discord, ))
                ret = pull.fetchone()[0]
                if ret:
                    return ret
                else:
                    return None
            except:
                return None
            finally: conn.close()

        def pullHostedId(self):
            conn = sqlite3.connect('bugs_DB.sqlite')
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON;')
            try:
                if self.type == 'apex':
                    pull = cur.execute("SELECT hosted_id FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)", (self.discord, ),)
                    ret = pull.fetchone()[0]
                    if ret:
                        return ret
                elif self.type == 'finals':
                    pull = cur.execute('SELECT hosted_id FROM Finals_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)', (self.discord, ),)
                    ret = pull.fetchone()[0]
                    if ret:
                        return ret
                elif self.type == 'xdefiant':
                    pull = cur.execute('SELECT hosted_id FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)', (self.discord, ),)
                    ret = pull.fetchone()[0]
                    if ret:
                        return ret
            except:
                return None
    
    class Event:
        def __init__(self, discord, game):
            self.discord = discord
            self.game = game

        # CHECKS EVENT/SUBMISSION FLAG
        def isOn(self):
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT submission_flag FROM Events WHERE game = ?", (self.game,)
                )
                ret = pull.fetchone()[0]
                if ret:
                    return 2, ret
                else:
                    return 4, ret
            except:
                return 3, None 
            finally:
                conn.close()

        def submissionDelete(self, bugsId):
            try:
                # APEX
                if self.game == "apex":
                    # PULL BUGS DB
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()

                    pullFP = cur.execute(
                        "SELECT submission FROM Apex_Profile WHERE bugs_id = ?",
                        (bugsId,),
                    )
                    retFP = pullFP.fetchone()[0]

                    if retFP: 
                        cur.execute(
                            "UPDATE Apex_Profile SET submission = NULL WHERE bugs_id = ?",
                            (bugsId,),
                        )
                        conn.commit()
                        return 2
                    else:
                        return 3
                
                # FINALS
                elif self.game == "finals":
                    # PULL BUGS DB
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()

                    pullFP = cur.execute(
                        "SELECT submission FROM Finals_Profile WHERE bugs_id = ?",
                        (bugsId,),
                    )
                    retFP = pullFP.fetchone()[0]

                    if retFP:
                        cur.execute(
                            "UPDATE Finals_Profile SET submission = NULL WHERE bugs_id = ?",
                            (bugsId,),
                        )
                        conn.commit()
                        return 2
                    else:
                        return 3
                # XDEFIANT
                elif self.game == "xdefiant":
                    # PULL BUGS DB
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()

                    pullFP = cur.execute(
                        "SELECT submission FROM XDefiant_Profile WHERE bugs_id = ?",
                        (bugsId,),
                    )
                    retFP = pullFP.fetchone()[0]

                    if retFP:
                        cur.execute(
                            "UPDATE XDefiant_Profile SET submission = NULL WHERE bugs_id = ?",
                            (bugsId,),
                        )
                        conn.commit()
                        return 2
                    else:
                        return 3
            except:
                return 4
            finally: conn.close()

        def checkSubmission(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            try:
                if self.game == "apex":
                    pull = cur.execute(
                        "SELECT submission FROM Apex_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    ret = pull.fetchone()[0]
                
                    if ret:
                        return 2, ret
                    else:
                        return 3, None
            
                elif self.game == "finals":
                    pull = cur.execute(
                        "SELECT submission FROM Finals_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    ret = pull.fetchone()[0]
                
                    if ret:
                        return 2, ret
                    else:
                        return 3, None
                    
                elif self.game == "xdefiant":
                    pull = cur.execute(
                        "SELECT submission FROM XDefiant_Profile WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (self.discord,),
                    )
                    ret = pull.fetchone()[0]
                
                    if ret:
                        return 2, ret
                    else:
                        return 3, None
            except:
                return 4
            finally: conn.close()

        # SETS EVENT/SUBMISSION FLAG
        def eventFlag(self, flag):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE Events SET submission_flag = ? WHERE game = ?",
                    (
                        flag,
                        self.game,
                    ),
                )
                conn.commit()
                return 2
            except:
                return 3
            finally: conn.close()

        # SETS THE FLAG
        def pmntFlag(self, flag):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE Events SET pmnt_flag = ? WHERE game = ?",
                    (
                        flag,
                        self.game,
                    ),
                )
                conn.commit()
                return 2
            except:
                return 3
            finally: conn.close()

        # CHECKS THE FLAG
        def pmntOn(self):
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                pull = cur.execute(
                    "SELECT pmnt_flag FROM Events WHERE game = ?", (self.game,)
                )
                ret = pull.fetchone()[0]
                return 2, ret
            except:
                return 3, None

        def addPoints(self, points):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute('PRAGMA foreign_keys = ON;')
            cur = conn.cursor()
            try:
                if self.game == "apex":
                    cur.execute(
                        "UPDATE Apex_Profile SET points = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (points, self.discord),
                    )
                    conn.commit()
                    return 2
                elif self.game == "finals":
                    cur.execute(
                        "UPDATE Finals_Profile SET points = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (points, self.discord),
                    )
                    conn.commit()
                    return 2
                elif self.game == "xdefiant":
                    cur.execute(
                        "UPDATE XDefiant_Profile SET points = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                        (points, self.discord),
                    )
                    conn.commit()
                    return 2
            except:
                return 3

            finally: conn.close()

    class PrivateEvent:
        def __init__(self, event):
            self.event = event

        def competitorList(self):
            try:
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()

                pullCompetitors = cur.execute("SELECT bugs_id FROM Private_Event")
                retCompetitors = pullCompetitors.fetchall()
                if retCompetitors:
                    return 2, retCompetitors
            except:
                return 3, None
            finally: conn.close()

        def privEventDraw(self):
            try:
                competitors = {}
                conn = sqlite3.connect("bugs_DB.sqlite")
                conn.execute("PRAGMA foreign_keys = ON;")
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
                    if self.event == "apex":
                        pullWinner = cur.execute(
                            "SELECT gamertag FROM Apex_Profile WHERE bugs_id = ?",
                            (win,),
                        )
                        retWinner = pullWinner.fetchone()[0]
                    elif self.event == "finals":
                        pullWinner = cur.execute(
                            "SELECT gamertag FROM Finals_Profile WHERE bugs_id = ?",
                            (win,),
                        )
                        retWinner = pullWinner.fetchone()[0]
                    elif self.event == "xdefiant":
                        pullWinner = cur.execute(
                            "SELECT gamertag FROM XDefiant_Profile WHERE bugs_id = ?",
                            (win,),
                        )
                        retWinner = pullWinner.fetchone()[0]
                    winString += f"{retWinner}\n"

                return 2, winString
            except:
                return 3, None
            finally: conn.close()

    class PaymentVerify:
        def __init__(self, discord, guildId, event):
            self.discord = discord
            self.guildId = guildId
            self.event = event

        def pullAddr(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            try:
                pull = cur.execute(
                    "SELECT eth_addr FROM bugs_Profile WHERE discord = ?", (self.discord,)
                )
                ret = pull.fetchone()[0]
                return ret
            except:
                return None
            finally: conn.close()

        def checkPayment(self, addr):
            if self.event == "apex":
                wallet = bugsApexAddr
            elif self.event == 'finals':
                wallet = bugsFinalsAddr
            elif self.event == 'xdefiant':
                wallet = bugsXdefAddr
            else:
                return 4, None

            startBlock, endBlock = Blocks.startBlock, Blocks.endBlock
            if startBlock is not None and endBlock is not None:
                pass
            else:
                return 6, None
 
            EtherscanUrl = f"{TESTNET_BASE_URL}?module=account&action=txlist&address={addr}&startblock={startBlock}&endblock={endBlock}&page=1&offset=10&sort=dec&apikey={ETHSCAN_API_KEY}"
            try:
                req = get(EtherscanUrl)
                req.raise_for_status()
                data = req.json()
                if data.get("status") != '1':
                    raise ValueError(f"API ERROR: {data.get('message')}")
            except RequestException as e:
                return f"Network-related error occurred: {e}", 6
            except ValueError as e:
                return f"Data processing error occurred: {e}", 6
            except Exception as e:
                return f"An unexpected error occurred: {e}", 6
            _value = False
            _toAddr = False
            result = data["result"]
            for item in result:
                toAddr = item["to"]
                value = item["value"]
                if toAddr == wallet and value == eventEntryCost:
                    txHash = item["hash"]
                    _value = True
                    _toAddr = True
                    break
            if not (_value and _toAddr):
                msg = f"Sorry mate looks like you haven't sent the Entry Cost of 0.005 ETH sent to this wallet {bugsApexAddr} "
                return 3, msg
            if _value and _toAddr:
                try:
                    # APEX
                    if self.event == "apex":
                        # UPDATE BUGS PROFILE AND ASSIGN COMPETITOR ROLE
                        conn = sqlite3.connect("bugs_DB.sqlite")
                        conn.execute("PRAGMA foreign_keys = ON;")
                        cur = conn.cursor()
                        pullRole = cur.execute(
                            "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                            (self.guildId,),
                        )
                        retRole = pullRole.fetchone()[0]
                        competitorRole = int(retRole)

                        cur.execute(
                            "UPDATE Apex_Profile SET elligible = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                            (
                                txHash,
                                self.discord,
                            ),
                        )
                        conn.commit()
                        return 2, competitorRole
                    # FINALS
                    elif self.event == "finals":
                        # UPDATE BUGS PROFILE AND ASSIGN COMPETITOR ROLE
                        conn = sqlite3.connect("bugs_DB.sqlite")
                        conn.execute("PRAGMA foreign_keys = ON;")
                        cur = conn.cursor()
                        pullRole = cur.execute(
                            "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                            (self.guildId,),
                        )
                        retRole = pullRole.fetchone()[0]
                        competitorRole = int(retRole)

                        cur.execute(
                            "UPDATE Finals_Profile SET elligible = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                            (
                                txHash,
                                self.discord,
                            ),
                        )
                        conn.commit()
                        return 2, competitorRole
                    
                    # XDEFIANT
                    elif self.event == "xdefiant":
                        # UPDATE BUGS PROFILE AND ASSIGN COMPETITOR ROLE
                        conn = sqlite3.connect("bugs_DB.sqlite")
                        conn.execute("PRAGMA foreign_keys = ON;")
                        cur = conn.cursor()
                        pullRole = cur.execute(
                            "SELECT competitor_role FROM Stoke_Guilds WHERE guild = ?",
                            (self.guildId,),
                        )
                        retRole = pullRole.fetchone()[0]
                        competitorRole = int(retRole)

                        cur.execute(
                            "UPDATE XDefiant_Profile SET elligible = ? WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",
                            (
                                txHash,
                                self.discord,
                            ),
                        )
                        conn.commit()
                        return 2, competitorRole
                except:
                    return 4, "Transaction not found"
                finally: conn.close()

    class Wipe:
        def __init__(self, event):
            self.event = event

        def wipeEvent(self):
            conn = sqlite3.connect("bugs_DB.sqlite")
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            try:
                # APEX
                if self.event == "apex":
                    cur.execute(
                        "UPDATE Apex_Profile SET elligible = NULL, submission = NULL, points = NULL"
                    )
                    conn.commit()
                    return 2

                # FINALS
                elif self.event == "finals":
                    cur.execute(
                        "UPDATE Finals_Profile SET elligible = NULL, submission = NULL, points = NULL"
                    )
                    conn.commit()
                    return 2
                
                # XDEFIANT
                elif self.event == "xdefiant":
                    cur.execute(
                        "UPDATE XDefiant_Profile SET elligible = NULL, submission = NULL, points = NULL"
                    )
                    conn.commit()
                    return 2
            except:
                return 3
            finally: conn.close()

    class Wallet:
        def pullBal(self):
            try:
                bals = []
                pullTreasury = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullTreasury = int(pullTreasury) / ETH_VALUE
                bals.append(pullTreasury)
                # APEX
                pullApex = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsApexAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullApex = int(pullApex) / ETH_VALUE
                bals.append(pullApex)
                # FINALS
                pullFinals = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsFinalsAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullFinals = int(pullFinals) / ETH_VALUE
                bals.append(pullFinals)
                # XDEFIANT
                pullXdef = get(
                    f"{BASE_URL}?module=account&action=balance&address={bugsXdefAddr}&tag=latest&apikey={ETHSCAN_API_KEY}"
                ).json()["result"]
                pullXdef = int(pullXdef) / ETH_VALUE
                bals.append(pullXdef)
                return 2, bals
            except:
                return 3, None

    class Log:
        def __init__(self, bugsId, guildId, flags, discord=None):
            self.bugsId = bugsId
            self.guildId = guildId
            self.flags = flags
            self.discord = discord

        def log(self, channel, cmd):
            try:
                time = datetime.now()
                timestamp = time.strftime("%m/%d/%Y %H:%M")
                if channel == "buggin":
                    fhand = open("logs/buggin.txt", "a")
                    fhand.write(
                        f"Time: {timestamp} | Guild: {self.guildId} | User: {self.bugsId} | Cmd: {cmd} | Flags: {self.flags}\n"
                    )
                elif channel == "scSubmission":
                    fhand = open("logs/scSubmission.txt", "a")
                    fhand.write(
                        f"Time: {timestamp} | Guild: {self.guildId} | User: {self.bugsId} | Cmd: {cmd} | Flags: {self.flags}\n"
                    )
                elif channel == "Admin":
                    fhand = open("logs/Admin.txt", "a")
                    fhand.write(
                        f"Time: {timestamp} | Guild: {self.guildId} | User: {self.bugsId} | Cmd: {cmd} | Flags: {self.flags}\n"
                    )
                elif channel == "other":
                    fhand = open("logs/other.txt", "a")
                    fhand.write(
                        f"Time: {timestamp} | Guild: {self.guildId} | User: {self.bugsId} | Cmd: {cmd} | Flags: {self.flags}\n"
                    )
                elif channel == "score":
                    fhand = open("logs/score.txt", "a")
                    fhand.write(
                        f"Time: {timestamp} | Guild: {self.guildId} | User: {self.bugsId} | Cmd: {cmd} | Flags: {self.flags}\n"
                    )
                elif channel == "serv":
                    fhand = open("logs/server.txt", "a")
                    fhand.write(
                        f"Time: {timestamp} | Guild: {self.guildId} | User: {self.bugsId} | Cmd: {cmd} | Flags: {self.flags}\n"
                    )
            except:
                pass
            finally: fhand.close()

        def setupLog(self, cmd, guildName):
            time = datetime.now()
            timestamp = time.strftime("%m/%d/%Y %H:%M")
            fhand = open("logs/backend.txt", "a")
            fhand.write(
                f"Time: {timestamp} | Guild: {guildName} | Cmd: {cmd} | Flags: {self.flags}\n"
            )
            fhand.close()
            return

        def leaveLog(self, guildName, cmd):
            time = datetime.now()
            timestamp = time.strftime("%m/%d/%Y %H:%M")
            fhand = open("logs/backend.txt", "a")
            fhand.write(
                f"Time: {timestamp} | Guild: {guildName} | Cmd: {cmd} | Flags: {self.flags}\n"
            )
            fhand.close()
            return

        def wipeLog(self, cmd):
            time = datetime.now()
            timestamp = time.strftime("%m/%d/%Y %H:%M")
            fhand = open("logs/backend.txt", "a")
            fhand.write(
                f"Time: {timestamp} | Guild: {self.guildId} | User: {self.discord} | Cmd: {cmd} | Flags: {self.flags}\n"
            )
            fhand.close()
            return

        def manualRevLog(self, filepath, game):
            time = datetime.now()
            timestamp = time.strftime("%m/%d/%Y %H:%M")
            with open(f'manualRev/{game}Reader.txt', 'a') as f:
                f.write(f"Time: {timestamp} | bugsId: {self.bugsId} | guildId: {self.guildId} | file: {filepath}| Flags: {self.flags}\n")
            return

    class Security:
        def __init__(self, discord, bugsId, filepath):
            self.discord = discord
            self.bugsId = bugsId
            self.filepath = filepath

        def checkImage(self):
            try:
                response = get(self.filepath) 
                img = Image.open(BytesIO(response.content))
                exifData = piexif.load(img.info['exif'])
                software = exifData.get('0th', {}).get(piexif.ImageIFD.Software)
                if software:
                    return software.decode('utf-8'), 5
                else:
                    return None, 2
                
            except KeyError:
                return "No EXIF metadata available", 3
            except Exception as e:
                return e, 4
