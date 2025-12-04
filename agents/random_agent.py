"""
My Random Agent for Connect Four

This agent chooses valid moves randomly.
Used as baseline for comparison.
"""

import random


class RandomAgent:
    """
    Simple agent that plays randomly
    """

    def __init__(self, env, player_name=None):
        """
        Initialize random agent

        Args:
            env: PettingZoo environment
            player_name: Optional agent name
        """
        self.env = env
        
        self.player_name = player_name or "RandomAgent"

    def choose_action(self, observation, reward=0.0, terminated=False, truncated=False, info=None, action_mask=None):
        """
        Choose random valid action

        Args:
            observation: Current board state (6, 7, 2)
            reward: Previous action reward
            terminated: Is game over?
            truncated: Was game truncated?
            info: Additional info
            action_mask: Valid actions mask (1=valid, 0=invalid)

        Returns:
            action: Column index (0-6) to play
        """
        # Get valid actions from mask
        valid_actions = [i for i, valid in enumerate(action_mask) if valid == 1]
        
        # Choose randomly from valid actions
        if valid_actions:
            return random.choice(valid_actions)
        else:
            return None  # No valid moves (shouldn't happen)

