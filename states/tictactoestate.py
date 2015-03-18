from abstract import absstate

class TicTacToeStateClass(absstate.AbstractState):
    def __init__(self):
        self.current_state = {
            "state_val": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "current_player": 1
        }

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state

    # RETURNS A NEW DEEP COPY OF THIS STATE CLASS.
    def create_copy(self):
        new_state = {
            "state_val": [],
            "current_player": self.current_state["current_player"]
        }

        for elem in self.current_state["state_val"]:
            new_state["state_val"].append(list(elem))

        new_state_obj = TicTacToeStateClass()
        new_state_obj.set_current_state(new_state)
        return new_state_obj