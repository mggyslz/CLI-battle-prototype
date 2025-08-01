import numpy as np
from colorama import Fore, Style
from character import Character
from game_utils import colored_text, roll_dice
from combat_mechanics import calculate_elemental_effects, check_combo, attempt_block

class Orc(Character):
    def __init__(self, name, hp, attack, defense):
        super().__init__(name, hp, attack, defense)
        self.attack_buff_turns = 0
        self.block_chance = 0.1  # Orcs have lower block chance
        self.elemental_affinity = 'fire'  # Orcs have natural fire affinity

    def cleave(self, enemy, is_bot=False):
        # Combo system
        combo_multiplier = check_combo(self, "cleave")
        
        damage = (self.attack + (self.equipment.attack_boost if self.equipment else 0)) * combo_multiplier
        if self.attack_buff_turns > 0:
            print(colored_text(f"🔥 {self.name} is BUFFED! +20% damage!", Fore.GREEN, Style.BRIGHT))
            damage *= 1.2
            self.attack_buff_turns -= 1
            
        damage = calculate_elemental_effects(self, enemy, damage)
        damage, crit_miss_result = self.apply_dice(damage, is_bot)
        
        if crit_miss_result == "miss":
            print(colored_text(f"🪓 {self.name}'s Cleave misses wildly!", Fore.BLUE))
            return
            
        final_damage = max(0, int(damage) - enemy.defense)
        enemy.hp -= final_damage
        
        if crit_miss_result == "crit":
            print(colored_text(f"💀 BRUTAL CRITICAL CLEAVE! {final_damage} damage!", Fore.MAGENTA, Style.BRIGHT))
        else:
            print(colored_text(f"🪓 {self.name} uses Cleave! Deals {final_damage} damage!", Fore.RED))

    def berserk_strike(self, enemy, is_bot=False):
        combo_multiplier = check_combo(self, "berserk_strike")
        damage = (self.attack * 1.8 * combo_multiplier) + (self.equipment.attack_boost if self.equipment else 0)
        if self.attack_buff_turns > 0:
            print(colored_text(f"🔥 {self.name} is BUFFED! +20% damage!", Fore.GREEN, Style.BRIGHT))
            damage *= 1.2
            self.attack_buff_turns -= 1
            
        damage = calculate_elemental_effects(self, enemy, damage)
        damage, crit_miss_result = self.apply_dice(damage, is_bot)
        
        if crit_miss_result == "miss":
            print(colored_text(f"💢 {self.name}'s Berserk Strike goes wild!", Fore.BLUE))
        else:
            # Berserk strikes ignore 50% of block chance
            original_block = enemy.block_chance
            enemy.block_chance *= 0.5
            damage = attempt_block(enemy, damage)
            enemy.block_chance = original_block
            
            final_damage = max(0, int(damage) - enemy.defense)
            enemy.hp -= final_damage
            
            if crit_miss_result == "crit":
                print(colored_text(f"🩸 BERSERK CRITICAL HIT! {final_damage} damage!", Fore.MAGENTA, Style.BRIGHT))
            else:
                print(colored_text(f"🩸 {self.name} uses Berserk Strike! Deals {final_damage} damage!", Fore.RED, Style.BRIGHT))
        
        # Self damage is reduced if orc is FROZEN
        self_damage_multiplier = 0.5 if "FROZEN" in self.status_effects else 1.0
        self_damage = int(0.1 * self.max_hp * self_damage_multiplier)
        self.hp -= self_damage
        print(colored_text(f"💔 {self.name} takes {self_damage} recoil damage!", Fore.YELLOW))

    def roar(self, is_bot=False):
        self.attack_buff_turns = 2
        self.add_status_effect("BUFFED", 2)
        print(colored_text(f"🦁 {self.name} lets out a MIGHTY ROAR!", Fore.GREEN, Style.BRIGHT))
        print(colored_text("💪 Attack buffed for next 2 turns!", Fore.GREEN))
        
        # Roar has chance to inflict SHOCKED status
        if np.random.random() < 0.5 and hasattr(self, 'elemental_affinity') and self.elemental_affinity == 'lightning':
            enemies = [e for e in [self.p1, self.p2] if e != self]
            for enemy in enemies:
                enemy.add_status_effect("SHOCKED")
                print(colored_text(f"⚡ The roar SHOCKS {enemy.name}!", Fore.YELLOW, Style.BRIGHT))

    def apply_dice(self, dmg, is_bot=False):
        dice = roll_dice(is_bot)
        
        # Orcs have higher chance for strong hits
        if dice == 1:
            print(colored_text("💥 CRITICAL MISS!", Fore.RED, Style.BRIGHT))
            return 0, "miss"
        elif dice == 20:
            print(colored_text("🎯 CRITICAL HIT! 2.5x DAMAGE!", Fore.MAGENTA, Style.BRIGHT))  # Orcs get 2.5x instead of 2x
            return dmg * 2.5, "crit"
        elif dice <= 4:  # Slightly worse weak hits
            print(colored_text(f"📉 Dice {dice}: Weak hit!", Fore.RED))
            return dmg * 0.7, "normal"
        elif dice <= 14:
            print(colored_text(f"⚡ Dice {dice}: Normal hit.", Fore.YELLOW))
            return dmg, "normal"
        else:
            print(colored_text(f"🔥 Dice {dice}: Strong hit!", Fore.GREEN))
            return dmg * 1.3, "normal"  # Orcs get stronger strong hits