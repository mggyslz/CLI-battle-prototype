import numpy as np
from colorama import Fore, Style
from character import Character
from game_utils import colored_text, roll_dice
from combat_mechanics import calculate_elemental_effects, check_combo, attempt_block, attempt_dodge
import time

class Ninja(Character):
    def __init__(self, name, hp, attack, defense):
        super().__init__(name, hp, attack, defense)
        self.dodge_chance = 0.25  # Ninjas have high dodge chance
        self.shadowstep_cooldown = 0
        self.stealth_active = False
        self.elemental_affinity = 'shadow'  # Ninjas have shadow affinity
        self.shuriken_count = 6  # Limited shurikens per battle

    def shadowstep(self, is_bot=False):
        """Dodge/Mobility skill that increases dodge chance and can counter-attack"""
        if self.shadowstep_cooldown > 0:
            print(colored_text(f"⛔ Shadowstep is on cooldown ({self.shadowstep_cooldown} turns left)!", Fore.RED))
            return False
        
        print(colored_text(f"💨 {self.name} vanishes into the shadows!", Fore.MAGENTA, Style.BRIGHT))
        
        # Temporarily boost dodge chance
        self.dodge_chance += 0.4  # Total 65% dodge chance for 1 turn
        self.stealth_active = True
        self.shadowstep_cooldown = 3
        
        print(colored_text(f"👤 {self.name} becomes nearly untouchable! Dodge chance increased!", Fore.CYAN))
        return True

    def twin_fang_slash(self, enemy, is_bot=False):
        """Basic combo attack with two strikes"""
        combo_multiplier = check_combo(self, "twin_fang_slash")
        
        # Check if enemy dodges
        if attempt_dodge(enemy):
            return
        
        print(colored_text(f"🗡️ {self.name} unleashes Twin Fang Slash!", Fore.CYAN, Style.BRIGHT))
        
        total_damage = 0
        for i in range(2):  # Two strikes
            damage = (self.attack * 0.8 * combo_multiplier) + (self.equipment.attack_boost if self.equipment else 0)
            
            # Stealth bonus
            if self.stealth_active:
                damage *= 1.3  # 30% bonus from stealth
                print(colored_text(f"  🌙 Strike {i+1} from the shadows! +30% damage", Fore.MAGENTA))
            
            damage = calculate_elemental_effects(self, enemy, damage)
            damage, crit_miss_result = self.apply_dice(damage, is_bot)
            
            if crit_miss_result == "miss":
                print(colored_text(f"  Strike {i+1}: MISSES!", Fore.BLUE))
                continue
            
            damage = attempt_block(enemy, damage)
            final_damage = max(0, int(damage) - enemy.defense)
            enemy.hp -= final_damage
            total_damage += final_damage
            
            if crit_miss_result == "crit":
                print(colored_text(f"  Strike {i+1}: CRITICAL! {final_damage} damage", Fore.MAGENTA, Style.BRIGHT))
            else:
                print(colored_text(f"  Strike {i+1}: {final_damage} damage", Fore.YELLOW))
            
            time.sleep(0.4)
        
        print(colored_text(f"🗡️ Total Twin Fang damage: {total_damage}!", Fore.RED, Style.BRIGHT))
        
        # Clear stealth after attacking
        if self.stealth_active:
            self.stealth_active = False
            self.dodge_chance -= 0.4  # Reset dodge chance

    def shuriken_storm(self, enemy, is_bot=False):
        """Ranged area attack with limited uses"""
        if self.shuriken_count <= 0:
            print(colored_text(f"⛔ {self.name} is out of shurikens!", Fore.RED))
            return False
        
        # Use 2-3 shurikens per storm
        shurikens_used = min(np.random.randint(2, 4), self.shuriken_count)
        self.shuriken_count -= shurikens_used
        
        print(colored_text(f"🌟 {self.name} hurls {shurikens_used} shurikens in a deadly storm!", Fore.CYAN, Style.BRIGHT))
        
        total_damage = 0
        for i in range(shurikens_used):
            # Each shuriken has independent hit chance
            if attempt_dodge(enemy, 0.1):  # Slight dodge chance per shuriken
                print(colored_text(f"  Shuriken {i+1}: Dodged!", Fore.BLUE))
                continue
            
            damage = (self.attack * 0.6) + (self.equipment.attack_boost if self.equipment else 0)
            damage = calculate_elemental_effects(self, enemy, damage)
            damage, crit_miss_result = self.apply_dice(damage, is_bot)
            
            if crit_miss_result == "miss":
                print(colored_text(f"  Shuriken {i+1}: MISSES!", Fore.BLUE))
                continue
            
            # Shurikens are harder to block
            original_block = enemy.block_chance
            enemy.block_chance *= 0.3
            damage = attempt_block(enemy, damage)
            enemy.block_chance = original_block
            
            final_damage = max(0, int(damage) - enemy.defense // 2)  # Reduced armor effectiveness
            enemy.hp -= final_damage
            total_damage += final_damage
            
            if crit_miss_result == "crit":
                print(colored_text(f"  Shuriken {i+1}: CRITICAL HIT! {final_damage} damage", Fore.MAGENTA))
            else:
                print(colored_text(f"  Shuriken {i+1}: {final_damage} damage", Fore.YELLOW))
            
            time.sleep(0.3)
        
        print(colored_text(f"🌟 Shuriken Storm total damage: {total_damage}!", Fore.RED, Style.BRIGHT))
        print(colored_text(f"🎯 Shurikens remaining: {self.shuriken_count}", Fore.LIGHTBLACK_EX))
        
        # Chance to apply shadow effect to all nearby enemies
        if np.random.random() < 0.6:
            enemy.add_status_effect("SHADOWED")
            print(colored_text(f"🌙 {enemy.name} is surrounded by shadows!", Fore.MAGENTA))
        
        return True

    def smoke_bomb_escape(self, is_bot=False):
        """Emergency ability - heal slightly and reset cooldowns"""
        if hasattr(self, 'smoke_bomb_used') and self.smoke_bomb_used:
            print(colored_text(f"⛔ Smoke bomb already used this battle!", Fore.RED))
            return False
        
        print(colored_text(f"💨 {self.name} throws a smoke bomb and vanishes!", Fore.MAGENTA, Style.BRIGHT))
        
        # Small heal
        heal_amount = int(self.max_hp * 0.15)
        self.hp = min(self.max_hp, self.hp + heal_amount)
        
        # Reset shadowstep cooldown
        self.shadowstep_cooldown = 0
        
        # Temporary invulnerability for this turn
        self.add_status_effect("UNTOUCHABLE")
        self.smoke_bomb_used = True
        
        print(colored_text(f"✨ {self.name} heals {heal_amount} HP and resets cooldowns!", Fore.GREEN))
        print(colored_text(f"👻 {self.name} cannot be targeted this turn!", Fore.CYAN))
        
        return True

    def apply_dice(self, dmg, is_bot=False):
        dice = roll_dice(is_bot)
        
        # Ninjas have balanced dice mechanics with slight crit bias
        if dice == 1:
            print(colored_text("💥 CRITICAL MISS!", Fore.RED, Style.BRIGHT))
            return 0, "miss"
        elif dice == 20:
            print(colored_text("🎯 CRITICAL HIT! 2.2x DAMAGE!", Fore.MAGENTA, Style.BRIGHT))
            return dmg * 2.2, "crit"
        elif dice <= 3:
            print(colored_text(f"📉 Dice {dice}: Weak hit!", Fore.RED))
            return dmg * 0.75, "normal"
        elif dice <= 13:
            print(colored_text(f"⚡ Dice {dice}: Normal hit.", Fore.YELLOW))
            return dmg, "normal"
        else:
            print(colored_text(f"🔥 Dice {dice}: Strong hit!", Fore.GREEN))
            return dmg * 1.25, "normal"

    def reduce_cooldowns(self):
        """Called at end of turn to reduce cooldowns"""
        if self.shadowstep_cooldown > 0:
            self.shadowstep_cooldown -= 1
        
        # Reset temporary dodge bonus if stealth wore off
        if not self.stealth_active and self.dodge_chance > 0.25:
            self.dodge_chance = 0.25