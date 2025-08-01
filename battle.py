import time
import numpy as np
from colorama import Fore, Style
from game_utils import colored_text, print_separator, print_banner, battle_ascii, champion
from knight import Knight
from orc import Orc
from mage import Mage
from ninja import Ninja
from items import Potion, Bomb
from boss import Boss

class Battle:
    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.turn = 1
        self.p1.p1, self.p1.p2 = self.p1, self.p2
        self.p2.p1, self.p2.p2 = self.p1, self.p2

    def display_health_bars(self):
        print("\n")
        print_separator("=", 45, Fore.MAGENTA)
        print(f"{colored_text(self.p1.name, Fore.CYAN, Style.BRIGHT)}:")
        print(f"{self.p1.health_bar()} {self.p1.hp}/{self.p1.max_hp} HP")
        print("")
        print(f"{colored_text(self.p2.name, Fore.YELLOW, Style.BRIGHT)}:")
        print(f"{self.p2.health_bar()} {self.p2.hp}/{self.p2.max_hp} HP")
        print_separator("=", 45, Fore.MAGENTA)

    def fight(self):
        print(battle_ascii())
        print_banner("⚔️  BATTLE COMMENCES  ⚔️", Fore.RED)
        print(colored_text(f"\n{self.p1.name} VS {self.p2.name}", Fore.WHITE, Style.BRIGHT))

        self.p1.show_stats()
        print("")
        self.p2.show_stats()
        time.sleep(2)

        while self.p1.is_alive() and self.p2.is_alive():
            print(f"\n")
            print_banner(f"TURN {self.turn}", Fore.YELLOW, "~")
            self.display_health_bars()

            for current, enemy in [(self.p1, self.p2), (self.p2, self.p1)]:
                if not current.is_alive():
                    continue

                if "STUNNED" in current.status_effects:
                    print(colored_text(f"💫 {current.name} is STUNNED and loses their turn!", Fore.CYAN, Style.BRIGHT))
                    current.clear_status_effect("STUNNED")
                    time.sleep(1.5)
                    continue

                if "UNTOUCHABLE" in current.status_effects:
                    print(colored_text(f"👻 {current.name} is untouchable this turn!", Fore.MAGENTA, Style.BRIGHT))
                    current.clear_status_effect("UNTOUCHABLE")
                    time.sleep(1.5)
                    continue

                print(f"\n{colored_text(f'{current.name}\'s turn:', Fore.CYAN if current == self.p1 else Fore.YELLOW, Style.BRIGHT)}")
                self.player_turn(current, enemy)
                time.sleep(1)
                self.display_health_bars()

                if not enemy.is_alive():
                    self.victory_sequence(current, enemy)
                    return

            for player in [self.p1, self.p2]:
                if player.equipment and player.equipment.durability > 0:
                    player.equipment.wear_down()
                self.handle_elemental_effects(player)
                if isinstance(player, Mage):
                    player.reduce_cooldowns()
                if isinstance(player, Ninja):
                    player.reduce_cooldowns()
                if isinstance(player, Boss):
                    player.reduce_cooldowns()

            self.turn += 1
            time.sleep(1)

    def handle_elemental_effects(self, player):
        if "BURNING" in player.status_effects:
            burn_damage = int(player.max_hp * 0.05)
            player.hp -= burn_damage
            print(colored_text(f"🔥 {player.name} takes {burn_damage} burn damage!", Fore.RED, Style.BRIGHT))
        
        if "BLEEDING" in player.status_effects:
            bleed_damage = int(player.max_hp * 0.03)
            player.hp -= bleed_damage
            print(colored_text(f"🩸 {player.name} takes {bleed_damage} bleed damage!", Fore.RED))
            player.status_effects.remove("BLEEDING")

        if "FRIGHTENED" in player.status_effects:
            print(colored_text(f"😰 {player.name} is still frightened!", Fore.YELLOW))
            player.status_effects.remove("FRIGHTENED")

        if "FROZEN" in player.status_effects:
            print(colored_text(f"❄️ {player.name} is slowed by the freezing effect!", Fore.CYAN))
            player.status_effects.remove("FROZEN")

        if "SHADOWED" in player.status_effects:
            print(colored_text(f"🌙 {player.name} struggles to see through the shadows!", Fore.MAGENTA))
            player.status_effects.remove("SHADOWED")

    def victory_sequence(self, winner, loser):
        time.sleep(1)
        print(colored_text(f"\n💀 {loser.name} is DEFEATED!", Fore.RED, Style.BRIGHT))
        time.sleep(1)
        print_banner(f"🏆 {winner.name} WINS! 🏆", Fore.GREEN)
        print_separator("=", 50, Fore.YELLOW)
        print(colored_text(f"  {winner.name} stands victorious!", Fore.CYAN, Style.BRIGHT))
        print(champion())
        print_separator("=", 50, Fore.YELLOW)
        for _ in range(3):
            print(colored_text("🎉", Fore.MAGENTA, Style.BRIGHT), end=" ")
            time.sleep(0.3)
        print("\n")

    def player_turn(self, player, enemy):
        is_bot = "Bot" in player.name

        if isinstance(player, Boss):
            choice = player.boss_ai_choice(enemy)
            print(colored_text(f"🤖 {player.name} prepares a {choice.replace('_', ' ').title()}!", Fore.LIGHTBLACK_EX))
            time.sleep(0.8)
        
            if choice == "claw_strike":
                player.claw_strike(enemy, is_bot)
            elif choice == "fire_breath":
                player.fire_breath(enemy, is_bot)
            elif choice == "wing_slam":
                player.wing_slam(enemy, is_bot)
            elif choice == "roar_of_terror":
                player.roar_of_terror(enemy, is_bot)
            elif choice == "berserker_fury":
                player.berserker_fury(enemy, is_bot)
            else:
                player.claw_strike(enemy, is_bot)
            return

        if isinstance(player, Knight):
            if is_bot:
                choice = str(np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.2, 0.2, 0.2, 0.1]))
                print(colored_text(f"🤖 {player.name} chooses option {choice}", Fore.LIGHTBLACK_EX))
                time.sleep(0.8)
            else:
                print(colored_text("Choose your action:", Fore.WHITE, Style.BRIGHT))
                print(f"{colored_text('1)', Fore.RED)} Sword Slash")
                print(f"{colored_text('2)', Fore.YELLOW)} Shield Bash")
                print(f"{colored_text('3)', Fore.MAGENTA)} Mighty Strike")
                print(f"{colored_text('4)', Fore.CYAN)} Rapid Strikes (3 hits)")
                print(f"{colored_text('5)', Fore.GREEN)} Use Item")
                choice = input(colored_text("Enter choice (1-5): ", Fore.CYAN))

            if choice == "1": player.sword_slash(enemy, is_bot)
            elif choice == "2": player.shield_bash(enemy, is_bot)
            elif choice == "3": player.mighty_strike(enemy, is_bot)
            elif choice == "4": player.rapid_strikes(enemy, is_bot)
            elif choice == "5" and not is_bot: self.use_item(player, enemy)
            else: player.sword_slash(enemy, is_bot)

        elif isinstance(player, Orc):
            if is_bot:
                if player.attack_buff_turns <= 0 and np.random.random() < 0.6:
                    choice = "3"
                else:
                    choice = str(np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.1, 0.1]))
                print(colored_text(f"🤖 {player.name} chooses option {choice}", Fore.LIGHTBLACK_EX))
                time.sleep(0.8)
            else:
                print(colored_text("Choose your action:", Fore.WHITE, Style.BRIGHT))
                print(f"{colored_text('1)', Fore.RED)} Cleave")
                print(f"{colored_text('2)', Fore.MAGENTA)} Berserk Strike")
                print(f"{colored_text('3)', Fore.GREEN)} Roar")
                print(f"{colored_text('4)', Fore.GREEN)} Use Item")
                choice = input(colored_text("Enter choice (1-4): ", Fore.CYAN))

            if choice == "1": player.cleave(enemy, is_bot)
            elif choice == "2": player.berserk_strike(enemy, is_bot)
            elif choice == "3": player.roar(is_bot)
            elif choice == "4" and not is_bot: self.use_item(player, enemy)
            else: player.cleave(enemy, is_bot)

        elif isinstance(player, Mage):
            if is_bot:
                if player.cooldowns["meteor"] == 0 and np.random.random() < 0.4:
                    choice = "3"
                elif player.hp < player.max_hp // 2 and player.cooldowns["heal"] == 0:
                    choice = "2"
                else:
                    choice = str(np.random.choice([1, 2, 3], p=[0.6, 0.2, 0.2]))
                print(colored_text(f"🤖 {player.name} chooses option {choice}", Fore.LIGHTBLACK_EX))
                time.sleep(0.8)
            else:
                print(colored_text("Choose your action:", Fore.WHITE, Style.BRIGHT))
                print(f"{colored_text('1)', Fore.CYAN)} Arcane Lance")
                print(f"{colored_text('2)', Fore.GREEN)} Celestial Healing (self-heal)")
                print(f"{colored_text('3)', Fore.RED)} Meteor Fall (AoE)")
                choice = input(colored_text("Enter choice (1-3): ", Fore.CYAN))

            if choice == "1": player.arcane_lance(enemy, is_bot)
            elif choice == "2": player.celestial_healing()
            elif choice == "3": player.meteor_fall([enemy], is_bot)
            else: player.arcane_lance(enemy, is_bot)

        elif isinstance(player, Ninja):
            if is_bot:
                if player.shadowstep_cooldown == 0 and np.random.random() < 0.3:
                    choice = "1"
                elif player.shuriken_count > 0 and np.random.random() < 0.4:
                    choice = "3"
                elif hasattr(player, 'smoke_bomb_used') and not player.smoke_bomb_used and player.hp < player.max_hp * 0.3:
                    choice = "4"
                else:
                    choice = "2"
                print(colored_text(f"🤖 {player.name} chooses option {choice}", Fore.LIGHTBLACK_EX))
                time.sleep(0.8)
            else:
                print(colored_text("Choose your action:", Fore.WHITE, Style.BRIGHT))
                print(f"{colored_text('1)', Fore.MAGENTA)} Shadowstep (Dodge boost)")
                print(f"{colored_text('2)', Fore.CYAN)} Twin Fang Slash")
                print(f"{colored_text('3)', Fore.YELLOW)} Shuriken Storm ({player.shuriken_count} left)")
                print(f"{colored_text('4)', Fore.RED)} Smoke Bomb Escape")
                print(f"{colored_text('5)', Fore.GREEN)} Use Item")
                choice = input(colored_text("Enter choice (1-5): ", Fore.CYAN))

            if choice == "1":
                if not player.shadowstep(is_bot):
                    player.twin_fang_slash(enemy, is_bot)
            elif choice == "2":
                player.twin_fang_slash(enemy, is_bot)
            elif choice == "3":
                if not player.shuriken_storm(enemy, is_bot):
                    player.twin_fang_slash(enemy, is_bot)
            elif choice == "4":
                if not player.smoke_bomb_escape(is_bot):
                    player.twin_fang_slash(enemy, is_bot)
            elif choice == "5" and not is_bot:
                self.use_item(player, enemy)
            else:
                player.twin_fang_slash(enemy, is_bot)

    def use_item(self, player, enemy):
        if not player.items:
            print(colored_text("No items available!", Fore.RED))
            return

        print(colored_text("Available items:", Fore.CYAN))
        for i, item in enumerate(player.items):
            print(f"{i+1}) {item.name}")

        try:
            choice = int(input("Choose item: ")) - 1
            if 0 <= choice < len(player.items):
                item = player.items.pop(choice)
                if isinstance(item, Potion):
                    item.use(player)
                elif isinstance(item, Bomb):
                    item.use(player, enemy)
            else:
                print(colored_text("Invalid choice!", Fore.RED))
        except (ValueError, IndexError):
            print(colored_text("Invalid choice!", Fore.RED))
