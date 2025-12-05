"""
Tournament system for comparing agents
Exercise 4: Design and implement tests
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from pettingzoo.classic import connect_four_v3
from agents.random_agent import RandomAgent
from agents.smart_agent import SmartAgent
from agents.minimax_agent import MinimaxAgent


def run_tournament(agent_classes, num_games=10, render_mode=None):
    """
    Run a tournament between multiple agent classes

    Parameters:
        agent_classes: list of agent classes to compare
        num_games: number of games between each agent pair
        render_mode: rendering mode (None for speed)

    Returns:
        dict: tournament results
    """
    results = {}
    
    # Initialize results
    for agent_class in agent_classes:
        class_name = agent_class.__name__
        results[class_name] = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'points': 0  # 3 points for win, 1 for draw
        }
    
    # Play each agent pair
    for i, agent_class1 in enumerate(agent_classes):
        for j, agent_class2 in enumerate(agent_classes):
            if i >= j:
                continue  # Avoid duplicates and self-play
                
            print(f"\n{agent_class1.__name__} vs {agent_class2.__name__}")
            
            # Play num_games with each agent as first player
            for game in range(num_games):
                # First match: agent1 starts
                winner = play_game(agent_class1, agent_class2, game * 2, render_mode)
                update_results(results, agent_class1.__name__, agent_class2.__name__, winner)
                
                # Second match: agent2 starts  
                winner = play_game(agent_class2, agent_class1, game * 2 + 1, render_mode)
                update_results(results, agent_class2.__name__, agent_class1.__name__, winner)
    
    return results


def play_game(agent_class1, agent_class2, seed, render_mode=None):
    """
    Play a game between two agents

    Parameters:
        agent_class1: first agent class (plays first)
        agent_class2: second agent class
        seed: seed for reproducibility
        render_mode: rendering mode

    Returns:
        str: winning agent class name, or "Draw" for draw
    """
    env = connect_four_v3.env(render_mode=render_mode)
    env.reset(seed=seed)
    
    agent1 = agent_class1(env, agent_class1.__name__)
    agent2 = agent_class2(env, agent_class2.__name__)
    agents = {"player_0": agent1, "player_1": agent2}
    
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
    
    env.close()

    # Determine winner
    # When game ends: reward=-1 means last_agent lost, reward=1 means last_agent won
    if final_reward == -1:
        # last_agent lost, so the other player won
        if last_agent == "player_0":
            winner_class = agents["player_1"].__class__.__name__
        else:
            winner_class = agents["player_0"].__class__.__name__
        return winner_class
    elif final_reward == 1:
        # last_agent won
        winner_class = agents[last_agent].__class__.__name__
        return winner_class
    else:
        return "Draw"


def update_results(results, agent1_name, agent2_name, winner):
    """
    Update tournament results

    Parameters:
        results: results dictionary
        agent1_name: first agent name
        agent2_name: second agent name  
        winner: winner name or "Draw"
    """
    if winner == "Draw":
        results[agent1_name]['draws'] += 1
        results[agent2_name]['draws'] += 1
        results[agent1_name]['points'] += 1
        results[agent2_name]['points'] += 1
    else:
        if winner == agent1_name:
            results[agent1_name]['wins'] += 1
            results[agent2_name]['losses'] += 1
            results[agent1_name]['points'] += 3
        else:
            results[agent2_name]['wins'] += 1
            results[agent1_name]['losses'] += 1
            results[agent2_name]['points'] += 3


def print_tournament_results(results):
    """
    Print tournament results in readable format
    """
    print("\n" + "="*60)
    print("TOURNAMENT RESULTS")
    print("="*60)
    print(f"{'Agent':<20} {'Wins':<10} {'Losses':<10} {'Draws':<10} {'Points':<10}")
    print("-"*60)
    
    # Sort by points descending
    sorted_results = sorted(results.items(), key=lambda x: x[1]['points'], reverse=True)
    
    for agent_name, stats in sorted_results:
        print(f"{agent_name:<20} {stats['wins']:<10} {stats['losses']:<10} {stats['draws']:<10} {stats['points']:<10}")
    
    print("="*60)


def main():
    """Main function to run tournament"""
    # List of agents to compare
    agents_to_test = [RandomAgent, SmartAgent, MinimaxAgent]
    
    print("Starting tournament...")
    results = run_tournament(agents_to_test, num_games=5)  # Reduced for testing
    
    print_tournament_results(results)


if __name__ == "__main__":
    main()

    main()
