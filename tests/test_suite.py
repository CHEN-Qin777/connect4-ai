"""
Automated test suite for Connect 4 agents
Exercise 4: Design and implement tests
"""

import sys
import os
import time
import tracemalloc
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pettingzoo.classic import connect_four_v3
from agents.random_agent import RandomAgent
from agents.smart_agent import SmartAgent


class TestSuite:
    """
    Test suite for evaluating agents
    """

    def __init__(self):
        self.env = connect_four_v3.env(render_mode=None)
        self.env.reset()
        self.results = {}

    def run_functional_tests(self):
        """Run functional tests"""
        print("=== Functional Tests ===")
        
        # Test 1: Valid move selection
        self.test_valid_move_selection()
        
        # Test 2: Action mask respect
        self.test_action_mask_respect()
        
        # Test 3: Game end handling
        self.test_game_end_handling()
        
        # Test 4: Win detection
        self.test_win_detection()
        
        # Test 5: Block detection
        self.test_block_detection()

    def run_performance_tests(self):
        """Run performance tests"""
        print("\n=== Performance Tests ===")
        
        # Test time per move
        self.test_time_per_move()
        
        # Test memory usage
        self.test_memory_usage()

    def run_strategic_tests(self):
        """Run strategic tests"""
        print("\n=== Strategic Tests ===")
        
        # Test against random agent
        self.test_vs_random_agent()
        
        # Test specific scenarios
        self.test_specific_scenarios()

    def test_valid_move_selection(self):
        """Test agent only chooses valid moves"""
        print("Test: Valid move selection")
        agent = SmartAgent(self.env)
        
        # Create mask with only some valid columns
        action_mask = [0, 1, 0, 1, 0, 1, 0]  # Columns 1, 3, 5 valid
        observation = np.zeros((6, 7, 2))
        
        action = agent.choose_action(observation, action_mask=action_mask)
        
        assert action in [1, 3, 5], f"Agent played invalid column: {action}"
        print("✓ Agent only chooses valid moves")

    def test_action_mask_respect(self):
        """Test agent respects action mask"""
        print("Test: Action mask respect")
        agent = SmartAgent(self.env)
        
        # Test with all columns full except one
        action_mask = [0, 0, 0, 1, 0, 0, 0]  # Only column 3 valid
        observation = np.zeros((6, 7, 2))
        
        action = agent.choose_action(observation, action_mask=action_mask)
        
        assert action == 3, f"Agent should play column 3, played {action}"
        print("✓ Agent respects action mask")

    def test_game_end_handling(self):
        """Test agent handles game end correctly"""
        print("Test: Game end handling")
        agent = SmartAgent(self.env)
        
        # In terminal state, agent shouldn't be called to choose move
        # This test verifies agent can handle terminated/truncated parameters
        observation = np.zeros((6, 7, 2))
        action_mask = [1, 1, 1, 1, 1, 1, 1]
        
        # Call with terminated=True
        action = agent.choose_action(
            observation, 
            terminated=True, 
            action_mask=action_mask
        )
        
        # Agent can return None or a move, but shouldn't crash
        assert action is None or action in range(7)
        print("✓ Agent handles game end correctly")

    def test_win_detection(self):
        """Test agent detects immediate wins"""
        print("Test: Win detection")
        agent = SmartAgent(self.env)
        
        # Scenario: 3 aligned pieces, need 4th
        board = np.zeros((6, 7, 2))
        board[5, 0, 0] = 1  # SmartAgent (channel 0)
        board[5, 1, 0] = 1
        board[5, 2, 0] = 1
        
        action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
        
        assert action == 3, f"Agent should play column 3 to win, played {action}"
        print("✓ Agent detects immediate wins")

    def test_block_detection(self):
        """Test agent detects blocking needs"""
        print("Test: Block detection")
        agent = SmartAgent(self.env)
        
        # Scenario: opponent has 3 aligned pieces
        board = np.zeros((6, 7, 2))
        board[5, 0, 1] = 1  # Opponent (channel 1)
        board[5, 1, 1] = 1
        board[5, 2, 1] = 1
        
        action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
        
        assert action == 3, f"Agent should play column 3 to block, played {action}"
        print("✓ Agent detects blocking needs")

    def test_time_per_move(self):
        """Test execution time per move"""
        print("Test: Time per move")
        agent = SmartAgent(self.env)
        
        # Measure time for 100 decisions
        board = np.zeros((6, 7, 2))
        action_mask = [1, 1, 1, 1, 1, 1, 1]
        
        start_time = time.time()
        for _ in range(100):
            agent.choose_action(board, action_mask=action_mask)
        end_time = time.time()
        
        time_per_move = (end_time - start_time) / 100
        print(f"Average time per move: {time_per_move:.4f} seconds")
        
        # Check it's reasonable (less than 0.1 second)
        assert time_per_move < 0.1, f"Time per move too long: {time_per_move}"
        print("✓ Time per move acceptable")

    def test_memory_usage(self):
        """Test memory usage"""
        print("Test: Memory usage")
        agent = SmartAgent(self.env)
        
        # Start memory tracing
        tracemalloc.start()
        
        # Make some decisions
        board = np.zeros((6, 7, 2))
        action_mask = [1, 1, 1, 1, 1, 1, 1]
        
        for _ in range(10):
            agent.choose_action(board, action_mask=action_mask)
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Current memory usage: {current / 10**6:.2f} MB")
        print(f"Peak memory usage: {peak / 10**6:.2f} MB")
        
        # Check it's reasonable (less than 10 MB)
        assert peak < 10 * 10**6, f"Memory usage too high: {peak / 10**6} MB"
        print("✓ Memory usage acceptable")

    def test_vs_random_agent(self):
        """Test win rate against random agent"""
        print("Test: Win rate against RandomAgent")
        
        num_games = 50
        smart_wins = 0
        random_wins = 0
        draws = 0
        
        for game in range(num_games):
            env = connect_four_v3.env(render_mode=None)
            env.reset(seed=game + 300)
            
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
            # When game ends: reward=-1 means last_agent lost, reward=1 means last_agent won
            if final_reward == -1:
                # last_agent lost, so the other player won
                if last_agent == "player_0":  # SmartAgent was player_0, it lost
                    random_wins += 1
                else:
                    smart_wins += 1
            elif final_reward == 1:
                # last_agent won
                if last_agent == "player_0":  # SmartAgent was player_0
                    smart_wins += 1
                else:
                    random_wins += 1
            else:
                draws += 1

            env.close()
        
        smart_win_rate = smart_wins / num_games * 100
        print(f"Results over {num_games} games:")
        print(f"SmartAgent wins: {smart_wins} ({smart_win_rate:.1f}%)")
        print(f"RandomAgent wins: {random_wins} ({random_wins/num_games*100:.1f}%)")
        print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
        
        # Success criterion: > 80% win rate
        assert smart_win_rate > 80, f"SmartAgent should win >80% of games, but got {smart_win_rate}%"
        print("✓ Win rate acceptable")

    def test_specific_scenarios(self):
        """Test specific scenarios from test plan"""
        print("Test: Specific scenarios")
        agent = SmartAgent(self.env)
        
        # Scenario 1: Immediate win
        board = np.zeros((6, 7, 2))
        board[5, 0, 0] = 1
        board[5, 1, 0] = 1
        board[5, 2, 0] = 1
        
        action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
        assert action == 3, f"Scenario 1 failed: should play 3, played {action}"
        print("✓ Scenario 1: Immediate win")
        
        # Scenario 2: Block opponent win
        board = np.zeros((6, 7, 2))
        board[5, 0, 1] = 1
        board[5, 1, 1] = 1
        board[5, 2, 1] = 1
        
        action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
        assert action == 3, f"Scenario 2 failed: should play 3, played {action}"
        print("✓ Scenario 2: Block opponent win")
        
        # Scenario 3: Center preference
        board = np.zeros((6, 7, 2))
        action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
        assert action == 3, f"Scenario 3 failed: should play 3, played {action}"
        print("✓ Scenario 3: Center preference")
        
        # Scenario 4: Avoid full columns
        board = np.zeros((6, 7, 2))
        # Fill column 0
        for row in range(6):
            board[row, 0, 0] = 1
        action_mask = [0, 1, 1, 1, 1, 1, 1]  # Column 0 full
        
        action = agent.choose_action(board, action_mask=action_mask)
        assert action != 0, f"Scenario 4 failed: played full column {action}"
        print("✓ Scenario 4: Avoid full columns")

    def run_all_tests(self):
        """Run all tests"""
        self.run_functional_tests()
        self.run_performance_tests()
        self.run_strategic_tests()
        print("\n🎉 All tests passed!")


if __name__ == "__main__":
    test_suite = TestSuite()
    test_suite.run_all_tests()
