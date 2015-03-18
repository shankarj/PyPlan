from abstract import absstate

'''
dice_config - Faces on the five dices. Including the ones rolled and the unrolled.
score_sheet - Scores of 13 categories. Zero based index.
current_roll - 1 - 3. One based index.
'''

class YahtzeeStateClass(absstate.AbstractState):
    def __init__(self):
        self.current_state = {
            "state_val": {
                    "current_roll": 0,
                    "dice_config": [1] * 5,
                    "score_sheet": [[None] * 2 for _ in xrange(13)]
            },
            "current_player": 1
        }

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state

    # RETURNS A NEW DEEP COPY OF THIS STATE CLASS.
    def create_copy(self):
        new_state = {
            "state_val":
                {
                    "current_roll": self.current_state["state_val"]["current_roll"],
                    "dice_config": list(self.current_state["state_val"]["dice_config"]),
                    "score_sheet": []
                },
            "current_player": self.current_state["current_player"]
        }

        for elem in self.current_state["state_val"]["score_sheet"]:
            new_state["state_val"]["score_sheet"].append(list(elem))

        new_state_obj = YahtzeeStateClass()
        new_state_obj.set_current_state(new_state)
        return new_state_obj