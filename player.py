
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
        self._basicEffect = []
        self._weak = []
        self._shield = []
        self._poison = []

    def addHandCards(self, cards, harmed):
        self._cards.extend(cards)
        removeNum = len(self._cards) - self._maxCards
        if removeNum > 0:
            tmpNo = []
            for ca in self._cards: print(ca)
            for i in range(removeNum):
                dis = int(input("discard: "))
                assert(dis in range(len(self._cards)))
                tmpNo.append(dis)
            self.removeHandCards(tmpNo, show=False)
        return removeNum

    def removeHandCards(self, discardNo, show):
        discards = [v for i,v in enumerate(self._cards) if i in discardNo]
        self._cards = [v for i,v in enumerate(self._cards) if i not in discardNo]
        self._gameEngine.removeCards(self.getId(), discards, show)

    def getId(self):
        return self._id

    def getColor(self):
        return self._isRed

    def getActionAllowInfo(self, teamColor):
        info = {
            "attack": teamColor != self._isRed,
            "weak":   len(self._weak) == 0,
            "shield": len(self._shield) == 0,
            "poison": True,
        }
        return info

    def getCounterAllowInfo(self, teamColor, prevID):
        info = {
            "counter": teamColor != self._isRed and prevID != self._id
        }
        return info

    def roundStart(self):
        pass

    def beforeAction(self):
        pass
        
    def action(self, allowInfo):
        for ca in self._cards: print(ca)
        cardNo = int(input("choose 1 card (0~{}): ".format(len(self._cards)-1)))
        assert(cardNo >= 0 and cardNo <len(self._cards))
        if self._cards[cardNo].isAttack():
            self._attack(cardNo, allowInfo["attack"])

    def _attack(self, cardNo, candidate):
        target = int(input("target" + str(candidate) + ": "))
        assert(target in candidate)
        element = self._cards[cardNo].getElement()
        info = self.createAttackOrCounterInfo(
                "attack", self.getId(), 
                target, element, 2, True)
        self.removeHandCards([cardNo], True)
        self._gameEngine.attackOrCounter(info)

    def _magic(self):
        pass

    def _special(self):
        pass

    def roundEnd(self):
        pass

    def counter(self, info):
        """return hit, counterInfo"""
        if info["counterable"] == 2:
            return True, None
        elif info["counterable"] == 1:
            avail = self._getAvailCards("forCounter", info["element"])
            cardNo = int(input("Avail " + str(avail) + ": "))
            if cardNo in avail:
                element = self._cards[cardNo].getElement()

                if element == "light":
                    self.removeHandCards([cardNo], True)
                    return False, None
                    
                target = int(input("target" + str(info["counter"]) + ": "))
                assert(target in info["counter"])

                counterInfo = self.createAttackOrCounterInfo(
                    "counter", self.getId(), 
                    target, element, 2, False)
                self.removeHandCards([cardNo], True)
                return False, counterInfo
            else:
                return self.checkShield(), None
        else:
            avail = self._getAvailCards("isLight")
            cardNo = int(input("light " + str(avail) + ": "))
            if cardNo in avail:
                self.removeHandCards([cardNo], True)
                return False, None
            else:
                return self.checkShield(), None

    def _getAvailCards(self, funcName, *arg, **kwarg):
        print("Hand cards:")
        for ca in self._cards: print(ca)
        avail = []
        for i in range(len(self._cards)):
            if getattr(self._cards[i], funcName)(*arg, **kwarg):
                avail.append(i)
        return avail
    
    def checkShield(self):
        """return hit or not"""
        if len(self._shield) != 0:
            self._gameEngine.removeCards(self.getId(), [self._shield.pop()], False)
            return False
        else:
            return True

    def createAttackOrCounterInfo(self, _type, frm, to, element, value, gem):
        Info = {
            "type": _type,
            "from": frm,
            "to": to,
            "element": element,
            "counterable": 0 if element == "darkness" else 1, # force = 2
            "value": value,
            "gem": gem,
        }
        return Info

    def useHeal(self, info):
        if self._heal:
            healNum = int(input("use heal ("+str(self._heal)+"): "))
            assert(healNum<=self._heal and healNum>=0)
            info["value"] -= healNum
            self._heal -= healNum
        else:
            return

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