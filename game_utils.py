import numpy as np
import time
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# ====== Color Helpers ======
def colored_text(text, color=Fore.WHITE, style=Style.NORMAL):
    return f"{style}{color}{text}{Style.RESET_ALL}"

def print_banner(text, color=Fore.CYAN, char="=", width=50):
    print(colored_text(char * width, color))
    print(colored_text(f"{text:^{width}}", color, Style.BRIGHT))
    print(colored_text(char * width, color))

def print_separator(char="-", width=40, color=Fore.YELLOW):
    print(colored_text(char * width, color))

# ====== ASCII Art ======
def champion():
    return  """
        ___________
       '._==_==_=_.'  
       .-\:      /-.  
      | (|:.     |) |  
       '-|:.     |-'  
         \::.    /   
          '::. .'     
            ) (       
          _.' '._
         |=======|     
         """

def battle_ascii():
    return colored_text("""
    ⚔️  EPIC BATTLE COMMENCES  ⚔️
       🛡️  PREPARE FOR WAR  🛡️
    """, Fore.RED, Style.BRIGHT)

# ====== Roll Dice ======
def roll_dice(is_bot=False):
    if not is_bot:
        input(colored_text("Press Enter to roll the d20...", Fore.YELLOW, Style.BRIGHT))
    
    print(colored_text("🎲 Rolling...", Fore.CYAN))
    
    # Dramatic rolling animation
    for i in range(3):
        print(colored_text(f"   {'.' * (i + 1)}", Fore.WHITE))
        time.sleep(0.3)
    
    result = np.random.randint(1, 21)
    
    # Color based on roll quality
    if result == 20:
        print(colored_text(f"🎯 NATURAL 20! You rolled: {result}! 🎯", Fore.MAGENTA, Style.BRIGHT))
    elif result == 1:
        print(colored_text(f"💥 CRITICAL FAIL! You rolled: {result}! 💥", Fore.RED, Style.BRIGHT))
    elif result >= 16:
        print(colored_text(f"⚡ EXCELLENT! You rolled: {result}!", Fore.GREEN, Style.BRIGHT))
    elif result >= 11:
        print(colored_text(f"✓ Good roll: {result}", Fore.YELLOW))
    else:
        print(colored_text(f"📉 Low roll: {result}", Fore.RED))
    
    time.sleep(0.8)
    return result