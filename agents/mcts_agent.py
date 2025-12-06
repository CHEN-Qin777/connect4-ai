"""
MCTS Agent (Monte Carlo Tree Search) for Connect Four
Exercise 5: Advanced challenges

Improvements:
- Intelligent simulations: Use heuristics instead of pure random
- Early termination: Stop simulation if winner is clear
- Better move ordering and threat detection
"""

import numpy as np
import time
import math
from copy import deepcopy


class MCTSNode:
    """Node in the MCTS tree"""
    
    def __init__(self, state, action_mask, parent=None, action=None, player=0):
        """
        Initialize MCTS node
        
        Args:
            state: Board state (6, 7, 2) numpy array
            action_mask: Valid actions mask
            parent: Parent node
            action: Action that led to this node
            player: Player who just moved (0 or 1)
        """
        self.state = state.copy()
        self.action_mask = action_mask.copy()
        self.parent = parent
        self.action = action
        self.player = player
        
        self.children = {}
        self.visits = 0
        self.value = 0.0
        
        # Get valid actions, prioritize center columns
        valid = [i for i in range(len(action_mask)) if action_mask[i] == 1]
        # Sort by distance from center (center first for better exploration)
        self.untried_actions = sorted(valid, key=lambda x: abs(x - 3))
    
    def is_fully_expanded(self):
        """Check if all children have been expanded"""
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        """Check if this is a terminal node"""
        return len(self.untried_actions) == 0 and len(self.children) == 0
    
    def best_child(self, c=1.41):
        """
        Select best child using UCB1 formula
        
        Args:
            c: Exploration constant (sqrt(2) is theoretically optimal)
        
        Returns:
            Best child node according to UCB1
        """
        if not self.children:
            return None
            
        best_score = -float('inf')
        best_child = None
        
        for action, child in self.children.items():
            if child.visits == 0:
                # Unvisited nodes have infinite priority
                score = float('inf')
            else:
                # UCB1 formula: exploitation + exploration
                exploit = child.value / child.visits
                explore = c * math.sqrt(math.log(self.visits + 1) / child.visits)
                score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child
    
    def best_action(self):
        """
        Return action with most visits (most robust choice)
        
        Returns:
            Best action based on visit count
        """
        if not self.children:
            valid_actions = [i for i in range(len(self.action_mask)) if self.action_mask[i] == 1]
            if valid_actions:
                return np.random.choice(valid_actions)
            return 0
            
        best_visits = -1
        best_action = None
        
        for action, child in self.children.items():
            if child.visits > best_visits:
                best_visits = child.visits
                best_action = action
        
        return best_action


