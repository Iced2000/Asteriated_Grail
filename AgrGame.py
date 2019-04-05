import player
import card

class AgrGame(object):
    def __init__(self):
        self._pile = card.AgrCardCollection("card/cardDB.txt")

        self._blueGem = 0
        self._blueCrystal = 0
        self._blueMorale = 15
        self._blueGrail = 0

        self._redGem = 0
        self._redCrystal = 0
        self._redMorale = 15
        self._redGrail = 0
        
        self._seat = {
            0: player.BasePlayer(self, 0, True),
            1: player.BasePlayer(self, 1, False),
            2: player.BasePlayer(self, 2, True),
            3: player.BasePlayer(self, 3, True),
            4: player.BasePlayer(self, 4, False),
            5: player.BasePlayer(self, 5, False),
        }
        self._currentPlayerID = 0
        self._playerNum = len(self._seat)

        for i in range(self._playerNum):
            self.drawCards(num=4, harmed=False, _id=i)

    def __str__(self):
        return "blue_{}_{}_{}_{}_red_{}_{}_{}_{}".format(
            self._blueGem, self._blueCrystal, self._blueMorale, self._blueGrail,
            self._redGem, self._redCrystal, self._redMorale, self._redGrail)

    def run(self):
        while(True):
            print(self)
            currPlayer = self._seat[self._currentPlayerID]
            self._roundStartPhase(currPlayer)
            self._beforeActionPhase(currPlayer)
            self._actionPhase(currPlayer)
            self._roundEndPhase(currPlayer)
            print()

            self._currentPlayerID += 1
            if self._currentPlayerID == self._playerNum:
                self._currentPlayerID = 0

    def drawCards(self, num, harmed, _id):
        overflow = self._seat[_id].addHandCards(self._pile.deal(num), harmed)
        if harmed:
            if overflow > 0:
                self.adjustMorale(overflow, self._seat[_id].getColor())
        else:
            return

    def removeCards(self, playerID, cards, show):
        if show:
            pass
        else:
            pass
        self._pile.recycle(cards)

    def adjustMorale(self, num, isRed):
        if isRed:
            self._redMorale -= num
        else:
            self._blueMorale -= num

    def addJewel(self, gem, isRed):
        if isRed:
            if self._redGem + self._redCrystal == 5:
                return
            if gem: self._redGem += 1
            else:   self._redCrystal += 1
        else:
            if self._blueGem + self._blueCrystal == 5:
                return
            if gem: self._blueGem += 1
            else:   self._blueCrystal += 1
        return

    def getPlayer(self):
        return self._seat

    def _roundStartPhase(self, player):
        player.roundStart()

    def _beforeActionPhase(self, player):
        player.beforeAction()

    def _actionPhase(self, player):
        player.action(self._processAllowInfo(dict(), "getActionAllowInfo", player.getColor()))

    def _roundEndPhase(self, player):
        player.roundEnd()

    def _processAllowInfo(self, processedInfo, funcName, *args):
        tmpInfo = getattr(self._seat[0], funcName)(*args)
        for key in tmpInfo.keys():
            processedInfo[key] = []
            if tmpInfo[key]:
                processedInfo[key].append(0)

        for i in range(1, self._playerNum):
            tmpInfo = getattr(self._seat[i], funcName)(*args)
            for key in tmpInfo.keys():
                if tmpInfo[key]:
                    processedInfo[key].append(i)
        return processedInfo

    ##########################################################

    def respond(funcName, order=True):
        def outer_d_f(f):
            def d_f(self, *args, **kwargs):
                if order:
                    for playerNo in range(self._playerNum):
                        getattr(self._seat[playerNo], funcName)(*args, **kwargs)
                f(self, *args, **kwargs)
                if not order:
                    for playerNo in range(self._playerNum):
                        getattr(self._seat[playerNo], funcName)(*args, **kwargs)
            return d_f
        return outer_d_f
    
    @respond("respondForAttackOrCounterLaunch")
    def attackOrCounter(self, info):
        self._processAllowInfo(
            info, "getCounterAllowInfo", 
            self._seat[info["to"]].getColor(), info["from"])

        hit, counterInfo = self._seat[info["to"]].counter(info)

        if hit:
            self.attackOrCounterHit(info)
        else:
            self.attackOrCounterMiss(info)
            if counterInfo is not None:
                self.attackOrCounter(counterInfo)

    @respond("respondForAttackOrCounterHit")
    def attackOrCounterHit(self, info):
        self.addJewel(info["gem"], self._seat[info["from"]].getColor())
        self.calculateDamage(info)

    @respond("respondForAttackOrCounterMiss")
    def attackOrCounterMiss(self, info):
        pass

    ################################################
    @respond("respondForTimeLine3")
    def calculateDamage(self, info):
        self.askForHeal(info)

    @respond("respondForTimeLine4")
    def askForHeal(self, info):
        self._seat[info["to"]].useHeal(info)
        self.calculateTotalDamage(info)

    @respond("respondForTimeLine5")
    def calculateTotalDamage(self, info):
        self.getDamage(info)

    @respond("respondForTimeLine6", False)
    def getDamage(self, info):
        self.drawCards(info["value"], True, info["to"])

if __name__ == '__main__':
    game = AgrGame()
    game.run()