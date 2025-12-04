"""
My Smart Agent for Connect Four

This agent uses rule-based heuristics to play strategically.
Exercise 3: Implement rule-based agent
"""

import random
import numpy as np


class SmartAgent:
    """
    Rule-based agent that plays strategically
    """

    def __init__(self, env, player_name=None):
        """
        Initialize smart agent

        Parameters:
            env: PettingZoo environment
            player_name: Optional agent name
        """
        self.env = env
        self.action_space = env.action_space(env.agents[0])
        self.player_name = player_name or "SmartAgent"
        self.ROW_COUNT = 6
        self.COLUMN_COUNT = 7

    def choose_action(self, observation, reward=0.0, terminated=False, truncated=False, info=None, action_mask=None):
        """
        Choose action using rule-based strategy

        Strategy priority:
        1. Win if possible
        2. Block opponent from winning
        3. Play center if available
        4. Random valid move

        Parameters:
            observation: Current board state (6, 7, 2)
            reward: Previous action reward
            terminated: Is game over?
            truncated: Was game truncated?
            info: Additional info
            action_mask: Valid actions mask

        Returns:
            action: Column to play
        """
        # Get valid actions
        valid_actions = self._get_valid_actions(action_mask)

        # Rule 1: Try to win
        winning_move = self._find_winning_move(observation, valid_actions, channel=0)
        if winning_move is not None:
            return winning_move

        # Rule 2: Block opponent
        blocking_move = self._find_winning_move(observation, valid_actions, channel=1)
        if blocking_move is not None:
            return blocking_move

        # Rule 3: Prefer center
        center_preference = [3, 2, 4, 1, 5, 0, 6]  # Column preference order
        for col in center_preference:
            if col in valid_actions:
                return col

        # Rule 4: Random fallback
        return random.choice(valid_actions)

    def _get_valid_actions(self, action_mask):
        """
        Get list of valid column indices

        Parameters:
            action_mask: numpy array (7,) with 1 for valid, 0 for invalid

        Returns:
            list of valid column indices
        """
        return [i for i, valid in enumerate(action_mask) if valid == 1]

    def _find_winning_move(self, observation, valid_actions, channel):
        """
        Find move that creates 4 in a row for specified player

        Parameters:
            observation: Current board state (6, 7, 2)
            valid_actions: List of valid column indices
            channel: 0 for current player, 1 for opponent

        Returns:
            column index if winning move found, None otherwise
        """
        # Create board copy for simulation
        board = observation.copy()
        
        for col in valid_actions:
            row = self._get_next_row(board, col)
            if row is not None:
                # Simulate placing piece
                board[row, col, channel] = 1
                
                # Check if this creates win
                if self._check_win_from_position(board, row, col, channel):
                    return col
                
                # Undo simulation
                board[row, col, channel] = 0
        
        return None

    def _get_next_row(self, board, col):
        """
        Find which row piece would land in if dropped in column

        Parameters:
            board: numpy array (6, 7, 2)
            col: column index (0-6)

        Returns:
            row index if space available, None if column full
        """
        # Start from bottom row (5) and go up
        for row in range(5, -1, -1):
            # Position is empty if both channels are 0
            if board[row, col, 0] == 0 and board[row, col, 1] == 0:
                return row
        return None  # Column full

    def _check_win_from_position(self, board, row, col, channel):
        """
        Check if placing piece at (row, col) creates 4 in a row

        Parameters:
            board: numpy array (6, 7, 2)
            row: row index (0-5)
            col: column index (0-6)
            channel: 0 or 1 (which player's pieces to check)

        Returns:
            True if position creates 4 in a row, False otherwise
        """
        # Directions to check: (delta_row, delta_col)
        directions = [
            (0, 1),   # Horizontal →
            (1, 0),   # Vertical ↓
            (1, 1),   # Diagonal ↘
            (1, -1)   # Diagonal ↙
        ]
        
        for d_row, d_col in directions:
            count = 1  # Count current piece
            
            # Check positive direction
            for i in range(1, 4):
                r, c = row + i * d_row, col + i * d_col
                if (0 <= r < 6 and 0 <= c < 7 and 
                    board[r, c, channel] == 1):
                    count += 1
                else:
                    break
            
            # Check negative direction
            for i in range(1, 4):
                r, c = row - i * d_row, col - i * d_col
                if (0 <= r < 6 and 0 <= c < 7 and 
                    board[r, c, channel] == 1):
                    count += 1
                else:
                    break
            
            # If we have 4 aligned pieces, it's a win
            if count >= 4:
                return True
        
        return False