class MCTSAgent:
    """
    Monte Carlo Tree Search agent with intelligent simulations
    
    Features:
    - Smart rollout policy using heuristics
    - Early termination when outcome is clear
    - Threat detection and blocking
    - Center-biased move selection
    """
    
    def __init__(self, env, time_limit=1.0, player_name="MCTSAgent", 
                 exploration_constant=1.41):
        """
        Initialize MCTS agent
        
        Args:
            env: PettingZoo environment
            time_limit: Time budget per move in seconds
            player_name: Display name for agent
            exploration_constant: UCB1 exploration parameter
        """
        self.env = env
        self.time_limit = time_limit
        self.player_name = player_name
        self.exploration_constant = exploration_constant
        self.iterations = 0
        
        # Statistics for debugging
        self.early_terminations = 0
        self.total_simulations = 0
    
    def choose_action(self, observation, reward, termination, truncation, info, action_mask):
        """
        Choose action using MCTS with intelligent simulations
        
        Args:
            observation: Current board state
            reward: Current reward (unused)
            termination: Whether game ended
            truncation: Whether game was truncated
            info: Additional info
            action_mask: Valid actions mask
        
        Returns:
            Selected action (column index)
        """
        valid_actions = [i for i in range(len(action_mask)) if action_mask[i] == 1]
        
        # Edge case: no valid actions
        if not valid_actions:
            return 0
        
        # Edge case: only one choice
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        # Priority 1: Take winning move immediately
        for action in valid_actions:
            if self._is_winning_move(observation, action, 0):
                return action
        
        # Priority 2: Block opponent's winning move
        for action in valid_actions:
            if self._is_winning_move(observation, action, 1):
                return action
        
        # Priority 3: Check for double threat creation
        for action in valid_actions:
            if self._creates_double_threat(observation, action, 0):
                return action
        
        # Run MCTS for remaining cases
        root = MCTSNode(observation, action_mask, player=1)
        
        start_time = time.time()
        self.iterations = 0
        self.early_terminations = 0
        self.total_simulations = 0
        
        while time.time() - start_time < self.time_limit:
            self._mcts_iteration(root, observation)
            self.iterations += 1
            
            # Safety limit to prevent infinite loops
            if self.iterations > 50000:
                break
        
        best_action = root.best_action()
        
        # Fallback if MCTS failed
        if best_action is None or action_mask[best_action] != 1:
            best_action = self._get_heuristic_action(observation, valid_actions, 0)
        
        return best_action
    
    def _mcts_iteration(self, root, initial_state):
        """
        Run one iteration of MCTS (Selection -> Expansion -> Simulation -> Backpropagation)
        
        Args:
            root: Root node of search tree
            initial_state: Starting board state
        """
        node = root
        state = initial_state.copy()
        current_player = 0  # We are player 0
        
        # === SELECTION PHASE ===
        # Traverse tree using UCB1 until we reach a leaf or unexpanded node
        while node.is_fully_expanded() and node.children:
            node = node.best_child(self.exploration_constant)
            if node is None:
                break
            state = self._apply_action(state, node.action, 1 - current_player)
            current_player = 1 - current_player
        
        if node is None:
            return
        
        # === EXPANSION PHASE ===
        # Add a new child node for an untried action
        if node.untried_actions:
            # Select action using heuristic ordering
            action = self._select_expansion_action(state, node.untried_actions, current_player)
            node.untried_actions.remove(action)
            
            new_state = self._apply_action(state, action, current_player)
            new_mask = self._get_action_mask(new_state)
            
            child = MCTSNode(new_state, new_mask, parent=node, 
                           action=action, player=current_player)
            node.children[action] = child
            node = child
            state = new_state
            current_player = 1 - current_player
        
        # === SIMULATION PHASE ===
        # Run intelligent simulation from leaf node
        self.total_simulations += 1
        result = self._intelligent_simulate(state, current_player)
        
        # === BACKPROPAGATION PHASE ===
        # Update statistics up the tree
        while node is not None:
            node.visits += 1
            # Value from our perspective (player 0)
            if node.player == 0:
                node.value += result
            else:
                node.value += (1 - result)
            node = node.parent
    
    def _select_expansion_action(self, state, untried_actions, player):
        """
        Select which action to expand using heuristics
        
        Args:
            state: Current board state
            untried_actions: List of unexpanded actions
            player: Current player
        
        Returns:
            Selected action to expand
        """
        # Priority: winning moves > blocking moves > threatening moves > center
        
        # Check for winning move
        for action in untried_actions:
            if self._is_winning_move(state, action, player):
                return action
        
        # Check for blocking opponent's win
        for action in untried_actions:
            if self._is_winning_move(state, action, 1 - player):
                return action
        
        # Check for threat creation
        for action in untried_actions:
            if self._creates_threat(state, action, player):
                return action
        
        # Default: prefer center columns
        center_actions = [a for a in untried_actions if a in [2, 3, 4]]
        if center_actions:
            return center_actions[0]
        
        return untried_actions[0]
    
    def _intelligent_simulate(self, state, current_player):
        """
        Intelligent simulation using heuristics instead of pure random
        
        Features:
        - Takes winning moves immediately
        - Blocks opponent's winning moves
        - Prefers center columns
        - Early termination when outcome is clear
        
        Args:
            state: Starting state for simulation
            current_player: Player to move first
        
        Returns:
            Result: 1.0 (we win), 0.0 (we lose), 0.5 (draw)
        """
        sim_state = state.copy()
        player = current_player
        
        # Track consecutive advantageous positions for early termination
        advantage_score = self._evaluate_position(sim_state)
        
        for move_num in range(42):  # Max moves in Connect Four
            # Check for terminal state
            winner = self._check_winner(sim_state)
            if winner is not None:
                if winner == 0:
                    return 1.0  # We win
                elif winner == 1:
                    return 0.0  # Opponent wins
                else:
                    return 0.5  # Draw
            
            # Get valid actions
            valid_actions = self._get_valid_actions(sim_state)
            if not valid_actions:
                return 0.5  # Draw
            
            # === EARLY TERMINATION CHECK ===
            # If position is heavily one-sided, terminate early
            if move_num > 6:  # Only after some moves have been played
                current_eval = self._evaluate_position(sim_state)
                
                # Strong advantage for us - likely win
                if current_eval > 500:
                    self.early_terminations += 1
                    return 0.9
                
                # Strong advantage for opponent - likely loss
                if current_eval < -500:
                    self.early_terminations += 1
                    return 0.1
                
                # Overwhelming advantage
                if current_eval > 1000:
                    self.early_terminations += 1
                    return 1.0
                
                if current_eval < -1000:
                    self.early_terminations += 1
                    return 0.0
            
            # === INTELLIGENT MOVE SELECTION ===
            action = self._get_heuristic_action(sim_state, valid_actions, player)
            sim_state = self._apply_action(sim_state, action, player)
            player = 1 - player
        
        return 0.5  # Draw if max moves reached
    
    def _get_heuristic_action(self, state, valid_actions, player):
        """
        Select action using heuristics (smart random)
        
        Priority:
        1. Winning move
        2. Block opponent's win
        3. Create double threat
        4. Create single threat
        5. Center preference with randomness
        
        Args:
            state: Current board state
            valid_actions: List of valid actions
            player: Current player
        
        Returns:
            Selected action
        """
        opponent = 1 - player
        
        # Priority 1: Take winning move
        for action in valid_actions:
            if self._is_winning_move(state, action, player):
                return action
        
        # Priority 2: Block opponent's winning move
        for action in valid_actions:
            if self._is_winning_move(state, action, opponent):
                return action
        
        # Priority 3: Create double threat (fork)
        for action in valid_actions:
            if self._creates_double_threat(state, action, player):
                return action
        
        # Priority 4: Block opponent's double threat
        for action in valid_actions:
            if self._creates_double_threat(state, action, opponent):
                return action
        
        # Priority 5: Create single threat
        threat_actions = [a for a in valid_actions if self._creates_threat(state, action, player)]
        if threat_actions and np.random.random() < 0.7:
            return np.random.choice(threat_actions)
        
        # Priority 6: Prefer center columns with probability
        center_actions = [a for a in valid_actions if a in [3]]
        if center_actions and np.random.random() < 0.4:
            return center_actions[0]
        
        near_center = [a for a in valid_actions if a in [2, 4]]
        if near_center and np.random.random() < 0.3:
            return np.random.choice(near_center)
        
        # Priority 7: Avoid edges slightly
        non_edge = [a for a in valid_actions if a not in [0, 6]]
        if non_edge and np.random.random() < 0.6:
            return np.random.choice(non_edge)
        
        # Default: random from valid actions
        return np.random.choice(valid_actions)
    
    def _evaluate_position(self, state):
        """
        Evaluate board position for early termination decision
        
        Positive score = good for player 0 (us)
        Negative score = good for player 1 (opponent)
        
        Args:
            state: Board state to evaluate
        
        Returns:
            Position score (integer)
        """
        score = 0
        
        # Count threats and pieces for each player
        for player in range(2):
            multiplier = 1 if player == 0 else -1
            
            # Center column control
            for row in range(6):
                if state[row, 3, player] == 1:
                    score += 4 * multiplier
                if state[row, 2, player] == 1 or state[row, 4, player] == 1:
                    score += 2 * multiplier
            
            # Evaluate all possible winning lines
            score += self._count_threats_score(state, player) * multiplier
        
        return score
    
    def _count_threats_score(self, state, player):
        """
        Count weighted score for threats
        
        Args:
            state: Board state
            player: Player to evaluate
        
        Returns:
            Threat score
        """
        score = 0
        opponent = 1 - player
        
        # Check all possible 4-in-a-row windows
        windows = self._get_all_windows(state)
        
        for window_cells in windows:
            player_count = sum(1 for r, c in window_cells if state[r, c, player] == 1)
            opponent_count = sum(1 for r, c in window_cells if state[r, c, opponent] == 1)
            
            # Only count if opponent hasn't blocked this line
            if opponent_count == 0:
                if player_count == 3:
                    score += 100  # One away from winning
                elif player_count == 2:
                    score += 10   # Two in a row
                elif player_count == 1:
                    score += 1    # Started a line
        
        return score
    
    def _get_all_windows(self, state):
        """
        Get all possible 4-cell windows on the board
        
        Returns:
            List of windows, each window is list of (row, col) tuples
        """
        windows = []
        
        # Horizontal windows
        for row in range(6):
            for col in range(4):
                windows.append([(row, col+i) for i in range(4)])
        
        # Vertical windows
        for row in range(3):
            for col in range(7):
                windows.append([(row+i, col) for i in range(4)])
        
        # Diagonal (positive slope)
        for row in range(3, 6):
            for col in range(4):
                windows.append([(row-i, col+i) for i in range(4)])
        
        # Diagonal (negative slope)
        for row in range(3):
            for col in range(4):
                windows.append([(row+i, col+i) for i in range(4)])
        
        return windows
    
    def _creates_threat(self, state, action, player):
        """
        Check if action creates a threat (3 in a row with open end)
        
        Args:
            state: Current board state
            action: Action to check
            player: Player making the move
        
        Returns:
            True if move creates a threat
        """
        new_state = self._apply_action(state, action, player)
        opponent = 1 - player
        
        # Find where the piece landed
        placed_row = -1
        for row in range(6):
            if new_state[row, action, player] == 1:
                if row == 5 or (state[row, action, player] == 0):
                    placed_row = row
                    break
        
        if placed_row == -1:
            return False
        
        # Check all directions from placed piece
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1  # Count the placed piece
            open_ends = 0
            
            # Check positive direction
            for i in range(1, 4):
                r, c = placed_row + dr * i, action + dc * i
                if 0 <= r < 6 and 0 <= c < 7:
                    if new_state[r, c, player] == 1:
                        count += 1
                    elif new_state[r, c, opponent] == 0:
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break
            
            # Check negative direction
            for i in range(1, 4):
                r, c = placed_row - dr * i, action - dc * i
                if 0 <= r < 6 and 0 <= c < 7:
                    if new_state[r, c, player] == 1:
                        count += 1
                    elif new_state[r, c, opponent] == 0:
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break
            
            # Threat: 3 pieces with at least one open end
            if count >= 3 and open_ends >= 1:
                return True
        
        return False
    
    def _creates_double_threat(self, state, action, player):
        """
        Check if action creates a double threat (fork)
        Two or more ways to win next turn
        
        Args:
            state: Current board state
            action: Action to check
            player: Player making the move
        
        Returns:
            True if move creates double threat
        """
        new_state = self._apply_action(state, action, player)
        
        # Count how many winning moves player would have
        threats = 0
        valid_actions = self._get_valid_actions(new_state)
        
        for next_action in valid_actions:
            if self._is_winning_move(new_state, next_action, player):
                threats += 1
                if threats >= 2:
                    return True
        
        return False
    
    def _apply_action(self, state, action, player):
        """
        Apply action to state and return new state
        
        Args:
            state: Current board state
            action: Column to place piece
            player: Player making the move (0 or 1)
        
        Returns:
            New board state
        """
        new_state = state.copy()
        column = action
        
        # Find lowest empty row in column (gravity)
        for row in range(5, -1, -1):
            if new_state[row, column, 0] == 0 and new_state[row, column, 1] == 0:
                new_state[row, column, player] = 1
                break
        
        return new_state
    
    def _get_action_mask(self, state):
        """
        Get valid actions mask for state
        
        Args:
            state: Board state
        
        Returns:
            Binary mask of valid actions
        """
        mask = np.zeros(7, dtype=np.int8)
        for col in range(7):
            # Column is valid if top cell is empty
            if state[0, col, 0] == 0 and state[0, col, 1] == 0:
                mask[col] = 1
        return mask
    
    def _get_valid_actions(self, state):
        """
        Get list of valid action indices
        
        Args:
            state: Board state
        
        Returns:
            List of valid column indices
        """
        valid = []
        for col in range(7):
            if state[0, col, 0] == 0 and state[0, col, 1] == 0:
                valid.append(col)
        return valid
    
    def _check_winner(self, state):
        """
        Check if there's a winner
        
        Args:
            state: Board state
        
        Returns:
            0 (player 0 wins), 1 (player 1 wins), 2 (draw), or None (ongoing)
        """
        # Check for each player
        for player in range(2):
            # Horizontal
            for row in range(6):
                for col in range(4):
                    if all(state[row, col+i, player] == 1 for i in range(4)):
                        return player
            
            # Vertical
            for row in range(3):
                for col in range(7):
                    if all(state[row+i, col, player] == 1 for i in range(4)):
                        return player
            
            # Diagonal (positive slope /)
            for row in range(3, 6):
                for col in range(4):
                    if all(state[row-i, col+i, player] == 1 for i in range(4)):
                        return player
            
            # Diagonal (negative slope \)
            for row in range(3):
                for col in range(4):
                    if all(state[row+i, col+i, player] == 1 for i in range(4)):
                        return player
        
        # Check for draw (all columns full)
        if all(state[0, col, 0] == 1 or state[0, col, 1] == 1 for col in range(7)):
            return 2
        
        return None
    
    def _is_winning_move(self, state, action, player):
        """
        Check if action is a winning move for player
        
        Args:
            state: Current board state
            action: Action to check
            player: Player making the move
        
        Returns:
            True if move wins the game
        """
        new_state = self._apply_action(state, action, player)
        return self._check_winner(new_state) == player
    
    def get_stats(self):
        """
        Get statistics about the last search
        
        Returns:
            Dictionary with search statistics
        """
        return {
            'iterations': self.iterations,
            'total_simulations': self.total_simulations,
            'early_terminations': self.early_terminations,
            'early_termination_rate': (self.early_terminations / max(1, self.total_simulations)) * 100
        }



