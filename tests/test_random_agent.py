"""
Tests for RandomAgent
Exercise 2: Implement random agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pettingzoo.classic import connect_four_v3
from agents.random_agent import RandomAgent


def test_single_game():
    """
    Test a single game between two random agents
    """
    # Create environment
    env = connect_four_v3.env(render_mode=None)
    env.reset(seed=42)
    
    # Create two agents
    agent1 = RandomAgent(env, "Player1")
    agent2 = RandomAgent(env, "Player2")
    
    agents = {"player_0": agent1, "player_1": agent2}
    move_count = 0
    
    print("Starting test game:")
    
    # Play complete game
    for agent_name in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        
        if termination or truncation:
            action = None
            if reward == 1:
                print(f"{agent_name} wins!")
            elif reward == 0:
                print("Draw!")
            else:
                print(f"Game ended with reward: {reward}")
        else:
            # Agent chooses move
            current_agent = agents[agent_name]
            action = current_agent.choose_action(
                observation['observation'],
                reward,
                termination,
                truncation,
                info,
                observation['action_mask']
            )
            move_count += 1
            print(f"Move {move_count}: {agent_name} plays column {action}")
        
        env.step(action)
    
    env.close()
    print(f"Game finished in {move_count} moves")
    return move_count


def test_multiple_games(num_games=10):
    """
    Test multiple games and compute statistics
    
    Parameters:
        num_games: Number of games to play
    """
    env = connect_four_v3.env(render_mode=None)
    
    wins_player0 = 0
    wins_player1 = 0
    draws = 0
    total_moves = 0
    move_counts = []
    
    for game in range(num_games):
        env.reset(seed=game + 100)  # Different seeds for each game
        agent1 = RandomAgent(env, "Player1")
        agent2 = RandomAgent(env, "Player2")
        agents = {"player_0": agent1, "player_1": agent2}
        
        moves = 0
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
                moves += 1
        
        # Analyze result
        # When game ends: reward=-1 means last_agent lost, reward=1 means last_agent won
        if final_reward == -1:
            # last_agent lost, so the other player won
            if last_agent == "player_0":
                wins_player1 += 1
            else:
                wins_player0 += 1
        elif final_reward == 1:
            # last_agent won
            if last_agent == "player_0":
                wins_player0 += 1
            else:
                wins_player1 += 1
        else:
            draws += 1
        
        total_moves += moves
        move_counts.append(moves)
    
    env.close()
    
    # Display statistics
    print(f"\n=== Statistics over {num_games} games ===")
    print(f"Player 0 wins: {wins_player0} ({wins_player0/num_games*100:.1f}%)")
    print(f"Player 1 wins: {wins_player1} ({wins_player1/num_games*100:.1f}%)")
    print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
    print(f"Average moves per game: {total_moves/num_games:.1f}")
    print(f"Minimum moves: {min(move_counts)}")
    print(f"Maximum moves: {max(move_counts)}")
    
    return {
        'wins_player0': wins_player0,
        'wins_player1': wins_player1,
        'draws': draws,
        'avg_moves': total_moves / num_games
    }


if __name__ == "__main__":
    print("Testing single game:")
    moves = test_single_game()
    
    print("\n" + "="*50)
    print("Testing multiple games:")
    stats = test_multiple_games(20)
