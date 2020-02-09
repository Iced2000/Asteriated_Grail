TAKE = 100
BUY = 200
SYN = 300

def askBinary(msg):
    act = input("{} or not [Y/N]".format(msg))
    if act in "Yy":
        return True
    elif act in "Nn":
        return False
    else:
        print("invalid input")
        raise

def askSelection(msg, avail, num, allowOutOfIdx=False):
    "return selction in avail or not, selection"
    tmp = []
    print("Avail: {}, choose {} of them".format(str(avail), num))
    for i in range(num):
        ipt = int(input(msg))
        if not allowOutOfIdx:
            assert(ipt in range(len(avail)))
        elif ipt not in range(len(avail)):
            return False, []
        tmp.append(avail[ipt])
    if num == 1:
        return True, tmp[0]
    else:
        return True, tmp

def askRange(msg, mini, maxi):
    print("range from {} to {}".format(mini, maxi))
    num = int(input(msg))
    assert(num <= maxi and num >= mini)
    return num

def checkAtt(player, info):
    return info["from"] == player.getId() and info["type"] == "attack"

def checkAoC(player, info):
    return info["from"] == player.getId() and info["type"] in ["attack", "counter"]


########################### Jewel ################################

def checkTotalJewel(jewel, num):
    return jewel[0] + jewel[1] >= num

def checkJewel(jewel, target, force=False):
    if force:
        return jewel[0] >= target[0] and jewel[1] >= target[1]
    else:
        return jewel[0] >= target[0] and jewel[0] + jewel[1] >= target[0] + target[1]

def getTotalJewelCombination(jewel, num, force=False):
    res = []
    startPoint = 1 if not force else num
    for i in range(startPoint, num + 1):
        for j in range(i + 1):
            tmp = (j, i - j)
            if checkJewel(jewel, tmp, force=True):
                res.append(tmp)
    return res

def getJewelCombination(jewel, target):
    comb = []
    candidate = getTotalJewelCombination(jewel, target[0] + target[1], force=True)
    for candi in candidate:
        if checkJewel(candi, target):
            comb.append(candi)
    return comb

def addJewel(jewel, target, maxJewel):
    resGem, resCrys = jewel
    prevGem, prevCrys = jewel

    resGem += target[0]
    resCrys += target[1]

    if resGem + resCrys > maxJewel:
        resGem = min(resGem, maxJewel - min(prevCrys, resCrys))
        resCrys = maxJewel - resGem
    return (resGem, resCrys)