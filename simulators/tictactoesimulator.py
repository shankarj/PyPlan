from abstract import abssimulator
from actions import tictactoeaction
from states import tictactoestate
from copy import deepcopy

"""
Simulator Class for TicTacToe

NOTE :
------

1. self.winningplayer = None -> Implies that the game is a draw. 
							    Otherwise this variable holds the winning player's number.
								Player number 1 for X. 2 for O.

2. Reward scheme : Win = +3.0. Lose = -3.0. Draw = 0. Every move = -1
"""


class TicTacToeSimulatorClass(abssimulator.AbstractSimulator):
	def __init__(self, num_players):
		self.current_state = tictactoestate.TicTacToeStateClass()
		self.numplayers = num_players
		self.winningplayer = None
		self.gameover = False

	def reset_simulator(self):
		self.winningplayer = None
		self.current_state = tictactoestate.TicTacToeStateClass()
		self.gameover = False

	def change_simulator_state(self, current_state):
		self.current_state = deepcopy(current_state)

	def change_turn(self):
		new_turn = self.current_state.get_current_state()["current_player"] + 1
		new_turn %= self.numplayers

		if new_turn == 0:
			self.current_state.get_current_state()["current_player"] = self.numplayers
		else:
			self.current_state.get_current_state()["current_player"] = new_turn

	def take_action(self, action):
		actionvalue = action.get_action()
		position = actionvalue['position']
		value = actionvalue['value']
		self.current_state.get_current_state()["state_val"][position[0]][position[1]] = value
		self.gameover = self.is_terminal()

		reward = [0.0] * self.numplayers
		reward[self.current_state.get_current_state()["current_player"] - 1] -= 1.0

		if self.winningplayer is not None:
			for player in xrange(self.numplayers):
				if player == self.winningplayer - 1:
					reward[player] += 10.0
				else:
					reward[player] -= 10.0

		return reward

	def get_valid_actions(self):
		actions_list = []

		for x in xrange(len(self.current_state.get_current_state()["state_val"])):
			for y in xrange(len(self.current_state.get_current_state()["state_val"][0])):
				if self.current_state.get_current_state()["state_val"][x][y] == 0:
					action = {}
					action['position'] = [x, y]
					action['value'] = self.current_state.get_current_state()["current_player"]
					actions_list.append(tictactoeaction.TicTacToeActionClass(action))

		return actions_list

	def is_terminal(self):
		xcount = 0
		ocount = 0

		current_state_val = self.current_state.get_current_state()["state_val"]
		current_player = self.current_state.get_current_state()["current_player"]

		# Horizontal check for hit
		for x in xrange(len(current_state_val)):
			for y in xrange(len(current_state_val[0])):
				if current_state_val[x][y] == 1:
					xcount += 1
				elif current_state_val[x][y] == 2:
					ocount += 1

			if xcount == 3:
				self.winningplayer = 1
				break
			elif ocount == 3:
				self.winningplayer = 2
				break
			else:
				xcount = 0
				ocount = 0

		# Vertical check for hit
		if self.winningplayer == None:
			for y in xrange(len(current_state_val[0])):
				for x in xrange(len(current_state_val)):
					if current_state_val[x][y] == 1:
						xcount += 1
					elif current_state_val[x][y] == 2:
						ocount += 1

				if xcount == 3:
					self.winningplayer = 1
					break
				elif ocount == 3:
					self.winningplayer = 2
					break
				else:
					xcount = 0
					ocount = 0

		# Diagonal One Check for Hit
		x = 0
		y = 0
		xcount = 0
		ocount = 0

		if self.winningplayer == None:
			while x < len(current_state_val):
				if current_state_val[x][y] == 1:
					xcount += 1
				elif current_state_val[x][y] == 2:
					ocount += 1

				x += 1
				y += 1

			if xcount == 3:
				self.winningplayer = 1
			elif ocount == 3:
				self.winningplayer = 2
			else:
				xcount = 0
				ocount = 0

		# Diagonal Two Check for Hit
		x = 0
		y = len(current_state_val[0]) - 1
		xcount = 0
		ocount = 0

		if self.winningplayer == None:
			while x < len(current_state_val):
				if current_state_val[x][y] == 1:
					xcount += 1
				elif current_state_val[x][y] == 2:
					ocount += 1

				x += 1
				y -= 1

			if xcount == 3:
				self.winningplayer = 1
			elif ocount == 3:
				self.winningplayer = 2
			else:
				xcount = 0
				ocount = 0

		if self.winningplayer == None:
			#CHECK IF THE BOARD IS FULL
			x = 0
			y = 0
			game_over = True

			for x in xrange(len(current_state_val)):
				for y in xrange(len(current_state_val[0])):
					if current_state_val[x][y] == 0:
						game_over = False
						break

			if game_over == True:
				return True
			else:
				return False
		else:
			return True
