# combat_mechanics.py
from colorama import Fore, Style
from game_utils import colored_text
import numpy as np

ELEMENTAL_EFFECTS = {
    'fire': {
        'damage_mod': 1.2,
        'effect': 'BURNING',
        'effect_desc': 'takes damage over time',
        'color': Fore.RED
    },
    'ice': {
        'damage_mod': 0.9,
        'effect': 'FROZEN',
        'effect_desc': 'slows attack speed',
        'color': Fore.CYAN
    },
    'lightning': {
        'damage_mod': 1.1,
        'effect': 'SHOCKED',
        'effect_desc': 'chance to stun',
        'color': Fore.YELLOW
    },
    'shadow': {
        'damage_mod': 1.15,
        'effect': 'SHADOWED',
        'effect_desc': 'reduced accuracy',
        'color': Fore.MAGENTA
    }
}

def calculate_elemental_effects(attacker, defender, base_damage, element=None):
    # Use the provided element or fallback to attacker's affinity
    active_element = element or attacker.elemental_affinity
    
    if not active_element:
        return base_damage
    
    effect_info = ELEMENTAL_EFFECTS.get(active_element)
    if not effect_info:
        return base_damage
    
    # Apply damage modifier
    modified_damage = base_damage * effect_info['damage_mod']
    
    # Chance to apply status effect
    if np.random.random() < 0.4:  # 40% chance
        defender.add_status_effect(effect_info['effect'])
        print(colored_text(
            f"✨ {defender.name} is {effect_info['effect']}! {effect_info['effect_desc']}!",
            effect_info['color'], Style.BRIGHT
        ))
    
    return modified_damage

def check_combo(character, current_move):
    if character.last_move == current_move:
        character.combo_counter += 1
    else:
        character.combo_counter = 1
    
    character.last_move = current_move
    
    if character.combo_counter >= 3:
        combo_bonus = 1.2 + (0.1 * character.combo_counter)
        print(colored_text(
            f"🔥 COMBO x{character.combo_counter}! Damage multiplier: {combo_bonus:.1f}x",
            Fore.MAGENTA, Style.BRIGHT
        ))
        return combo_bonus
    return 1.0

def attempt_block(defender, damage):
    block_roll = np.random.random()
    if block_roll < defender.block_chance:
        blocked_damage = damage * 0.5  # Blocks 50% of damage
        print(colored_text(
            f"🛡️ {defender.name} blocks the attack! Reduces damage by 50%!",
            Fore.BLUE, Style.BRIGHT
        ))
        return blocked_damage
    return damage

def attempt_dodge(defender, base_dodge_chance=0.0):
    """Check if defender dodges the attack completely"""
    dodge_chance = base_dodge_chance + getattr(defender, 'dodge_chance', 0)
    if np.random.random() < dodge_chance:
        print(colored_text(
            f"💨 {defender.name} dodges the attack completely!",
            Fore.CYAN, Style.BRIGHT
        ))
        return True
    return False