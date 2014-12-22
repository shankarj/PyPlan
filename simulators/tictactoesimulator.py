from abstract import abssimulator
from actions import tictactoeaction
from copy import deepcopy

"""
Simulator Class for TicTacToe

NOTE :
------

1. self.winningplayer = None -> Implies that the game is a draw. 
							    Otherwise this variable holds the winning player's number.
								Player number 1 for X. 2 for O.
"""
class TicTacToeSimulatorClass(abssimulator.AbstractSimulator):

	def __init__ (self, playerturn, numplayers = 2):
		self.playerturn = playerturn
		self.numplayers = numplayers
		self.winningplayer = None

	def get_next_turn(self):
		self.playerturn += 1
		self.playerturn = self.playerturn % self.numplayers

		if self.playerturn == 0:
			self.playerturn = self.numplayers

		return self.playerturn
	
	def take_action(self, action):
		actionvalue = action.get_action()
		position = actionvalue['position']
		value = actionvalue['value']
		self.current_state[position[0]][position[1]] = value
	
	def get_valid_actions(self):
		actions_list = []

		for x in xrange(len(self.current_state)):
			for y in xrange(len(self.current_state[0])):
				if self.current_state[x][y] == 0:
					action['position'] = [x, y]
					action['value'] = self.playerturn
					actions_list.append(tictactoeaction.TicTacToeActionClass(action))


	def set_state(self, state):
		self.current_state = deepcopy(state)

	def get_winning_player(self):
		return self.winningplayer

	def is_terminal(self):		
		xcount = 0
		ocount = 0

		# Horizontal check for hit
		for x in xrange(len(self.current_state)):
			for y in xrange(len(self.current_state[0])):
				if self.current_state[x][y] == 1:
					xcount += 1
				elif self.current_state[x][y] == 2:
					ocount += 1

			if xcount == 3:
				self.winningplayer = 1
			elif ycount == 3:
				self.winningplayer = 2
			else:
				xcount = 0
				ocount = 0

		# Vertical check for hit
		if self.winningplayer == None:
			for y in xrange(len(self.current_state[0])):
				for x in xrange(len(self.current_state)):
					if self.current_state[x][y] == 1:
						xcount += 1
					elif self.current_state[x][y] == 2:
						ocount += 1

				if xcount == 3:
					self.winningplayer = 1
				elif ycount == 3:
					self.winningplayer = 2
				else:
					xcount = 0
					ocount = 0

		# Diagonal One Check for Hit
		x = 0
		y = 0
		xcount = 0
		ocount = 0

		if self.winningplayer == None:
			while x < len(self.current_state):
				if self.current_state[x][y] == 1:
					xcount += 1
				elif self.current_state[x][y] == 2:
					ocount += 1

				x += 1
				y += 1

				if xcount == 3:
					self.winningplayer = 1
				elif ycount == 3:
					self.winningplayer = 2
				else:
					xcount = 0
					ocount = 0

		# Diagonal Two Check for Hit
		x = 0
		y = len(self.current_state[0])
		xcount = 0
		ocount = 0

		if self.winningplayer == None:
			while x < len(self.current_state):
				if self.current_state[x][y] == 1:
					xcount += 1
				elif self.current_state[x][y] == 2:
					ocount += 1

				x += 1
				y -= 1

				if xcount == 3:
					self.winningplayer = 1
				elif ycount == 3:
					self.winningplayer = 2
				else:
					xcount = 0
				ocount = 0

		if self.winningplayer == None:
			return False
		else:
			return True


	def get_current_state(self):
		return self.current_state