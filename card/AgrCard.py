

class AgrCard(object):
    
    def __init__(self, _id, _type, _element, 
                _property, _name, _uniq1=None, _uniq2=None):
        self._id       = _id
        self._type     = _type # attack or magic
        self._element  = _element
        self._property = _property
        self._name     = _name
        self._uniq1    = _uniq1
        self._uniq2    = _uniq2

    def __str__(self):
        return "{}_{}_{}_{}_{}".format(
            self._type, self._element, self._name, self._uniq1, self._uniq2)


    def isMagic(self):
        return self._type == "magic"

    def isAttack(self):
        return self._type == "attack"
        
    def forCounter(self, element):
        return (self.isAttack() and (self.isDark() or self._element == element)) or self.isLight()

    def forMissileCounter(self):
        return self.isMissile() or self.isLight()

    def isDark(self):
        return self._element == "darkness"

    def isLight(self, element=None):
        return self._element == "light"

    def isWind(self):
        return self._element == "wind"

    def isWindAttack(self):
        return self.isWind() and self.isAttack()

    def isNotLight(self):
        return not self.isLight()

    def isMagicAction(self):
        return self.isMagic() and self.isNotLight()

    def isWeak(self):
        return self._name == "虛弱"

    def isMissile(self):
        return self._name == "魔彈"

    def isShield(self):
        return self._name == "聖盾"

    def isPoison(self):
        return self._name == "中毒"

    def getMagicName(self):
        if self.isLight():
            return "light"
        elif self.isWeak():
            return "weak"
        elif self.isMissile():
            return "missile"
        elif self.isShield():
            return "shield"
        elif self.isPoison():
            return "poison"
        else:
            print("Invalid Type")
            raise

    def getElement(self):
        return self._element

    ########### unique skills #############

    def isJiFengJi(self):
        return "疾風技" in [self._uniq1, self._uniq2]

    def isLieFengJi(self):
        return "烈風技" in [self._uniq1, self._uniq2]