from .BasePlayer import BasePlayer
from .utils import *

class SwordMaster(BasePlayer):
    def __init__(self, gameEngine, respond, idx, isRed):
        super(SwordMaster, self).__init__(gameEngine, respond, idx, isRed)
        self._skillReset()
        self._respond.addTimeLine1(self, "FastWind")
        self._respond.addTimeLine1(self, "HardWind")
        self._respond.addTimeLine1(self, "HolySword")

    def FuryWind(self):
        self.__FuryWindUsed = True
        self._attackAction += 1
        availCard = self._getAvailCards("isWindAttack")
        _, cardNum = askSelection("Card:", availCard, 1)
        self._attack(cardNum)

    def SwordShadow(self):
        self.__SwordShadowUsed = True
        self._useJewel(gem=0, crystal=1)
        self._attackAction += 1

    def FastWind(self, info):
        if checkAtt(self, info) and info["card"].isFastWind():
            if askBinary("Use FastWind"):
                self._attackAction += 1

    def HardWind(self, info):
        if checkAoC(self, info) and info["card"].isHardWind() and self._gameEngine.getPlayer()[info["to"]].hasShield():
            if askBinary("Use HardWind"):
                info["counterable"] = 0
                info["shieldable"] = False

    def HolySword(self, info):
        if checkAtt(self, info) and self.__attNum == 2:
            if askBinary("Use HolySword"):
                info["counterable"] = 2

    def _postAttack(self):
        self.__attNum += 1
        avail = []
        if not self.__FuryWindUsed and self._getAvailCards("isWindAttack"):
            avail.append(1000)
        if not self.__SwordShadowUsed and self.checkJewel(gem=0, crystal=1):
            avail.append(1001)

        if avail:
            inAvail, actNum = askSelection("Acts:", avail, 1, allowOutOfIdx=True)
            if not inAvail:
                return
            elif actNum == 1000:
                self.FuryWind()
            elif actNum == 1001:
                self.SwordShadow()
    
    def _skillReset(self):
        self.__attNum = 0
        self.__FuryWindUsed = False
        self.__SwordShadowUsed = False
