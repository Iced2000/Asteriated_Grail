TimeLine1Order = [
    "FastWind",
    "HardWind",
    "BloodSword",
    "BloodRoar",
    "AccurateShot",
    "HolySword",
    "ThunderBolt",

]
TimeLine2Order = [
    "PenetrateShot",
    "Tear",
]
TimeLine3Order = []
TimeLine4Order = []
TimeLine5Order = []
TimeLine6Order = []

class Respond(object):
    def __init__(self):
        self.TimeLine1 = []
        self.TimeLine2 = []
        self.TimeLine3 = []
        self.TimeLine4 = []
        self.TimeLine5 = []
        self.TimeLine6 = []

    def addTimeLine1(self, player, funcName):
        self.TimeLine1.append((funcName, player))

    def addTimeLine2(self, player, funcName):
        self.TimeLine2.append((funcName, player))

    def addTimeLine3(self, player, funcName):
        self.TimeLine3.append((funcName, player))

    def addTimeLine4(self, player, funcName):
        self.TimeLine4.append((funcName, player))

    def addTimeLine5(self, player, funcName):
        self.TimeLine5.append((funcName, player))

    def addTimeLine6(self, player, funcName):
        self.TimeLine6.append((funcName, player))

    def sortAll(self):
        self.TimeLine1.sort(key = lambda i: TimeLine1Order.index(i[0]))
        self.TimeLine2.sort(key = lambda i: TimeLine2Order.index(i[0]))
        self.TimeLine3.sort(key = lambda i: TimeLine3Order.index(i[0]))
        self.TimeLine4.sort(key = lambda i: TimeLine4Order.index(i[0]))
        self.TimeLine5.sort(key = lambda i: TimeLine5Order.index(i[0]))
        self.TimeLine6.sort(key = lambda i: TimeLine6Order.index(i[0]))

    def respondTimeLine1(self, *args, **kwargs):
        for fn, player in self.TimeLine1:
            getattr(player, fn)(*args, **kwargs)

    def respondTimeLine2(self, *args, **kwargs):
        for fn, player in self.TimeLine2:
            getattr(player, fn)(*args, **kwargs)

    def respondTimeLine3(self, *args, **kwargs):
        for fn, player in self.TimeLine3:
            getattr(player, fn)(*args, **kwargs)

    def respondTimeLine4(self, *args, **kwargs):
        for fn, player in self.TimeLine4:
            getattr(player, fn)(*args, **kwargs)

    def respondTimeLine5(self, *args, **kwargs):
        for fn, player in self.TimeLine5:
            getattr(player, fn)(*args, **kwargs)

    def respondTimeLine6(self, *args, **kwargs):
        for fn, player in self.TimeLine6:
            getattr(player, fn)(*args, **kwargs)
        