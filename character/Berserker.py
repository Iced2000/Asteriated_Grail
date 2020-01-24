from .BasePlayer import BasePlayer
from .utils import *

class Berserker(BasePlayer):
    def __init__(self, gameEngine, respond, idx, isRed):
        super(Berserker, self).__init__(gameEngine, respond, idx, isRed)
        self._ATK = 3 # Crazy
        self._respond.addTimeLine1(self, "BloodSword")
        self._respond.addTimeLine1(self, "BloodRoar")
        self._respond.addTimeLine2(self, "Tear")

    def BloodSword(self, info):
        if checkAtt(self, info) and info["card"].isBloodSword():
            handCardNum = self._gameEngine.getPlayer()[info["to"]].getHandCardNum()
            if handCardNum in [2, 3] and askBinary("Use BloodSword"):
                info["value"] += (4 - handCardNum)

    def BloodRoar(self, info):
        if checkAtt(self, info) and info["card"].isBloodRoar():
            healNum = self._gameEngine.getPlayer()[info["to"]].getHeal()
            if healNum == 2 and askBinary("Use BloodRoar"):
                info["counterable"] = 2

    def Tear(self, info):
        if checkAoC(self, info) and info.get("hit", False):
            if self.checkJewel(gem=1, crystal=0) and askBinary("Use Tear"):
                self._useJewel(gem=1, crystal=0)
                info["value"] += 2
