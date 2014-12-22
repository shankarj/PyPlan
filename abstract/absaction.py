import abc
from abc import ABCMeta

class AbstractAction:
	__metaclass__ = ABCMeta

	@abc.abstractmethod
	def set_action(self, **action):
		raise NotImplementedError

	@abc.abstractmethod
	def valid_actions(self):
		raise NotImplementedError