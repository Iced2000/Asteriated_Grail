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
            assert(ipt in avail)
        elif ipt not in avail:
            return False, []
        tmp.append(ipt)
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