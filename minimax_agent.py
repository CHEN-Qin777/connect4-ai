"""
Minimax Agent with Alpha-Beta Pruning for Connect Four
Exercise 5: Advanced challenges
"""

import numpy as np
import random
import math
import time


class MinimaxAgent:
    """
    Agent using Minimax algorithm with alpha-beta pruning
    """

    def __init__(self, env, depth=4, player_name=None):
        """
        Initialize Minimax agent

        Parameters:
            env: PettingZoo environment
            depth: How many moves to look ahead
            player_name: Optional agent name
        """
        self.env = env
        self.depth = depth
        self.player_name = player_name or f"Minimax(d={depth})"
        self.ROW_COUNT = 6
        self.COLUMN_COUNT = 7
        self.AI_PIECE = 1  # Our agent
        self.OPPONENT_PIECE = 0  # Opponent

    def choose_action(self, observation, reward=0.0, terminated=False, truncated=False, info=None, action_mask=None):
        """
        Choose action using Minimax algorithm

        Parameters:
            observation: Current board state
            reward: Previous action reward
            terminated: Is game over?
            truncated: Was game truncated?
            info: Additional info
            action_mask: Valid actions mask

        Returns:
            action: Column to play
        """
        # Convert observation to simple board format
        board = self._observation_to_board(observation)
        
        # Get valid moves
        valid_actions = [i for i, valid in enumerate(action_mask) if valid == 1]
        
        # Check immediate winning moves (optimization)
        for col in valid_actions:
            row = self._get_next_open_row(board, col)
            if row is not None:
                board[row][col] = self.AI_PIECE
                if self._winning_move(board, self.AI_PIECE):
                    return col
                board[row][col] = 0  # Undo
        
        # Check blocking moves (optimization)
        for col in valid_actions:
            row = self._get_next_open_row(board, col)
            if row is not None:
                board[row][col] = self.OPPONENT_PIECE
                if self._winning_move(board, self.OPPONENT_PIECE):
                    return col
                board[row][col] = 0  # Undo
        
        # Use Minimax for strategic decisions
        best_score = -math.inf
        best_action = valid_actions[0]
        
        # Order columns by preference (center first)
        ordered_actions = self._order_columns(valid_actions)
        
        for col in ordered_actions:
            row = self._get_next_open_row(board, col)
            if row is not None:
                # Simulate move
                board[row][col] = self.AI_PIECE
                
                # Evaluate with Minimax
                score = self._minimax(board, self.depth - 1, -math.inf, math.inf, False)
                
                # Undo simulation
                board[row][col] = 0
                
                if score > best_score:
                    best_score = score
                    best_action = col
        
        return best_action

    def _minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning

        Parameters:
            board: Current board state
            depth: Remaining depth to search
            alpha: Best value for maximizer
            beta: Best value for minimizer
            maximizing_player: True if maximizing player's turn

        Returns:
            float: evaluation score
        """
        # Base case: depth reached or terminal node
        valid_locations = self._get_valid_locations(board)
        is_terminal = self._is_terminal_node(board)
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if self._winning_move(board, self.AI_PIECE):
                    return 100000000000000 + depth  # Prefer faster wins
                elif self._winning_move(board, self.OPPONENT_PIECE):
                    return -100000000000000 - depth  # Prefer slower losses
                else:
                    return 0  # Draw
            else:
                return self._evaluate_board(board, self.AI_PIECE)

        if maximizing_player:
            value = -math.inf
            for col in self._order_columns(valid_locations):
                row = self._get_next_open_row(board, col)
                if row is not None:
                    board[row][col] = self.AI_PIECE
                    value = max(value, self._minimax(board, depth - 1, alpha, beta, False))
                    board[row][col] = 0  # Undo
                    
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break  # Beta pruning
            return value
        else:
            value = math.inf
            for col in self._order_columns(valid_locations):
                row = self._get_next_open_row(board, col)
                if row is not None:
                    board[row][col] = self.OPPONENT_PIECE
                    value = min(value, self._minimax(board, depth - 1, alpha, beta, True))
                    board[row][col] = 0  # Undo
                    
                    beta = min(beta, value)
                    if alpha >= beta:
                        break  # Alpha pruning
            return value

    def _evaluate_board(self, board, piece):
        """
        Evaluate board position for given player

        Parameters:
            board: Board state
            piece: Player piece to evaluate

        Returns:
            float: score (positive = good for player)
        """
        score = 0
        opponent_piece = self.OPPONENT_PIECE if piece == self.AI_PIECE else self.AI_PIECE

        # Prefer center
        center_array = [board[i][3] for i in range(self.ROW_COUNT)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Evaluate 4-piece windows
        # Horizontal
        for r in range(self.ROW_COUNT):
            row_array = [board[r][c] for c in range(self.COLUMN_COUNT)]
            for c in range(self.COLUMN_COUNT - 3):
                window = row_array[c:c+4]
                score += self._evaluate_window(window, piece, opponent_piece)

        # Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [board[r][c] for r in range(self.ROW_COUNT)]
            for r in range(self.ROW_COUNT - 3):
                window = col_array[r:r+4]
                score += self._evaluate_window(window, piece, opponent_piece)

        # Positive diagonal (ascending)
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self._evaluate_window(window, piece, opponent_piece)

        # Negative diagonal (descending)
        for r in range(3, self.ROW_COUNT):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r-i][c+i] for i in range(4)]
                score += self._evaluate_window(window, piece, opponent_piece)

        return score

    def _evaluate_window(self, window, piece, opponent_piece):
        """
        Evaluate 4-piece window

        Parameters:
            window: List of 4 pieces
            piece: Our piece
            opponent_piece: Opponent piece

        Returns:
            int: score for this window
        """
        score = 0

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opponent_piece) == 3 and window.count(0) == 1:
            score -= 4

        return score

    def _observation_to_board(self, observation):
        """
        Convert PettingZoo observation to simple board format

        Parameters:
            observation: PettingZoo observation (6, 7, 2)

        Returns:
            list: 6x7 board with 0=empty, 1=us, 2=opponent
        """
        board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT), dtype=int)
        
        # Channel 0: current player pieces
        # Channel 1: opponent pieces
        for r in range(self.ROW_COUNT):
            for c in range(self.COLUMN_COUNT):
                if observation[r, c, 0] == 1:
                    board[r][c] = self.AI_PIECE
                elif observation[r, c, 1] == 1:
                    board[r][c] = self.OPPONENT_PIECE
        
        return board

    def _get_valid_locations(self, board):
        """Get list of valid columns"""
        return [c for c in range(self.COLUMN_COUNT) if board[0][c] == 0]

    def _get_next_open_row(self, board, col):
        """Find next open row in column"""
        for r in range(self.ROW_COUNT - 1, -1, -1):
            if board[r][col] == 0:
                return r
        return None

    def _is_terminal_node(self, board):
        """Check if node is terminal (win or board full)"""
        return (self._winning_move(board, self.AI_PIECE) or 
                self._winning_move(board, self.OPPONENT_PIECE) or 
                len(self._get_valid_locations(board)) == 0)

    def _winning_move(self, board, piece):
        """Check if player has won"""
        # Check horizontal wins
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT):
                if (board[r][c] == piece and 
                    board[r][c+1] == piece and 
                    board[r][c+2] == piece and 
                    board[r][c+3] == piece):
                    return True

        # Check vertical wins
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT - 3):
                if (board[r][c] == piece and 
                    board[r+1][c] == piece and 
                    board[r+2][c] == piece and 
                    board[r+3][c] == piece):
                    return True

        # Check positive diagonals
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT - 3):
                if (board[r][c] == piece and 
                    board[r+1][c+1] == piece and 
                    board[r+2][c+2] == piece and 
                    board[r+3][c+3] == piece):
                    return True

        # Check negative diagonals
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(3, self.ROW_COUNT):
                if (board[r][c] == piece and 
                    board[r-1][c+1] == piece and 
                    board[r-2][c+2] == piece and 
                    board[r-3][c+3] == piece):
                    return True

        return False

    def _order_columns(self, columns):
        """Order columns by preference (center first)"""
        center = self.COLUMN_COUNT // 2
        return sorted(columns, key=lambda x: abs(x - center))