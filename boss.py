from colorama import Fore, Style
import numpy as np
import time
from game_utils import colored_text, print_banner, print_separator

class Boss:
    """Special boss enemies with unique mechanics"""
    def __init__(self, name, hp, attack, defense, special_abilities):
        self.name = name + " Bot"  # Add Bot to name for AI recognition
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.special_abilities = special_abilities
        self.status_effects = []
        self.equipment = None
        self.items = []
        self.gold = 0
        self.phase = 1
        self.max_phase = 3
        self.rage_counter = 0
        self.block_chance = 0.05  # Bosses can block weakly
        self.dodge_chance = 0.05  # Bosses can dodge weakly
        self.last_move = None      # For combo system
        self.combo_counter = 0     # For combo system
        self.elemental_affinity = None  # Can be set by equipment
        self.cooldowns = {
            "fire_breath": 0,
            "wing_slam": 0,
            "roar_of_terror": 0,
            "berserker_fury": 0
        }
        
        # Battle references (set during battle)
        self.p1 = None  
        self.p2 = None  
    
    def is_alive(self):
        return self.hp > 0
    
    def clear_status_effect(self, effect):
        """Remove a status effect"""
        if effect in self.status_effects:
            self.status_effects.remove(effect)
    
    def add_status_effect(self, effect, duration=1):
        """Add status effect with resistance to CC spam"""
        if effect in ["STUNNED", "FROZEN"]:
            # 50% chance to resist if already affected
            if effect in self.status_effects and np.random.random() < 0.5:
                print(colored_text(f"👹 {self.name} resists {effect}!", Fore.MAGENTA))
                return
                
        if effect not in self.status_effects:
            self.status_effects.append(effect)
            # Special handling for burning (reduced damage)
            if effect == "BURNING":
                print(colored_text(f"🔥 {self.name} is burning (reduced effect)!", Fore.RED))

    def equip(self, equipment):
        """Equip an item and update elemental affinity"""
        self.equipment = equipment
        if hasattr(equipment, 'elemental_type'):
            self.elemental_affinity = equipment.elemental_type

    def health_bar(self, bar_length=25):
        hp_ratio = self.hp / self.max_hp
        filled = int(bar_length * hp_ratio)
        bar = (colored_text('█' * filled, 
               Fore.RED if hp_ratio < 0.3 else Fore.YELLOW if hp_ratio < 0.6 else Fore.GREEN)
               + colored_text('░' * (bar_length - filled), Fore.LIGHTBLACK_EX))
        return f"[{bar}] BOSS"
    
    def show_stats(self):
        print_separator("~", 40, Fore.RED)
        print(colored_text(f"👹 {self.name} - Phase {self.phase}", Fore.RED, Style.BRIGHT))
        print(f"HP: {self.health_bar()} {self.hp}/{self.max_hp}")
        print(f"ATK: {colored_text(str(self.attack), Fore.RED)} | DEF: {colored_text(str(self.defense), Fore.BLUE)}")
        
        # Show equipment if exists
        if self.equipment:
            print(f"Equip: {self.equipment.name}")
        
        # Show active status effects
        if self.status_effects:
            print(f"Status: {', '.join(self.status_effects)}")
        
        # Show cooldowns
        active_cds = [name for name, cd in self.cooldowns.items() if cd > 0]
        if active_cds:
            print(f"Cooldowns: {', '.join(active_cds)}")
    
    def phase_transition(self):
        """Enhanced phase change with status cleansing"""
        if self.phase < self.max_phase and self.hp <= (self.max_hp * (self.max_phase - self.phase) / self.max_phase):
            self.phase += 1
            print(colored_text(f"💀 {self.name} enters Phase {self.phase}!", Fore.RED, Style.BRIGHT))
            
            # Cleanse negative effects
            for effect in ["STUNNED", "FROZEN", "BURNING", "SHOCKED"]:
                if effect in self.status_effects:
                    self.status_effects.remove(effect)
            
            # Stat boosts
            self.attack = int(self.attack * 1.2)
            self.defense = int(self.defense * 1.1)
            self.hp = min(self.max_hp, self.hp + int(self.max_hp * 0.1))
            
            # Reset cooldowns
            for ability in self.cooldowns:
                self.cooldowns[ability] = 0
            
            # Phase-specific buffs
            if self.phase == 2:
                print(colored_text("🔥 Attacks now inflict BURNING!", Fore.RED))
            elif self.phase == 3:
                self.block_chance = 0.1  # Better blocking in final phase
                print(colored_text("⚡ Entered BERSERK MODE! Cooldowns reduced!", Fore.YELLOW))
            
            time.sleep(2)
            return True
        return False
    # Boss Attack Methods
    def claw_strike(self, enemy, is_bot=True):
        """Basic claw attack"""
        if is_bot:
            print(colored_text(f"🦅 {self.name} slashes with razor-sharp claws!", Fore.RED, Style.BRIGHT))
        
        damage = np.random.randint(self.attack - 3, self.attack + 3)
        actual_damage = max(1, damage - enemy.defense)
        enemy.hp -= actual_damage
        
        print(colored_text(f"💥 {enemy.name} takes {actual_damage} damage!", Fore.RED))
        
        # Phase 2+: Chance to inflict bleeding
        if self.phase >= 2 and np.random.random() < 0.3:
            enemy.status_effects.append("BLEEDING")
            print(colored_text(f"🩸 {enemy.name} is bleeding!", Fore.RED))
    
    def fire_breath(self, enemy, is_bot=True):
        """Fire breath attack with burning effect"""
        if self.cooldowns["fire_breath"] > 0:
            print(colored_text(f"🔥 Fire Breath is on cooldown! Using claw strike instead.", Fore.YELLOW))
            self.claw_strike(enemy, is_bot)
            return
        
        if is_bot:
            print(colored_text(f"🔥 {self.name} unleashes a torrent of flames!", Fore.RED, Style.BRIGHT))
        
        damage = np.random.randint(self.attack + 5, self.attack + 10)
        actual_damage = max(1, damage - enemy.defense // 2)  # Fire breath bypasses some defense
        enemy.hp -= actual_damage
        
        print(colored_text(f"🔥 {enemy.name} is engulfed in flames for {actual_damage} damage!", Fore.RED))
        
        # Apply burning effect
        if "BURNING" not in enemy.status_effects:
            enemy.status_effects.append("BURNING")
            print(colored_text(f"🔥 {enemy.name} is burning!", Fore.RED))
        
        self.cooldowns["fire_breath"] = 3
    
    def wing_slam(self, enemy, is_bot=True):
        """Powerful wing attack that can stun"""
        if self.cooldowns["wing_slam"] > 0:
            print(colored_text(f"💨 Wing Slam is on cooldown! Using claw strike instead.", Fore.YELLOW))
            self.claw_strike(enemy, is_bot)
            return
        
        if is_bot:
            print(colored_text(f"💨 {self.name} spreads massive wings and slams down!", Fore.MAGENTA, Style.BRIGHT))
        
        damage = np.random.randint(self.attack + 3, self.attack + 8)
        actual_damage = max(1, damage - enemy.defense)
        enemy.hp -= actual_damage
        
        print(colored_text(f"💥 {enemy.name} is crushed for {actual_damage} damage!", Fore.RED))
        
        # Chance to stun
        if np.random.random() < 0.4:
            enemy.status_effects.append("STUNNED")
            print(colored_text(f"💫 {enemy.name} is stunned by the impact!", Fore.CYAN))
        
        self.cooldowns["wing_slam"] = 2
    
    def roar_of_terror(self, enemy, is_bot=True):
        """Intimidating roar that reduces enemy stats"""
        if self.cooldowns["roar_of_terror"] > 0:
            print(colored_text(f"👹 Roar of Terror is on cooldown! Using claw strike instead.", Fore.YELLOW))
            self.claw_strike(enemy, is_bot)
            return
        
        if is_bot:
            print(colored_text(f"👹 {self.name} lets out a bone-chilling roar!", Fore.RED, Style.BRIGHT))
        
        # Reduce enemy attack temporarily
        original_attack = enemy.attack
        enemy.attack = max(1, int(enemy.attack * 0.8))
        enemy.status_effects.append("FRIGHTENED")
        
        print(colored_text(f"😰 {enemy.name} is frightened and weakened! (Attack: {original_attack} → {enemy.attack})", Fore.YELLOW))
        
        self.cooldowns["roar_of_terror"] = 4
    
    def berserker_fury(self, enemy, is_bot=True):
        """Phase 3 ultimate attack - multiple strikes"""
        if self.phase < 3:
            print(colored_text(f"😡 Not in final phase yet! Using claw strike instead.", Fore.YELLOW))
            self.claw_strike(enemy, is_bot)
            return
            
        if self.cooldowns["berserker_fury"] > 0:
            print(colored_text(f"😡 Berserker Fury is on cooldown! Using claw strike instead.", Fore.YELLOW))
            self.claw_strike(enemy, is_bot)
            return
        
        if is_bot:
            print(colored_text(f"😡 {self.name} enters a berserker fury!", Fore.RED, Style.BRIGHT))
        
        # Multiple attacks
        total_damage = 0
        for i in range(3):
            damage = np.random.randint(self.attack - 2, self.attack + 2)
            actual_damage = max(1, damage - enemy.defense)
            enemy.hp -= actual_damage
            total_damage += actual_damage
            print(colored_text(f"💥 Strike {i+1}: {actual_damage} damage!", Fore.RED))
            time.sleep(0.5)
        
        print(colored_text(f"🔥 Total fury damage: {total_damage}!", Fore.RED, Style.BRIGHT))
        self.cooldowns["berserker_fury"] = 5
    
    def boss_ai_choice(self, enemy):
        """AI logic for boss attacks"""
        available_abilities = []
        
        # Check which abilities are available (not on cooldown)
        if self.cooldowns["fire_breath"] == 0:
            available_abilities.append("fire_breath")
        if self.cooldowns["wing_slam"] == 0:
            available_abilities.append("wing_slam")
        if self.cooldowns["roar_of_terror"] == 0:
            available_abilities.append("roar_of_terror")
        if self.cooldowns["berserker_fury"] == 0 and self.phase >= 3:
            available_abilities.append("berserker_fury")
        
        # Always have claw strike available
        available_abilities.append("claw_strike")
        
        # AI decision making
        if self.phase == 3 and "berserker_fury" in available_abilities and np.random.random() < 0.4:
            return "berserker_fury"
        
        if self.hp < self.max_hp * 0.3 and "roar_of_terror" in available_abilities and np.random.random() < 0.5:
            return "roar_of_terror"
        
        if self.phase >= 2 and "fire_breath" in available_abilities and np.random.random() < 0.3:
            return "fire_breath"
        
        if "wing_slam" in available_abilities and np.random.random() < 0.25:
            return "wing_slam"
        
        # Default to claw strike
        return "claw_strike"
    
    def reduce_cooldowns(self):
        """Reduce cooldowns at end of turn"""
        for ability in self.cooldowns:
            if self.cooldowns[ability] > 0:
                self.cooldowns[ability] -= 1