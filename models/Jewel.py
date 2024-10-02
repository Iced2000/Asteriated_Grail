# models/Jewel.py

class AgrJewel:
    def __init__(self, interface, maxJewel=5):
        self.gem = 0
        self.crystal = 0
        self.max_jewel = maxJewel
        self.interface = interface

    def add_jewel(self, gem_add=0, crystal_add=0):
        if self.can_add(gem_add, crystal_add):
            self.gem += gem_add
            self.crystal += crystal_add
            self.interface.send_message(f"Added {gem_add} gem(s) and {crystal_add} crystal(s).", debug=True)
            return True
        else:
            self.interface.send_message("Cannot add jewels beyond the maximum limit.", debug=True)
            return False

    def can_add(self, gem_add=0, crystal_add=0):
        return (self.gem + gem_add + self.crystal + crystal_add) <= self.max_jewel

    def remove_jewel(self, gem_remove=0, crystal_remove=0):
        if self.gem >= gem_remove and self.crystal >= crystal_remove:
            self.gem -= gem_remove
            self.crystal -= crystal_remove
            self.interface.send_message(f"Removed {gem_remove} gem(s) and {crystal_remove} crystal(s).", debug=True)
            return True
        else:
            self.interface.send_message("Not enough jewels to remove.", debug=True)
            return False
        
    def get_jewel_combination(self, min_num, max_num, gem_min=0, crystal_min=0):
        if max_num < gem_min + crystal_min or max_num > self.max_jewel:
            return None
        if gem_min > self.gem or crystal_min > self.crystal:
            return None
        
        combinations = []
        for total_jewels in range(max(min_num, gem_min + crystal_min), min(max_num, self.total_jewels()) + 1):
            for gem in range(max(gem_min, total_jewels - self.crystal), min(self.gem, total_jewels - crystal_min) + 1):
                crystal = total_jewels - gem
                if crystal >= crystal_min and gem <= self.gem and crystal <= self.crystal:
                    combinations.append((gem, crystal))
        
        return combinations

    def total_jewels(self):
        return self.gem + self.crystal
    
    def __str__(self):
        return f"{self.gem}/{self.crystal}"