# models/Jewel.py

class AgrJewel:
    def __init__(self, maxJewel=5):
        self._gem = 0
        self._crystal = 0
        self._max_jewel = maxJewel

    def can_add(self, gem_add=0, crystal_add=0):
        return (self._gem + gem_add + self._crystal + crystal_add) <= self._max_jewel
    
    def can_remove(self, gem_remove=0, crystal_remove=0):
        return self._gem >= gem_remove and self._crystal >= crystal_remove
    
    def add_jewel(self, gem_add=0, crystal_add=0):
        if self.can_add(gem_add, crystal_add):
            self._gem += gem_add
            self._crystal += crystal_add
        else:
            raise ValueError("Cannot add jewels beyond the maximum limit.")

    def remove_jewel(self, gem_remove=0, crystal_remove=0):
        if self.can_remove(gem_remove, crystal_remove):
            self._gem -= gem_remove
            self._crystal -= crystal_remove
        else:
            raise ValueError("Not enough jewels to remove.")
        
    def get_jewel_combination(self, min_num, max_num, gem_min=0, crystal_min=0):
        if max_num < gem_min + crystal_min or max_num > self._max_jewel:
            raise ValueError("Invalid maximum number of jewels.")
        if gem_min > self._gem or crystal_min > self._crystal:
            raise ValueError("Not enough jewels to remove.")
        
        combinations = []
        for total_jewels in range(max(min_num, gem_min + crystal_min), min(max_num, self.total_jewels()) + 1):
            for gem in range(max(gem_min, total_jewels - self._crystal), min(self._gem, total_jewels - crystal_min) + 1):
                crystal = total_jewels - gem
                if crystal >= crystal_min and gem <= self._gem and crystal <= self._crystal:
                    combinations.append((gem, crystal))
        
        return combinations

    def total_jewels(self):
        return self._gem + self._crystal
    
    def __str__(self):
        return f"{self._gem}/{self._crystal}"