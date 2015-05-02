from abstract import absaction

class Connect4ActionClass(absaction.AbstractAction):

	def __init__(self, action):
		self.actionposition = action['position']
		self.action = action['value']

	def get_action(self):
		temp = {}
		temp['position'] = self.actionposition
		temp['value'] = self.action
		return temp

	def get_minified_repr(self):
		return [self.actionposition, self.action]

	def set_minified_repr(self, minified_val):
		self.actionposition = minified_val[0]
		self.action = minified_val[1]
