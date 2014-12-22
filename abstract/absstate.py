import abc
from abc import ABCMeta

class AbstractState:
	__metaclass__ = ABCMeta

	@abc.abstractmethod
	def get_current_state(self):
		raise NotImplementedError

	@abc.abstractmethod
	def set_current_state(self):
		raise NotImplementedError