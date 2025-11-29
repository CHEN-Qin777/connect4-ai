"""
MCTS Agent (Monte Carlo Tree Search) for Connect Four
Exercise 5: Advanced challenges
"""

import numpy as np
import random
import math
import time


class MCTSNode:
    """
    Node in MCTS tree
    """

    def __init__(self, board, player, parent=None, move=None):
        """
        Initialize MCTS node

        Parameters:
            board: Game state
            player: Whose turn (0 or 1)
            parent: Parent node
            move: Move that led to this node
        """
        self.board = board        # Game state
        self.player = player      # Player turn
        self.parent = parent      # Parent node
        self.move = move          # Move that led here
        self.children = []        # Child nodes
        self.visits = 0           # Times visited
        self.wins = 0             # Times led to win
        self.untried_moves = self._get_valid_moves(board)  # Untried moves

    def is_fully_expanded(self):
        """Check if all children have been added"""
        return len(self.untried_moves) == 0

    def best_child(self, c=1.41):
        """
        Select best child using UCB1

        Parameters:
            c: exploration constant

        Returns:
            MCTSNode: best child
        """
        choices_weights = [
            (child.wins / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits)
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def _get_valid_moves(self, board):
        """Get valid moves from this state"""
        return [c for c in range(7) if board[0][c] == 0]


class MCTSAgent:
    """
    Agent using Monte Carlo Tree Search
    """

    def __init__(self, env, time_limit=1.0, player_name=None):
        """
        Initialize MCTS agent

        Parameters:
            env: PettingZoo environment
            time_limit: Time budget per move (seconds)
            player_name: Optional agent name
        """
        self.env = env
        self.time_limit = time_limit
        self.player_name = player_name or "MCTS"
        self.ROW_COUNT = 6
        self.COLUMN_COUNT = 7
        self.AI_PIECE = 1
        self.OPPONENT_PIECE = 0

    def choose_action(self, observation, reward=0.0, terminated=False, truncated=False, info=None, action_mask=None):
        """
        Choose action using MCTS

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
        # Convert observation
        board = self._observation_to_board(observation)
        
        # Create root node
        root = MCTSNode(board, player=0)  # We are player 0

        start_time = time.time()

        # Run MCTS until time limit
        simulations = 0
        while time.time() - start_time < self.time_limit:
            # 1. Selection
            node = self._select(root)

            # 2. Expansion
            if not self._is_terminal(node):
                node = self._expand(node)

            # 3. Simulation
            result = self._simulate(node)

            # 4. Backpropagation
            self._backpropagate(node, result)

            simulations += 1

        # Choose best move (exploitation only)
        best_child = root.best_child(c=0)  # c=0 means exploitation only
        print(f"MCTS: {simulations} simulations performed")
        return best_child.move

    def _select(self, node):
        """
        Select promising node to explore

        Returns:
            node: node to expand
        """
        while node.is_fully_expanded() and not self._is_terminal(node):
            node = node.best_child()
        return node

    def _expand(self, node):
        """
        Add new child to node

        Returns:
            new_child: new child node
        """
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            
            # Create new state
            new_board = self._make_move(node.board.copy(), move, node.player)
            new_player = 1 - node.player  # Switch player
            
            # Create new child
            child = MCTSNode(new_board, new_player, parent=node, move=move)
            node.children.append(child)
            return child
        
        return node

    def _simulate(self, node):
        """
        Play random game from node

        Returns:
            result: result (1 for win, 0 for loss, 0.5 for draw)
        """
        current_board = node.board.copy()
        current_player = node.player
        
        while not self._is_terminal_board(current_board):
            # Choose random move
            valid_moves = [c for c in range(7) if current_board[0][c] == 0]
            if not valid_moves:
                break  # Draw
                
            move = random.choice(valid_moves)
            current_board = self._make_move(current_board, move, current_player)
            
            # Check win
            if self._winning_move(current_board, current_player):
                # Return result from original node's perspective
                return 1.0 if current_player == 0 else 0.0
            
            current_player = 1 - current_player
        
        # Draw
        return 0.5

    def _backpropagate(self, node, result):
        """
        Update statistics up the tree

        Parameters:
            node: Leaf node where simulation started
            result: Game result
        """
        while node is not None:
            node.visits += 1
            # For root node (player 0), win is good result
            if node.player == 0:
                node.wins += result
            else:
                node.wins += (1 - result)  # Inverse for opponent
            node = node.parent

    def _is_terminal(self, node):
        """Check if game is over for this node"""
        return self._is_terminal_board(node.board)

    def _is_terminal_board(self, board):
        """Check if game is over for this board"""
        return (self._winning_move(board, 0) or 
                self._winning_move(board, 1) or 
                len([c for c in range(7) if board[0][c] == 0]) == 0)

    def _winning_move(self, board, piece):
        """Check if player has won"""
        # Check horizontal wins
        for c in range(4):
            for r in range(6):
                if (board[r][c] == piece and 
                    board[r][c+1] == piece and 
                    board[r][c+2] == piece and 
                    board[r][c+3] == piece):
                    return True

        # Check vertical wins
        for c in range(7):
            for r in range(3):
                if (board[r][c] == piece and 
                    board[r+1][c] == piece and 
                    board[r+2][c] == piece and 
                    board[r+3][c] == piece):
                    return True

        # Check positive diagonals
        for c in range(4):
            for r in range(3):
                if (board[r][c] == piece and 
                    board[r+1][c+1] == piece and 
                    board[r+2][c+2] == piece and 
                    board[r+3][c+3] == piece):
                    return True

        # Check negative diagonals
        for c in range(4):
            for r in range(3, 6):
                if (board[r][c] == piece and 
                    board[r-1][c+1] == piece and 
                    board[r-2][c+2] == piece and 
                    board[r-3][c+3] == piece):
                    return True

        return False

    def _make_move(self, board, col, player):
        """
        Make move on board

        Parameters:
            board: Current board
            col: Column to play
            player: Player who plays

        Returns:
            new_board: New board
        """
        new_board = board.copy()
        for r in range(5, -1, -1):
            if new_board[r][col] == 0:
                new_board[r][col] = player
                break
        return new_board

    def _observation_to_board(self, observation):
        """
        Convert PettingZoo observation to simple board format
        """
        board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT), dtype=int)
        
        for r in range(self.ROW_COUNT):
            for c in range(self.COLUMN_COUNT):
                if observation[r, c, 0] == 1:
                    board[r][c] = self.AI_PIECE
                elif observation[r, c, 1] == 1:
                    board[r][c] = self.OPPONENT_PIECE
        
        return board