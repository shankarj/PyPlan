import abc
from abc import ABCMeta

class AbstractSimulator:
	__metaclass__ = ABCMeta
	
	@abc.abstractmethod
	def __init__ (self, playerturn, numplayers = 2):
		raise NotImplementedError

	@abc.abstractmethod
	def take_action(self):
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
	def get_current_state(self):
		raise NotImplementedError

	@abc.abstractmethod
	def get_next_turn(self):
		raise NotImplementedError

	@abc.abstractmethod
	def get_winning_player(self):
		raise NotImplementedError


