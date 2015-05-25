from abstract import absstate

'''
1 - BLACK
2 - WHITE
'''

class OthelloStateClass(absstate.AbstractState):
    def __init__(self):
        self.current_state = {
            "state_val": [[0] * 8 for _ in xrange(8)],
            "current_player": 1
        }

        self.current_state["state_val"][3][3] = 2
        self.current_state["state_val"][3][4] = 1
        self.current_state["state_val"][4][3] = 1
        self.current_state["state_val"][4][4] = 2

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

        new_state_obj = OthelloStateClass()
        new_state_obj.set_current_state(new_state)
        return new_state_obj