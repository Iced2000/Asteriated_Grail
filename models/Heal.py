class Heal:
    def __init__(self, max_amount=2):
        self.max_amount = max_amount
        self.amount = 0

    def add(self, amount):
        if self.amount + amount <= self.max_amount:
            self.amount += amount
        else:
            self.amount = self.max_amount

    def remove(self, amount):
        if self.amount - amount >= 0:
            self.amount -= amount
        else:
            self.amount = 0

    def get_amount(self):
        return self.amount
    
    def __str__(self):
        return f"Heal: {self.amount}"

