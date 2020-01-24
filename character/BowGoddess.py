from .BasePlayer import BasePlayer
from .utils import *

class BowGoddess(BasePlayer):
    def __init__(self, gameEngine, respond, idx, isRed):
        super(BowGoddess, self).__init__(gameEngine, respond, idx, isRed)
        self._respond.addTimeLine1(self, "AccurateShot")
        self._respond.addTimeLine1(self, "ThunderBolt")
        self._respond.addTimeLine2(self, "PenetrateShot")

    def ThunderBolt(self, info):
        if checkAoC(self, info) and info["card"].isThunder() and info["counterable"] != 2:
            info["counterable"] = 0

    def PenetrateShot(self, info):
        if checkAtt(self, info) and not info.get("hit", True):
            avail = self._getAvailCards("isMagic")
            inAvail, cardNum = askSelection("Cards:", avail, 1, allowOutOfIdx=True)
            if inAvail:
                self.removeHandCards([cardNum], show=True)
                magicInfo = self._createInfo(
                    typ = "magic",
                    frm = self.getId(),
                    to = info["to"],
                    card = None, 
                    value = 2,
                    gem = None,
                )
                self._gameEngine.calculateDamage(magicInfo)
            else:
                return

    def FlashTrap(self):
        candidate = self._gameEngine.getCandidate("allExceptI", selfId=self.getId())
        _, target = askSelection("target:", candidate, 1)

        magicInfo = self._createInfo(
            typ = "magic",
            frm = self.getId(),
            to = target,
            card = None, 
            value = 2,
            gem = None,
        )
        self._gameEngine.calculateDamage(magicInfo)

    def AccurateShot(self, info):
        if checkAoC(self, info) and info["card"].isAccurateShot():
            if askBinary("Use AccurateShot"):
                info["value"] -= 1
                info["counterable"] = 2

    def Snipe(self):
        self._useJewel(gem=0, crystal=1)
        candidate = self._gameEngine.getCandidate("allExceptI", selfId=self.getId())
        _, targetNo = askSelection("target:", candidate, 1)
        hcn = self._gameEngine.getPlayer()[targetNo].getHandCardNum()
        if hcn < 5:
            self._gameEngine.drawCards(5 - hcn, True, targetNo)
        if askBinary("One more attack action"):
            self._attackAction += 1

    def _getAvailMagic(self):
        avail = []
        if self._getAvailCards("isFlashTrap"):
            avail.append(1002)
        if self.checkJewel(gem=0, crystal=1):
            avail.append(1003)
        return avail

    def _magic(self, magicNum):
        super(BowGoddess, self)._magic(magicNum)
        if magicNum == 1002:
            avail = self._getAvailCards("isFlashTrap")
            _, cardNum = askSelection("Cards:", avail, 1)
            self.removeHandCards([cardNum], show=True)
            self.FlashTrap()
        elif magicNum == 1003:
            self.Snipe()