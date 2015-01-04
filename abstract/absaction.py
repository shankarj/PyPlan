import abc
from abc import ABCMeta

class AbstractAction:
	__metaclass__ = ABCMeta

	@abc.abstractmethod
	def get_action(self):
		raise NotImplementedError