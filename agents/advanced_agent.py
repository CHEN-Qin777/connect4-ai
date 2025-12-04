"""
Advanced Agent for Connect 4 using Minimax with memoization and suicide detection
This agent is optimized for MLArena competition with time and memory constraints.
"""

import numpy as np
import random
import math
import time

class AdvancedAgent:
    def __init__(self, env, player_name=None):
        """
        Initialize advanced agent with Minimax and memoization

        Args:
            env: PettingZoo environment
            player_name: Optional agent name
        """
        self.env = env
        # Target depth: 6
        # With transposition table (TT), we can reach depth 6 within 3 seconds
        # Depth 6 consistently beats depth 5 and is more stable than iterative search
        self.depth = 6
        self.ROW_COUNT = 6
        self.COLUMN_COUNT = 7
        self.AI_PIECE = 2  # AI piece
        self.PLAYER_PIECE = 1  # Player piece
        
        # Transposition table: stores already calculated positions {bytes: score}
        self.memo = {}
        
        # Precomputed search order: center priority for better pruning
        self.col_order = [3, 2, 4, 1, 5, 0, 6]

    def choose_action(self, observation, reward=0.0, terminated=False, truncated=False, info=None, action_mask=None):
        """
        Choose action using optimized Minimax

        Strategy:
        1. Immediate win/block checks
        2. Minimax with memoization
        3. Suicide move detection

        Returns:
            int: Column to play (0-6)
        """
        # Clear memory each turn (or keep it, but clear to avoid memory issues and sync problems)
        self.memo = {} 
        
        # 1. Board analysis
        board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT), dtype=int)
        board[observation[:, :, 0] == 1] = self.AI_PIECE
        board[observation[:, :, 1] == 1] = self.PLAYER_PIECE

        # 2. [Ultra-fast reaction layer] No search tree, direct checks
        valid_moves = self.get_valid_locations(board)
        
        # A. If I have immediate win, play it!
        for col in valid_moves:
            row = self.get_next_open_row(board, col)
            board[row][col] = self.AI_PIECE
            if self.winning_move(board, self.AI_PIECE):
                return col
            board[row][col] = 0 # Undo
            
        # B. If opponent has immediate win, block!
        for col in valid_moves:
            row = self.get_next_open_row(board, col)
            board[row][col] = self.PLAYER_PIECE
            if self.winning_move(board, self.PLAYER_PIECE):
                return col # Only saving move
            board[row][col] = 0 # Undo

        # 3. [Main brain] Minimax with memoization
        # Depth 6 with memoization can be computed in 1-2 seconds
        try:
            col, score = self.minimax(board, self.depth, -math.inf, math.inf, True)
        except TimeoutError:
            # In case of timeout (unlikely), choose randomly
            col = None

        # 4. [Safety net] Suicide detection
        # Mechanism absent from basic "advanced" version, key to victory
        if col is None:
            if not valid_moves: return None
            col = random.choice(valid_moves)
        
        # Check if move is suicidal
        if self.is_suicide_move(board, col):
            # Try to find alternative
            best_safe_col = None
            best_safe_score = -math.inf
            
            # Re-evaluate remaining safe moves
            for c in valid_moves:
                if not self.is_suicide_move(board, c):
                    # Simple scoring: center priority
                    score = 0
                    if c == 3: score += 5
                    elif c in [2, 4]: score += 3
                    
                    if score > best_safe_score:
                        best_safe_score = score
                        best_safe_col = c
            
            if best_safe_col is not None:
                print(f"Correction: move {col} was suicidal, playing {best_safe_col} instead")
                col = best_safe_col
            # If all moves are suicidal, play anyway

        return col

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        """
        Minimax algorithm with alpha-beta pruning and memoization

        Args:
            board: Board state
            depth: Remaining depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizingPlayer: True if maximizing player's turn

        Returns:
            tuple: (column, score)
        """
        # Transposition table lookup
        board_bytes = board.tobytes()
        if board_bytes in self.memo:
            return None, self.memo[board_bytes]

        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, self.AI_PIECE):
                    return (None, 10000000 + depth)  # Prefer faster wins
                elif self.winning_move(board, self.PLAYER_PIECE):
                    return (None, -10000000 - depth)  # Prefer slower losses
                else: 
                    return (None, 0)  # Draw
            else: 
                return (None, self.score_position(board, self.AI_PIECE))

        # Move order optimization: center first for better pruning
        valid_locations.sort(key=lambda x: abs(x - 3)) 

        if maximizingPlayer:
            value = -math.inf
            column = valid_locations[0]
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                board[row][col] = self.AI_PIECE
                
                new_score = self.minimax(board, depth-1, alpha, beta, False)[1]
                board[row][col] = 0 # Undo
                
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta: break
            
            # Store in memory
            self.memo[board_bytes] = value
            return column, value

        else: 
            value = math.inf
            column = valid_locations[0]
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                board[row][col] = self.PLAYER_PIECE
                
                new_score = self.minimax(board, depth-1, alpha, beta, True)[1]
                board[row][col] = 0 # Undo
                
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta: break
                
            self.memo[board_bytes] = value
            return column, value

    def is_suicide_move(self, board, col):
        """
        Check if this move is suicidal (opponent can win next move)

        Args:
            board: Board state
            col: Column to check

        Returns:
            bool: True if move is suicidal
        """
        temp_board = board.copy()
        row = self.get_next_open_row(temp_board, col)
        if row is None: return False
        temp_board[row][col] = self.AI_PIECE
        
        # Check all possible opponent responses
        for opp_c in self.get_valid_locations(temp_board):
            opp_r = self.get_next_open_row(temp_board, opp_c)
            temp_board[opp_r][opp_c] = self.PLAYER_PIECE
            if self.winning_move(temp_board, self.PLAYER_PIECE):
                return True
            temp_board[opp_r][opp_c] = 0 # Undo
        return False

    def score_position(self, board, piece):
        """
        Evaluate board position

        Args:
            board: Board state
            piece: Piece to evaluate

        Returns:
            int: Position score
        """
        score = 0
        opp_piece = self.PLAYER_PIECE if piece == self.AI_PIECE else self.AI_PIECE

        # 1. High weight for center
        center_array = list(board[:, 3])
        center_count = center_array.count(piece)
        score += center_count * 6

        # 2. Full board scan
        # Optimization: group 4 direction checks
        # Horizontal
        for r in range(self.ROW_COUNT):
            row_array = list(board[r, :])
            for c in range(self.COLUMN_COUNT - 3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece, opp_piece)
        # Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = list(board[:, c])
            for r in range(self.ROW_COUNT - 3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece, opp_piece)
        # Positive diagonal
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece, opp_piece)
        # Negative diagonal
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece, opp_piece)
        return score

    def evaluate_window(self, window, piece, opp_piece):
        """
        Evaluate 4-piece window

        Args:
            window: 4-piece window
            piece: Our piece
            opp_piece: Opponent piece

        Returns:
            int: Window score
        """
        score = 0
        # Adjusted weights to make AI more aggressive
        if window.count(piece) == 4: score += 1000000
        elif window.count(piece) == 3 and window.count(0) == 1: score += 100 # 3 in a row big bonus
        elif window.count(piece) == 2 and window.count(0) == 2: score += 10

        # Defense: opponent 3 in a row must be penalized, but not infinitely to avoid blocking lost games
        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 8000 
        
        return score

    # --- Basic tools ---
    def get_valid_locations(self, board):
        """Get valid columns"""
        return [c for c in range(self.COLUMN_COUNT) if board[0][c] == 0]
    
    def get_next_open_row(self, board, col):
        """Find next open row (fast search)"""
        for r in range(self.ROW_COUNT - 1, -1, -1):
            if board[r][col] == 0: return r
        return None
    
    def is_terminal_node(self, board):
        """Check if node is terminal"""
        return self.winning_move(board, self.AI_PIECE) or self.winning_move(board, self.PLAYER_PIECE) or len(self.get_valid_locations(board)) == 0
    
    def winning_move(self, board, piece):
        """Check wins (optimized method in Python)"""
        # Horizontal
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece: return True
        # Vertical
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT - 3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece: return True
        # Positive diagonals
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT - 3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece: return True
        # Negative diagonals
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(3, self.ROW_COUNT):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece: return True
        return False
