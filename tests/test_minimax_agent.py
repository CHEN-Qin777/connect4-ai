"""
Tests for MinimaxAgent
Exercise 5: Advanced challenges
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pettingzoo.classic import connect_four_v3
from agents.minimax_agent import MinimaxAgent
from agents.smart_agent import SmartAgent
from agents.random_agent import RandomAgent


def test_minimax_basic():
    """Basic test of MinimaxAgent"""
    print("Test: Basic functioning of MinimaxAgent")
    
    env = connect_four_v3.env(render_mode=None)
    env.reset(seed=42)
    
    agent = MinimaxAgent(env, depth=3)
    observation, reward, termination, truncation, info = env.last()
    
    action = agent.choose_action(
        observation['observation'],
        reward,
        termination,
        truncation,
        info,
        observation['action_mask']
    )
    
    assert action in range(7), f"Invalid action: {action}"
    print("✓ MinimaxAgent works correctly")


def test_minimax_vs_random():
    """Test Minimax vs RandomAgent"""
    print("Test: Minimax vs RandomAgent")
    
    num_games = 50  # Reduced for quick tests
    minimax_wins = 0
    random_wins = 0
    draws = 0
    
    for game in range(num_games):
        env = connect_four_v3.env(render_mode=None)
        env.reset(seed=game + 400)
        
        minimax_agent = MinimaxAgent(env, depth=3, player_name="Minimax")
        random_agent = RandomAgent(env, "Random")
        agents = {"player_0": minimax_agent, "player_1": random_agent}
        
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
            if last_agent == "player_0":  # Minimax was player_0
                minimax_wins += 1
            else:
                random_wins += 1
        else:
            draws += 1
        
        env.close()
    
    minimax_win_rate = minimax_wins / num_games * 100
    print(f"Results Minimax vs Random ({num_games} games):")
    print(f"Minimax wins: {minimax_wins} ({minimax_win_rate:.1f}%)")
    print(f"Random wins: {random_wins} ({random_wins/num_games*100:.1f}%)")
    print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
    
    # Minimax should beat Random
    assert minimax_win_rate > 50, f"Minimax should win >50% of games, but got {minimax_win_rate}%"
    print("✓ Minimax beats RandomAgent")


def test_minimax_vs_smart():
    """Test Minimax vs SmartAgent"""
    print("Test: Minimax vs SmartAgent")
    
    num_games = 30  # Reduced because it's slower
    minimax_wins = 0
    smart_wins = 0
    draws = 0
    
    for game in range(num_games):
        env = connect_four_v3.env(render_mode=None)
        env.reset(seed=game + 500)
        
        minimax_agent = MinimaxAgent(env, depth=3, player_name="Minimax")
        smart_agent = SmartAgent(env, "Smart")
        agents = {"player_0": minimax_agent, "player_1": smart_agent}
        
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
            if last_agent == "player_0":  # Minimax was player_0
                minimax_wins += 1
            else:
                smart_wins += 1
        else:
            draws += 1
        
        env.close()
    
    print(f"Results Minimax vs Smart ({num_games} games):")
    print(f"Minimax wins: {minimax_wins}")
    print(f"Smart wins: {smart_wins}")
    print(f"Draws: {draws}")
    
    # No strict assertion because it depends on depth
    print("✓ Test Minimax vs SmartAgent completed")


def test_different_depths():
    """Test different search depths"""
    print("Test: Depth comparison")
    
    env = connect_four_v3.env(render_mode=None)
    env.reset(seed=42)
    
    observation, reward, termination, truncation, info = env.last()
    action_mask = observation['action_mask']
    
    for depth in [2, 3, 4]:
        print(f"Depth {depth}:")
        
        agent = MinimaxAgent(env, depth=depth)
        
        # Measure time
        start_time = time.time()
        action = agent.choose_action(
            observation['observation'],
            reward,
            termination,
            truncation,
            info,
            action_mask
        )
        end_time = time.time()
        
        time_taken = end_time - start_time
        print(f"  Time: {time_taken:.2f}s, Action: {action}")
        
        # Check time is reasonable
        assert time_taken < 10, f"Too long for depth {depth}: {time_taken}s"
    
    env.close()
    print("✓ Depth test completed")


def test_evaluation_function():
    """Test evaluation function"""
    print("Test: Evaluation function")
    
    env = connect_four_v3.env()
    agent = MinimaxAgent(env, depth=3)
    
    # Test with empty board
    board = np.zeros((6, 7), dtype=int)
    score = agent._evaluate_board(board, agent.AI_PIECE)
    print(f"Empty board score: {score}")
    
    # Test with 3 in a row
    board[5, 0] = agent.AI_PIECE
    board[5, 1] = agent.AI_PIECE
    board[5, 2] = agent.AI_PIECE
    score = agent._evaluate_board(board, agent.AI_PIECE)
    print(f"Score with 3 in a row: {score}")
    
    assert score > 0, "Evaluation function should give positive score for good position"
    print("✓ Evaluation function works correctly")


if __name__ == "__main__":
    print("Starting MinimaxAgent tests...")
    
    test_minimax_basic()
    test_evaluation_function()
    test_different_depths()
    test_minimax_vs_random()
    test_minimax_vs_smart()
    
    print("\n🎉 All MinimaxAgent tests passed!")

