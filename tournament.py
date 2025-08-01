# tournament_fixed.py - Fixed version with working bots and boss

from colorama import Fore, Style
import numpy as np
import time
from game_utils import colored_text, print_banner, print_separator
from equipment import Equipment, ElementalEquipment
from knight import Knight
from orc import Orc
from mage import Mage
from ninja import Ninja
from boss import Boss
from battle import Battle
from items import Potion, Bomb

class Arena:
    def __init__(self, name, description, effects, color):
        self.name = name
        self.description = description
        self.effects = effects  # Dictionary of effects that apply to battles
        self.color = color
    
    def apply_effects(self, battle):
        """Apply arena effects to the battle"""
        for effect_type, effect_value in self.effects.items():
            if effect_type == "fire_boost":
                for player in [battle.p1, battle.p2]:
                    if hasattr(player, 'elemental_affinity') and player.elemental_affinity == 'fire':
                        player.attack = int(player.attack * effect_value)
            elif effect_type == "ice_boost":
                for player in [battle.p1, battle.p2]:
                    if hasattr(player, 'elemental_affinity') and player.elemental_affinity == 'ice':
                        player.defense = int(player.defense * effect_value)
            elif effect_type == "lightning_chance":
                # Lightning strikes randomly during battle
                if np.random.random() < effect_value:
                    target = np.random.choice([battle.p1, battle.p2])
                    damage = np.random.randint(10, 20)
                    target.hp -= damage
                    print(colored_text(f"⚡ Lightning strikes {target.name} for {damage} damage!", Fore.YELLOW, Style.BRIGHT))
            elif effect_type == "healing_aura":
                # Gradual healing each turn
                for player in [battle.p1, battle.p2]:
                    heal_amount = int(player.max_hp * effect_value)
                    player.hp = min(player.max_hp, player.hp + heal_amount)
            elif effect_type == "poison_mist":
                # Poison damage each turn
                for player in [battle.p1, battle.p2]:
                    poison_damage = int(player.max_hp * effect_value)
                    player.hp -= poison_damage
                    print(colored_text(f"☠️ Poison mist damages {player.name} for {poison_damage}!", Fore.GREEN))

class Weather:
    def __init__(self, name, description, effects, color):
        self.name = name
        self.description = description
        self.effects = effects
        self.color = color
    
    def apply_effects(self, battle):
        """Apply weather effects to the battle"""
        for effect_type, effect_value in self.effects.items():
            if effect_type == "fire_weakness":
                for player in [battle.p1, battle.p2]:
                    if hasattr(player, 'elemental_affinity') and player.elemental_affinity == 'fire':
                        player.attack = int(player.attack * effect_value)
            elif effect_type == "lightning_boost":
                for player in [battle.p1, battle.p2]:
                    if hasattr(player, 'elemental_affinity') and player.elemental_affinity == 'lightning':
                        player.attack = int(player.attack * effect_value)
            elif effect_type == "ice_boost":
                for player in [battle.p1, battle.p2]:
                    if hasattr(player, 'elemental_affinity') and player.elemental_affinity == 'ice':
                        player.attack = int(player.attack * effect_value)

class Shop:
    def __init__(self):
        self.items = {
            "Health Potion": {"price": 50, "item": Potion(40), "description": "Restores 40 HP"},
            "Greater Potion": {"price": 100, "item": Potion(80), "description": "Restores 80 HP"},
            "Bomb": {"price": 75, "item": Bomb(30), "description": "Deals 30 damage"},
            "Mega Bomb": {"price": 150, "item": Bomb(50), "description": "Deals 50 damage"},
            "Steel Sword": {"price": 200, "item": Equipment("Steel Sword", attack_boost=8), "description": "+8 Attack"},
            "Dragon Armor": {"price": 250, "item": Equipment("Dragon Armor", defense_boost=6), "description": "+6 Defense"},
            "Flame Blade": {"price": 300, "item": ElementalEquipment("Flame Blade", "fire", attack_boost=6), "description": "+6 Attack, Fire affinity"},
            "Frost Shield": {"price": 300, "item": ElementalEquipment("Frost Shield", "ice", defense_boost=5), "description": "+5 Defense, Ice affinity"},
        }
    
    def display_shop(self, player):
        print_banner("🏪  TOURNAMENT SHOP  🏪", Fore.YELLOW)
        print(colored_text(f"Gold: {player.gold} 💰", Fore.YELLOW, Style.BRIGHT))
        print_separator("=", 50, Fore.YELLOW)
        
        for i, (name, info) in enumerate(self.items.items(), 1):
            color = Fore.GREEN if player.gold >= info["price"] else Fore.RED
            print(colored_text(f"{i}) {name} - {info['price']} gold", color, Style.BRIGHT))
            print(colored_text(f"   {info['description']}", Fore.LIGHTBLACK_EX))
            print()
        
        print(colored_text("0) Exit Shop", Fore.CYAN))
        print_separator("=", 50, Fore.YELLOW)
    
    def buy_item(self, player, choice):
        items_list = list(self.items.items())
        if 1 <= choice <= len(items_list):
            item_name, item_info = items_list[choice - 1]
            if player.gold >= item_info["price"]:
                player.gold -= item_info["price"]
                if isinstance(item_info["item"], Equipment):
                    player.equip(item_info["item"])
                else:
                    player.items.append(item_info["item"])
                print(colored_text(f"✅ Purchased {item_name}!", Fore.GREEN, Style.BRIGHT))
                return True
            else:
                print(colored_text("💸 Not enough gold!", Fore.RED))
                return False
        return False


