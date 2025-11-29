"""
Script to explore PettingZoo observation structure
Exercise 1: Understand Connect 4 and PettingZoo framework
"""

from pettingzoo.classic import connect_four_v3
import numpy as np


def print_board(observation):
    """
    Print human-readable version of the board
    
    Args:
        observation: numpy array of shape (6, 7, 2)
            observation[:,:,0] = current player's pieces
            observation[:,:,1] = opponent's pieces
    """
    board = np.zeros((6, 7), dtype=str)
    
    # Fill board with symbols
    for row in range(6):
        for col in range(7):
            if observation[row, col, 0] == 1:
                board[row, col] = 'X'  # Current player
            elif observation[row, col, 1] == 1:
                board[row, col] = 'O'  # Opponent
            else:
                board[row, col] = '.'  # Empty cell
    
    # Print board (row 0 at top)
    print("Game board:")
    for row in range(6):
        print(" ".join(board[row]))
    print("0 1 2 3 4 5 6")  # Column indices


def main():
    """Main function to explore observations"""
    # Create environment
    env = connect_four_v3.env()
    env.reset(seed=42)
    
    # Get first observation
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        
        if termination or truncation:
            break
        
        # Display observation structure
        print("Agent:", agent)
        print("Observation keys:", observation.keys())
        print("Observation shape:", observation['observation'].shape)
        print("Action mask:", observation['action_mask'])
        print()
        
        # Display board
        print_board(observation['observation'])
        
        # Make some moves to see changes
        env.step(3)  # Play in column 3
        if agent == env.agents[0]:
            break
    
    env.close()


if __name__ == "__main__":
    main()