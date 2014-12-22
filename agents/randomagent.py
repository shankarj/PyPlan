from abstract import absagent
import random
from copy import deepcopy

class RandomAgentClass(absagent.AbstractAgent):

	myname = "RANDOM"

	def __init__(self, agentid, simulator, rollout_policy = None, heuristic = 0):
		self.agentid = agentid
		self.agentname = str(aid) + myname
		self.simulator = deepcopy(simulator)
		self.agentclass = rollout_policy
		self.heuristicvalue = heuristic
		self.playerturn = agentturn

	def select_action(self):
		valid_actions = self.simulator.valid_actions()
		actions_count = len(valid_actions)

		if actions_count == 1:
			choice = 0
		else:
			choice = random.randrange(actions_count)
		
		return actions[choice]



