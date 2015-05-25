from abstract import abssimulator
from actions import othelloaction
from states import othellostate

"""
Simulator Class for Othello

NOTE :
------

1. self.winningplayer = None -> Implies that the game is a draw.
							    Otherwise this variable holds the winning player's number.
								Player number 1 for X. 2 for O.

2. Reward scheme : Win = +1.0. Lose = -1.0. Draw = 0.
"""


class OthelloSimulatorClass(abssimulator.AbstractSimulator):
    def __init__(self, num_players):
        self.current_state = othellostate.OthelloStateClass()
        self.numplayers = num_players
        self.winningplayer = None
        self.gameover = False

    def create_copy(self):
        new_sim_obj = OthelloSimulatorClass(self.numplayers)
        new_sim_obj.change_simulator_state(self.current_state.create_copy())
        new_sim_obj.winningplayer = self.winningplayer
        new_sim_obj.gameover = self.gameover
        return new_sim_obj

    def reset_simulator(self):
        self.winningplayer = None
        self.current_state = othellostate.OthelloStateClass()
        self.gameover = False

    def get_simulator_state(self):
        return self.current_state

    def change_simulator_state(self, current_state):
        self.current_state = current_state.create_copy()

    def change_turn(self):
        new_turn = self.current_state.get_current_state()["current_player"] + 1
        new_turn %= self.numplayers

        if new_turn == 0:
            self.current_state.get_current_state()["current_player"] = self.numplayers
        else:
            self.current_state.get_current_state()["current_player"] = new_turn

    def print_board(self):
        curr_state = self.current_state.get_current_state()["state_val"]
        outp = "CURRENT BOARD : "
        for elem in curr_state:
            outp += "\n" + str(elem)
        return outp

    def take_action(self, action):
        actionvalue = action.get_action()
        position = actionvalue['position']
        value = actionvalue['value']

        # CHECK FOR NULL ACTION
        if value == -1:
            return [0.0] * self.numplayers

        self.current_state.get_current_state()["state_val"][position[0]][position[1]] = value

        # UPDATE THE BOARD
        i = position[0]
        j = position[1]
        self.color_coins(value, [i-1, j], "U", True)
        self.color_coins(value, [i+1, j], "D", True)
        self.color_coins(value, [i, j+1], "R", True)
        self.color_coins(value, [i, j-1], "L", True)
        self.color_coins(value, [i-1, j+1], "UR", True)
        self.color_coins(value, [i+1, j+1], "DR", True)
        self.color_coins(value, [i-1, j-1], "UL", True)
        self.color_coins(value, [i+1, j-1], "DL", True)

        self.gameover = self.is_terminal()

        reward = [0.0] * self.numplayers

        if self.winningplayer is not None:
            for player in xrange(self.numplayers):
                if player == self.winningplayer - 1:
                    reward[player] += 1.0
                else:
                    reward[player] -= 1.0

        return reward

    def color_coins(self, curr_turn, curr_posn, direction, do_color):
        i = curr_posn[0]
        j = curr_posn[1]

        if i >7 or i<0 or j>7 or j<0:
            return False
        elif self.current_state.get_current_state()["state_val"][i][j] == 0:
            return False

        if self.current_state.get_current_state()["state_val"][i][j] == curr_turn:
            return True
        else:
            if direction == "U":
                new_posn = [i-1, j]
            elif direction == "D":
                new_posn = [i+1, j]
            elif direction == "R":
                new_posn = [i, j+1]
            elif direction == "L":
                new_posn = [i, j-1]
            elif direction == "UR":
                new_posn = [i-1, j+1]
            elif direction == "DR":
                new_posn = [i+1, j+1]
            elif direction == "UL":
                new_posn = [i-1, j-1]
            elif direction == "DL":
                new_posn = [i+1, j-1]

            ret = self.color_coins(curr_turn, new_posn, direction, do_color)
            if ret == True:
                if do_color:
                    self.current_state.get_current_state()["state_val"][i][j] = curr_turn

            return ret

    def get_valid_actions(self, curr_player=-1):
        actions_list = []

        if curr_player == -1:
            value = self.current_state.get_current_state()["current_player"]
        else:
            value = curr_player

        curr_board = self.current_state.get_current_state()["state_val"]
        for i in xrange(8):
            for j in xrange(8):
                if curr_board[i][j] == 0:
                    possible_count = 0

                    if i>=1 and curr_board[i-1][j] != value:
                        possible_count += int(self.color_coins(value, [i-1, j], "U", False))
                    if i<=6 and curr_board[i+1][j] != value:
                        possible_count += int(self.color_coins(value, [i+1, j], "D", False))
                    if j<=6 and curr_board[i][j+1] != value:
                        possible_count += int(self.color_coins(value, [i, j+1], "R", False))
                    if j>=1 and curr_board[i][j-1] != value:
                        possible_count += int(self.color_coins(value, [i, j-1], "L", False))
                    if i>=1 and j<=6 and curr_board[i-1][j+1] != value:
                        possible_count += int(self.color_coins(value, [i-1, j+1], "UR", False))
                    if i<=6 and j<=6 and curr_board[i+1][j+1] != value:
                        possible_count += int(self.color_coins(value, [i+1, j+1], "DR", False))
                    if i>=1 and j>=1 and curr_board[i-1][j-1] != value:
                        possible_count += int(self.color_coins(value, [i-1, j-1], "UL", False))
                    if i<=6 and j>=1 and curr_board[i+1][j-1] != value:
                        possible_count += int(self.color_coins(value, [i+1, j-1], "DL", False))

                    if possible_count > 0:
                        action = {}
                        action['position'] = [i, j]
                        action['value'] = self.current_state.get_current_state()["current_player"]
                        actions_list.append(othelloaction.OthelloActionClass(action))

        #ALWAYS ADD NULL ACTION
        action = {}
        action['position'] = [-1, -1]
        action['value'] = -1
        actions_list.append(othelloaction.OthelloActionClass(action))
        return actions_list

    def is_terminal(self):
        for_player_1 = self.get_valid_actions(1)
        for_player_2 = self.get_valid_actions(2)

        if len(for_player_1) > 1 or len(for_player_2) > 1:
            return False
        else:
            return True
