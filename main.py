import dealer
from agents import *
from simulators import *


def call_dealer():
	simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(starting_player = 1, num_players = 2)

	agent_one = randomagent.RandomAgentClass(simulator = simulator_obj)
	agent_two = uniformagent.UniformRolloutAgentClass(simulator = simulator_obj, rollout_policy = agent_one, pull_count = 3)
	agent_three = uniformagent.UniformRolloutAgentClass(simulator = simulator_obj, rollout_policy = agent_two, pull_count = 3)

	agents_list = [agent_three,agent_two]
	dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations = 1)
	dealer_object.start_simulation()

if __name__ == "__main__":
	call_dealer()