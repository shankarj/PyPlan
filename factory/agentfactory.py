from agents import randomagent
from agents import uniformagent

def create_agent(agent_type, agentid, rollout, heuristic):
	if agent_type == 1:
		return randomagent.RandomAgentClass(agentid, rollout, heuristic)
	if agent_type == 2:
		return uniformagent.UniformAgentClass(agentid, rollout, heuristic)
	else:
		print "Invalid Simulator type"