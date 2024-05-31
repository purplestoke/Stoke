import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import requests
import sqlite3
import os
from stoke import Stoke
from API_Tokens import stoke, bugsServerId
import cv2
import numpy as np
from ImageReader import ImageReader

#BUTTONS
class ConfirmationView(nextcord.ui.View):
    def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None

    @nextcord.ui.button(label="Yes Replace", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="No, Keep Original", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()

class apex_event(commands.Cog):
    def __init__(self, client):
        self.client = client

    # EVENT LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        # CHECKING FOR AN IMG IN CHANNEL
        if not message.attachments:
            return
        mem = message.author
        discord = mem.id
        logFlags = []
        
        # CHECK TO MAKE SURE STOKE DOESNT RESPOND TO HIS OWN MSG
        if discord == stoke:
            return
        
        # VARIABLES
        channel = "scSubmission"
        guildId = message.guild.id

        # ONLY RESPONDS TO MESSAGES IN THE SUBMISSION CHANNEL
        guildIns = Stoke().Guilds(channel, guildId)
        bugsGuildId = guildIns.pullId()
        flag2, ret = guildIns.pullChannel()
        logFlags.append(flag2)

        if message.channel.id != ret:
            return

        # VARIABLES CONT
        stokeIns = Stoke()
        game = "apex"
        eventIns = stokeIns.Event(discord, game)
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)

        # CHECK IF EVENT ON
        flag, check = eventIns.isOn()
        logFlags.append(flag)
        if check == 1:
            flag1, bugsId = bugsProfileIns.bugsId()
            logFlags.append(flag1)
            if flag1 != 2:
                return
        else:
            return
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)


        # CHECK FOR APEX ROLE
        if "apex" in [role.name.lower() for role in mem.roles]:
            # CHECK FOR COMPETITOR ROLE
            if "competitor" in [role.name.lower() for role in mem.roles]:
                # CHECK FOR AN ALREADY SUBMITTED IMAGE
                flag3, check = eventIns.checkSubmission()
                logFlags.append(flag3)
                if flag3 == 2:
                    view = ConfirmationView()
                    ynDel = await message.channel.send(
                        f"You have already used a submission for this tournament.\n\nIf you would like to replace it select the button.",
                        view=view
                    )
                    await view.wait()
                    if view.value is None:
                        await ynDel.edit(content="No response in time, keeping original")
                        return
                    elif view.value is True:
                        #NEED TO DELETE PREVIOUS IMG
                        # CHECK IF IN BUGS SERVER
                        if guildId == bugsServerId:
                            # PULL COMMUNITY ID FROM PLAYER PROFILE
                            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, 'apex', hosted=True)
                            hostedId = playerProfileIns.pullHostedId()
                            if hostedId:
                                fp = f"apex_sc/{bugsGuildId}/{hostedId}/apexSc{bugsId}.jpg"
                            else:
                                logFlags.append("Hosted id not Found")
                                await message.channel.send("I had an issue finding your previous submission")
                                return
                        else:
                            fp = f"apex_sc/{bugsGuildId}/apexSc{bugsId}.jpg"
                        os.remove(fp)
                        subDel = eventIns.submissionDelete(bugsId)
                        subDelFlag = f"subDelA{str(subDel)}"
                        logFlags.append(subDelFlag)
                    elif view.value is False:
                        await message.channel.send("Keeping Original.")
                        return

               
                # DEALING WITH IMG
                attachments = message.attachments
                for attachment in attachments:
                    if any(
                        attachment.filename.lower().endswith(ext)
                        for ext in [".png", ".jpg"]
                    ):
                        screenshot_url = attachment.url

                    # CHECK IMAGE METADATA
                    securityIns = stokeIns.Security(discord, bugsId, screenshot_url)
                    resp, secFlag = securityIns.checkImage()
                    if resp == None:
                        resp = 'None'
                    logFlags.append(resp + str(secFlag))
                    if secFlag == 5:
                        logIns.log(channel, cmd="AscSec")
                        await message.channel.send("Error saving image")
                        return


                    # HANDLING IMAGE
                    imgWidth = 1920
                    # DOWNLOADING IMAGE
                    response = requests.get(screenshot_url)
                    imgData = np.frombuffer(response.content, dtype=np.uint8)
                    # CONVERT THE BYTES TO A FORMAT OPENCV CAN HANDLE
                    img = cv2.imdecode(imgData, cv2.IMREAD_UNCHANGED)

                    # CALCULATE NEW DIMENSIONS
                    ogHeight, ogWidth = img.shape[:2]
                    aspectRatio = ogWidth / ogHeight
                    newHeight = int(imgWidth / aspectRatio)

                    # RESIZE THE IMAGE
                    resizedImg = cv2.resize(img, (imgWidth, newHeight))

                    # SETTING FLAG IN DB TO 1
                    file_name = f"apexSc{bugsId}.jpg"
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE Apex_Profile SET submission = 1 WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",(discord,),
                    )
                    conn.commit()
                    conn.close()

                    # CREATE FOLDER OF DISCORD MEMBER
                    # IF IN BUGS DISCORD
                    if guildId == bugsServerId:
                            # PULL COMMUNITY ID FROM PLAYER PROFILE
                            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, 'apex', hosted=True)
                            hostedId = playerProfileIns.pullHostedId()
                            if hostedId:
                                hosted = True
                            else:
                                logFlags.append("Hosted id not Found")
                                await message.channel.send("I had an issue finding information to save your screenshot")
                                return

                    parent_folder = "apex_sc"
                    file_folder = str(guildIns.pullId())
                    if hosted:
                        path = os.path.join(parent_folder, file_folder, str(hostedId))
                    else:
                        path = os.join(parent_folder, file_folder)
                    os.makedirs(path, exist_ok=True)

                    filePath = os.path.join(path, file_name)
                    #SAVE RESIZED IMAGE TO DIR
                    cv2.imwrite(filePath, resizedImg)

                    # USE IMAGE READER ON IMAGE
                    playerProfileIns = stokeIns.PlayerProfile(discord, guildId, type='apex', hosted=None)
                    ppRetFlag, gt = playerProfileIns.retrieve()
                    AR = ImageReader(filePath, gt, bugsId, bugsGuildId)
                    score, imgFlag = AR.ReadApex()
                    logFlags.append(imgFlag)
                    if imgFlag == 2:
                        finalFlag = AR.UpdateDB(score, game='apex')
                        logFlags.append(finalFlag)
                        # SEND MSG TO mem
                        logIns.log(
                            channel=channel,
                            cmd="Asc",
                        )
                        await message.channel.send(
                            f"Got your screenshot! You earned a total of {score} points!"
                        )
                        return
                    else:
                        await message.channel.send("Screenshot saved but there was en error when attempting to tally points.\nYour submission has been sent to purplestoke for manual review.")
                        return

