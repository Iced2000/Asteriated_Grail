from .BasePlayer import BasePlayer

class JianSheng(BasePlayer):
    def __init__(self, gameEngine, respond, idx, isRed):
        super(JianSheng, self).__init__(gameEngine, respond, idx, isRed)
        self.__skillReset()
        self._respond.addTimeLine1(self, "JiFengJi")
        self._respond.addTimeLine1(self, "LieFengJi")
        self._respond.addTimeLine1(self, "ShengJian")
        self._respond.addTimeLine2(self, "LieFengJi")

    def FengNu(self):
        self.__FengNuUsed = True
        self._attackAction += 1
        availCard = self._getAvailCards("isWindAttack")
        print("Available Cards:{}".format(str(availCard)))
        actNum = int(input("Action:"))
        self._attack(actNum)

    def JianYin(self):
        self.__JianYinUsed = True
        self._attackAction += 1
        self._useJewel(gem=0, crystal=1)
        availCard = self._getAvailCards("isAttack")
        print("Available Cards:{}".format(str(availCard)))
        actNum = int(input("Action:"))
        self._attack(actNum)

    def JiFengJi(self, info):
        if info["from"] == self.getId() and info["type"] == "attack" and info["card"].isJiFengJi():
            self._attackAction += 1

    def LieFengJi(self, info):
        if info["from"] == self.getId() and info["type"] in ["attack", "counter"] and \
                info["card"].isLieFengJi() and self._gameEngine.getPlayer()[info["to"]].hasShield():
            info["counterable"] = 0
            info["shieldable"] = False

    def ShengJian(self, info):
        if info["from"] == self.getId() and info["type"] == "attack" and self.__attNum == 2:
            info["counterable"] = 2

    def _postAttack(self):
        self.__attNum += 1
        avail = []
        if not self.__FengNuUsed and self._getAvailCards("isWindAttack"):
            avail.append(1000)
        if not self.__JianYinUsed and (self._gem or self._crystal):
            avail.append(2000)

        if avail:
            print("Available acts:{}".format(str(avail)))
            actNum = int(input("Action:"))
            if actNum not in avail: return
            
            if actNum == 1000:
                self.FengNu()
            elif actNum == 2000:
                self.JianYin()
    
    def __skillReset(self):
        self.__attNum = 0
        self.__FengNuUsed = False
        self.__JianYinUsed = False
