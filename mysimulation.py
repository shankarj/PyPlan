from agents import *
from simulators import *

# --------------------------------------------------------
# SET THESE VARIABLES BEFORE RUNNING A CUSTOM SIMULATION.
# --------------------------------------------------------
game_name = "-TEMP-NAME-"
output_file_name = "TEMPFILE.txt"
players_count = 2
simulation_count = 5
simulation_horizon = 20

# --------------------------------------------------------
# THESE VARIABLES SHOULD NOT BE MODIFIED HERE.
# --------------------------------------------------------
agents_list = []
simulator_obj = None

# --------------------------------------------------------
# USE THIS FUNCTION TO CREATE YOUR OWN SIMULATION.
# THIS FUNCTION SHOULD RETURN AN ARRAY WITH TWO VALUES.
# VALUE 0 - THE SIMULATOR OBJECT
# VALUE 1 - THE AGENTS LIST
# EXAMPLE : return [simulator_obj, agents_list]
# --------------------------------------------------------
def create_simulation():

    # EXAMPLE CODE TO RUN A CONNECT4 GAME BETWEEN A RANDOM AND UCT AGENT (WITH SIMCOUNT = 100)

    simulator_obj = connect4simulator.Connect4SimulatorClass(num_players = players_count)
    agent_random = randomagent.RandomAgentClass(simulator=simulator_obj)
    agent_uct = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_random, tree_policy="UCB",
                                        num_simulations=100,
                                        uct_constant=0.8,
                                        horizon=100,
                                        time_limit=-1) #TIME LIMIT SHOULD BE -1 IF ONLY SIM COUNT IS TO BE CONSIDERED.

    agents_list.append(agent_random)
    agents_list.append(agent_uct)

    return [simulator_obj, agents_list]