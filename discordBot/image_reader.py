import pytesseract
import cv2
import re
from functions import Functions
from API_Tokens import *
from stoke import Stoke


class APEXREADER:
    def __init__(self, filepath, gamertag, bugsId, guildId):
        self.filepath = filepath
        self.gamertag = gamertag
        self.bugsId = bugsId
        self.guildId = guildId

    def ReadApex(self):
        pytesseract.pytesseract.tesseract_cmd = r"bugsvenv\Tesseract-OCR\tesseract.exe"
        stokeIns = Stoke()
        _filepath = self.filepath
        _gamertag = self.gamertag
        _bugsId = self.bugsId
        _guildId = self.guildId
        imgData = []
        logFlags = []
        logIns = stokeIns.Log(_bugsId, _guildId, logFlags, discord=None)

        img = cv2.imread(_filepath)
        ogHeight, ogWidth, _ = img.shape
        ogAspecRatio = ogWidth / ogHeight
        newHeight = int(1920 / ogAspecRatio)
        resized = cv2.resize(img, (1920, newHeight))
        cv2.imwrite(_filepath, resized)
        image = cv2.imread(_filepath)

        # BOX FOR CENTER KILLS
        center_box_width = 170
        center_box_height = 65

        center_x = 730
        center_y = 370

        center_box_kills = (center_x, center_y, center_box_width, center_box_height)

        # BOX FOR CENTER DAMAGE
        center_dmg_width = 130
        center_dmg_height = 65

        dmg_x = 730
        dmg_y = 450
        center_box_dmg = (dmg_x, dmg_y, center_dmg_width, center_dmg_height)

        # PLACEMENT
        top_right_box_width = 225
        top_right_box_height = 80

        top_right_x = 1355
        top_right_y = 110

        top_right_box = (
            top_right_x,
            top_right_y,
            top_right_box_width,
            top_right_box_height,
        )

        # GAMERTAG
        gamertag_x = 730
        gamertag_y = 280
        gamertag_width = 180
        gamertag_height = 45

        gamertag_box = (gamertag_x, gamertag_y, gamertag_width, gamertag_height)

        center_kills_roi = image[
            center_box_kills[1] : center_box_kills[1] + center_box_kills[3],
            center_box_kills[0] : center_box_kills[0] + center_box_kills[2],
        ]

        center_dmg_roi = image[
            center_box_dmg[1] : center_box_dmg[1] + center_box_dmg[3],
            center_box_dmg[0] : center_box_dmg[0] + center_box_dmg[2],
        ]

        top_right_roi = image[
            top_right_box[1] : top_right_box[1] + top_right_box[3],
            top_right_box[0] : top_right_box[0] + top_right_box[2],
        ]
        gamertag_roi = image[
            gamertag_box[1] : gamertag_box[1] + gamertag_box[3],
            gamertag_box[0] : gamertag_box[0] + gamertag_box[2],
        ]

        # Convert regions to grayscale for better OCR performance
        center_kills_gray_roi = cv2.cvtColor(center_kills_roi, cv2.COLOR_BGR2GRAY)
        center_dmg_gray_roi = cv2.cvtColor(center_dmg_roi, cv2.COLOR_BGR2GRAY)
        top_right_gray_roi = cv2.cvtColor(top_right_roi, cv2.COLOR_BGR2GRAY)
        gamertag_gray_roi = cv2.cvtColor(gamertag_roi, cv2.COLOR_BGR2GRAY)

        # DEBUG
        # cv2.imshow("centerKills", center_kills_gray_roi)
        # cv2.imshow("centerDmg", center_dmg_gray_roi)
        # cv2.imshow("topR", top_right_gray_roi)
        # cv2.imshow("gt", gamertag_gray_roi)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows

        # Apply OCR using pytesseract
        center_kills_text = pytesseract.image_to_string(
            center_kills_gray_roi, lang="eng", config="--psm 6"
        )
        center_dmg_text = pytesseract.image_to_string(
            center_dmg_gray_roi, lang="eng", config="--psm 6"
        )
        top_right_text = pytesseract.image_to_string(
            top_right_gray_roi, lang="eng", config="--psm 6"
        )
        gamertag_text = pytesseract.image_to_string(
            gamertag_gray_roi, lang="eng", config="--psm 6"
        )

        # FILTER GAMERTAG
        gt = gamertag_text.strip()
        imgData.append(gt)

        # FILTER PLACEMENT
        placePattern = r"PLACED (\d{1,2})"
        placeMatch = re.search(placePattern, top_right_text)
        placement = placeMatch.group(1)
        imgData.append(placement)

        # FILTER KILLS
        killsPattern = r"(\d+)/(\d+)/(\d+)"
        match = re.search(killsPattern, center_kills_text)
        kills = match.group(1)
        imgData.append(kills)

        # FILTER DAMAGE
        dmgPattern = r"(\d+)"
        dmgMatch = re.search(dmgPattern, center_dmg_text)
        dmg = dmgMatch.group()
        imgData.append(dmg)

        # ADD POINTS TO DATA AND SEND TO DB
        gt = imgData[0]
        matchPlacement = imgData[1]
        matchKills = imgData[2]
        matchDmg = imgData[3]
        totalPoints = []

        if gt == _gamertag:
            flag = 2
        else:
            flag = 3
        logFlags.append(flag)
        # IF FLAG IS 3 WE CANCEL THE SCRIPT AND ADD
        # THE FILEPATH TO A FILE FOR PURPLESTOKE TO MANUALLY ADD POINTS

        # PLACEMENT POINTS
        placementPoints = Functions.ApexPlacement(matchPlacement)
        totalPoints.append(placementPoints)

        # KILL POINTS
        killPoints = int(matchKills) * 5
        if killPoints > 75:
            killPoints = 75
        totalPoints.append(killPoints)

        # DAMAGE POINTS
        dmgPoints = int(matchDmg) * 0.01
        dmgPoints = round(dmgPoints)
        if dmgPoints > 40:
            dmgPoints = 40
        totalPoints.append(dmgPoints)

        # SUM POINTS TOGETHER
        score = 0
        for point in totalPoints:
            score = score + point

        # RETURN POINTS
        if score < 161:
            flag = 2
            logFlags.append(flag)
            logIns.log(_channel="serv", _cmd="apexReader")
            return score, flag
        else:
            flag = 5
            logFlags.append(flag)
            logIns.log(_channel="serv", _cmd="apexReader")
            score = None
            return score, flag


def ReadFinals(self):
    pytesseract.pytesseract.tesseract_cmd = r"bugsvenv\Tesseract-OCR\tesseract.exe"
    stokeIns = Stoke()
    _filepath = self.filepath
    _gamertag = self.gamertag
    _bugsId = self.bugsId
    _guildId = self.guildId
    imgData = []
    logFlags = []
    logIns = stokeIns.Log(_bugsId, _guildId, logFlags, discord=None)

    img = cv2.imread(_filepath)
    ogHeight, ogWidth, _ = img.shape
    ogAspecRatio = ogWidth / ogHeight
    newHeight = int(1920 / ogAspecRatio)
    resized = cv2.resize(img, (1920, newHeight))
    cv2.imwrite(_filepath, resized)
    image = cv2.imread(_filepath)
