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
