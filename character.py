from colorama import Fore, Style
from game_utils import colored_text, print_separator
from items import Potion, Bomb

# ====== Character Class ======
class Character:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.equipment = None
        self.items = [Potion(), Bomb()]  # Start with some items
        self.status_effects = []
        self.elemental_affinity = None  # 'fire', 'ice', 'lightning', etc
        self.combo_counter = 0
        self.last_move = None
        self.block_chance = 0  # Base block chance
    
    def equip(self, equipment):
        self.equipment = equipment
        print(colored_text(f"⚔️ {self.name} equips {equipment.name}!", Fore.CYAN, Style.BRIGHT))
    
    def is_alive(self):
        return self.hp > 0
    
    def is_critical(self):
        return self.hp <= (self.max_hp * 0.2)
    
    def show_stats(self):
        print_separator("~", 35, Fore.BLUE)
        status_display = ""
        if self.status_effects:
            status_str = " ".join([colored_text(f"[{effect}]", Fore.CYAN) for effect in self.status_effects])
            status_display = f" {status_str}"
        
        print(colored_text(f"{self.name}{status_display}", Fore.WHITE, Style.BRIGHT))
        print(f"HP: {self.health_bar()} {self.hp}/{self.max_hp}")
        
        # Color code stats
        atk_color = Fore.RED if self.attack >= 20 else Fore.YELLOW
        def_color = Fore.BLUE if self.defense >= 10 else Fore.WHITE
        print(f"ATK: {colored_text(str(self.attack), atk_color)} | DEF: {colored_text(str(self.defense), def_color)}")
        
        if self.equipment:
            print(f"Equipped: {colored_text(self.equipment.name, Fore.MAGENTA)} {self.equipment.durability_display()}")
        else:
            print(colored_text("No equipment equipped", Fore.LIGHTBLACK_EX))

    def health_bar(self, bar_length=20):
        hp_ratio = self.hp / self.max_hp
        filled_length = int(bar_length * hp_ratio)
        empty_length = bar_length - filled_length
        
        # Color based on health
        if hp_ratio > 0.6:
            bar_color = Fore.GREEN
            bar_char = '█'
        elif hp_ratio > 0.3:
            bar_color = Fore.YELLOW
            bar_char = '▓'
        else:
            bar_color = Fore.RED
            bar_char = '▒'
        
        bar = colored_text(bar_char * filled_length, bar_color) + colored_text('░' * empty_length, Fore.LIGHTBLACK_EX)
        
        critical_indicator = ""
        if self.is_critical():
            critical_indicator = colored_text(" ⚠️ CRITICAL!", Fore.RED, Style.BRIGHT)
        
        return f"[{bar}]{critical_indicator}"

    def add_status_effect(self, effect, duration=1):
        self.status_effects.append(effect)
        if duration > 1:
            # Could implement duration tracking here
            pass

    def clear_status_effect(self, effect):
        if effect in self.status_effects:
            self.status_effects.remove(effect)