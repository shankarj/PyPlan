from simulators import *
from states import *
from agents import *

def check_tetris():
    sim = tetrissimulator.TetrisSimulatorClass(1)
    sim.current_state.get_current_state()["state_val"]["current_board"] = [[1, 0, 1, 0, 1, 1, 1, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 0, 1, 1, 1, 1, 0, 1], [1, 1, 0, 0, 1, 1, 0, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1, 0, 1, 0], [1, 0, 0, 0, 0, 1, 0, 0, 1, 1], [1, 1, 1, 0, 0, 1, 1, 0, 1, 0], [0, 1, 0, 0, 0, 1, 1, 0, 1, 0], [1, 1, 1, 0, 0, 0, 1, 1, 1, 1], [0, 1, 0, 0, 0, 1, 1, 1, 0, 0], [1, 1, 1, 0, 1, 1, 0, 1, 0, 0], [1, 1, 0, 0, 1, 1, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 1, 1, 0, 0], [1, 1, 0, 0, 1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 1, 1, 1, 0, 0, 0], [1, 1, 0, 1, 1, 1, 0, 0, 0, 0], [0, 1, 1, 1, 0, 1, 1, 0, 0, 0], [1, 1, 0, 1, 1, 1, 0, 0, 0, 0]]

    sim.current_state.get_current_state()["state_val"]["current_piece"] = 4
    sim.current_state.get_current_state()["state_val"]["next_piece"] = 3
    agent_one = randomagent.RandomAgentClass(simulator=sim)
    agent_three = uniformagent.UniformRolloutAgentClass(simulator=sim, rollout_policy=agent_one,
                                                         pull_count=1)
    print sim.is_terminal()
    #agent_three.select_action(sim.current_state)
    sim.change_turn()
    #print sim.get_valid_actions()[0].get_action()
    print sim.print_board()
    # # action = {}
    # # action["position"] = [18, 0]
    # # action["piece_number"] = 2
    # # action["rot_number"] = 1
    # # print "REWARD : " + str(sim.take_action(action))
    # print sim.print_board()


def check_yahtzee():
    sim = yahtzeesimulator.YahtzeeSimulatorClass(num_players = 1)
    score_sheet = [[None] * 2 for _ in xrange(13)]
    current_roll = 1
    starting_player = 1
    dice_config = [6, 4, 2, 3, 5]
    state_val = {"current_roll": current_roll,
                          "dice_config": dice_config,
                          "score_sheet": score_sheet}
    current_state = {"state_val": state_val,
                              "current_player": starting_player}
    stateobj = yahtzeestate.YahtzeeStateClass()
    stateobj.set_current_state(current_state)
    sim.change_simulator_state(stateobj)

    #print sim.get_category_points(dice_config, 10)

    agent_one = randomagent.RandomAgentClass(simulator=sim)
    agent_two = uniformagent.UniformRolloutAgentClass(simulator=sim, rollout_policy=agent_one, pull_count=1)
    agent_uct = uctagent.UCTAgentClass(simulator=sim, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=2000,
                                        uct_constant=50,
                                        horizon=100,
                                        time_limit=2)

    action = agent_uct.select_action(sim.current_state)
    print action.get_action()

    print sim.take_action(action)



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
    check_yahtzee()