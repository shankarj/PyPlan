from simulators import *
from states import *

def check_terminal_function():
    sim = tictactoesimulator.TicTacToeSimulatorClass(2)
    stateobj = tictactoestate.TicTacToeStateClass()
    stateobj.set_current_state([[2,1,0], [2,1,2], [2,0,1]])
    sim.set_state(stateobj)
    assert sim.is_terminal(), "Failed"
    print "SUCCESS. WINNER : " + str(sim.winningplayer)

if __name__ == "__main__":
    check_terminal_function()