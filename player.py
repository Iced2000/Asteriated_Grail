
TAKE = 100
BUY = 200
SYN = 300

class BasePlayer(object):

    def __init__(self, gameEngine, idx, isRed):
        self.__id = idx
        self.__gameEngine = gameEngine
        self.__isRed = isRed
        self.__ATK = 2
        self.__heal = 0
        self.__gem = 0
        self.__crystal = 0
        self.__cards = []
        self.__maxCards = 6
        self.__maxJewels = 3
        self.__basicEffect = {
            "weak": [],
            "shield": [],
            "poison": [],
        }
        self.__generalAction = 0
        self.__attackAction = 0
        self.__magicAction = 0
        self.__specialAction = 0

        self.__roundSkip = False

    def __str__(self):
        return "Player {}\n\tGem:{} Crystal:{}\n\tWeak:{} Shield:{} Poison:{}\n\tHeal:{}".format(
            self.getId(), self.__gem, self.__crystal, len(self.__basicEffect["weak"]), 
            len(self.__basicEffect["shield"]), len(self.__basicEffect["poison"]), self.__heal)

    def printHandCards(self):
        print(self)
        print("Player {}'s Hand cards:".format(self.getId()))
        for ca in self.__cards: print(ca)

    def addHandCards(self, cards, harmed):
        self.__cards.extend(cards)
        removeNum = len(self.__cards) - self.__maxCards
        if removeNum > 0:
            tmpNo = []
            self.printHandCards()
            for i in range(removeNum):
                dis = int(input("discard: "))
                assert(dis in range(len(self.__cards)))
                tmpNo.append(dis)
            self.removeHandCards(tmpNo, show=False)
        return removeNum

    def removeHandCards(self, discardNum, show, recycle=True):
        discards = [v for i,v in enumerate(self.__cards) if i in discardNum]
        self.__cards = [v for i,v in enumerate(self.__cards) if i not in discardNum]
        self.__gameEngine.removeCards(self.getId(), discards, show, recycle)

    def getId(self):
        return self.__id

    def getColor(self):
        return self.__isRed

    def allowAttack(self, teamColor):
        return teamColor != self.getColor()

    def allowCounter(self, teamColor, prevID):
        return teamColor != self.getColor() and prevID != self.getId()

    def allowWeak(self):
        return len(self.__basicEffect["weak"]) == 0

    def allowShield(self):
        return len(self.__basicEffect["shield"]) == 0

    def allowPoison(self):
        return True

    def roundStart(self):
        pass

    def beforeAction(self):
        self.__checkPoison()
        self.__checkWeak()
        
    def action(self):
        self.__generalAction = 1 if not self.__roundSkip else 0
        
        while self.__generalAction + self.__attackAction + self.__magicAction + self.__specialAction:

            if self.__generalAction:
                availCard, availMagic, availSP = self.__getAvailCards("isNotLight"), self.__getAvailMagic(), self.__getAvailSP()
            elif self.__attackAction:
                availCard, availMagic, availSP = self.__getAvailCards("isAttack"), [], []
            elif self.__magicAction:
                availCard, availMagic, availSP = self.__getAvailCards("isMagicAction"), self.__getAvailMagic(), []
            else:
                availCard, availMagic, availSP = [], [], self.__getAvailSP()

            print("Available Cards:{}\nAvailable Special:{}".format(str(availCard), str(availSP)))
            actNum = int(input("Action:"))

            if actNum in availCard and self.__cards[actNum].isAttack():
                self.__attack(actNum)
            elif actNum in availCard:
                self.__basicMagic(actNum)
            elif actNum in availSP:
                self.__special(actNum)
            elif actNum in availMagic:
                self.__magic(actNum)
            else:
                raise

    def roundEnd(self):
        self.__roundSkip = False

    def addBasicEffect(self, effectType, card):
        if effectType == "weak":
            self.__basicEffect["weak"].append(card)
        elif effectType == "shield":
            self.__basicEffect["shield"].append(card)
        elif effectType == "poison":
            self.__basicEffect["poison"].append(card)
        else:
            raise

    def counter(self, info):
        """return hit, counterInfo"""
        if info["counterable"] == 2:
            return True, None
        elif info["counterable"] in [0, 1]:
            cardType = "forCounter" if info["counterable"] == 1 else "isLight"
            availCard = self.__getAvailCards(cardType, info["element"])
            cardNum = int(input("Avail " + str(availCard) + ": "))

            if cardNum in availCard:
                if self.__cards[cardNum].getElement() == "light":
                    counterInfo = None
                else:
                    target = int(input("target" + str(info["candidate"]) + ": "))
                    assert(target in info["candidate"])

                    counterInfo = self.__createInfo(
                        typ = "counter",
                        frm = self.getId(),
                        to = target,
                        element = self.__cards[cardNum].getElement(), 
                        value = 2,
                        gem = False,
                    )
                self.removeHandCards([cardNum], show=True)
                return False, counterInfo
            else:
                return self.__checkShield(), None
        else:
            raise

    def missile(self, info):
        availCard = self.__getAvailCards("forMissileCounter")
        cardNum = int(input("Avail " + str(availCard) + ": "))
        if cardNum in availCard:
            if self.__cards[cardNum].getElement() == "light":
                missileInfo = None
            else:
                target = int(input("target" + str(info["candidate"]) + ": "))
                assert(target in info["candidate"])

                missileInfo = self.__createInfo(
                    typ = "magic",
                    frm = self.getId(),
                    to = target,
                    element = self.__cards[cardNum].getElement(), 
                    value = info["value"],
                    gem = None,
                )
            self.removeHandCards([cardNum], True)
            return False, missileInfo
        else:
            return self.__checkShield(), None

    def useHeal(self, info):
        if self.__heal:
            maxHeal = min(info["value"], self.__heal, info["healable"])
            print("max healable:", maxHeal)
            healNum = int(input("use heal: "))
            assert(healNum<=maxHeal and healNum>=0)
            info["value"] -= healNum
            self.__heal -= healNum
        else:
            return

    def __checkPoison(self):
        if self.__basicEffect["poison"]:
            info = self.__createInfo(
                typ = "magic",
                frm = None,
                to = self.getId(),
                element = None, 
                value = len(self.__basicEffect["poison"]),
                gem = None,
            )
            self.__gameEngine.removeCards(self.getId(), 
                self.__basicEffect["poison"], False, True)
            self.__basicEffect["poison"] = []
            self.__gameEngine.poison(info)

    def __checkWeak(self):
        if self.__basicEffect["weak"]:
            self.__gameEngine.removeCards(self.getId(), 
                self.__basicEffect["weak"], False, True)
            self.__basicEffect["weak"] = []
            ps = input("Weak! Pass or not?[Y/N]")
            if ps == 'Y':
                self.__roundSkip = True
            else:
                self.__gameEngine.drawCards(3, True, self.getId())

    def __getAvailCards(self, funcName, *arg, **kwarg):
        self.printHandCards()
        avail = []
        for i in range(len(self.__cards)):
            if getattr(self.__cards[i], funcName)(*arg, **kwarg):
                avail.append(i)
        return avail

    def __getAvailSP(self):
        availSP = []
        teamGem, teamCrystal = self.__gameEngine.getTeamJewel(self.getColor())
        if (teamGem or teamCrystal) and ((self.__gem + self.__crystal) < self.__maxJewels):
            availSP.append(TAKE)
        if (self.__maxCards - len(self.__cards)) >= 3:
            availSP.append(BUY)
            if (teamGem + teamCrystal) >= 3:
                availSP.append(SYN)
        return availSP

    def __getAvailMagic(self):
        return []

    def __attack(self, cardNum):
        candidate = self.__gameEngine.getCandidate("attack", frm=self.getId())
        target = int(input("target" + str(candidate) + ": "))

        if target in candidate:
            if self.__generalAction > 0:
                self.__generalAction -= 1
            elif self.__attackAction > 0:
                self.__attackAction -= 1
            else:
                raise
            info = self.__createInfo(
                        typ = "attack",
                        frm = self.getId(),
                        to = target,
                        element = self.__cards[cardNum].getElement(), 
                        value = self.__ATK,
                        gem = True,
                    )
            self.removeHandCards([cardNum], show=True)
            self.__gameEngine.attackOrCounter(info)
        else:
            print("restart")

    def __basicMagic(self, cardNum):
        magicType = self.__cards[cardNum].getMagicName()
        candidate = self.__gameEngine.getCandidate(magicType, frm=self.getId())
        target = int(input("target" + str(candidate) + ": "))

        if target in candidate:
            if self.__generalAction > 0:
                self.__generalAction -= 1
            elif self.__magicAction > 0:
                self.__magicAction -= 1
            else:
                raise

            if magicType in ["weak", "shield", "poison"]:
                self.__gameEngine.addBasicEffect(magicType, target, self.__cards[cardNum], self.getId())
                self.removeHandCards([cardNum], show=True, recycle=False)

            elif magicType == "missile":
                info = self.__createInfo(
                    typ = "magic",
                    frm = self.getId(),
                    to = target,
                    element = self.__cards[cardNum].getElement(), 
                    value = 2,
                    gem = None,
                )
                self.removeHandCards([cardNum], True)
                self.__gameEngine.missile(info)
            else:
                raise
        else:
            print("restart")

    def __special(self, spType):
        if self.__generalAction > 0:
            self.__generalAction -= 1
        elif self.__specialAction > 0:
            self.__specialAction -= 1
        else:
            raise

        if spType == TAKE:
            self.__specialTake()
        elif spType == BUY:
            self.__specialBuy()
        elif spType == SYN:
            self.__specialSyn()
        else:
            raise

    def __specialTake(self):
        teamGem, teamCrystal = self.__gameEngine.getTeamJewel(self.getColor())
        maxTake = self.__maxJewels - self.__gem - self.__crystal
        gem, crystal = 0, 0
        while (gem+crystal) > 2 or (gem+crystal) <= 0 or \
                (gem+crystal) > maxTake or gem > teamGem or crystal > teamCrystal:
            print("TeamGem:{}, TeamCrystal:{}, Max Take:{}".format(teamGem, teamCrystal, maxTake, 2))
            gem = int(input("No. of Gem:"))
            crystal = int(input("No. of Cry:"))
        for i in range(gem):
            self.__gem += 1
            self.__gameEngine.delJewel(gem=True, isRed=self.getColor())
        for i in range(crystal):
            self.__crystal += 1
            self.__gameEngine.delJewel(gem=False, isRed=self.getColor())

    def __specialBuy(self):
        self.__gameEngine.drawCards(3, True, self.getId())
        self.__gameEngine.addJewel(True, self.getColor())
        self.__gameEngine.addJewel(False, self.getColor())

    def __specialSyn(self):
        teamGem, teamCrystal = self.__gameEngine.getTeamJewel(self.getColor())
        self.__gameEngine.drawCards(3, True, self.getId())
        gem, crystal = 0, 0
        while (gem+crystal) != 3 or gem > teamGem or crystal > teamCrystal:
            print("TeamGem:{}, TeamCrystal:{}".format(teamGem, teamCrystal))
            gem = int(input("No. of Gem:"))
            crystal = int(input("No. of Cry:"))
        for i in range(gem):
            self.__gameEngine.delJewel(True, self.getColor())
        for i in range(crystal):
            self.__gameEngine.delJewel(False, self.getColor())
        self.__gameEngine.addAgrail(self.getColor())

    def __magic(self):
        raise

    def __checkShield(self):
        """return hit or not"""
        if len(self.__basicEffect["shield"]) != 0:
            self.__gameEngine.removeCards(self.getId(), [self.__basicEffect["shield"].pop()], False, True)
            return False
        else:
            return True

    def __createInfo(self, typ, frm, to, element, value, gem, healable=1e5):
        Info = {
            "type": typ,
            "from": frm,
            "to": to,
            "element": element,
            "counterable": 0 if element == "darkness" else 1, # force = 2
            "value": value,
            "gem": gem,
            "healable": healable
        }
        return Info

    #############################################
    def respondForAttackOrCounterLaunch(self, info):
        pass

    def respondForAttackOrCounterHit(self, info):
        pass

    def respondForAttackOrCounterMiss(self, info):
        pass

    def respondForTimeLine3(self, info):
        pass

    def respondForTimeLine4(self, info):
        pass

    def respondForTimeLine5(self, info):
        pass
    
    def respondForTimeLine6(self, info):
        pass