class finals_event(commands.Cog):
    def __init__(self, client):
        self.client = client

    # FINALS EVENT LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        # CHECKING FOR AN IMG IN CHANNEL
        if not message.attachments:
            return
        mem = message.author
        discord = mem.id
        logFlags = []
        
        # CHECK TO MAKE SURE STOKE DOESNT RESPOND TO HIS OWN MSG
        if discord == stoke:
            return
        
        # VARIABLES
        channel = "scSubmission"
        guildId = message.guild.id

        # ONLY RESPONDS TO MESSAGES IN THE SUBMISSION CHANNEL
        guildIns = Stoke().Guilds(channel, guildId)
        bugsGuildId = guildIns.pullId()
        flag2, ret = guildIns.pullChannel()
        logFlags.append(flag2)

        if message.channel.id != ret:
            return

        # VARIABLES CONT
        stokeIns = Stoke()
        game = "finals"
        eventIns = stokeIns.Event(discord, game)
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)

        # CHECK IF EVENT ON
        flag, check = eventIns.isOn()
        logFlags.append(flag)
        if check == 1:
            flag1, bugsId = bugsProfileIns.bugsId()
            logFlags.append(flag1)
            if flag1 != 2:
                return
        else:
            return
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)


        # CHECK FOR FINALS ROLE
        if "finals" in [role.name.lower() for role in mem.roles]:
            # CHECK FOR COMPETITOR ROLE
            if "competitor" in [role.name.lower() for role in mem.roles]:
                flag3, check = eventIns.checkSubmission()
                logFlags.append(flag3)
                if flag3 == 2:
                    view = ConfirmationView()
                    ynDel = await message.channel.send(
                        f"You have already used a submission for this tournament.\n\nIf you would like to replace it select the button.",
                        view=view
                    )
                    await view.wait()
                    if view.value is None:
                        await ynDel.edit(content="No response in time, keeping original")
                        return
                    elif view.value is True:
                        #NEED TO DELETE PREVIOUS IMG
                        # CHECK IF IN BUGS SERVER
                        if guildId == bugsServerId:
                            # PULL COMMUNITY ID FROM PLAYER PROFILE
                            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, 'finals', hosted=True)
                            hostedId = playerProfileIns.pullHostedId()
                            if hostedId:
                                fp = f"finals_sc/{bugsGuildId}/{hostedId}/finalsSc{bugsId}.jpg"
                            else:
                                logFlags.append("Hosted id not Found")
                                await message.channel.send("I had an issue finding your previous submission")
                                return
                        else:
                            fp = f"finals_sc/{bugsGuildId}/finalsSc{bugsId}.jpg"
                        os.remove(fp)
                        subDel = eventIns.submissionDelete(bugsId)
                        subDelFlag = f"subDelF{str(subDel)}"
                        logFlags.append(subDelFlag)
                    elif view.value is False:
                        await message.channel.send("Keeping Original.")
                        return

               
                # DEALING WITH IMG
                attachments = message.attachments
                for attachment in attachments:
                    if any(
                        attachment.filename.lower().endswith(ext)
                        for ext in [".png", ".jpg"]
                    ):
                        screenshot_url = attachment.url

                    # CHECK IMAGE METADATA
                    securityIns = stokeIns.Security(discord, bugsId, screenshot_url)
                    resp, secFlag = securityIns.checkImage()
                    if resp == None:
                        resp = 'None'
                    logFlags.append(resp + str(secFlag))
                    if secFlag == 5:
                        logIns.log(channel, cmd="FscSec")
                        await message.channel.send("Error saving image")
                        return

                    # HANDLING IMAGE
                    imgWidth = 1920
                    # DOWNLOADING IMAGE
                    response = requests.get(screenshot_url)
                    imgData = np.frombuffer(response.content, dtype=np.uint8)
                    # CONVERT THE BYTES TO A FORMAT OPENCV CAN HANDLE
                    img = cv2.imdecode(imgData, cv2.IMREAD_UNCHANGED)

                    # CALCULATE NEW DIMENSIONS
                    ogHeight, ogWidth = img.shape[:2]
                    aspectRatio = ogWidth / ogHeight
                    newHeight = int(imgWidth / aspectRatio)

                    # RESIZE THE IMAGE
                    resizedImg = cv2.resize(img, (imgWidth, newHeight))

                    # SETTING FLAG IN DB TO 1
                    file_name = f"finalsSc{bugsId}.jpg"
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE Finals_Profile SET submission = 1 WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",(discord,),
                    )
                    conn.commit()
                    conn.close()

                    # CREATE FOLDER OF DISCORD MEMBER
                    # IF IN BUGS DISCORD
                    if guildId == bugsServerId:
                            # PULL COMMUNITY ID FROM PLAYER PROFILE
                            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, 'finals', hosted=True)
                            hostedId = playerProfileIns.pullHostedId()
                            if hostedId:
                                hosted = True
                            else:
                                logFlags.append("Hosted id not Found")
                                await message.channel.send("I had an issue finding information to save your screenshot")
                                return
                    parent_folder = "finals_sc"
                    file_folder = str(guildIns.pullId())
                    if hosted:
                        path = os.path.join(parent_folder, file_folder, str(hostedId))
                    else:
                        path = os.join(parent_folder, file_folder)
                    os.makedirs(path, exist_ok=True)
                    path = os.path.join(parent_folder, file_folder)
                    os.makedirs(path, exist_ok=True)
                    filePath = os.path.join(path, file_name)
                    #SAVE RESIZED IMAGE TO DIR
                    cv2.imwrite(filePath, resizedImg)

                    # USE IMAGE READER ON IMAGE
                    playerProfileIns = stokeIns.PlayerProfile(discord, guildId, type='finals', hosted=None)
                    ppRetFlag, gt = playerProfileIns.retrieve()
                    AR = ImageReader(filePath, gt, bugsId, bugsGuildId)
                    score, imgFlag = AR.ReadFinals()
                    logFlags.append(imgFlag)
                    if imgFlag == 2:
                        finalFlag = AR.UpdateDB(score, game='finals')
                        logFlags.append(finalFlag)
                        # SEND MSG TO mem
                        logIns.log(
                            channel=channel, 
                            cmd="Fsc",
                        )
                        await message.channel.send(
                            f"Got your screenshot! You earned a total of {score} points!"
                        )
                        return
                    else:
                        await message.channel.send("Screenshot saved but there was en error when attempting to tally points.\nYour image has been sent to purplestoke for manual review.")
                        return

