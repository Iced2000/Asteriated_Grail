

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
        pass

    def isAttack(self):
        return self._type == "attack"
        
    def forCounter(self, element):
        return (self.isAttack() and (self.isDark() or self._element == element)) or self.isLight()

    def isDark(self):
        return self._element == "darkness"

    def isLight(self):
        return self._element == "light"

    def getElement(self):
        return self._element

        