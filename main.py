import time
import numpy as np
from colorama import Fore, Style
from game_utils import colored_text, print_banner, print_separator
from equipment import Equipment, ElementalEquipment
from tournament import start_tournament_mode
from knight import Knight
from orc import Orc
from mage import Mage
from ninja import Ninja
from battle import Battle

# ====== Main Menu ======
def main_menu():
    while True:
        print_banner("⚔️  BATTLE ARENA  ⚔️", Fore.MAGENTA)
        print(colored_text("1) Player vs Bot", Fore.CYAN, Style.BRIGHT))
        print(colored_text("2) Player vs Player", Fore.YELLOW, Style.BRIGHT))
        print(colored_text("3) Tournament Mode", Fore.MAGENTA, Style.BRIGHT))
        print(colored_text("4) Quit", Fore.RED))
        print_separator("=", 30, Fore.MAGENTA)
        choice = input(colored_text("Enter choice (1/2/3/4): ", Fore.WHITE, Style.BRIGHT))
        
        if choice == "1":
            start_game_vs_bot()
        elif choice == "2":
            start_game_vs_player()
        elif choice == "3":
            start_tournament_mode()
        elif choice == "4":
            print(colored_text("⚔️ Farewell, warrior! ⚔️", Fore.CYAN, Style.BRIGHT))
            break
        else:
            print(colored_text("Invalid choice!", Fore.RED))

def choose_character(player_name="Player"):
    print_banner(f"{player_name} - Choose Your Fighter", Fore.BLUE)
    print(colored_text("1) 🛡️  Knight", Fore.CYAN, Style.BRIGHT))
    print(colored_text("   • High defense, balanced attacks", Fore.LIGHTBLACK_EX))
    print(colored_text("   • Special: Shield Bash (stun chance)", Fore.LIGHTBLACK_EX))
    print()
    print(colored_text("2) 🪓 Orc", Fore.RED, Style.BRIGHT))
    print(colored_text("   • High attack, brutal strikes", Fore.LIGHTBLACK_EX))
    print(colored_text("   • Special: Roar (damage buff)", Fore.LIGHTBLACK_EX))
    print()
    print(colored_text("3) 🧙‍♂️ Mage", Fore.MAGENTA, Style.BRIGHT))
    print(colored_text("   • Ranged spellcaster, heals and nukes", Fore.LIGHTBLACK_EX))
    print(colored_text("   • Special: Celestial Healing & Meteor Fall", Fore.LIGHTBLACK_EX))
    print()
    print(colored_text("4) 🥷 Ninja", Fore.YELLOW, Style.BRIGHT))
    print(colored_text("   • High speed, stealth attacks", Fore.LIGHTBLACK_EX))
    print(colored_text("   • Special: Shadowstep & Shuriken Storm", Fore.LIGHTBLACK_EX))
    print_separator("=", 35, Fore.BLUE)

    choice = input(colored_text("Enter 1, 2, 3, or 4: ", Fore.WHITE, Style.BRIGHT))
    if choice == "1":
        return Knight(f"{player_name} Knight", 150, 15, 8)
    elif choice == "2":
        return Orc(f"{player_name} Orc", 170, 18, 6)
    elif choice == "3":
        return Mage(f"{player_name} Mage", 140, 16, 5)
    elif choice == "4":
        return Ninja(f"{player_name} Ninja", 130, 17, 4)
    else:
        print(colored_text("Defaulting to Knight!", Fore.YELLOW))
        return Knight(f"{player_name} Knight", 120, 15, 8)

def choose_equipment():
    print_banner("⚔️  Choose Your Equipment  ⚔️", Fore.MAGENTA)
    print(colored_text("1) ⚔️  Sword", Fore.RED, Style.BRIGHT))
    print(colored_text("   • +5 Attack Power", Fore.LIGHTBLACK_EX))
    print("")
    print(colored_text("2) 🛡️  Armor", Fore.BLUE, Style.BRIGHT))
    print(colored_text("   • +4 Defense", Fore.LIGHTBLACK_EX))
    print("")
    print(colored_text("3) 🛡️  Shield", Fore.CYAN, Style.BRIGHT))
    print(colored_text("   • +2 Defense", Fore.LIGHTBLACK_EX))
    print("")
    print(colored_text("4) 🔥 Flaming Sword", Fore.RED, Style.BRIGHT))
    print(colored_text("   • +4 Attack, Fire affinity", Fore.LIGHTBLACK_EX))
    print("")
    print(colored_text("5) ❄️ Frost Armor", Fore.CYAN, Style.BRIGHT))
    print(colored_text("   • +3 Defense, Ice affinity", Fore.LIGHTBLACK_EX))
    print("")
    print(colored_text("6) 🌙 Shadow Daggers", Fore.MAGENTA, Style.BRIGHT))
    print(colored_text("   • +3 Attack, Shadow affinity", Fore.LIGHTBLACK_EX))
    print_separator("=", 30, Fore.MAGENTA)
    
    choice = input(colored_text("Enter 1-6: ", Fore.WHITE, Style.BRIGHT))
    if choice == "1":
        return Equipment("Sword", attack_boost=5)
    elif choice == "2":
        return Equipment("Armor", defense_boost=4)
    elif choice == "3":
        return Equipment("Shield", defense_boost=2)
    elif choice == "4":
        return ElementalEquipment("Flaming Sword", "fire", attack_boost=4)
    elif choice == "5":
        return ElementalEquipment("Frost Armor", "ice", defense_boost=3)
    elif choice == "6":
        return ElementalEquipment("Shadow Daggers", "shadow", attack_boost=3)
    else:
        print(colored_text("Defaulting to Sword!", Fore.YELLOW))
        return Equipment("Sword", attack_boost=5)

def start_game_vs_player():
    print_banner("⚔️  PLAYER VS PLAYER  ⚔️", Fore.GREEN)
    p1 = choose_character("Player 1")
    p1.equip(choose_equipment())
    print("")
    p2 = choose_character("Player 2") 
    p2.equip(choose_equipment())
    battle = Battle(p1, p2)
    battle.fight()

def start_game_vs_bot():
    print_banner("🤖  PLAYER VS BOT  🤖", Fore.CYAN)
    p1 = choose_character("Player")
    p1.equip(choose_equipment())
    
    bot_class = np.random.choice(["Knight", "Orc", "Mage", "Ninja"])
    if bot_class == "Knight":
        bot = Knight("Bot Knight", 150, 15, 8)
    elif bot_class == "Orc":
        bot = Orc("Bot Orc", 170, 18, 6)
    elif bot_class == "Mage":
        bot = Mage("Bot Mage", 140, 16, 5)
    else:  # Ninja
        bot = Ninja("Bot Ninja", 130, 17, 4)

    bot_equipment = np.random.choice([
        Equipment("Sword", attack_boost=5),
        Equipment("Armor", defense_boost=4),
        Equipment("Shield", defense_boost=2),
        ElementalEquipment("Flaming Sword", "fire", attack_boost=4),
        ElementalEquipment("Frost Armor", "ice", defense_boost=3),
        ElementalEquipment("Shadow Daggers", "shadow", attack_boost=3)
    ])
    bot.equip(bot_equipment)
    print(colored_text(f"\n🤖 Bot chose {bot_class} with {bot_equipment.name}!", Fore.YELLOW, Style.BRIGHT))
    time.sleep(1.5)
    
    battle = Battle(p1, bot)
    battle.fight()

# ====== Run Game ======
if __name__ == "__main__":
    main_menu()