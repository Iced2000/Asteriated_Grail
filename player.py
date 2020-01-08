
TAKE = 100
BUY = 200
SYN = 300

class BasePlayer(object):

    def __init__(self, _gameEngine, _id, _isRed):
        self._id = _id
        self._gameEngine = _gameEngine
        self._isRed = _isRed
        self._heal = 0
        self._gem = 0
        self._crystal = 0
        self._cards = []
        self._maxCards = 6
        self._maxJewels = 3
        self._basicEffect = {
            "weak": [],
            "shield": [],
            "poison": [],
        }
        self._generalAction = 0
        self._attackAction = 0
        self._magicAction = 0
        self._specialAction = 0

        self._roundSkip = False

    def __str__(self):
        return "Player {}\n\tGem:{} Crystal:{}\n\tWeak:{} Shield:{} Poison:{}\n\tHeal:{}".format(
            self.getId(), self._gem, self._crystal, len(self._basicEffect["weak"]), 
            len(self._basicEffect["shield"]), len(self._basicEffect["poison"]), self._heal)

    def addHandCards(self, cards, harmed):
        self._cards.extend(cards)
        removeNum = len(self._cards) - self._maxCards
        if removeNum > 0:
            tmpNo = []
            self._printHandCards()
            for i in range(removeNum):
                dis = int(input("discard: "))
                assert(dis in range(len(self._cards)))
                tmpNo.append(dis)
            self.removeHandCards(tmpNo, show=False)
        return removeNum

    def removeHandCards(self, discardNum, show, recycle=True):
        discards = [v for i,v in enumerate(self._cards) if i in discardNum]
        self._cards = [v for i,v in enumerate(self._cards) if i not in discardNum]
        self._gameEngine.removeCards(self.getId(), discards, show, recycle)

    def getId(self):
        return self._id

    def getColor(self):
        return self._isRed

    def allowAttack(self, teamColor):
        return teamColor != self._isRed

    def allowCounter(self, teamColor, prevID):
        return teamColor != self._isRed and prevID != self._id

    def allowWeak(self):
        return len(self._basicEffect["weak"]) == 0

    def allowShield(self):
        return len(self._basicEffect["shield"]) == 0

    def allowPoison(self):
        return True

    def roundStart(self):
        pass

    def beforeAction(self):
        if self._basicEffect["poison"]:
            info = self.createInfo(
                "magic", None,
                self.getId(), None,
                len(self._basicEffect["poison"]), None
            )
            self._gameEngine.removeCards(self.getId(), 
                self._basicEffect["poison"].copy(), False, True)
            self._basicEffect["poison"] = []
            self._gameEngine.poison(info)

        if self._basicEffect["weak"]:
            self._gameEngine.removeCards(self.getId(), 
                [self._basicEffect["weak"].pop()], False, True)
            ps = input("Weak! Pass or not?[Y/N]")
            if ps == 'Y':
                self._roundSkip = True
            else:
                self._gameEngine.drawCards(3, True, self.getId())

    def action(self):
        if not self._roundSkip:
            self._generalAction = 1
        while(self._generalAction + self._attackAction + self._magicAction + self._specialAction):
            if self._generalAction:
                avail = self._getAvailCards("isNotLight")
                availSP = self._getAvailSP()
            elif self._attackAction:
                avail = self._getAvailCards("isAttack")
            elif self._magicAction:
                avail = self._getAvailCards("isMagicAction")
            else:
                availSP = self._getAvailSP()

            print("Available Cards:{}\nAvailable Special:{}".format(str(avail), str(availSP)))
            actNum = int(input("Action:"))
            if actNum in avail:
                if self._cards[actNum].isAttack():
                    actionType = "attack"
                elif self._cards[actNum].isMagicAction():
                    actionType = self._cards[actNum].getMagicName()
                else:
                    raise

                candidate = self._gameEngine.getCandidate(actionType, frm=self.getId())
                target = int(input("target" + str(candidate) + ": "))
                if target in candidate:
                    if self._cards[actNum].isAttack():
                        self.attack(actNum, target)
                    else:
                        self.basicMagic(actNum, target, actionType)
                else:
                    print("restart")
                    continue
            elif actNum in availSP:
                self._special(actNum)
            else:
                raise

    def attack(self, cardNum, target):
        if self._generalAction > 0:
            self._generalAction -= 1
        elif self._attackAction > 0:
            self._attackAction -= 1
        else:
            print("No attack action left!")
            raise
        element = self._cards[cardNum].getElement()
        info = self.createInfo(
                "attack", self.getId(),
                target, element, 2, True)
        self.removeHandCards([cardNum], True)
        self._gameEngine.attackOrCounter(info)

    def basicMagic(self, cardNum, target, actionType):
        if self._generalAction > 0:
            self._generalAction -= 1
        elif self._magicAction > 0:
            self._magicAction -= 1
        else:
            print("No magic action left!")
            raise

        if actionType == "weak" or actionType == "shield" or actionType == "poison":
            self._gameEngine.addBasicEffect(actionType, target, self._cards[cardNum], self.getId())
            self.removeHandCards([cardNum], True, recycle=False)
        elif actionType == "missile":
            info = self.createInfo(
                "magic", self.getId(),
                target, self._cards[cardNum].getElement(),
                2, None
            )
            self.removeHandCards([cardNum], True)
            self._gameEngine.missile(info)
        else:
            raise


    def _special(self, actionType):
        if self._generalAction > 0:
            self._generalAction -= 1
        elif self._specialAction > 0:
            self._specialAction -= 1
        else:
            print("No special action left!")
            raise

        teamGem, teamCrystal = self._gameEngine.getJewel(self.getColor())
        if actionType == TAKE:
            maxTake = self._maxJewels - self._gem - self._crystal
            gem, crystal = 0, 0
            while (gem+crystal) > 2 or (gem+crystal) <= 0 or \
                    (gem+crystal) > maxTake or gem > teamGem or crystal > teamCrystal:
                print("TeamGem:{}, TeamCrystal:{}, Max Take:{}".format(teamGem, teamCrystal, maxTake, 2))
                gem = int(input("No. of Gem:"))
                crystal = int(input("No. of Cry:"))
            for i in range(gem):
                self._gem += 1
                self._gameEngine.delJewel(True, self.getColor())
            for i in range(crystal):
                self._crystal += 1
                self._gameEngine.delJewel(False, self.getColor())

        elif actionType == BUY:
            self._gameEngine.drawCards(3, True, self.getId())
            self._gameEngine.addJewel(True, self.getColor())
            self._gameEngine.addJewel(False, self.getColor())

        elif actionType == SYN:
            self._gameEngine.drawCards(3, True, self.getId())
            gem, crystal = 0, 0
            while (gem+crystal) != 3 or gem > teamGem or crystal > teamCrystal:
                print("TeamGem:{}, TeamCrystal:{}".format(teamGem, teamCrystal))
                gem = int(input("No. of Gem:"))
                crystal = int(input("No. of Cry:"))
            for i in range(gem):
                self._gameEngine.delJewel(True, self.getColor())
            for i in range(crystal):
                self._gameEngine.delJewel(False, self.getColor())
            self._gameEngine.addAgrail(self.getColor())
        else:
            raise

    def roundEnd(self):
        if self._roundSkip:
            self._roundSkip = False
        else:
            pass

    def addBasicEffect(self, effectType, card):
        if effectType == "weak":
            self._basicEffect["weak"].append(card)
        elif effectType == "shield":
            self._basicEffect["shield"].append(card)
        elif effectType == "poison":
            self._basicEffect["poison"].append(card)
        else:
            raise

    def counter(self, info):
        """return hit, counterInfo"""
        if info["counterable"] == 2:
            return True, None
        elif info["counterable"] == 1:
            avail = self._getAvailCards("forCounter", info["element"])
            cardNum = int(input("Avail " + str(avail) + ": "))
            if cardNum in avail:
                element = self._cards[cardNum].getElement()

                if element == "light":
                    self.removeHandCards([cardNum], True)
                    return False, None
                    
                target = int(input("target" + str(info["counter"]) + ": "))
                assert(target in info["counter"])

                counterInfo = self.createInfo(
                    "counter", self.getId(), 
                    target, element, 2, False)
                self.removeHandCards([cardNum], True)
                return False, counterInfo
            else:
                return self.checkShield(), None
        else:
            avail = self._getAvailCards("isLight")
            cardNum = int(input("light " + str(avail) + ": "))
            if cardNum in avail:
                self.removeHandCards([cardNum], True)
                return False, None
            else:
                return self.checkShield(), None

    def missile(self, info):
        avail = self._getAvailCards("forMissileCounter")
        cardNum = int(input("Avail " + str(avail) + ": "))
        if cardNum in avail:
            element = self._cards[cardNum].getElement()

            if element == "light":
                self.removeHandCards([cardNum], True)
                return False, None
                
            target = int(input("target" + str(info["candidate"]) + ": "))
            assert(target in info["candidate"])

            missileInfo = self.createInfo(
                "magic", self.getId(),
                target, element,
                info["value"], None)
            self.removeHandCards([cardNum], True)
            return False, missileInfo
        else:
            return self.checkShield(), None

    def _getAvailCards(self, funcName, *arg, **kwarg):
        self._printHandCards()
        avail = []
        for i in range(len(self._cards)):
            if getattr(self._cards[i], funcName)(*arg, **kwarg):
                avail.append(i)
        return avail

    def _getAvailSP(self):
        availSP = []
        teamGem, teamCrystal = self._gameEngine.getJewel(self.getColor())
        if (teamGem or teamCrystal) and ((self._gem + self._crystal) < self._maxJewels):
            availSP.append(TAKE)
        if (self._maxCards - len(self._cards)) >= 3:
            availSP.append(BUY)
            if (teamGem + teamCrystal) >= 3:
                availSP.append(SYN)
        return availSP

    def checkShield(self):
        """return hit or not"""
        if len(self._basicEffect["shield"]) != 0:
            self._gameEngine.removeCards(self.getId(), [self._basicEffect["shield"].pop()], False, True)
            return False
        else:
            return True

    def createInfo(self, _type, frm, to, element, value, gem, healable=1e5):
        Info = {
            "type": _type,
            "from": frm,
            "to": to,
            "element": element,
            "counterable": 0 if element == "darkness" else 1, # force = 2
            "value": value,
            "gem": gem,
            "healable": healable
        }
        return Info

    def useHeal(self, info):
        if self._heal:
            maxHeal = min(info["value"], self._heal, info["healable"])
            print("max healable:", maxHeal)
            healNum = int(input("use heal: "))
            assert(healNum<=maxHeal and healNum>=0)
            info["value"] -= healNum
            self._heal -= healNum
        else:
            return

    def _printHandCards(self):
        print(self)
        print("Player {}'s Hand cards:".format(self.getId()))
        for ca in self._cards: print(ca)

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