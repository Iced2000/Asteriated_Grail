

class AgrJewel(object):
    def __init__(self, maxJewel, gem=0, crystal=0):
        self._gem = gem
        self._crystal = crystal
        self._maxJewel = maxJewel

    def __str__(self):
        return "\tGem:{}, Crystal:{}\n".format(self._gem, self._crystal)

    def full(self):
        return self._gem + self._crystal >= self._maxJewel

    def residual(self):
        return self._maxJewel - self._gem - self._crystal

    def setMaxJewel(self, maxJewel):
        self._maxJewel = maxJewel

    def checkTotalJewel(self, num):
        return self._gem + self._crystal >= num
    
    def checkJewel(self, target, force=False):
        if force:
            return self._gem >= target[0] and self._crystal >= target[1]
        else:
            return self._gem >= target[0] and self._gem + self._crystal >= target[0] + target[1]
    
    def getTotalJewelCombination(self, num, force=False):
        res = []
        startPoint = 1 if not force else num
        for i in range(startPoint, num + 1):
            for j in range(i + 1):
                tmp = (j, i - j)
                if self.checkJewel(tmp, force=True):
                    res.append(tmp)
        return res
    
    def getJewelCombination(self, target):
        comb = []
        candidate = self.getTotalJewelCombination(target[0] + target[1], force=True)
        for candi in candidate:
            if candi[0] >= target[0] and candi[0] + candi[1] >= target[0] + target[1]:
                comb.append(candi)
        return comb
    
    def addJewel(self, target):
        prevGem, prevCrys = self._gem, self._crystal
        
        self._gem += target[0]
        self._crystal += target[1]
    
        if self._gem + self._crystal > self._maxJewel:
            self._gem = min(self._gem, self._maxJewel - min(prevCrys, self._crystal))
            self._crystal = self._maxJewel - self._gem

    