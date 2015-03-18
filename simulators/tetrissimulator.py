from abstract import abssimulator
from actions import tetrisaction
from states import tetrisstate
import random

class TetrisSimulatorClass(abssimulator.AbstractSimulator):
    def __init__(self, num_players):
        if num_players > 1:
            raise ValueError("Number of players cannot be more than 1 for tetris.")
        self.current_state = tetrisstate.TetrisStateClass()
        self.current_state.get_current_state()["state_val"]["current_piece"] = random.randrange(1, 6)
        self.current_state.get_current_state()["state_val"]["next_piece"] = random.randrange(1, 6)
        self.numplayers = num_players
        self.winningplayer = None
        self.gameover = False

    def create_copy(self):
        new_sim_obj = TetrisSimulatorClass(self.numplayers)
        new_sim_obj.change_simulator_state(self.current_state.create_copy())
        new_sim_obj.winningplayer = self.winningplayer
        new_sim_obj.gameover = self.gameover
        return new_sim_obj

    def reset_simulator(self):
        self.winningplayer = None
        self.current_state = tetrisstate.TetrisStateClass()
        self.current_state.get_current_state()["state_val"]["current_piece"] = random.randrange(1, 6)
        self.current_state.get_current_state()["state_val"]["next_piece"] = random.randrange(1, 6)
        self.gameover = False

    def get_simulator_state(self):
		return self.current_state

    def change_simulator_state(self, current_state):
        self.current_state = current_state.create_copy()

    def change_turn(self):
        self.current_state.get_current_state()["state_val"]["current_piece"] = self.current_state.get_current_state()["state_val"]["next_piece"]
        self.current_state.get_current_state()["state_val"]["next_piece"] = random.randrange(1, 6)
        self.gameover = self.is_terminal()

    #TETRIS SPECIFIC FUNCTION
    def get_piece_shape(self, piece_number, rotation_number=0):
        piece = None

        if piece_number == 1:
            if rotation_number == 0:
                piece = [[1,1],[1,0]]
            elif rotation_number == 1:
                piece = [[1,1],[0,1]]
            elif rotation_number == 2:
                piece = [[0,1],[1,1]]
            elif rotation_number == 3:
                piece = [[1,0],[1,1]]
        elif piece_number == 2:
            if rotation_number == 0:
                piece = [[1],[1],[1]]
            elif rotation_number == 1:
                piece = [[1,1,1]]
        elif piece_number == 3:
            if rotation_number == 0:
                piece = [[0,1,0], [1,1,1]]
            elif rotation_number == 1:
                piece = [[1,0],[1,1],[1,0]]
            elif rotation_number == 2:
                piece = [[1,1,1],[0,1,0]]
            elif rotation_number == 3:
                piece = [[0,1],[1,1],[0,1]]
        elif piece_number == 4:
            if rotation_number == 0:
                piece = [[1,1],[1,1]]
        elif piece_number == 5:
            if rotation_number == 0:
                piece = [[0,1,1],[1,1,0]]
            elif rotation_number == 1:
                piece = [[1,0], [1,1], [0,1]]
        elif piece_number == 6:
            if rotation_number == 0:
                piece = [[1,1,0],[0,1,1]]
            elif rotation_number == 1:
                piece = [[0,1], [1,1], [1,0]]

        return piece

    def take_action(self, action):
        action_val = action.get_action()
        x_position = action_val['position'][0]
        y_position = action_val['position'][1]
        piece = self.get_piece_shape(action_val['piece_number'], action_val['rot_number'])
        current_board = self.current_state.get_current_state()["state_val"]["current_board"]

        if piece is None:
            raise ValueError("Invalid rotation number.")

        # INSERT THE PIECE
        for x in xrange(len(piece)):
            for y in xrange(len(piece[0])):
                current_board[x_position+x][y_position+y] = piece[x][y]

        reward = [5.0] * self.numplayers

        # UPDATE THE BOARD
        for x in xrange(19, -1, -1):
            hit = True
            for y in xrange(10):
                if current_board[x][y] == 0:
                    hit = False
                    break
            if hit:
                reward[self.numplayers - 1] += 10.0
                for subx in xrange(x, -1, -1):
                    if subx == 0:
                        current_board[subx] = [0] * 10
                    else:
                        current_board[subx] = current_board[subx-1]

        return reward

    def get_valid_actions(self):
        actions_list = []
        current_board = self.current_state.get_current_state()["state_val"]["current_board"]
        current_piece_num = self.current_state.get_current_state()["state_val"]["current_piece"]
        board_height = len(current_board)
        board_width = len(current_board[0])

        for rot_num in xrange(0, 4):
            piece_shape = self.get_piece_shape(current_piece_num, rot_num)
            if piece_shape is not None:
                piece_width = len(piece_shape[0])
                piece_height = len(piece_shape)
                for y in xrange(10):
                    if y > (board_width - piece_width):
                        break
                    for x in xrange(20):
                        if x > (board_height - piece_height):
                            break
                        elif x == (board_height - piece_height):
                            action = {}
                            action['position'] = [x,y]
                            action['piece_number'] = current_piece_num
                            action['rot_number'] = rot_num
                            actions_list.append(tetrisaction.TetrisActionClass(action))
                            break
                        else:
                            if current_board[x][y] == 1:
                                break
                            # CHECK IF THE PIECE CAN BE PLACED AT THIS TOP LEFT POSITION
                            # WITH AT LEAST ONE PIECE IN ITS BOTTOM TO HOLD IT.
                            hold = False
                            for btm in xrange(piece_width):
                                if piece_shape[piece_height-1][btm] == 1:
                                    if current_board[x+piece_height][y+btm] == 1:
                                        hold = True
                                        break
                            if hold:
                                #COLLISION CHECK
                                collision = False
                                for subx in xrange(piece_height):
                                    for suby in range(piece_width):
                                        if piece_shape[subx][suby] == 1:
                                            if current_board[x+subx][y+suby] == 1:
                                                collision = True
                                                break
                                    if collision:
                                        break

                                if collision == False:
                                    action = {}
                                    action['position'] = [x,y]
                                    action['piece_number'] = current_piece_num
                                    action['rot_number'] = rot_num
                                    actions_list.append(tetrisaction.TetrisActionClass(action))
                                    hit = True
                                break
        return actions_list

    def is_terminal(self):
        if len(self.get_valid_actions()) > 0:
            return False
        else:
            return True

    def print_board(self):
        output = "CURRENT BOARD : \n"
        for x in xrange(20):
            output += str(self.current_state.get_current_state()["state_val"]["current_board"][x]) + "\n"

        return output