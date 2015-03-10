from abstract import absstate

'''
dice_config - Faces on the five dices. Including the ones rolled and the unrolled.
score_sheet - Scores of 13 categories. Zero based index.
current_roll - 1 - 3. One based index.
'''

class YahtzeeStateClass(absstate.AbstractState):
    def __init__(self):
        self.score_sheet = [[None, None]] * 13
        self.current_roll = 1
        self.starting_player = 1
        self.dice_config = [1] * 5
        self.state_val = {"current_roll": self.current_roll,
                          "dice_config": self.dice_config,
                          "score_sheet": self.score_sheet}
        self.current_state = {"state_val": self.state_val,
                              "current_player": self.starting_player}

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state