class xdefiant_event(commands.Cog):
    def __init__(self, client):
        self.client = client

    # XDEFIANT EVENT LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        # CHECKING FOR AN IMG IN CHANNEL
        if not message.attachments:
            return
        mem = message.author
        discord = mem.id
        logFlags = []
        
        # CHECK TO MAKE SURE STOKE DOESNT RESPOND TO HIS OWN MSG
        if discord == stoke:
            return
        
        # VARIABLES
        channel = "scSubmission"
        guildId = message.guild.id

        # ONLY RESPONDS TO MESSAGES IN THE SUBMISSION CHANNEL
        guildIns = Stoke().Guilds(channel, guildId)
        bugsGuildId = guildIns.pullId()
        flag2, ret = guildIns.pullChannel()
        logFlags.append(flag2)

        if message.channel.id != ret:
            return

        # VARIABLES CONT
        stokeIns = Stoke()
        game = "xdefiant"
        eventIns = stokeIns.Event(discord, game)
        bugsProfileIns = stokeIns.bugsProfile(discord, ethAddr=None)

        # CHECK IF EVENT ON
        flag, check = eventIns.isOn()
        logFlags.append(flag)
        if check == 1:
            flag1, bugsId = bugsProfileIns.bugsId()
            logFlags.append(flag1)
            if flag1 != 2:
                return
        else:
            return
        logIns = stokeIns.Log(bugsId, guildId, logFlags, discord)


        # CHECK FOR FINALS ROLE
        if "xdefiant" in [role.name.lower() for role in mem.roles]:
            # CHECK FOR COMPETITOR ROLE
            if "competitor" in [role.name.lower() for role in mem.roles]:
                flag3, check = eventIns.checkSubmission()
                logFlags.append(flag3)
                if flag3 == 2:
                    view = ConfirmationView()
                    ynDel = await message.channel.send(
                        f"You have already used a submission for this tournament.\n\nIf you would like to replace it select the button.",
                        view=view
                    )
                    await view.wait()
                    if view.value is None:
                        await ynDel.edit(content="No response in time, keeping original")
                        return
                    elif view.value is True:
                        #NEED TO DELETE PREVIOUS IMG
                        # CHECK IF IN BUGS SERVER
                        if guildId == bugsServerId:
                            # PULL COMMUNITY ID FROM PLAYER PROFILE
                            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, 'xdefiant', hosted=True)
                            hostedId = playerProfileIns.pullHostedId()
                            if hostedId:
                                fp = f"xdef_sc/{bugsGuildId}/{hostedId}/xdefSc{bugsId}.jpg"
                            else:
                                logFlags.append("Hosted id not Found")
                                await message.channel.send("I had an issue finding your previous submission")
                                return
                        else:
                            fp = f"xdef_sc/{bugsGuildId}/xdefSc{bugsId}.jpg"
                        os.remove(fp)
                        subDel = eventIns.submissionDelete(bugsId)
                        subDelFlag = f"subDelF{str(subDel)}"
                        logFlags.append(subDelFlag)
                    elif view.value is False:
                        await message.channel.send("Keeping Original.")
                        return

               
                # DEALING WITH IMG
                attachments = message.attachments
                for attachment in attachments:
                    if any(
                        attachment.filename.lower().endswith(ext)
                        for ext in [".png", ".jpg"]
                    ):
                        screenshot_url = attachment.url

                    # CHECK IMAGE METADATA
                    securityIns = stokeIns.Security(discord, bugsId, screenshot_url)
                    resp, secFlag = securityIns.checkImage()
                    if resp == None:
                        resp = 'None'
                    logFlags.append(resp + str(secFlag))
                    if secFlag == 5:
                        logIns.log(channel, cmd="XscSec")
                        await message.channel.send("Error saving image")
                        return

                    # HANDLING IMAGE
                    imgWidth = 1920
                    # DOWNLOADING IMAGE
                    response = requests.get(screenshot_url)
                    imgData = np.frombuffer(response.content, dtype=np.uint8)
                    # CONVERT THE BYTES TO A FORMAT OPENCV CAN HANDLE
                    img = cv2.imdecode(imgData, cv2.IMREAD_UNCHANGED)

                    # CALCULATE NEW DIMENSIONS
                    ogHeight, ogWidth = img.shape[:2]
                    aspectRatio = ogWidth / ogHeight
                    newHeight = int(imgWidth / aspectRatio)

                    # RESIZE THE IMAGE
                    resizedImg = cv2.resize(img, (imgWidth, newHeight))

                    # SETTING FLAG IN DB TO 1
                    file_name = f"xdefSc{bugsId}.jpg"
                    conn = sqlite3.connect("bugs_DB.sqlite")
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE XDefiant_Profile SET submission = 1 WHERE bugs_id IN(SELECT id FROM bugs_Profile WHERE discord = ?)",(discord,),
                    )
                    conn.commit()
                    conn.close()

                    # CREATE FOLDER OF DISCORD MEMBER
                    # IF IN BUGS DISCORD
                    if guildId == bugsServerId:
                            # PULL COMMUNITY ID FROM PLAYER PROFILE
                            playerProfileIns = stokeIns.PlayerProfile(discord, guildId, 'xdefiant', hosted=True)
                            hostedId = playerProfileIns.pullHostedId()
                            if hostedId:
                                hosted = True
                            else:
                                logFlags.append("Hosted id not Found")
                                await message.channel.send("I had an issue finding information to save your screenshot")
                                return
                    parent_folder = "xdef_sc"
                    file_folder = str(guildIns.pullId())
                    if hosted:
                        path = os.path.join(parent_folder, file_folder, str(hostedId))
                    else:
                        path = os.join(parent_folder, file_folder)
                    path = os.path.join(parent_folder, file_folder)
                    os.makedirs(path, exist_ok=True)
                    filePath = os.path.join(path, file_name)
                    #SAVE RESIZED IMAGE TO DIR
                    cv2.imwrite(filePath, resizedImg)

                    # USE IMAGE READER ON IMAGE
                    playerProfileIns = stokeIns.PlayerProfile(discord, guildId, type='xdefiant')
                    ppRetFlag, gt = playerProfileIns.retrieve()
                    AR = ImageReader(filePath, gt, bugsId, bugsGuildId)
                    score, imgFlag = AR.ReadXdef()
                    logFlags.append(imgFlag)
                    if imgFlag == 2:
                        finalFlag = AR.UpdateDB(score, game='xdefiant')
                        logFlags.append(finalFlag)
                        # SEND MSG TO mem
                        logIns.log(
                            channel=channel, 
                            cmd="Fsc",
                        )
                        await message.channel.send(
                            f"Got your screenshot! You earned a total of {score} points!"
                        )
                        return
                    elif imgFlag == 3:
                        logIns.log(
                            channel=channel,
                            cmd='Fsc'
                        )
                        await message.channel.send(f"Error: {score}")
                    else:
                        await message.channel.send("Screenshot saved but there was en error when attempting to tally points.\nYour image has been sent to purplestoke for manual review.")
                        return       


def setup(client):
    client.add_cog(apex_event(client))
    client.add_cog(finals_event(client))
    client.add_cog(xdefiant_event(client))