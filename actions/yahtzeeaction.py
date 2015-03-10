from abstract import absaction

'''

ACTION TYPE : NoOp / Select

Roll Action Value :
List of Dice to Roll - Ex. [0, 4]. Zero based index.

NoOp Action Value:
The category to select. (0 - 12)
Choose a category only when roll = 3

'''
class YahtzeeActionClass(absaction.AbstractAction):

	def __init__(self, action):
		self.actionvalue = action['value']
		self.actiontype = action['type']

	def get_action(self):
		temp = {}
		temp['type'] = self.actiontype
		temp['value'] = self.actionvalue
		return temp
