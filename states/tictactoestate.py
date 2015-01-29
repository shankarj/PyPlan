from abstract import absstate


class TicTacToeStateClass(absstate.AbstractState):
    def __init__(self):
        self.state_val = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.starting_player = 1
        self.current_state = {"state_val": self.state_val, "current_player": self.starting_player}

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state