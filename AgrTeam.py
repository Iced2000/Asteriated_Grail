import character.AgrJewel as AgrJewel

class AgrTeam(object):
    def __init__(self, isRed, players, gem=0, crystal=0, morale=15, grail=0):
        self._color = isRed
        self._jewel = AgrJewel.AgrJewel(maxJewel=5)
        self._morale = morale
        self._grail = grail
        self._players = players

    def __str__(self):
        return "{}\tMorale:{}, Grail:{}\n".format(str(self._jewel), self._morale, self._grail)

    def checkEnd(self):
        return self._grail == 5 or self._morale <= 0

    def addMorale(self, num):
        self._morale += num
        return self.checkEnd()

    def addGrail(self, num):
        self._grail += num
        return self.checkEnd()

    def addJewel(self, target=(0, 0)):
        self._jewel.addJewel(target)

    def checkTotalJewel(self, num):
        return self._jewel.checkTotalJewel(num)

    def checkJewel(self, target, force=False):
        return self._jewel.checkJewel(target, force)

    def getTotalJewelCombination(self, num, force=False):
        return self._jewel.getTotalJewelCombination(num, force)

if __name__ == '__main__':
    t = AgrTeam(True, 1, 3, 2)
    t.addJewel((1, 1))
    print(t)


    
