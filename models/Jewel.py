# models/Jewel.py

class AgrJewel:
    def __init__(self, maxJewel=5):
        self.gem = 0
        self.crystal = 0
        self.max_jewel = maxJewel

    def add_jewel(self, gem_add=0, crystal_add=0):
        if self.can_add(gem_add, crystal_add):
            self.gem += gem_add
            self.crystal += crystal_add
            print(f"Added {gem_add} gem(s) and {crystal_add} crystal(s).")
            return True
        else:
            print("Cannot add jewels beyond the maximum limit.")
            return False

    def can_add(self, gem_add=0, crystal_add=0):
        return (self.gem + gem_add + self.crystal + crystal_add) <= self.max_jewel

    def remove_jewel(self, gem_remove=0, crystal_remove=0):
        if self.gem >= gem_remove and self.crystal >= crystal_remove:
            self.gem -= gem_remove
            self.crystal -= crystal_remove
            print(f"Removed {gem_remove} gem(s) and {crystal_remove} crystal(s).")
            return True
        else:
            print("Not enough jewels to remove.")
            return False

    def __str__(self):
        return f"Gems: {self.gem}, Crystals: {self.crystal}"