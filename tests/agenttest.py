from agents import *
from simulators import *
from states import *

def uniform_decision_check():
    simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(num_players = 2)
    stateobj = tictactoestate.TicTacToeStateClass()
    stateobj.set_current_state([[2,1,0], [0,1,2], [2,0,1]])
    simulator_obj.change_simulator_values(stateobj, 2)

    agent_one = randomagent.RandomAgentClass(simulator = simulator_obj)
    agent_two = uniformagent.UniformRolloutAgentClass(simulator = simulator_obj, rollout_policy = agent_one, pull_count = 5)

    action = agent_two.select_action(simulator_obj.current_state, simulator_obj.playerturn)
    print action.get_action()

if __name__ == "__main__":
    uniform_decision_check()