from abstract import absstate

class TetrisStateClass(absstate.AbstractState):

	def __init__(self):
		self.current_state = {}
		self.current_state["state_val"] = {}
		self.current_state["state_val"] = {"current_board" : [[0] * 10 for _ in xrange(20)],
										   "current_piece" : None,
										   "next_piece" : None}

		self.current_state["current_player"] = 1

	def set_current_state(self, state):
		self.current_state = state

	def get_current_state(self):
		return self.current_state