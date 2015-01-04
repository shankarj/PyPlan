import abc
from abc import ABCMeta

class AbstractAgent:
	__metaclass__ = ABCMeta

	@abc.abstractmethod
	def select_action(self, simulator):
		raise NotImplementedError