class Tournament:
    def __init__(self, player):
        self.player = player
        # Initialize tournament-specific attributes if they don't exist
        if not hasattr(self.player, 'gold'):
            self.player.gold = 500  # Starting gold
        if not hasattr(self.player, 'tournament_wins'):
            self.player.tournament_wins = 0
        if not hasattr(self.player, 'items'):
            self.player.items = []
            
        self.current_round = 1
        self.max_rounds = 4  # 3 regular rounds + 1 boss fight
        
        # Tournament progression
        self.opponents = self.generate_opponents()
        self.current_opponent_index = 0
        
        # Arenas
        self.arenas = [
            Arena("Volcanic Crater", "Lava bubbles around the arena", 
                  {"fire_boost": 1.3, "ice_weakness": 0.8}, Fore.RED),
            Arena("Frozen Wasteland", "Ice and snow cover everything", 
                  {"ice_boost": 1.3, "fire_weakness": 0.8}, Fore.CYAN),
            Arena("Storm Peak", "Lightning crackles in the air", 
                  {"lightning_chance": 0.2}, Fore.YELLOW),
            Arena("Mystic Garden", "Healing energies flow through the area", 
                  {"healing_aura": 0.05}, Fore.GREEN),
            Arena("Toxic Swamp", "Poisonous mist fills the air", 
                  {"poison_mist": 0.03}, Fore.MAGENTA),
            Arena("Neutral Ground", "A balanced fighting arena", 
                  {}, Fore.WHITE)
        ]
        
        # Weather conditions
        self.weather_conditions = [
            Weather("Sunny", "Clear skies", {}, Fore.YELLOW),
            Weather("Rainy", "Rain weakens fire attacks", {"fire_weakness": 0.7}, Fore.BLUE),
            Weather("Thunderstorm", "Lightning empowers electric attacks", {"lightning_boost": 1.4}, Fore.YELLOW),
            Weather("Blizzard", "Snow strengthens ice attacks", {"ice_boost": 1.3}, Fore.CYAN),
            Weather("Sandstorm", "Dust reduces accuracy", {"accuracy_reduction": 0.1}, Fore.LIGHTYELLOW_EX)
        ]
        
        self.shop = Shop()
        
        # Create final boss
        self.final_boss = Boss("Ancient Shadow Dragon", 350, 28, 15, 
                             ["Claw Strike", "Fire Breath", "Wing Slam", "Roar of Terror", "Berserker Fury"])
        self.final_boss.equip(ElementalEquipment("Dragon Scale Armor", "fire", defense_boost=7))
    
    def generate_opponents(self):
        """Generate tournament opponents with proper Bot names"""
        opponents = []
        
        # Round 1: Weak bots
        opponent_class = np.random.choice([Knight, Orc, Mage, Ninja])
        # Create bot with adjusted stats - make sure to pass name with "Bot" in it
        bot_name = f"Novice {opponent_class.__name__} Bot"
        
        if opponent_class == Knight:
            opponent = Knight(bot_name, 
                            hp=int(self.player.max_hp * 0.8), 
                            attack=int(self.player.attack * 0.8), 
                            defense=int(self.player.defense * 0.8))
        elif opponent_class == Orc:
            opponent = Orc(bot_name, 
                         hp=int(self.player.max_hp * 0.8), 
                         attack=int(self.player.attack * 0.8), 
                         defense=int(self.player.defense * 0.8))
        elif opponent_class == Mage:
            opponent = Mage(bot_name, 
                          hp=int(self.player.max_hp * 0.8), 
                          attack=int(self.player.attack * 0.8), 
                          defense=int(self.player.defense * 0.8))
        else:  # Ninja
            opponent = Ninja(bot_name, 
                           hp=int(self.player.max_hp * 0.8), 
                           attack=int(self.player.attack * 0.8), 
                           defense=int(self.player.defense * 0.8))
        
        opponents.append(opponent)
        
        # Round 2: Equal bots
        opponent_class = np.random.choice([Knight, Orc, Mage, Ninja])
        bot_name = f"Veteran {opponent_class.__name__} Bot"
        
        if opponent_class == Knight:
            opponent = Knight(bot_name, 
                            hp=self.player.max_hp, 
                            attack=self.player.attack, 
                            defense=self.player.defense)
        elif opponent_class == Orc:
            opponent = Orc(bot_name, 
                         hp=self.player.max_hp, 
                         attack=self.player.attack, 
                         defense=self.player.defense)
        elif opponent_class == Mage:
            opponent = Mage(bot_name, 
                          hp=self.player.max_hp, 
                          attack=self.player.attack, 
                          defense=self.player.defense)
        else:  # Ninja
            opponent = Ninja(bot_name, 
                           hp=self.player.max_hp, 
                           attack=self.player.attack, 
                           defense=self.player.defense)
        
        opponents.append(opponent)
        
        # Round 3: Strong bots
        opponent_class = np.random.choice([Knight, Orc, Mage, Ninja])
        bot_name = f"Elite {opponent_class.__name__} Bot"
        
        if opponent_class == Knight:
            opponent = Knight(bot_name, 
                            hp=int(self.player.max_hp * 1.2), 
                            attack=int(self.player.attack * 1.2), 
                            defense=int(self.player.defense * 1.2))
        elif opponent_class == Orc:
            opponent = Orc(bot_name, 
                         hp=int(self.player.max_hp * 1.2), 
                         attack=int(self.player.attack * 1.2), 
                         defense=int(self.player.defense * 1.2))
        elif opponent_class == Mage:
            opponent = Mage(bot_name, 
                          hp=int(self.player.max_hp * 1.2), 
                          attack=int(self.player.attack * 1.2), 
                          defense=int(self.player.defense * 1.2))
        else:  # Ninja
            opponent = Ninja(bot_name, 
                           hp=int(self.player.max_hp * 1.2), 
                           attack=int(self.player.attack * 1.2), 
                           defense=int(self.player.defense * 1.2))
        
        opponents.append(opponent)
        
        return opponents
    
    def display_tournament_status(self):
        """Display current tournament progress"""
        print_banner("🏆  TOURNAMENT STATUS  🏆", Fore.MAGENTA)
        print(colored_text(f"Round: {self.current_round}/4", Fore.CYAN, Style.BRIGHT))
        print(colored_text(f"Wins: {self.player.tournament_wins}", Fore.GREEN, Style.BRIGHT))
        print(colored_text(f"Gold: {self.player.gold} 💰", Fore.YELLOW, Style.BRIGHT))
        print_separator("=", 30, Fore.MAGENTA)
    
    def shop_phase(self):
        """Allow player to shop between rounds"""
        if self.current_round > 1:  # No shop before first round
            print_banner("🛒  SHOP PHASE  🛒", Fore.YELLOW)
            print(colored_text("You can buy items and equipment!", Fore.CYAN))
            
            while True:
                self.shop.display_shop(self.player)
                try:
                    choice = int(input(colored_text("Enter choice: ", Fore.CYAN)))
                    if choice == 0:
                        break
                    else:
                        self.shop.buy_item(self.player, choice)
                        time.sleep(1)
                except ValueError:
                    print(colored_text("Invalid input!", Fore.RED))
    
    def battle_phase(self):
        """Execute a tournament battle"""
        # Select random arena and weather
        arena = np.random.choice(self.arenas)
        weather = np.random.choice(self.weather_conditions)
        
        print_banner(f"🏟️  ROUND {self.current_round} BATTLE  🏟️", Fore.BLUE)
        print(colored_text(f"Arena: {arena.name}", arena.color, Style.BRIGHT))
        print(colored_text(f"Weather: {weather.name}", weather.color))
        print(colored_text(f"Effect: {arena.description}", Fore.LIGHTBLACK_EX))
        if weather.name != "Sunny":
            print(colored_text(f"Weather Effect: {weather.description}", Fore.LIGHTBLACK_EX))
        print_separator("=", 40, Fore.BLUE)
        time.sleep(2)
        
        if self.current_round == 4:
            # Boss fight
            opponent = self.final_boss
            print(colored_text("👹 FINAL BOSS BATTLE! 👹", Fore.RED, Style.BRIGHT))
        else:
            # Regular tournament opponent
            opponent = self.opponents[self.current_opponent_index]
            self.current_opponent_index += 1
            
            # Give opponent some equipment
            equipment_options = [
                Equipment("Tournament Sword", attack_boost=np.random.randint(3, 7)),
                Equipment("Tournament Armor", defense_boost=np.random.randint(2, 5)),
                ElementalEquipment("Elemental Weapon", np.random.choice(["fire", "ice", "lightning"]), 
                                 attack_boost=np.random.randint(3, 6))
            ]
            if hasattr(opponent, 'equip'):  # Make sure the opponent has equip method
                opponent.equip(np.random.choice(equipment_options))
        
        # Create battle with environmental effects
        battle = Battle(self.player, opponent)
        
        # Apply arena and weather effects before battle
        arena.apply_effects(battle)
        weather.apply_effects(battle)
        
        # Start the battle
        battle.fight()
        
        if self.player.is_alive():
            # Award gold based on round
            gold_reward = 50 * self.current_round
            if self.current_round == 4:  # Boss fight
                gold_reward = 300
            
            self.player.gold += gold_reward
            self.player.tournament_wins += 1
            
            print(colored_text(f"💰 Victory! Earned {gold_reward} gold!", Fore.YELLOW, Style.BRIGHT))
            
            # Restore some HP after victory
            heal_amount = int(self.player.max_hp * 0.3)
            self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
            print(colored_text(f"❤️ Restored {heal_amount} HP!", Fore.GREEN))
            
            return True
        else:
            print(colored_text("💀 Tournament Over! You were defeated!", Fore.RED, Style.BRIGHT))
            return False
    
    def run_tournament(self):
        """Main tournament loop"""
        print_banner("🏆  WELCOME TO THE TOURNAMENT  🏆", Fore.MAGENTA)
        print(colored_text("Fight through 4 rounds to become champion!", Fore.CYAN, Style.BRIGHT))
        print(colored_text("• Win battles to earn gold", Fore.YELLOW))
        print(colored_text("• Shop for better equipment between rounds", Fore.YELLOW))
        print(colored_text("• Face the final boss in round 4!", Fore.RED))
        print_separator("=", 50, Fore.MAGENTA)
        input(colored_text("Press Enter to begin...", Fore.CYAN, Style.BRIGHT))
        
        for round_num in range(1, 5):
            self.current_round = round_num
            self.display_tournament_status()
            
            # Shop phase (except before first round)
            self.shop_phase()
            
            # Battle phase
            if not self.battle_phase():
                # Player was defeated
                print_banner("💀  TOURNAMENT ENDED  💀", Fore.RED)
                print(colored_text(f"You reached Round {round_num}", Fore.YELLOW))
                print(colored_text(f"Total Wins: {self.player.tournament_wins}", Fore.GREEN))
                return False
            
            if round_num == 4:
                # Tournament completed!
                print_banner("🏆  TOURNAMENT CHAMPION!  🏆", Fore.YELLOW)
                print(colored_text("You have conquered the tournament!", Fore.MAGENTA, Style.BRIGHT))
                print(colored_text("🎉 ULTIMATE VICTORY! 🎉", Fore.CYAN, Style.BRIGHT))
                return True
            
            # Rest between rounds
            print(colored_text(f"Round {round_num} complete! Preparing for next round...", Fore.GREEN))
            time.sleep(2)
        
        return True

# Integration function to add to main.py
def start_tournament_mode():
    """Function to integrate tournament mode into the main game"""
    print_banner("🏆  TOURNAMENT MODE  🏆", Fore.MAGENTA)
    
    # Player chooses character
    from main import choose_character, choose_equipment
    player = choose_character("Tournament")
    player.equip(choose_equipment())
    
    # Initialize and run tournament
    tournament = Tournament(player)
    tournament.run_tournament()

