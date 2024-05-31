import pytesseract
import cv2
import sqlite3
from stoke import Stoke
from ImageParser import ImageParser
import threading

class ImageReader:
    def __init__(self, filepath, gamertag, bugsId, guildId):
        self.filepath = filepath
        self.gamertag = gamertag
        self.bugsId = bugsId
        self.guildId = guildId
        self.box = None
        self.image = cv2.imread(self.filepath)
        pytesseract.pytesseract.tesseract_cmd = r'bugsvenv\Tesseract-OCR\tesseract.exe'
        self.stopEvent = threading.Event()  

    def extractText(self, roi):
        grayRoi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(grayRoi, lang='eng', config="--psm 6")

    def ReadApex(self):
        stokeIns = Stoke()
        imgParseIns = ImageParser(self.filepath, self.gamertag, self.bugsId, self.guildId)
        imgData = []
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)

        # GAMERTAG
        def processGamertag():
            if self.stopEvent.is_set():
                return
            gamertagBox = (730, 280, 180, 45)
            roi = self.image[gamertagBox[1]:gamertagBox[1]+gamertagBox[3], gamertagBox[0]:gamertagBox[0]+gamertagBox[2]]
            text = self.extractText(roi).strip()
            if text != self.gamertag:
                logIns.manualRevLog(self.filepath, game="apex")
                self.stopEvent.set()

        # PLACEMENT
        def processPlacement():
            if self.stopEvent.is_set():
                return
            topRightBox = (1355, 110, 225, 80)
            roi = self.image[topRightBox[1]:topRightBox[1]+topRightBox[3], topRightBox[0]:topRightBox[0]+topRightBox[2]]
            text = self.extractText(roi)
            placement = imgParseIns.apexPlacement(text)
            if not placement:
                logIns.manualRevLog(self.filepath, game="apex")
                self.stopEvent.set() 
            else:
                imgData.append(placement)
    
        # KILLS
        def processKills():
            if self.stopEvent.is_set():
                return
            killBox = (730, 370, 170, 65)
            roi = self.image[killBox[1]:killBox[1]+killBox[3], killBox[0]:killBox[0]+killBox[2]]
            text = self.extractText(roi)
            kills = imgParseIns.apexKills(text)
            if not kills:
                logIns.manualRevLog(self.filepath, game="apex")
                self.stopEvent.set() 
            else:
                imgData.append(kills)

        # DAMAGE
        def processDamage():
            if self.stopEvent.is_set():
                return
            dmgBox = (730, 450, 130, 65)
            roi = self.image[dmgBox[1]:dmgBox[1]+dmgBox[3], dmgBox[0]:dmgBox[0]+dmgBox[2]]
            text = self.extractText(roi)
            dmg = imgParseIns.apexDamage(text)
            if not dmg:
                logIns.manualRevLog(self.filepath, game="apex")
                self.stopEvent.set() 
            else:
                imgData.append(dmg)

        # THREADING
        threads = []
        threads.append(threading.Thread(target=processGamertag))
        threads.append(threading.Thread(target=processPlacement))
        threads.append(threading.Thread(target=processKills))
        threads.append(threading.Thread(target=processDamage))
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        if self.stopEvent.is_set():
            del self.image
            return None, "Sent to Manual Review"

        # AFTER THREADING
        if len(imgData) < 3:
            return None, "Incomplete Data"
        placementPts, killPts, dmgPts = imgData
        apexScore = placementPts + killPts + dmgPts

        if apexScore < 141:
            flag = 2
            logFlags.append(flag)
            logIns.log(channel="score", cmd="apexReader")
            return apexScore, flag
        else:
            flag = 5
            logFlags.append(flag)
            logIns.log(channel="score", cmd="apexReader")
            return None, flag

    def ReadFinals(self):
        stokeIns = Stoke()
        imgData = []
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        imgParserIns = ImageParser(self.filepath, self.gamertag, self.bugsId, self.guildId)

        # GAMERTAG 
        def processGamertag():
            if self.stopEvent.is_set():
                return
            # GAMERTAG BOXES
            pos1GtBox = (530, 330, 285, 30)
            pos2GtBox = (815, 330, 285, 30)
            pos3GtBox = (1103, 330, 285,30)
            
            # GAMERTAG ROI
            pos1GtRoi = self.image[
                pos1GtBox[1] : pos1GtBox[1] + pos1GtBox[3],
                pos1GtBox[0] : pos1GtBox[0] + pos1GtBox[2],
            ]
            pos2GtRoi = self.image[
                pos2GtBox[1] : pos2GtBox[1] + pos2GtBox[3],
                pos2GtBox[0] : pos2GtBox[0] + pos2GtBox[2],
            ]
            pos3GtRoi = self.image[
                pos3GtBox[1] : pos3GtBox[1] + pos3GtBox[3],
                pos3GtBox[0] : pos3GtBox[0] + pos3GtBox[2],
            ]

            # GAMERTAG CONVERT TO GRAYSCALE 
            gt1Text = self.extractText(pos1GtRoi)
            gt2Text = self.extractText(pos2GtRoi)
            gt3Text = self.extractText(pos3GtRoi)

            # ADD GAMERTAG DATA TO DIC
            pulledGts = {}
            pulledGts[2] = gt2Text.rstrip()
            pulledGts[3] = gt3Text.rstrip()
            pulledGts[1] = gt1Text.rstrip()
            for k, v in pulledGts.items():
                if v == self.gamertag.upper():
                    self.box = k
                    break
            if self.box:
                pass
            else:
                logIns.manualRevLog(self.filepath, game='finals')
                self.stopEvent.set()
        
        # BOX FOR PLACEMENT
        def processPlacement():
            if self.stopEvent.is_set():
                return
            placementBox = (530, 180, 860, 65)
            placementRoi = self.image[
                placementBox[1] : placementBox[1] + placementBox[3],
                placementBox[0] : placementBox[0] + placementBox[2],
            ]
            text = self.extractText(placementRoi)
            totalCashExtracted = imgParserIns.finalsPlacement(text.rstrip())
            if not totalCashExtracted:
                logIns.manualRevLog(self.filepath, game='finals')
                self.stopEvent.set()
                
            else:
                imgData.append(totalCashExtracted)


        # THREADING
        threads = []
        threads.append(threading.Thread(target=processGamertag))
        threads.append(threading.Thread(target=processPlacement))
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        if self.stopEvent.is_set():
            print("Error in Thread")
            del self.image
            return None, "Sent to Manual Review"
        
        # SCORES
        if self.box == 3:
            # POSITION 3 BOXES
            combatBox = (1103, 370, 285, 30)
            supportBox = (1103, 440, 285, 30)
            objBox = (1103, 405, 285, 30)
    
        elif self.box == 2:
            # POSITION 2 BOXES
            combatBox = (815, 370, 285, 30)
            supportBox = (815, 440, 285, 30)
            objBox = (815, 405, 285, 30)
            
        elif self.box == 1:       
            # POSITION 1 BOXES
            combatBox = (530, 370, 285, 30)
            supportBox = (530, 440, 285, 30)
            objBox = (530, 405, 285, 30)

        # MAKE BOXES
        combatRoi = self.image[combatBox[1]:combatBox[1]+combatBox[3], combatBox[0]:combatBox[0]+combatBox[2]]
        supportRoi = self.image[supportBox[1]:supportBox[1]+supportBox[3], supportBox[0]:supportBox[0]+supportBox[2]]
        objRoi = self.image[objBox[1]:objBox[1]+objBox[3], objBox[0]:objBox[0]+objBox[2]]

        # GET TEXT
        combatText = self.extractText(combatRoi)
        supportText = self.extractText(supportRoi)
        objText = self.extractText(objRoi)

        # PARSE USER INFO AND TALLY POINTS
        combatScore = imgParserIns.finalsScores(combatText.rstrip())
        supportScore = imgParserIns.finalsScores(supportText.rstrip())
        objScore = imgParserIns.finalsScores(objText.rstrip())

        if combatScore == None or supportScore == None or objScore == None:
            logIns.manualRevLog(self.filepath, game='finals')
            return None, "Sent to Manual Review"
        else:
            imgData.append(combatScore)
            imgData.append(supportScore)
            imgData.append(objScore)

        if len(imgData) == 4:
            score = round(imgData[0] + imgData[1] + imgData[2] + imgData[3])
            if score > 185:
                score = 185
            return score, 2
        else:
            logIns.manualRevLog(self.filepath, game='finals')
            return None, "Sent to Manual Review"

    def ReadXdef(self):
        stokeIns = Stoke()
        logFlags = []
        logIns = stokeIns.Log(self.bugsId, self.guildId, logFlags)
        imgParserIns = ImageParser(self.filepath, self.gamertag, self.bugsId, self.guildId)

        # SCORE BOX
        inc = 0
        val = False
        for i in range(6):
            scoreArea = (683, 282 + inc, 921, 43)
            scoreRoi = self.image[
                scoreArea[1] : scoreArea[1] + scoreArea[3],
                scoreArea[0]: scoreArea[0] + scoreArea[2],
            ]
            gray = cv2.cvtColor(scoreRoi, cv2.COLOR_BGR2GRAY)
            threshBlack = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 2
            )
            scoreText = pytesseract.image_to_string(threshBlack, lang='eng', config="--oem 3, --psm 6")
            inc += 43
            if self.gamertag in scoreText:
                val = True
                break
        if val == False:
            return "Gamertag not found in image", 3
        # PASS TO IMAGE PARSER
        score = imgParserIns.xdefScores(scoreText)
        if score:
            return score, 2
        else:
            logIns.manualRevLog(self.filepath, game='xdefiant')
            return None, "Sent to Manual Review"

    def UpdateDB(self, score, game):
        logFlags = []
        logIns = Stoke().Log(self.bugsId, self.guildId, logFlags, self.gamertag)
        # CONNECT TO DB AND UPDATE SCORE
        try:
            conn = sqlite3.connect('bugs_DB.sqlite')
            cur = conn.cursor()
            if game == "finals":
                cur.execute('UPDATE Finals_Profile SET points = ? WHERE bugs_id = ?', (score, self.bugsId))
            elif game == 'apex':
                cur.execute('UPDATE Apex_Profile SET points = ? WHERE bugs_id = ?', (score, self.bugsId))
            elif game == 'xdefiant':
                cur.execute('UPDATE XDefiant_Profile SET points = ? WHERE bugs_id = ?', (score, self.bugsId))
            conn.commit()
            logFlags.append(2)
            finalFlag = 2
        except sqlite3.Error as e:
            logFlags.append(e)
            finalFlag = 3
        except sqlite3.DataError as e:
            logFlags.append(e)
            finalFlag = 4
        except sqlite3.DatabaseError as e:
            logFlags.append(e)
            finalFlag = 4
        finally:
            conn.close()
            logIns.log(channel='serv', cmd="DBUpdate")
            return finalFlag
