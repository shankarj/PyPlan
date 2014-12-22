from abstract import absstate

class TicTacToeStateClass(absstate.AbstractState):

	def __init__(self):
		self.current_state = [[0,0,0], [0,0,0], [0,0,0]]

	def set_current_state(self, state):
		self.current_state = state

	def get_current_state(self):
		return self.current_state