"""
MCTS Agent (Monte Carlo Tree Search) for Connect Four
Exercise 5: Advanced challenges
"""


import numpy as np
import time
import math
from copy import deepcopy


class MCTSNode:
    """Node in the MCTS tree"""
    
    def __init__(self, state, action_mask, parent=None, action=None, player=0):
        self.state = state.copy()
        self.action_mask = action_mask.copy()
        self.parent = parent
        self.action = action  # Action that led to this node
        self.player = player  # Player who just moved (0 or 1)
        
        self.children = {}
        self.visits = 0
        self.value = 0.0
        
        # Get valid actions
        self.untried_actions = [i for i in range(len(action_mask)) if action_mask[i] == 1]
    
    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        return len(self.untried_actions) == 0 and len(self.children) == 0
    
    def best_child(self, c=1.41):
        """Select best child using UCB1"""
        if not self.children:
            return None
            
        best_score = -float('inf')
        best_child = None
        
        for action, child in self.children.items():
            if child.visits == 0:
                score = float('inf')
            else:
                exploit = child.value / child.visits
                explore = c * math.sqrt(math.log(self.visits + 1) / child.visits)
                score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child
    
    def best_action(self):
        """Return action with most visits"""
        if not self.children:
            # Return random valid action if no children
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
    """Monte Carlo Tree Search agent"""
    
    def __init__(self, env, time_limit=1.0, player_name="MCTSAgent"):
        self.env = env
        self.time_limit = time_limit
        self.player_name = player_name
        self.iterations = 0
    
    def choose_action(self, observation, reward, termination, truncation, info, action_mask):
        """Choose action using MCTS"""
        # Get valid actions
        valid_actions = [i for i in range(len(action_mask)) if action_mask[i] == 1]
        
        # Handle edge cases
        if not valid_actions:
            return 0
        
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        # Check for immediate winning move
        for action in valid_actions:
            if self._is_winning_move(observation, action, 0):
                return action
        
        # Check for blocking opponent's winning move
        for action in valid_actions:
            if self._is_winning_move(observation, action, 1):
                return action
        
        # Run MCTS
        root = MCTSNode(observation, action_mask, player=1)  # Opponent just moved
        
        start_time = time.time()
        self.iterations = 0
        
        while time.time() - start_time < self.time_limit:
            self._mcts_iteration(root, observation)
            self.iterations += 1
            
            # Safety limit
            if self.iterations > 10000:
                break
        
        best_action = root.best_action()
        
        # Fallback if MCTS failed
        if best_action is None or action_mask[best_action] != 1:
            best_action = np.random.choice(valid_actions)
        
        return best_action
    
    def _mcts_iteration(self, root, initial_state):
        """Run one iteration of MCTS"""
        node = root
        state = initial_state.copy()
        current_player = 0  # We are player 0
        
        # Selection - traverse tree using UCB1
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
            if node is None:
                break
            state = self._apply_action(state, node.action, 1 - current_player)
            current_player = 1 - current_player
        
        if node is None:
            return
        
        # Expansion - add a new child
        if node.untried_actions:
            action = np.random.choice(node.untried_actions)
            node.untried_actions.remove(action)
            
            new_state = self._apply_action(state, action, current_player)
            new_mask = self._get_action_mask(new_state)
            
            child = MCTSNode(new_state, new_mask, parent=node, action=action, player=current_player)
            node.children[action] = child
            node = child
            state = new_state
            current_player = 1 - current_player
        
        # Simulation - random playout
        result = self._simulate(state, current_player)
        
        # Backpropagation
        while node is not None:
            node.visits += 1
            # Value from our perspective (player 0)
            if node.player == 0:
                node.value += result
            else:
                node.value += (1 - result)
            node = node.parent
    
    def _simulate(self, state, current_player):
        """Random simulation from current state"""
        sim_state = state.copy()
        player = current_player
        
        for _ in range(42):  # Max moves in Connect Four
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
            
            # Random move
            action = np.random.choice(valid_actions)
            sim_state = self._apply_action(sim_state, action, player)
            player = 1 - player
        
        return 0.5  # Draw if max moves reached
    
    def _apply_action(self, state, action, player):
        """Apply action to state and return new state"""
        new_state = state.copy()
        column = action
        
        # Find lowest empty row in column
        for row in range(5, -1, -1):
            if new_state[row, column, 0] == 0 and new_state[row, column, 1] == 0:
                new_state[row, column, player] = 1
                break
        
        return new_state
    
    def _get_action_mask(self, state):
        """Get valid actions for state"""
        mask = np.zeros(7, dtype=np.int8)
        for col in range(7):
            if state[0, col, 0] == 0 and state[0, col, 1] == 0:
                mask[col] = 1
        return mask
    
    def _get_valid_actions(self, state):
        """Get list of valid actions"""
        valid = []
        for col in range(7):
            if state[0, col, 0] == 0 and state[0, col, 1] == 0:
                valid.append(col)
        return valid
    
    def _check_winner(self, state):
        """Check if there's a winner. Returns 0, 1, 2 (draw), or None"""
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
            
            # Diagonal (positive slope)
            for row in range(3, 6):
                for col in range(4):
                    if all(state[row-i, col+i, player] == 1 for i in range(4)):
                        return player
            
            # Diagonal (negative slope)
            for row in range(3):
                for col in range(4):
                    if all(state[row+i, col+i, player] == 1 for i in range(4)):
                        return player
        
        # Check for draw
        if all(state[0, col, 0] == 1 or state[0, col, 1] == 1 for col in range(7)):
            return 2
        
        return None
    
    def _is_winning_move(self, state, action, player):
        """Check if action is a winning move for player"""
        new_state = self._apply_action(state, action, player)
        return self._check_winner(new_state) == player

