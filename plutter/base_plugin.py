from abc import ABCMeta, abstractmethod


class BasePlugin:
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_method_call(self, method_call, result):
        pass

    @property
    @abstractmethod
    def channel_name(self):
        pass
