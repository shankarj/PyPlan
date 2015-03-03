from simulators import *
from states import *

def check_terminal_function():
    sim = tictactoesimulator.TicTacToeSimulatorClass(2)
    stateobj = tictactoestate.TicTacToeStateClass()
    stateobj.set_current_state([[2,1,0], [2,1,2], [2,0,1]])
    sim.set_state(stateobj)
    assert sim.is_terminal(), "Failed"
    print "SUCCESS. WINNER : " + str(sim.winningplayer)

def connect4_get_valid_actions():
    sim = connect4simulator.Connect4SimulatorClass(2)
    stateobj = connect4state.Connect4StateClass(2)
    stateobj.get_current_state()[0] |= 1 << 10
    stateobj.get_current_state()[0] |= 1 << 5
    stateobj.get_current_state()[0] |= 1 << 19
    stateobj.get_current_state()[0] |= 1 << 24
    stateobj.get_current_state()[0] |= 1 << 31
    stateobj.get_current_state()[0] |= 1 << 42
    stateobj.get_current_state()[0] |= 1 << 43
    sim.set_state(stateobj)

    action_list = sim.get_valid_actions()
    for val in action_list:
        print val.get_action()["position"]

def connect4_is_terminal():
    sim = connect4simulator.Connect4SimulatorClass(2)
    stateobj = connect4state.Connect4StateClass(2)

    stateobj.get_current_state()["state_val"][0] = 270549120
    #stateobj.get_current_state()["state_val"][1] = 177405811938474

    #stateobj.get_current_state()["state_val"][1] |= 0 << 4
    #stateobj.get_current_state()["state_val"][0] |= 0 << 5


    sim.change_simulator_state(stateobj)

    print sim.is_terminal()
    assert sim.is_terminal(), "Not a terminal State"
    #print "SUCCESS. WINNER : " + str(sim.winningplayer)

    print(sim.print_board())

if __name__ == "__main__":
    connect4_is_terminal()