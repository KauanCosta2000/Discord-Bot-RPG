import re
import random
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DiceRoll:
    def __init__(self, notation: str):
        self.notation = notation.strip()
        self.results = []
        self.total = 0
        self.exploded = []
        self.advantage = False
        self.disadvantage = False
        
    def __str__(self):
        return f"{self.notation}: {self.total} ({', '.join(map(str, self.results))})"

class DiceParser:
    """Advanced dice notation parser and roller"""
    
    DICE_PATTERN = re.compile(r'(\d+)d(\d+)([+-]\d+)?(![<>]\d+)?', re.IGNORECASE)
    
    @staticmethod
    def roll(notation: str) -> DiceRoll:
        """Parse and roll dice notation"""
        notation = notation.strip()
        roll = DiceRoll(notation)
        
        # Handle advantage/disadvantage
        if notation.startswith('adv '):
            roll.advantage = True
            notation = notation[4:]
        elif notation.startswith('dis '):
            roll.disadvantage = True
            notation = notation[4:]
        
        # Parse dice notation
        match = DiceParser.DICE_PATTERN.match(notation)
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")
        
        num_dice = int(match.group(1))
        dice_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        special = match.group(4)
        
        # Roll dice
        rolls = []
        for _ in range(num_dice):
            roll_result = random.randint(1, dice_sides)
            rolls.append(roll_result)
            
            # Handle exploding dice
            if special and special.startswith('!'):
                if special.startswith('!>'):
                    threshold = int(special[2:])
                    while roll_result >= threshold:
                        new_roll = random.randint(1, dice_sides)
                        rolls.append(new_roll)
                        roll.exploded.append(new_roll)
                        roll_result = new_roll
        
        # Handle advantage/disadvantage
        if roll.advantage or roll.disadvantage:
            second_rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
            if roll.advantage:
                rolls = [max(r1, r2) for r1, r2 in zip(rolls, second_rolls)]
            else:  # disadvantage
                rolls = [min(r1, r2) for r1, r2 in zip(rolls, second_rolls)]
        
        roll.results = rolls
        roll.total = sum(rolls) + modifier
        
        return roll
    
    @staticmethod
    def roll_multiple(notations: List[str]) -> List[DiceRoll]:
        """Roll multiple dice notations"""
        return [DiceParser.roll(notation) for notation in notations]
    
    @staticmethod
    def success_threshold(roll: DiceRoll, threshold: int) -> Dict[str, Any]:
        """Calculate success based on threshold"""
        successes = sum(1 for result in roll.results if result >= threshold)
        return {
            'successes': successes,
            'failures': len(roll.results) - successes,
            'total': roll.total,
            'threshold': threshold
        }
    
    @staticmethod
    def initiative_roll(character_name: str, modifier: int = 0) -> Dict[str, Any]:
        """Roll initiative for a character"""
        roll = DiceParser.roll('1d20')
        total = roll.total + modifier
        return {
            'character': character_name,
            'roll': roll.total,
            'modifier': modifier,
            'total': total,
            'string': f"{character_name}: {roll.total} + {modifier} = {total}"
        }

class InitiativeTracker:
    """Track initiative order for encounters"""
    
    def __init__(self):
        self.participants = []
        self.current_turn = 0
        self.round_number = 1
        
    def add_participant(self, name: str, initiative: int, hp: int = None, ac: int = None):
        """Add participant to initiative"""
        self.participants.append({
            'name': name,
            'initiative': initiative,
            'hp': hp,
            'ac': ac,
            'status': 'active'
        })
        
        # Sort by initiative (descending)
        self.participants.sort(key=lambda x: x['initiative'], reverse=True)
    
    def remove_participant(self, name: str):
        """Remove participant from initiative"""
        self.participants = [p for p in self.participants if p['name'].lower() != name.lower()]
    
    def next_turn(self):
        """Move to next turn"""
        if not self.participants:
            return None
            
        self.current_turn = (self.current_turn + 1) % len(self.participants)
        if self.current_turn == 0:
            self.round_number += 1
            
        return self.get_current()
    
    def get_current(self):
        """Get current participant"""
        if not self.participants:
            return None
        return self.participants[self.current_turn]
    
    def get_order(self):
        """Get full initiative order"""
        return self.participants
    
    def reset(self):
        """Reset initiative tracker"""
        self.participants = []
        self.current_turn = 0
        self.round_number = 1