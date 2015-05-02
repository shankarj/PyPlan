from abstract import absstate


class Connect4StateClass(absstate.AbstractState):
    def __init__(self, num_players):
        self.current_state = {
            "state_val": [0] * num_players,
            "current_player": 1
        }

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state

    def get_minified_repr(self):
        return [self.current_state["state_val"], self.current_state["current_player"]]

    def set_minified_rep(self, minified_val):
        self.current_state = {
            "state_val": minified_val[0],
            "current_player": minified_val[1]
        }

    # RETURNS A NEW DEEP COPY OF THIS STATE CLASS.
    def create_copy(self):
        new_state = {
            "state_val": list(self.current_state["state_val"]),
            "current_player": self.current_state["current_player"]
        }

        new_state_obj = Connect4StateClass(len(self.current_state["state_val"]))
        new_state_obj.set_current_state(new_state)
        return new_state_obj