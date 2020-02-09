import character
import card
import Respond
import AgrTeam

class AgrGame(object):
    def __init__(self):
        self._pile = card.AgrCardCollection("card/cardDB.txt")
        self._respond = Respond.Respond()

        self._redTeam = AgrTeam.AgrTeam(isRed=True, players=[0, 2, 3])
        self._blueTeam = AgrTeam.AgrTeam(isRed=True, players=[1, 4, 5])
        
        self._seat = {
            0: character.BasePlayer(self, self._redTeam, self._respond, 0, True),
            1: character.BasePlayer(self, self._blueTeam, self._respond, 1, False),
            2: character.BasePlayer(self, self._redTeam, self._respond, 2, True),
            3: character.BasePlayer(self, self._redTeam, self._respond, 3, True),
            4: character.BasePlayer(self, self._blueTeam, self._respond, 4, False),
            5: character.BasePlayer(self, self._blueTeam, self._respond, 5, False),
        }

        self._respond.sortAll()
        self._currentPlayerID = 0
        self._playerNum = len(self._seat)

        for i in range(self._playerNum):
            self.drawCards(num=4, harmed=False, _id=i)

    def __str__(self):
        return "blue\n" + str(self._blueTeam) + "red\n" + str(self._redTeam)

    def run(self):
        while(True):
            print(self)
            currPlayer = self._seat[self._currentPlayerID]
            self.__roundStartPhase(currPlayer)
            self.__beforeActionPhase(currPlayer)
            self.__actionPhase(currPlayer)
            self.__roundEndPhase(currPlayer)
            print()

            self._currentPlayerID = (self._currentPlayerID + 1) % self._playerNum

    def gameEnd(self, isRed):
        team = 'red' if isRed else 'blue'
        print("Congratulation, {} team wins.".format(team))
        exit(0)

    def drawCards(self, num, harmed, _id):
        overflow = self._seat[_id].addHandCards(self._pile.deal(num), harmed)
        if harmed:
            if overflow > 0:
                self.addMorale(-overflow, self._seat[_id].getColor())
        else:
            return

    def removeCards(self, playerID, cards, show, recycle):
        if show:
            for c in cards:
                self._seat[playerID].checkSeal(c.getElement())
        else:
            pass
        if recycle:
            self._pile.recycle(cards)

    def addMorale(self, num, isRed):
        if isRed:
            if self._redTeam.addMorale(num):
                self.gameEnd(False)
        else:
            if self._blueTeam.addMorale(num):
                self.gameEnd(True)

    def addGrail(self, isRed):
        if isRed:
            if self._redTeam.addGrail(1):
                self.gameEnd(True)
        else:
            if self._blueTeam.addGrail(1):
                self.gameEnd(False)

    def addJewel(self, jewel, isRed):
        if jewel == None:
            return
        if isRed:
            self._redTeam.addJewel(jewel)
        else:
            self._blueTeam.addJewel(jewel)

    def getTeamJewel(self, isRed):
        if isRed:
            return self._redGem, self._redCrystal
        else:
            return self._blueGem, self._blueCrystal

    def addBasicEffect(self, effectType, playerNo, card, frm):
        self._seat[playerNo].addBasicEffect(effectType, card)

    def getPlayer(self):
        return self._seat

    def __roundStartPhase(self, player):
        player.roundStart()

    def __beforeActionPhase(self, player):
        player.beforeAction()

    def __actionPhase(self, player):
        player.action()

    def __roundEndPhase(self, player):
        player.roundEnd()

    def getCandidate(self, method, **kwargs):
        candidate = []
        if method == "missile":
            frm = kwargs['frm']
            to = (frm + 1) % self._playerNum
            while self._seat[frm].getColor() == self._seat[to].getColor():
                to = (to + 1) % self._playerNum
            return [to]

        for playerNo in range(self._playerNum):
            if method == "attack":
                if self._seat[playerNo].allowAttack(self._seat[kwargs['frm']].getColor()):
                    candidate.append(playerNo)
            elif method == "counter":
                if self._seat[playerNo].allowCounter(self._seat[kwargs['to']].getColor(), kwargs['frm']):
                    candidate.append(playerNo)
            elif method == "weak":
                if self._seat[playerNo].allowWeak():
                    candidate.append(playerNo)
            elif method == "shield":
                if self._seat[playerNo].allowShield():
                    candidate.append(playerNo)
            elif method == "poison":
                if self._seat[playerNo].allowPoison():
                    candidate.append(playerNo)
            elif method == "allExceptI":
                if self._seat[playerNo].getId() != kwargs['selfId']:
                    candidate.append(playerNo)
            else:
                raise
        return candidate

    ##########################################################

    def respond(funcName, order=True):
        def outer_d_f(f):
            def d_f(self, *args, **kwargs):
                if order:
                    getattr(self._respond, funcName)(*args, **kwargs)
                f(self, *args, **kwargs)
                if not order:
                    getattr(self._respond, funcName)(*args, **kwargs)
            return d_f
        return outer_d_f
    
    @respond("respondTimeLine1")
    def attackOrCounter(self, info):
        info["candidate"] = self.getCandidate("counter", to=info["to"], frm=info["from"])

        hit, counterInfo = self._seat[info["to"]].counter(info)

        if hit:
            info["hit"] = True
            self.attackOrCounterHit(info)
        else:
            info["hit"] = False
            self.attackOrCounterMiss(info)
            if counterInfo is not None:
                self.attackOrCounter(counterInfo)
    
    def missile(self, info):
        info["candidate"] = self.getCandidate("missile", frm=info["to"])
        hit, passInfo = self._seat[info["to"]].missile(info)
        if hit:
            self.missileHit(info)
        else:
            self.missileMiss(info)
            if passInfo is not None:
                self.missile(passInfo)

    @respond("respondTimeLine2")
    def attackOrCounterHit(self, info):
        self.addJewel(info["jewel"], self._seat[info["from"]].getColor())
        self.calculateDamage(info)

    @respond("respondTimeLine2")
    def attackOrCounterMiss(self, info):
        pass

    def missileHit(self, info):
        self.calculateDamage(info)

    def missileMiss(self, info):
        info['value'] += 1

    ################################################
    #@respond("respondForTimeLine3")
    def calculateDamage(self, info):
        self.askForHeal(info)

    #@respond("respondForTimeLine4")
    def askForHeal(self, info):
        self._seat[info["to"]].useHeal(info)
        self.calculateTotalDamage(info)

    #@respond("respondForTimeLine5")
    def calculateTotalDamage(self, info):
        self.getDamage(info)

    #@respond("respondForTimeLine6", False)
    def getDamage(self, info):
        self.drawCards(info["value"], True, info["to"])

if __name__ == '__main__':
    game = AgrGame()
    game.run()