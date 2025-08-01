from colorama import Fore, Style
from game_utils import colored_text

# ====== Item Classes ======
class Potion:
    def __init__(self, heal_amount=30):
        self.name = "Health Potion"
        self.heal_amount = heal_amount
    
    def use(self, character):
        old_hp = character.hp
        character.hp = min(character.max_hp, character.hp + self.heal_amount)
        healed = character.hp - old_hp
        print(colored_text(f"🧪 {character.name} drinks a potion and heals {healed} HP!", Fore.GREEN, Style.BRIGHT))

class Bomb:
    def __init__(self, damage=25):
        self.name = "Explosive Bomb"
        self.damage = damage
    
    def use(self, user, target):
        # Bomb always hits
        final_damage = max(0, self.damage - target.defense // 2)  # Armor partially protects
        target.hp -= final_damage
        user.hp -= 5  # Self damage from explosion
        print(colored_text(f"💣 {user.name} throws a bomb! Deals {final_damage} damage to {target.name}!", Fore.RED, Style.BRIGHT))
        print(colored_text(f"💥 {user.name} takes 5 blast damage!", Fore.YELLOW))