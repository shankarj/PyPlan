from abstract import absagent
import random
from copy import deepcopy

class RandomAgentClass(absagent.AbstractAgent):

	myname = "RANDOM"

	def __init__(self, agentid, rollout_policy = None, heuristic = 0):
		self.agentid = agentid
		self.agentname = str(agentid) + self.myname
		self.rollout_agent = rollout_policy
		self.heuristicvalue = heuristic

	def select_action(self, simulator):
		self.simulator = deepcopy(simulator)
		
		valid_actions = self.simulator.get_valid_actions()
		actions_count = len(valid_actions)

		if actions_count == 1:
			choice = 0
		else:
			choice = random.randrange(actions_count)
		
		return valid_actions[choice]



