from agents import randomagent

def create_agent(agent_type, agentid, rollout, heuristic):
	if agent_type == 1:
		return randomagent.RandomAgentClass(agentid, rollout, heuristic)
	else:
		print "Invalid Simulator type"