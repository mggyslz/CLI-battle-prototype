from colorama import Fore, Style
from game_utils import colored_text

# ====== Equipment Class ======
class Equipment:
    def __init__(self, name, attack_boost=0, defense_boost=0, durability=5):
        self.name = name
        self.attack_boost = attack_boost
        self.defense_boost = defense_boost
        self.max_durability = durability
        self.durability = durability
    
    def wear_down(self):
        self.durability -= 1
        if self.durability <= 0:
            print(colored_text(f"💔 {self.name} BROKE!", Fore.RED, Style.BRIGHT))
            self.attack_boost = 0
            self.defense_boost = 0
        elif self.durability == 1:
            print(colored_text(f"⚠️  {self.name} is about to break!", Fore.YELLOW))

    def durability_display(self):
        ratio = self.durability / self.max_durability
        if ratio > 0.6:
            return colored_text(f"[{self.durability}/{self.max_durability}]", Fore.GREEN)
        elif ratio > 0.3:
            return colored_text(f"[{self.durability}/{self.max_durability}]", Fore.YELLOW)
        else:
            return colored_text(f"[{self.durability}/{self.max_durability}]", Fore.RED) 

class ElementalEquipment(Equipment):
    def __init__(self, name, element, attack_boost=0, defense_boost=0, durability=5):
        super().__init__(name, attack_boost, defense_boost, durability)
        self.element = element
        
    def on_equip(self, character):
        super().on_equip(character)
        character.elemental_affinity = self.element
        print(colored_text(
            f"✨ {character.name} gains {self.element} affinity!",
            Fore.MAGENTA, Style.BRIGHT
        ))