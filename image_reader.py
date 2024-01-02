import pytesseract
import cv2
import re
import sqlite3
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
        pytesseract.pytesseract.tesseract_cmd = r'bugsvenv\Tesseract-OCR\tesseract.exe'  
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

        #DEBUG
        #cv2.imshow("centerKills", center_kills_gray_roi)
        #cv2.imshow("centerDmg", center_dmg_gray_roi)
        #cv2.imshow("topR", top_right_gray_roi)
        #cv2.imshow("gt", gamertag_gray_roi)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows

        # Apply OCR using pytesseract
        center_kills_text = pytesseract.image_to_string(center_kills_gray_roi, lang='eng', config='--psm 6')
        center_dmg_text = pytesseract.image_to_string(center_dmg_gray_roi, lang='eng', config='--psm 6')
        top_right_text = pytesseract.image_to_string(top_right_gray_roi, lang='eng', config='--psm 6')
        gamertag_text = pytesseract.image_to_string(gamertag_gray_roi, lang='eng', config='--psm 6')

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
        pytesseract.pytesseract.tesseract_cmd = r'bugsvenv\Tesseract-OCR\tesseract.exe'  
        stokeIns = Stoke()
        _filepath = self.filepath
        _gamertag = self.gamertag
        _bugsId = self.bugsId
        _guildId = self.guildId
        imgData = []
        logFlags = []
        logIns = stokeIns.Log(_bugsId, _guildId, logFlags, discord=None)
        pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    
        imgData = []
    
        img = cv2.imread(_filepath)
        ogHeight, ogWidth, _ = img.shape
        ogAspecRatio = ogWidth / ogHeight
        newHeight = int(1920 / ogAspecRatio)
        resized = cv2.resize(img, (1920, newHeight))
        cv2.imwrite(_filepath, resized)
        image = cv2.imread(_filepath)
    
        # BOX FOR PLACEMENT
        placement_box_width = 860
        placement_box_height = 65
        placement_x = 530
        placement_y = 180
        placement_box = (
            placement_x,
            placement_y,
            placement_box_width,
            placement_box_height,
        )
    
        # BOX FOR POSITION 1
        # DEFAULT WIDTHS AND HEIGHTS
        pos1_box_width = 285
        pos1_x = 530
        # POSITION 1 GAMERTAG BOX
        gt_box_height = 30
        gt_y = 330
        pos1_gt_box = (pos1_x, gt_y, pos1_box_width, gt_box_height)
        # POSITION 1 COMBAT BOX
        cmbt_height = 35
        cmbt_y = 370
        pos1_cmbt_box = (pos1_x, cmbt_y, pos1_box_width, cmbt_height)
        # POSITION 1 OBJECTIVE BOX
        obj_height = 35
        obj_y = 405
        pos1_obj_box = (pos1_x, obj_y, pos1_box_width, obj_height)
        # POSITION 1 SUPPORT BOX
        supp_height = 35
        supp_y = 440
        pos1_supp_box = (pos1_x, supp_y, pos1_box_width, supp_height)
    
        # BOX FOR POSITION 2
        # DEFAULT WIDHTS AND HEIGHTS
        pos2_box_width = 288
        pos2_x = 815
        # POSITION 2 GAMERTAG BOX
        pos2_gt_box = (pos2_x, gt_y, pos2_box_width, gt_box_height)
        # POSITION 2 COMBAT BOX
        pos2_cmbt_box = (pos2_x, cmbt_y, pos2_box_width, cmbt_height)
        # POSITION 2 OBJECTIVE BOX
        pos2_obj_box = (pos2_x, obj_y, pos2_box_width, obj_height)
        # POSITION 2 SUPPORT BOX
        pos2_supp_box = (pos2_x, supp_y, pos2_box_width, supp_height)
    
        # BOX FOR POSITION 3
        # DEFAULT WIDTHS AND HEIGHTS
        pos3_box_width = 283
        pos3_x = 1103
        # POSITION 3 GAMERTAG BOX
        pos3_gt_box = (pos3_x, gt_y, pos3_box_width, gt_box_height)
        # POSITION 3 COMBAT BOX
        pos3_cmbt_box = (pos3_x, cmbt_y, pos3_box_width, cmbt_height)
        # POSITION 3 OBJECTIVE BOX
        pos3_obj_box = (pos3_x, obj_y, pos3_x, obj_height)
        # POSITION 3 SUPPORT BOX
        pos3_supp_box = (pos3_x, supp_y, pos3_box_width, supp_height)
    
        placement_roi = image[
            placement_box[1] : placement_box[1] + placement_box[3],
            placement_box[0] : placement_box[0] + placement_box[2],
        ]
        # POSITION 1 ROI
        pos1_gt_roi = image[
            pos1_gt_box[1] : pos1_gt_box[1] + pos1_gt_box[3],
            pos1_gt_box[0] : pos1_gt_box[0] + pos1_gt_box[2],
        ]
    
        pos1_cmbt_roi = image[
            pos1_cmbt_box[1] : pos1_cmbt_box[1] + pos1_cmbt_box[3],
            pos1_cmbt_box[0] : pos1_cmbt_box[0] + pos1_cmbt_box[2],
        ]
    
        pos1_supp_roi = image[
            pos1_supp_box[1] : pos1_supp_box[1] + pos1_supp_box[3],
            pos1_supp_box[0] : pos1_supp_box[0] + pos1_supp_box[2],
        ]
    
        pos1_obj_roi = image[
            pos1_obj_box[1] : pos1_obj_box[1] + pos1_obj_box[3],
            pos1_obj_box[0] : pos1_obj_box[0] + pos1_obj_box[2],
        ]
        # POSITION 2 ROI
        pos2_gt_roi = image[
            pos2_gt_box[1] : pos2_gt_box[1] + pos2_gt_box[3],
            pos2_gt_box[0] : pos2_gt_box[0] + pos2_gt_box[2],
        ]
    
        pos2_cmbt_roi = image[
            pos2_cmbt_box[1] : pos2_cmbt_box[1] + pos2_cmbt_box[3],
            pos2_cmbt_box[0] : pos2_cmbt_box[0] + pos2_cmbt_box[2],
        ]
    
        pos2_supp_roi = image[
            pos2_supp_box[1] : pos2_supp_box[1] + pos2_supp_box[3],
            pos2_supp_box[0] : pos2_supp_box[0] + pos2_supp_box[2],
        ]
    
        pos2_obj_roi = image[
            pos2_obj_box[1] : pos2_obj_box[1] + pos2_obj_box[3],
            pos2_obj_box[0] : pos2_obj_box[0] + pos2_obj_box[2],
        ]
        # POSITION 3 ROI
        pos3_gt_roi = image[
            pos3_gt_box[1] : pos3_gt_box[1] + pos3_gt_box[3],
            pos3_gt_box[0] : pos3_gt_box[0] + pos3_gt_box[2],
        ]
    
        pos3_cmbt_roi = image[
            pos3_cmbt_box[1] : pos3_cmbt_box[1] + pos3_cmbt_box[3],
            pos3_cmbt_box[0] : pos3_cmbt_box[0] + pos3_cmbt_box[2],
        ]
    
        pos3_supp_roi = image[
            pos3_supp_box[1] : pos3_supp_box[1] + pos3_supp_box[3],
            pos3_supp_box[0] : pos3_supp_box[0] + pos3_supp_box[2],
        ]
    
        pos3_obj_roi = image[
            pos3_obj_box[1] : pos3_obj_box[1] + pos3_obj_box[3],
            pos3_obj_box[0] : pos3_obj_box[0] + pos3_obj_box[2],
        ]
    
        # CONVERT TO GRAYSCALE
        # PLACEMENT
        placement_gray_roi = cv2.cvtColor(placement_roi, cv2.COLOR_BGR2GRAY)
        # POSITION 1
        pos1_gt_gray_roi = cv2.cvtColor(pos1_gt_roi, cv2.COLOR_BGR2GRAY)
        pos1_cmbt_gray_roi = cv2.cvtColor(pos1_cmbt_roi, cv2.COLOR_BGR2GRAY)
        pos1_supp_gray_roi = cv2.cvtColor(pos1_supp_roi, cv2.COLOR_BGR2GRAY)
        pos1_obj_gray_roi = cv2.cvtColor(pos1_obj_roi, cv2.COLOR_BGR2GRAY)
        # POSITION 2
        pos2_gt_gray_roi = cv2.cvtColor(pos2_gt_roi, cv2.COLOR_BGR2GRAY)
        pos2_cmbt_gray_roi = cv2.cvtColor(pos2_cmbt_roi, cv2.COLOR_BGR2GRAY)
        pos2_supp_gray_roi = cv2.cvtColor(pos2_supp_roi, cv2.COLOR_BGR2GRAY)
        pos2_obj_gray_roi = cv2.cvtColor(pos2_obj_roi, cv2.COLOR_BGR2GRAY)
        # POSITION 3
        pos3_gt_gray_roi = cv2.cvtColor(pos3_gt_roi, cv2.COLOR_BGR2GRAY)
        pos3_cmbt_gray_roi = cv2.cvtColor(pos3_cmbt_roi, cv2.COLOR_BGR2GRAY)
        pos3_supp_gray_roi = cv2.cvtColor(pos3_supp_roi, cv2.COLOR_BGR2GRAY)
        pos3_obj_gray_roi = cv2.cvtColor(pos3_obj_roi, cv2.COLOR_BGR2GRAY)
    
        """
        # DEBUG
        # PLACEMENT
        cv2.imshow("PLACEMENT", placement_gray_roi)
        # POSITION 1
        cv2.imshow("POS1_GT", pos1_gt_gray_roi)
        cv2.imshow("POS1_CMBT", pos1_cmbt_gray_roi)
        cv2.imshow("POS1_SUPP", pos1_supp_gray_roi)
        cv2.imshow("POS1_OBJ", pos1_obj_gray_roi)
        # POSITION 2
        cv2.imshow("POS2_GT", pos2_gt_gray_roi)
        cv2.imshow("POS2_CMBT", pos2_cmbt_gray_roi)
        cv2.imshow("POS2_SUPP", pos2_supp_gray_roi)
        cv2.imshow("POS2_OBJ", pos2_obj_gray_roi)
        # POSITION 3
        cv2.imshow("POS3_GT", pos3_gt_gray_roi)
        cv2.imshow("POS3_CMBT", pos3_cmbt_gray_roi)
        cv2.imshow("POS3_SUPP", pos3_supp_gray_roi)
        cv2.imshow("POS3_OBJ", pos3_obj_gray_roi)
    
        cv2.waitKey(0)
        cv2.destroyAllWindows
        """
        # APPLY OCR USING PYTESSERACT
        # PLACEMENT
        placement_txt = pytesseract.image_to_string(
            placement_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(placement_txt)
        # POSITION 1
        pos1_gt_txt = pytesseract.image_to_string(
            pos1_gt_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos1_gt_txt)
        pos1_cmbt_txt = pytesseract.image_to_string(
            pos1_cmbt_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos1_cmbt_txt)
        pos1_supp_txt = pytesseract.image_to_string(
            pos1_supp_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos1_supp_txt)
        pos1_obj_txt = pytesseract.image_to_string(
            pos1_obj_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos1_obj_txt)
        # POSITION 2
        pos2_gt_txt = pytesseract.image_to_string(
            pos2_gt_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos2_gt_txt)
        pos2_cmbt_txt = pytesseract.image_to_string(
            pos2_cmbt_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos2_cmbt_txt)
        pos2_supp_txt = pytesseract.image_to_string(
            pos2_supp_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos2_supp_txt)
        pos2_obj_txt = pytesseract.image_to_string(
            pos2_obj_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos2_obj_txt)
        # POSITION 3
        pos3_gt_txt = pytesseract.image_to_string(
            pos3_gt_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos3_gt_txt)
        pos3_cmbt_txt = pytesseract.image_to_string(
            pos3_cmbt_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos3_cmbt_txt)
        pos3_supp_txt = pytesseract.image_to_string(
            pos3_supp_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos3_supp_txt)
        pos3_obj_txt = pytesseract.image_to_string(
            pos3_obj_gray_roi, lang="eng", config="--psm 6"
        )
        imgData.append(pos3_obj_txt)
    
        placementRead = imgData[0]
        pos1Read = imgData[1:5]
        pos2Read = imgData[5:9]
        pos3Read = imgData[9:]
    
        print(f"PLACEMENT {placementRead}")
        print(f"POSITION1 {pos1Read}")
        print(f"POSITION2 {pos2Read}")
        print(f"POSITION3 {pos3Read}")
    
            
