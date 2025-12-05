"""
Full Tournament system for comparing all agents
Includes: Random, Smart, Minimax, Advanced, and MCTS agents
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import numpy as np
from pettingzoo.classic import connect_four_v3
from agents.random_agent import RandomAgent
from agents.smart_agent import SmartAgent
from agents.minimax_agent import MinimaxAgent
from agents.advanced_agent import AdvancedAgent
from agents.mcts_agent import MCTSAgent


def create_agent(agent_class, env, name):
    """Create agent with appropriate parameters"""
    if agent_class == MCTSAgent:
        return agent_class(env, time_limit=0.5, player_name=name)
    else:
        return agent_class(env, name)


def run_tournament(agent_classes, num_games=10, render_mode=None):
    """
    Run a tournament between multiple agent classes
    """
    results = {}
    
    # Initialize results
    for agent_class in agent_classes:
        class_name = agent_class.__name__
        results[class_name] = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'points': 0
        }
    
    # Play each agent pair
    for i, agent_class1 in enumerate(agent_classes):
        for j, agent_class2 in enumerate(agent_classes):
            if i >= j:
                continue
                
            print(f"\n{'='*50}")
            print(f"🎮 {agent_class1.__name__} vs {agent_class2.__name__}")
            print(f"{'='*50}")
            
            wins_1 = 0
            wins_2 = 0
            draws = 0
            
            for game in range(num_games):
                # First match: agent1 starts
                try:
                    winner = play_game(agent_class1, agent_class2, game * 2, render_mode)
                    update_results(results, agent_class1.__name__, agent_class2.__name__, winner)
                    if winner == agent_class1.__name__:
                        wins_1 += 1
                    elif winner == agent_class2.__name__:
                        wins_2 += 1
                    else:
                        draws += 1
                except Exception as e:
                    print(f"  Error in game {game+1}a: {e}")
                    draws += 1
                
                # Second match: agent2 starts
                try:
                    winner = play_game(agent_class2, agent_class1, game * 2 + 1, render_mode)
                    update_results(results, agent_class2.__name__, agent_class1.__name__, winner)
                    if winner == agent_class1.__name__:
                        wins_1 += 1
                    elif winner == agent_class2.__name__:
                        wins_2 += 1
                    else:
                        draws += 1
                except Exception as e:
                    print(f"  Error in game {game+1}b: {e}")
                    draws += 1
                
                print(f"  Game {game+1}/{num_games}: {agent_class1.__name__} {wins_1} - {wins_2} {agent_class2.__name__} (Draws: {draws})")
            
            print(f"  Final: {agent_class1.__name__} {wins_1} - {wins_2} {agent_class2.__name__} (Draws: {draws})")
    
    return results


def play_game(agent_class1, agent_class2, seed, render_mode=None):
    """
    Play a game between two agents
    """
    env = connect_four_v3.env(render_mode=render_mode)
    env.reset(seed=seed)
    
    agent1 = create_agent(agent_class1, env, agent_class1.__name__)
    agent2 = create_agent(agent_class2, env, agent_class2.__name__)
    
    agents = {"player_0": agent1, "player_1": agent2}
    
    final_reward = 0
    last_agent = None
    
    for agent_name in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        last_agent = agent_name
        
        if termination or truncation:
            final_reward = reward
            break
        
        current_agent = agents[agent_name]
        action_mask = observation['action_mask']
        
        # Safety check for valid actions
        valid_actions = [i for i in range(len(action_mask)) if action_mask[i] == 1]
        
        if not valid_actions:
            # No valid actions - game should end
            break
        
        try:
            action = current_agent.choose_action(
                observation['observation'],
                reward,
                termination,
                truncation,
                info,
                action_mask
            )
            
            # Validate action
            if action_mask[action] != 1:
                # Invalid action, choose random valid one
                action = np.random.choice(valid_actions)
                
        except Exception as e:
            # Fallback to random on error
            action = np.random.choice(valid_actions)
        
        env.step(action)
    
    env.close()

    # Determine winner
    if final_reward == -1:
        if last_agent == "player_0":
            return agents["player_1"].__class__.__name__
        else:
            return agents["player_0"].__class__.__name__
    elif final_reward == 1:
        return agents[last_agent].__class__.__name__
    else:
        return "Draw"


def update_results(results, agent1_name, agent2_name, winner):
    """Update tournament results"""
    if winner == "Draw":
        results[agent1_name]['draws'] += 1
        results[agent2_name]['draws'] += 1
        results[agent1_name]['points'] += 1
        results[agent2_name]['points'] += 1
    elif winner == agent1_name:
        results[agent1_name]['wins'] += 1
        results[agent2_name]['losses'] += 1
        results[agent1_name]['points'] += 3
    else:
        results[agent2_name]['wins'] += 1
        results[agent1_name]['losses'] += 1
        results[agent2_name]['points'] += 3


def print_tournament_results(results):
    """Print tournament results"""
    print("\n" + "="*70)
    print("🏆 TOURNAMENT RESULTS 🏆")
    print("="*70)
    print(f"{'Rank':<6} {'Agent':<20} {'Wins':<8} {'Losses':<8} {'Draws':<8} {'Points':<8} {'Win%':<8}")
    print("-"*70)
    
    sorted_results = sorted(results.items(), key=lambda x: (x[1]['points'], x[1]['wins']), reverse=True)
    
    for rank, (agent_name, stats) in enumerate(sorted_results, 1):
        total_games = stats['wins'] + stats['losses'] + stats['draws']
        win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0
        
        medal = ""
        if rank == 1: medal = "🥇"
        elif rank == 2: medal = "🥈"
        elif rank == 3: medal = "🥉"
        
        print(f"{medal}{rank:<5} {agent_name:<20} {stats['wins']:<8} {stats['losses']:<8} {stats['draws']:<8} {stats['points']:<8} {win_rate:.1f}%")
    
    print("="*70)


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🎮 CONNECT FOUR FULL TOURNAMENT 🎮")
    print("="*70)
    print("\nAgents participating:")
    print("  1. RandomAgent    - Random moves")
    print("  2. SmartAgent     - Simple heuristics")
    print("  3. MinimaxAgent   - Minimax with alpha-beta")
    print("  4. AdvancedAgent  - Advanced minimax")
    print("  5. MCTSAgent      - Monte Carlo Tree Search")
    print("="*70)
    
    # Run tournament
    agents = [RandomAgent, SmartAgent, MinimaxAgent, AdvancedAgent, MCTSAgent]
    results = run_tournament(agents, num_games=3)
    print_tournament_results(results)


if __name__ == "__main__":
    main()
