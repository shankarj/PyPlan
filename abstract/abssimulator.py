import abc
from abc import ABCMeta

class AbstractSimulator:
	__metaclass__ = ABCMeta

	@abc.abstractmethod
	def reset_simulator(self):
		raise NotImplementedError

	@abc.abstractmethod
	def change_simulator_state(self, current_state):
		raise NotImplementedError

	@abc.abstractmethod
	def get_simulator_state(self):
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
	def change_turn(self):
		raise NotImplementedError

	@abc.abstractmethod
	def create_copy(self):
		raise NotImplementedError

	@abc.abstractmethod
	def is_terminal(self):
		raise NotImplementedError

	@abc.abstractmethod
	def change_turn(self):
		raise NotImplementedError



