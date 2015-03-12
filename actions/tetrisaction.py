from abstract import absaction

class TetrisActionClass(absaction.AbstractAction):

	def __init__(self, action):
		self.actionposition = action['position']
		self.actionpiece = action['piece_number']
		self.actionpiece_rot_num = action['rot_number']

	def get_action(self):
		temp = {}
		temp['position'] = self.actionposition
		temp['piece_number'] = self.actionpiece
		temp['rot_number'] = self.actionpiece_rot_num
		return temp
