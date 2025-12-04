"""
Tests for SmartAgent
Exercise 3: Implement rule-based agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from pettingzoo.classic import connect_four_v3
from agents.smart_agent import SmartAgent
from agents.random_agent import RandomAgent


def test_get_valid_actions():
    """Test _get_valid_actions function"""
    env = connect_four_v3.env()
    agent = SmartAgent(env)
    
    # Test with all columns valid
    mask = [1, 1, 1, 1, 1, 1, 1]
    assert agent._get_valid_actions(mask) == [0, 1, 2, 3, 4, 5, 6]
    
    # Test with some invalid columns
    mask = [0, 1, 0, 1, 0, 1, 0]
    assert agent._get_valid_actions(mask) == [1, 3, 5]
    
    print("✓ _get_valid_actions: OK")


def test_get_next_row():
    """Test _get_next_row function"""
    env = connect_four_v3.env()
    agent = SmartAgent(env)
    
    # Empty board - piece goes to bottom
    board = np.zeros((6, 7, 2))
    assert agent._get_next_row(board, 3) == 5
    
    # Column with one piece - next piece goes on top
    board[5, 3, 0] = 1  # Player 0 has piece at bottom
    assert agent._get_next_row(board, 3) == 4
    
    # Full column
    for row in range(6):
        board[row, 0, 0] = 1
    assert agent._get_next_row(board, 0) is None
    
    print("✓ _get_next_row: OK")


def test_check_win_from_position():
    """Test _check_win_from_position function"""
    env = connect_four_v3.env()
    agent = SmartAgent(env)
    
    # Test horizontal win
    board = np.zeros((6, 7, 2))
    board[5, 0, 0] = 1
    board[5, 1, 0] = 1
    board[5, 2, 0] = 1
    # Add winning piece
    board[5, 3, 0] = 1
    assert agent._check_win_from_position(board, 5, 3, 0) == True
    
    # Test vertical win
    board = np.zeros((6, 7, 2))
    board[2, 3, 0] = 1
    board[3, 3, 0] = 1
    board[4, 3, 0] = 1
    board[5, 3, 0] = 1
    assert agent._check_win_from_position(board, 2, 3, 0) == True
    
    # Test no win
    board = np.zeros((6, 7, 2))
    board[5, 0, 0] = 1
    board[5, 1, 0] = 1
    assert agent._check_win_from_position(board, 5, 1, 0) == False
    
    print("✓ _check_win_from_position: OK")


def test_find_winning_move():
    """Test _find_winning_move function"""
    env = connect_four_v3.env()
    agent = SmartAgent(env)
    
    # Scenario: 3 aligned pieces, need 4th
    board = np.zeros((6, 7, 2))
    board[5, 0, 0] = 1
    board[5, 1, 0] = 1
    board[5, 2, 0] = 1
    # Column 3 should be winning move
    valid_actions = [0, 1, 2, 3, 4, 5, 6]
    
    winning_move = agent._find_winning_move(board, valid_actions, channel=0)
    assert winning_move == 3
    
    # Test no winning move
    board = np.zeros((6, 7, 2))
    board[5, 0, 0] = 1
    winning_move = agent._find_winning_move(board, valid_actions, channel=0)
    assert winning_move is None
    
    print("✓ _find_winning_move: OK")


def test_smart_vs_random():
    """
    Test if smart agent is better than random agent
    """
    num_games = 20
    smart_wins = 0
    random_wins = 0
    draws = 0
    
    for game in range(num_games):
        env = connect_four_v3.env(render_mode=None)
        env.reset(seed=game + 200)
        
        smart_agent = SmartAgent(env, "Smart")
        random_agent = RandomAgent(env, "Random")
        agents = {"player_0": smart_agent, "player_1": random_agent}
        
        final_reward = 0
        last_agent = None
        
        for agent_name in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()
            last_agent = agent_name
            
            if termination or truncation:
                final_reward = reward
                break
            else:
                current_agent = agents[agent_name]
                action = current_agent.choose_action(
                    observation['observation'],
                    reward,
                    termination,
                    truncation,
                    info,
                    observation['action_mask']
                )
                env.step(action)
        
        # Analyze result
        if final_reward == 1:
            if last_agent == "player_0":  # SmartAgent was player_0
                smart_wins += 1
            else:
                random_wins += 1
        else:
            draws += 1
        
        env.close()
    
    smart_win_rate = smart_wins / num_games * 100
    print(f"\nResults SmartAgent vs RandomAgent ({num_games} games):")
    print(f"SmartAgent wins: {smart_wins} ({smart_win_rate:.1f}%)")
    print(f"RandomAgent wins: {random_wins} ({random_wins/num_games*100:.1f}%)")
    print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
    
    # Smart agent should have better win rate
    assert smart_win_rate > 50, f"SmartAgent should win >50% of games, but got {smart_win_rate}%"
    
    print("✓ test_smart_vs_random: OK - Smart agent is better than random agent")


def test_specific_scenarios():
    """Test specific scenarios"""
    env = connect_four_v3.env()
    agent = SmartAgent(env)
    
    print("\nTesting specific scenarios:")
    
    # Scenario 1: Immediate win
    board = np.zeros((6, 7, 2))
    board[5, 0, 0] = 1
    board[5, 1, 0] = 1
    board[5, 2, 0] = 1
    # Agent should play column 3 to win
    action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
    assert action == 3, f"Should play 3 to win, played {action}"
    print("✓ Scenario immediate win: OK")
    
    # Scenario 2: Block needed
    board = np.zeros((6, 7, 2))
    board[5, 0, 1] = 1  # Opponent
    board[5, 1, 1] = 1  # Opponent  
    board[5, 2, 1] = 1  # Opponent
    # Agent should play column 3 to block
    action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
    assert action == 3, f"Should play 3 to block, played {action}"
    print("✓ Scenario block needed: OK")
    
    # Scenario 3: Center preference
    board = np.zeros((6, 7, 2))
    # No immediate win or block needed
    action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
    assert action == 3, f"Should prefer center (3), played {action}"
    print("✓ Scenario center preference: OK")


if __name__ == "__main__":
    print("Starting SmartAgent tests...")
    
    test_get_valid_actions()
    test_get_next_row()
    test_check_win_from_position()
    test_find_winning_move()
    test_specific_scenarios()
    test_smart_vs_random()
    
    print("\n🎉 All SmartAgent tests passed!")
