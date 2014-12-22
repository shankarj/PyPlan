from agents import *
from states import *
from factory import *
from simulators import *

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
			temp_agent = actory.agentfactory.create_agent(agent_type, agent_count, self.simulator, None, 0)
			
			#ADD NEEDED ARGS TO TEMP_AGENT HERE AND THEN APPEND TO PLAYERLIST			
			self.playerlist.append(temp_agent)

		self.playercount = numplayers


	def start_simulation(self):
		raise NotImplementedError

	def write_history(self):
		raise NotImplementedError
