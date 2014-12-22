from abstract import absaction

class TicTacToeActionClass(absaction.AbstractAction):

	def __init__(self, **action):
		self.actionposition = action['position']
		self.action = action['value']

	def get_action(self):
		temp['position'] = self.actionposition
		temp['action'] = self.action
		return temp
