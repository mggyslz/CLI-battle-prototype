import numpy as np
from colorama import Fore, Style
from character import Character
from game_utils import colored_text, roll_dice
import time
from combat_mechanics import calculate_elemental_effects, check_combo, attempt_block

class Knight(Character):
    def __init__(self, name, hp, attack, defense):
        super().__init__(name, hp, attack, defense)
        self.block_chance = 0.3  # Knights have higher block chance
        self.elemental_affinity = None  # Can be set by equipment

    def sword_slash(self, enemy, is_bot=False):
        # Combo system
        combo_multiplier = check_combo(self, "sword_slash")
        
        damage = (self.attack + (self.equipment.attack_boost if self.equipment else 0)) * combo_multiplier
        damage = calculate_elemental_effects(self, enemy, damage)
        damage, crit_miss_result = self.apply_dice(damage, is_bot)
        
        if crit_miss_result == "miss":
            print(colored_text(f"⚡ {self.name}'s Sword Slash MISSES completely!", Fore.BLUE))
            return
            
        # Block chance
        damage = attempt_block(enemy, damage)
        
        final_damage = max(0, int(damage) - enemy.defense)
        enemy.hp -= final_damage
        
        if crit_miss_result == "crit":
            print(colored_text(f"💥 {self.name} lands a CRITICAL Sword Slash! Deals {final_damage} damage!", Fore.MAGENTA, Style.BRIGHT))
        else:
            print(colored_text(f"⚔️ {self.name} uses Sword Slash! Deals {final_damage} damage to {enemy.name}.", Fore.RED))

    def shield_bash(self, enemy, is_bot=False):
        damage = (self.attack * 0.75) + (self.equipment.attack_boost if self.equipment else 0)
        damage = calculate_elemental_effects(self, enemy, damage)
        damage, crit_miss_result = self.apply_dice(damage, is_bot)
        
        if crit_miss_result == "miss":
            print(colored_text(f"🛡️ {self.name}'s Shield Bash misses!", Fore.BLUE))
            return
            
        final_damage = max(0, int(damage) - enemy.defense)
        enemy.hp -= final_damage
        print(colored_text(f"🛡️ {self.name} uses Shield Bash! Deals {final_damage} damage!", Fore.YELLOW))
        
        # Enhanced stun chance with elemental effects
        stun_chance = 0.4 if "FROZEN" in enemy.status_effects else 0.3
        if np.random.random() < stun_chance:
            enemy.add_status_effect("STUNNED")
            print(colored_text(f"💫 {enemy.name} is STUNNED!", Fore.CYAN, Style.BRIGHT))

    def mighty_strike(self, enemy, is_bot=False):
        if np.random.random() < 0.7:
            combo_multiplier = check_combo(self, "mighty_strike")
            damage = (self.attack * 1.5 * combo_multiplier) + (self.equipment.attack_boost if self.equipment else 0)
            damage = calculate_elemental_effects(self, enemy, damage)
            damage, crit_miss_result = self.apply_dice(damage, is_bot)
            
            if crit_miss_result == "miss":
                print(colored_text(f"💪 {self.name}'s Mighty Strike misses!", Fore.BLUE))
                return
                
            # Block chance is halved for mighty strikes
            original_block = enemy.block_chance
            enemy.block_chance *= 0.5
            damage = attempt_block(enemy, damage)
            enemy.block_chance = original_block
            
            final_damage = max(0, int(damage) - enemy.defense)
            enemy.hp -= final_damage
            
            if crit_miss_result == "crit":
                print(colored_text(f"🔥 DEVASTATING CRITICAL MIGHTY STRIKE! {final_damage} damage!", Fore.MAGENTA, Style.BRIGHT))
            else:
                print(colored_text(f"💪 {self.name} uses Mighty Strike! Deals {final_damage} damage!", Fore.RED, Style.BRIGHT))
        else:
            print(colored_text(f"💢 {self.name} WHIFFS the Mighty Strike!", Fore.BLUE))

    def rapid_strikes(self, enemy, is_bot=False):
        print(colored_text(f"⚔️ {self.name} prepares a flurry of strikes!", Fore.CYAN, Style.BRIGHT))
        
        total_damage = 0
        hits = 3  # Number of hits
        
        for i in range(hits):
            damage = (self.attack * 0.6) + (self.equipment.attack_boost if self.equipment else 0)
            damage = calculate_elemental_effects(self, enemy, damage)
            damage, _ = self.apply_dice(damage, is_bot)
            damage = attempt_block(enemy, damage)
            final_damage = max(0, int(damage) - enemy.defense)
            enemy.hp -= final_damage
            total_damage += final_damage
            
            print(colored_text(f"  Strike {i+1}: {final_damage} damage", Fore.YELLOW))
            time.sleep(0.3)
        
        print(colored_text(f"⚔️ Total damage: {total_damage}!", Fore.RED, Style.BRIGHT))

    def apply_dice(self, dmg, is_bot=False):
        dice = roll_dice(is_bot)
        
        # Critical hit/miss system
        if dice == 1:
            print(colored_text("💥 CRITICAL MISS!", Fore.RED, Style.BRIGHT))
            return 0, "miss"
        elif dice == 20:
            print(colored_text("🎯 CRITICAL HIT! 2x DAMAGE!", Fore.MAGENTA, Style.BRIGHT))
            return dmg * 2, "crit"
        elif dice <= 5:
            print(colored_text(f"📉 Dice {dice}: Weak hit!", Fore.RED))
            return dmg * 0.8, "normal"
        elif dice <= 15:
            print(colored_text(f"⚡ Dice {dice}: Normal hit.", Fore.YELLOW))
            return dmg, "normal"
        else:
            print(colored_text(f"🔥 Dice {dice}: Strong hit!", Fore.GREEN))
            return dmg * 1.2, "normal"