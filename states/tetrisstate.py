from abstract import absstate


class TetrisStateClass(absstate.AbstractState):
    def __init__(self):
        self.current_state = {
            "state_val": {
                "current_board": [[0] * 10 for _ in xrange(20)],
                "current_piece": None,
                "next_piece": None
            },

            "current_player" : 1
        }

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state

    # RETURNS A NEW DEEP COPY OF THIS STATE CLASS.
    def create_copy(self):
        new_state = {
            "state_val": {
                "current_board": [],
                "current_piece": self.current_state["state_val"]["current_piece"],
                "next_piece": self.current_state["state_val"]["next_piece"]
            },

            "current_player" : self.current_state["current_player"]
        }


        for elem in self.current_state["state_val"]["current_board"]:
            new_state["state_val"]["current_board"].append(list(elem))

        new_state_obj = TetrisStateClass()
        new_state_obj.set_current_state(new_state)
        return new_state_obj