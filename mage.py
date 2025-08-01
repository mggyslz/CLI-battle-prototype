from character import Character
from game_utils import colored_text, roll_dice
from combat_mechanics import calculate_elemental_effects, check_combo
from colorama import Fore, Style

class Mage(Character):
    def __init__(self, name, hp, attack, defense):
        super().__init__(name, hp, attack, defense)
        self.cooldowns = {"heal": 0, "meteor": 0}
        self.elemental_affinity = 'lightning'

    def arcane_lance(self, enemy, is_bot=False):
        combo_multiplier = check_combo(self, "arcane_lance")
        damage = (self.attack + (self.equipment.attack_boost if self.equipment else 0)) * combo_multiplier
        damage = calculate_elemental_effects(self, enemy, damage, element="lightning")
        damage, crit_miss_result = self.apply_dice(damage, is_bot)

        if crit_miss_result == "miss":
            print(colored_text(f"⚡ {self.name}'s Arcane Lance MISSES!", Fore.BLUE))
            return

        final_damage = max(0, int(damage) - enemy.defense)
        enemy.hp -= final_damage

        if crit_miss_result == "crit":
            print(colored_text(f"⚡ CRITICAL LIGHTNING STRIKE! {final_damage} damage!", Fore.MAGENTA, Style.BRIGHT))
        else:
            print(colored_text(f"⚡ {self.name} casts Arcane Lance! Deals {final_damage} lightning damage.", Fore.CYAN))

    def celestial_healing(self):
        if self.cooldowns["heal"] > 0:
            print(colored_text(f"⛔ Celestial Healing is on cooldown ({self.cooldowns['heal']} turns left)!", Fore.RED))
            return

        heal_amount = int(self.attack * 1.5)
        self.hp = min(self.max_hp, self.hp + heal_amount)
        self.cooldowns["heal"] = 3

        print(colored_text(f"🌟 {self.name} heals for {heal_amount} HP using Celestial Healing!", Fore.GREEN, Style.BRIGHT))

    def meteor_fall(self, enemies, is_bot=False):
        if self.cooldowns["meteor"] > 0:
            print(colored_text(f"⛔ Meteor Fall is on cooldown ({self.cooldowns['meteor']} turns left)!", Fore.RED))
            return

        print(colored_text(f"☄️ {self.name} channels METEOR FALL... A fiery doom descends!", Fore.YELLOW, Style.BRIGHT))

        for enemy in enemies:
            base_damage = self.attack * 2.2
            damage = calculate_elemental_effects(self, enemy, base_damage, element="fire")
            damage, crit_miss_result = self.apply_dice(damage, is_bot)

            if crit_miss_result == "miss":
                print(colored_text(f"💫 Meteor misses {enemy.name}!", Fore.BLUE))
                continue

            final_damage = max(0, int(damage) - enemy.defense)
            enemy.hp -= final_damage

            if crit_miss_result == "crit":
                print(colored_text(f"🔥 DIRECT METEOR HIT on {enemy.name}! {final_damage} damage!", Fore.MAGENTA))
            else:
                print(colored_text(f"🔥 Meteor Fall hits {enemy.name} for {final_damage} damage!", Fore.RED))

        self.cooldowns["meteor"] = 4

    def apply_dice(self, dmg, is_bot=False):
        dice = roll_dice(is_bot)
        if dice == 1:
            return 0, "miss"
        elif dice == 20:
            return dmg * 2.0, "crit"
        elif dice <= 4:
            return dmg * 0.7, "normal"
        elif dice <= 14:
            return dmg, "normal"
        else:
            return dmg * 1.3, "normal"

    def reduce_cooldowns(self):
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1
