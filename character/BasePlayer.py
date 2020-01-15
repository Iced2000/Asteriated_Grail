TAKE = 100
BUY = 200
SYN = 300

class BasePlayer(object):

    def __init__(self, gameEngine, respond, idx, isRed):
        self._id = idx
        self._gameEngine = gameEngine
        self._respond = respond
        self._isRed = isRed
        self._ATK = 2
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

    def printHandCards(self):
        print(self)
        print("Player {}'s Hand cards:".format(self.getId()))
        for ca in self._cards: print(ca)

    def addHandCards(self, cards, harmed):
        self._cards.extend(cards)
        removeNum = len(self._cards) - self._maxCards
        if removeNum > 0:
            tmpNo = []
            self.printHandCards()
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

    def addJewel(self, isGem):
        if isGem:
            self._gem += 1
        else:
            self._crystal += 1

    def delJewel(self, isGem):
        if isGem:
            self._gem -= 1
        else:
            self._crystal -= 1

    def getId(self):
        return self._id

    def getColor(self):
        return self._isRed

    def allowAttack(self, teamColor):
        return teamColor != self.getColor()

    def allowCounter(self, teamColor, prevID):
        return teamColor != self.getColor() and prevID != self.getId()

    def allowWeak(self):
        return len(self._basicEffect["weak"]) == 0

    def allowShield(self):
        return len(self._basicEffect["shield"]) == 0

    def allowPoison(self):
        return True

    def hasShield(self):
        return True if self._basicEffect["shield"] else False

    def roundStart(self):
        pass

    def beforeAction(self):
        self._checkPoison()
        self._checkWeak()
        
    def action(self):
        self._generalAction = 1 if not self._roundSkip else 0
        
        while self._generalAction + self._attackAction + self._magicAction + self._specialAction:

            if self._generalAction:
                availCard, availMagic, availSP = self._getAvailCards("isNotLight"), self._getAvailMagic(), self._getAvailSP()
            elif self._attackAction:
                availCard, availMagic, availSP = self._getAvailCards("isAttack"), [], []
            elif self._magicAction:
                availCard, availMagic, availSP = self._getAvailCards("isMagicAction"), self._getAvailMagic(), []
            else:
                availCard, availMagic, availSP = [], [], self._getAvailSP()

            print("Available Cards:{}\nAvailable Special:{}".format(str(availCard), str(availSP)))
            actNum = int(input("Action:"))

            if actNum in availCard and self._cards[actNum].isAttack():
                self._attack(actNum)
            elif actNum in availCard:
                self._basicMagic(actNum)
            elif actNum in availSP:
                self._special(actNum)
            elif actNum in availMagic:
                self._magic(actNum)
            else:
                raise

    def roundEnd(self):
        self._roundSkip = False
        self._skillReset()

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
        elif info["counterable"] in [0, 1]:
            cardType = "forCounter" if info["counterable"] == 1 else "isLight"
            availCard = self._getAvailCards(cardType, info["card"].getElement())
            cardNum = int(input("Avail " + str(availCard) + ": "))

            if cardNum in availCard:
                if self._cards[cardNum].getElement() == "light":
                    counterInfo = None
                else:
                    target = int(input("target" + str(info["candidate"]) + ": "))
                    assert(target in info["candidate"])

                    counterInfo = self._createInfo(
                        typ = "counter",
                        frm = self.getId(),
                        to = target,
                        card = self._cards[cardNum], 
                        value = 2,
                        gem = False,
                    )
                self.removeHandCards([cardNum], show=True)
                return False, counterInfo
            else:
                return self._checkShield(info["shieldable"]), None
        else:
            raise

    def missile(self, info):
        availCard = self._getAvailCards("forMissileCounter")
        cardNum = int(input("Avail " + str(availCard) + ": "))
        if cardNum in availCard:
            if self._cards[cardNum].getElement() == "light":
                missileInfo = None
            else:
                target = int(input("target" + str(info["candidate"]) + ": "))
                assert(target in info["candidate"])

                missileInfo = self._createInfo(
                    typ = "magic",
                    frm = self.getId(),
                    to = target,
                    card = self._cards[cardNum], 
                    value = info["value"],
                    gem = None,
                )
            self.removeHandCards([cardNum], True)
            return False, missileInfo
        else:
            return self._checkShield(), None

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

    def _checkPoison(self):
        if self._basicEffect["poison"]:
            info = self._createInfo(
                typ = "magic",
                frm = None,
                to = self.getId(),
                card = None,
                value = len(self._basicEffect["poison"]),
                gem = None,
            )
            self._gameEngine.removeCards(self.getId(), 
                self._basicEffect["poison"], False, True)
            self._basicEffect["poison"] = []
            self._gameEngine.poison(info)

    def _checkWeak(self):
        if self._basicEffect["weak"]:
            self._gameEngine.removeCards(self.getId(), 
                self._basicEffect["weak"], False, True)
            self._basicEffect["weak"] = []
            ps = input("Weak! Pass or not?[Y/N]")
            if ps == 'Y':
                self._roundSkip = True
            else:
                self._gameEngine.drawCards(3, True, self.getId())

    def _getAvailCards(self, funcName, *arg, **kwarg):
        self.printHandCards()
        avail = []
        for i in range(len(self._cards)):
            if getattr(self._cards[i], funcName)(*arg, **kwarg):
                avail.append(i)
        return avail

    def _getAvailSP(self):
        availSP = []
        teamGem, teamCrystal = self._gameEngine.getTeamJewel(self.getColor())
        if (teamGem or teamCrystal) and ((self._gem + self._crystal) < self._maxJewels):
            availSP.append(TAKE)
        if (self._maxCards - len(self._cards)) >= 3:
            availSP.append(BUY)
            if (teamGem + teamCrystal) >= 3:
                availSP.append(SYN)
        return availSP

    def _getAvailMagic(self):
        return []

    def _attack(self, cardNum):
        candidate = self._gameEngine.getCandidate("attack", frm=self.getId())
        target = int(input("target" + str(candidate) + ": "))

        if target in candidate:
            if self._generalAction > 0:
                self._generalAction -= 1
            elif self._attackAction > 0:
                self._attackAction -= 1
            else:
                raise
            info = self._createInfo(
                        typ = "attack",
                        frm = self.getId(),
                        to = target,
                        card = self._cards[cardNum],
                        value = self._ATK,
                        gem = True,
                    )
            self.removeHandCards([cardNum], show=True)
            self._gameEngine.attackOrCounter(info)

            self._postAttack()
        else:
            print("restart")

    def _postAttack(self):
        pass

    def _basicMagic(self, cardNum):
        magicType = self._cards[cardNum].getMagicName()
        candidate = self._gameEngine.getCandidate(magicType, frm=self.getId())
        target = int(input("target" + str(candidate) + ": "))

        if target in candidate:
            if self._generalAction > 0:
                self._generalAction -= 1
            elif self._magicAction > 0:
                self._magicAction -= 1
            else:
                raise

            if magicType in ["weak", "shield", "poison"]:
                self._gameEngine.addBasicEffect(magicType, target, self._cards[cardNum], self.getId())
                self.removeHandCards([cardNum], show=True, recycle=False)

            elif magicType == "missile":
                info = self._createInfo(
                    typ = "magic",
                    frm = self.getId(),
                    to = target,
                    card = self._cards[cardNum], 
                    value = 2,
                    gem = None,
                )
                self.removeHandCards([cardNum], True)
                self._gameEngine.missile(info)
            else:
                raise

            self._postMagic()
        else:
            print("restart")

    def _postMagic(self):
        pass

    def _special(self, spType):
        if self._generalAction > 0:
            self._generalAction -= 1
        elif self._specialAction > 0:
            self._specialAction -= 1
        else:
            raise

        if spType == TAKE:
            self._specialTake()
        elif spType == BUY:
            self._specialBuy()
        elif spType == SYN:
            self._specialSyn()
        else:
            raise

    def _specialTake(self):
        teamGem, teamCrystal = self._gameEngine.getTeamJewel(self.getColor())
        maxTake = self._maxJewels - self._gem - self._crystal
        gem, crystal = 0, 0
        while (gem+crystal) > 2 or (gem+crystal) <= 0 or \
                (gem+crystal) > maxTake or gem > teamGem or crystal > teamCrystal:
            print("TeamGem:{}, TeamCrystal:{}, Max Take:{}".format(teamGem, teamCrystal, maxTake, 2))
            gem = int(input("No. of Gem:"))
            crystal = int(input("No. of Cry:"))
        for i in range(gem):
            self.addJewel(isGem=True)
            self._gameEngine.delJewel(gem=True, isRed=self.getColor())
        for i in range(crystal):
            self.addJewel(isGem=False)
            self._gameEngine.delJewel(gem=False, isRed=self.getColor())

    def _specialBuy(self):
        self._gameEngine.drawCards(3, True, self.getId())
        self._gameEngine.addJewel(True, self.getColor())
        self._gameEngine.addJewel(False, self.getColor())

    def _specialSyn(self):
        teamGem, teamCrystal = self._gameEngine.getTeamJewel(self.getColor())
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

    def _magic(self):
        raise

    def _checkShield(self, shieldable=True):
        """return hit or not"""
        if not shieldable:
            return True
        elif len(self._basicEffect["shield"]) != 0:
            self._gameEngine.removeCards(self.getId(), [self._basicEffect["shield"].pop()], False, True)
            return False
        else:
            return True

    def _createInfo(self, typ, frm, to, card, value, gem, healable=1e5):
        Info = {
            "type": typ,
            "from": frm,
            "to": to,
            "card": card,
            "counterable": 0 if card.isDark() else 1, # force = 2
            "value": value,
            "gem": gem,
            "healable": healable,
            "shieldable": True,
        }
        return Info

    def _skillReset(self):
        pass

    def _useJewel(self, gem, crystal, force=False):
        assert(gem <= self._gem and (gem + crystal) <= (self._gem + self._crystal))
        if force:
            assert(crystal <= self._crystal)
            gemUse = gem
            crysUse = crystal
        else:
            gemUse, crysUse = 0, 0
            while (gemUse+crysUse) != (gem+crystal) or gemUse > self._gem or crysUse > self._crystal or gemUse < gem:
                print("Total usage: Gem:{}, Crystal:{}\nYour Gem:{}, Crystal:{}".format(gem, crystal, self._gem, self._crystal))
                gemUse = int(input("No. of Gem:"))
                crysUse = int(input("No. of Cry:"))

        for i in range(gemUse):
            self.delJewel(isGem=True)
        for i in range(crysUse):
            self.delJewel(isGem=False)

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