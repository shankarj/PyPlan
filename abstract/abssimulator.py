import abc
from abc import ABCMeta

class AbstractSimulator:
	__metaclass__ = ABCMeta
	
	@abc.abstractmethod
	def __init__ (self, player_turn, num_players):
		raise NotImplementedError

	@abc.abstractmethod
	def reset_simulator(self):
		raise NotImplementedError

	@abc.abstractmethod
	def change_simulator_values(self, current_state, player_turn):
		raise NotImplementedError

	@abc.abstractmethod
	def take_action(self, action):
		"""
		
		This method takes the specified action over the current state
		and updates the current state after taking it. Ex. Moving a coin
		and updating the board after moving the coin
		
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def get_valid_actions(self):
		raise NotImplementedError

	@abc.abstractmethod
	def set_state(self, state):
		raise NotImplementedError

	@abc.abstractmethod
	def is_terminal(self):
		raise NotImplementedError

	@abc.abstractmethod
	def change_turn(self):
		raise NotImplementedError



