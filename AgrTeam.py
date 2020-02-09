import character.utils as utils

class AgrTeam(object):
    def __init__(self, isRed, players, gem=0, crystal=0, morale=15, grail=0):
        self._color = isRed
        self._gem = gem
        self._crystal = crystal
        self._morale = morale
        self._grail = grail
        self._players = players
        self._maxJewel = 5

    def __str__(self):
        return "\tGem:{}, Crystal:{}\n\tMorale:{}, Grail:{}\n".format(
            self._gem, self._crystal, self._morale, self._grail)

    def checkEnd(self):
        return self._grail == 5 or self._morale <= 0

    def addMorale(self, num):
        self._morale += num
        return self.checkEnd()

    def addGrail(self, num):
        self._grail += num
        return self.checkEnd()

    def getJewel(self):
        return (self._gem, self._crystal)

    def addJewel(self, target=(0, 0)):
        self._gem, self._crystal = utils.addJewel(self.getJewel(), target, self._maxJewel)
        
    def checkTotalJewel(self, num):
        return utils.checkTotalJewel(self.getJewel(), num)

    def checkJewel(self, target, force=False):
        return utils.checkJewel(self.getJewel(), target, force)

    def getJewelCombination(self, num, force=False):
        return utils.getJewelCombination(self.getJewel(), num, force)

if __name__ == '__main__':
    t = AgrTeam(True, 1, 3, 2)
    t.addJewel((1, 1))
    print(t)


    
