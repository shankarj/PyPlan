from abstract import absstate

class Connect4StateClass(absstate.AbstractState):

	def __init__(self, num_players):
		self.current_state = []

		for player in xrange(num_players):
			self.current_state.append(0)

	def set_current_state(self, state):
		self.current_state = state

	def get_current_state(self):
		return self.current_state