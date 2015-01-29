from agents import *
from simulators import *
from states import *


def uniform_decision_check():
    simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(num_players=2)
    stateobj = tictactoestate.TicTacToeStateClass()
    stateobj.set_current_state([[2, 1, 0], [0, 1, 2], [0, 0, 1]])
    simulator_obj.change_simulator_values(stateobj, 2)

    agent_one = randomagent.RandomAgentClass(simulator=simulator_obj)
    agent_two = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=500)

    action = agent_two.select_action(simulator_obj.current_state, simulator_obj.playerturn)
    print action.get_action()


def epsilon_decision_check():
    sim = connect4simulator.Connect4SimulatorClass(2)
    stateobj = connect4state.Connect4StateClass(2)
    stateobj.get_current_state()[0] |= 1 << 14
    stateobj.get_current_state()[0] |= 1 << 7
    stateobj.get_current_state()[0] |= 1

    stateobj.get_current_state()[1] |= 1 << 42
    stateobj.get_current_state()[1] |= 1 << 43

    sim.set_state(stateobj)

    simulator_obj = connect4simulator.Connect4SimulatorClass(num_players=2)
    simulator_obj.change_simulator_values(stateobj, 2)

    agent_one = randomagent.RandomAgentClass(simulator=simulator_obj)
    agent_two = incuniformagent.IncUniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=500)

    print simulator_obj.print_board()
    action = agent_two.select_action(simulator_obj.current_state, simulator_obj.playerturn)
    print action.get_action()

if __name__ == "__main__":
    epsilon_decision_check()
    #uniform_decision_check()