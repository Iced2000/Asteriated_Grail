from . import AgrCard
import random

class AgrCardCollection(object):
     
    def __init__(self, path):
        self._cards = []
        self._discards = []

        file = open(path, 'r', encoding="UTF-8")
        lines = file.readlines()
        file.close()

        for line in lines:
            self._cards.append(AgrCard.AgrCard(*line.split()))
        self._shuffle()

    def deal(self, num):
        tmpCards = []
        for i in range(num):
            try:
                tmpCards.append(self._cards.pop())
            except:
                self._cards.extend(self._discards)
                self._discards = []
                self._shuffle()
                tmpCards.append(self._cards.pop())
        return tmpCards

    def recycle(self, cards):
        self._discards.extend(cards)

    def _shuffle(self):
        random.shuffle(self._cards)
        

if __name__ == '__main__':
    AgrCardCollection()
