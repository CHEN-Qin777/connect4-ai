"""
Automated test suite for Connect 4 agents
Exercise 4: Design and implement tests - Improved with diagonal scenario
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
        self.test_cases = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }

    def _record_test_result(self, test_name, passed=True):
        """Record test results"""
        self.test_cases["total"] += 1
        if passed:
            self.test_cases["passed"] += 1
            print(f"✓ {test_name}")
        else:
            self.test_cases["failed"] += 1
            print(f"✗ {test_name}")

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
        
        # Test 6: Center preference
        self.test_center_preference()

    def run_performance_tests(self):
        """Run performance tests"""
        print("\n=== Performance Tests ===")
        
        # Test time per move
        self.test_time_per_move()
        
        # Test memory usage
        self.test_memory_usage()
        
        # Test stability over multiple games
        self.test_stability()

    def run_strategic_tests(self):
        """Run strategic tests"""
        print("\n=== Strategic Tests ===")
        
        # Test against random agent
        self.test_vs_random_agent()
        
        # Test specific scenarios
        self.test_specific_scenarios()
        
        # Test tournament (optional)
        # self.test_tournament()

    def test_valid_move_selection(self):
        """Test agent only chooses valid moves"""
        test_name = "Valid move selection"
        try:
            agent = SmartAgent(self.env)
            
            # Create mask with only some valid columns
            action_mask = [0, 1, 0, 1, 0, 1, 0]  # Columns 1, 3, 5 valid
            observation = np.zeros((6, 7, 2))
            
            action = agent.choose_action(observation, action_mask=action_mask)
            
            assert action in [1, 3, 5], f"Agent played invalid column: {action}"
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_action_mask_respect(self):
        """Test agent respects action mask"""
        test_name = "Action mask respect"
        try:
            agent = SmartAgent(self.env)
            
            # Test with all columns full except one
            action_mask = [0, 0, 0, 1, 0, 0, 0]  # Only column 3 valid
            observation = np.zeros((6, 7, 2))
            
            action = agent.choose_action(observation, action_mask=action_mask)
            
            assert action == 3, f"Agent should play column 3, played {action}"
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_game_end_handling(self):
        """Test agent handles game end correctly"""
        test_name = "Game end handling"
        try:
            agent = SmartAgent(self.env)
            
            # In terminal state, agent shouldn't be called to choose move
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
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_win_detection(self):
        """Test agent detects immediate wins"""
        test_name = "Win detection"
        try:
            agent = SmartAgent(self.env)
            
            # Scenario: 3 aligned pieces, need 4th
            board = np.zeros((6, 7, 2))
            board[5, 0, 0] = 1  # SmartAgent (channel 0)
            board[5, 1, 0] = 1
            board[5, 2, 0] = 1
            
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            
            assert action == 3, f"Agent should play column 3 to win, played {action}"
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_block_detection(self):
        """Test agent detects blocking needs"""
        test_name = "Block detection"
        try:
            agent = SmartAgent(self.env)
            
            # Scenario: opponent has 3 aligned pieces
            board = np.zeros((6, 7, 2))
            board[5, 0, 1] = 1  # Opponent (channel 1)
            board[5, 1, 1] = 1
            board[5, 2, 1] = 1
            
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            
            assert action == 3, f"Agent should play column 3 to block, played {action}"
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_center_preference(self):
        """Test agent prefers center columns"""
        test_name = "Center preference"
        try:
            agent = SmartAgent(self.env)
            
            # Empty board - should prefer center
            board = np.zeros((6, 7, 2))
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            
            # SmartAgent should prefer column 3 (center)
            assert action == 3, f"Agent should prefer center (3), played {action}"
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_time_per_move(self):
        """Test execution time per move"""
        test_name = "Time per move"
        try:
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
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_memory_usage(self):
        """Test memory usage"""
        test_name = "Memory usage"
        try:
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
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_stability(self):
        """Test stability over multiple games"""
        test_name = "Stability over multiple games"
        try:
            # Play 10 games to check for crashes or memory leaks
            print("Testing stability (10 games)...")
            
            for game in range(10):
                env = connect_four_v3.env(render_mode=None)
                env.reset(seed=game + 600)
                
                smart_agent = SmartAgent(env, "Smart")
                random_agent = RandomAgent(env, "Random")
                agents = {"player_0": smart_agent, "player_1": random_agent}
                
                for agent_name in env.agent_iter():
                    observation, reward, termination, truncation, info = env.last()
                    
                    if termination or truncation:
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
            
            print("No crashes or errors detected in 10 games.")
            self._record_test_result(test_name, True)
        except Exception as e:
            print(f"Error during stability test: {e}")
            self._record_test_result(test_name, False)

    def test_vs_random_agent(self):
        """Test win rate against random agent"""
        test_name = "Win rate against RandomAgent"
        try:
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
            self._record_test_result(test_name, True)
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def test_specific_scenarios(self):
        """Test specific scenarios from test plan"""
        test_name = "Specific scenarios"
        
        scenarios_passed = 0
        total_scenarios = 5
        
        try:
            agent = SmartAgent(self.env)
            
            print("\nTesting specific scenarios:")
            
            # Scenario 1: Immediate win
            board = np.zeros((6, 7, 2))
            board[5, 0, 0] = 1
            board[5, 1, 0] = 1
            board[5, 2, 0] = 1
            
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            if action == 3:
                print("✓ Scenario 1: Immediate win")
                scenarios_passed += 1
            else:
                print(f"✗ Scenario 1 failed: should play 3, played {action}")
            
            # Scenario 2: Block opponent win
            board = np.zeros((6, 7, 2))
            board[5, 0, 1] = 1
            board[5, 1, 1] = 1
            board[5, 2, 1] = 1
            
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            if action == 3:
                print("✓ Scenario 2: Block opponent win")
                scenarios_passed += 1
            else:
                print(f"✗ Scenario 2 failed: should play 3, played {action}")
            
            # Scenario 3: Center preference
            board = np.zeros((6, 7, 2))
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            if action == 3:
                print("✓ Scenario 3: Center preference")
                scenarios_passed += 1
            else:
                print(f"✗ Scenario 3 failed: should play 3, played {action}")
            
            # Scenario 4: Avoid full columns
            board = np.zeros((6, 7, 2))
            # Fill column 0
            for row in range(6):
                board[row, 0, 0] = 1
            action_mask = [0, 1, 1, 1, 1, 1, 1]  # Column 0 full
            
            action = agent.choose_action(board, action_mask=action_mask)
            if action != 0:
                print("✓ Scenario 4: Avoid full columns")
                scenarios_passed += 1
            else:
                print(f"✗ Scenario 4 failed: played full column {action}")
            
            # Scenario 5: Diagonal win detection
            # Create a board with a diagonal win opportunity
            board = np.zeros((6, 7, 2))
            # Set up a downward diagonal (top-left to bottom-right)
            # Position: X at (2,3), (3,2), (4,1), need to play (5,0) to complete diagonal
            # But let's create a situation where SmartAgent (channel 0) has 3 in a diagonal
            board[2, 3, 0] = 1
            board[3, 2, 0] = 1
            board[4, 1, 0] = 1
            # Need to complete at (5,0)
            
            action = agent.choose_action(board, action_mask=[1,1,1,1,1,1,1])
            
            # The agent should play column 0 to complete the diagonal
            if action == 0:
                print("✓ Scenario 5: Diagonal win detection")
                scenarios_passed += 1
            else:
                print(f"✗ Scenario 5 failed: should play 0 to complete diagonal, played {action}")
                print("Note: This test requires diagonal detection in SmartAgent")
            
            # Calculate scenario success rate
            scenario_success_rate = (scenarios_passed / total_scenarios) * 100
            print(f"\nScenarios passed: {scenarios_passed}/{total_scenarios} ({scenario_success_rate:.1f}%)")
            
            # Overall test passes if at least 4 out of 5 scenarios pass
            # (Scenario 5 might be optional depending on agent implementation)
            assert scenarios_passed >= 4, f"Only {scenarios_passed} out of {total_scenarios} scenarios passed"
            
            self._record_test_result(test_name, True)
            
        except AssertionError as e:
            print(f"Assertion failed: {e}")
            self._record_test_result(test_name, False)
        except Exception as e:
            print(f"Error: {e}")
            self._record_test_result(test_name, False)

    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("TEST REPORT")
        print("="*60)
        
        success_rate = (self.test_cases["passed"] / self.test_cases["total"]) * 100
        
        print(f"Total tests: {self.test_cases['total']}")
        print(f"Passed: {self.test_cases['passed']}")
        print(f"Failed: {self.test_cases['failed']}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ TEST SUITE PASSED")
        else:
            print("\n❌ TEST SUITE FAILED")
        
        print("="*60)

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("Starting comprehensive test suite...")
        
        self.run_functional_tests()
        self.run_performance_tests()
        self.run_strategic_tests()
        
        self.generate_report()
        
        if self.test_cases["failed"] == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {self.test_cases['failed']} test(s) failed.")
            return False


if __name__ == "__main__":
    test_suite = TestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
