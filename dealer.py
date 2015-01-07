import factory.simulatorfactory as simulatorfactory
import factory.agentfactory as agentfactory
import factory.statefactory as statefactory

class DealerClass:

	def __init__(self, agents_list, simulator_type, numplayers = 2, **other_args):
		self.playerturn = 1
		self.simulator = simulatorfactory.create_simulator(simulator_type, self.playerturn, numplayers)
		currentstate = statefactory.create_state(simulator_type)
		self.simulator.set_state(currentstate.get_current_state())
		self.playerlist = []
		agent_id = 0

		for agent_type in agents_list:
			agent_id += 1

			# BY DEFAULT THE ROLLOUT AGENT IS SET TO BE THE RANDOM AGENT HERE FOR TESTING

			if (agent_type == 2):
				rollout_policy = agentfactory.create_agent(1, agent_id, None, 0)
				agent_id += 1
			else:
				rollout_policy = None

			temp_agent = agentfactory.create_agent(agent_type, agent_id, rollout_policy, 0)
			
			#ADD NEEDED OTHER ARGS TO TEMP_AGENT HERE AND THEN APPEND TO PLAYERLIST			
			self.playerlist.append(temp_agent)

		self.playercount = numplayers

	def start_simulation(self):
		while self.simulator.is_terminal() == False:
			actual_agent_id = self.simulator.playerturn - 1
			action_to_take = self.playerlist[actual_agent_id].select_action(self.simulator)
			self.simulator.take_action(action_to_take)
			self.simulator.change_turn()

		winner = self.simulator.get_winning_player()

		print self.simulator.get_current_state()
		print "WINNER : " + str(winner)
		print "----------------------------------"

	def write_history(self):
		raise NotImplementedError
