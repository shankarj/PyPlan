import abc
from abc import ABCMeta

class AbstractAgent:
	__metaclass__ = ABCMeta

	@abc.abstractmethod
	def select_action(self, current_state):
		raise NotImplementedError

	@abc.abstractmethod
	def get_agent_name(self):
		raise NotImplementedError

	@abc.abstractmethod
	def create_copy(self):
		raise NotImplementedError